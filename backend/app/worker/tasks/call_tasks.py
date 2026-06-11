"""CallRevive AI — Missed call processing and voice session callback tasks."""
from __future__ import annotations

import asyncio
import logging
import requests
from datetime import datetime, timezone
import uuid

from app.core.config import get_settings
from app.worker.celery_app import celery_app
from app.db.session import SyncSessionLocal
from app.models.customer import Customer
from app.models.call import Call, CallDirection, CallStatus
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.models.call_recording import CallRecording

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.worker.tasks.call_tasks.process_missed_call", bind=True, max_retries=3)
def process_missed_call(self, call_data: dict) -> dict:
    """Main missed call recovery pipeline.
    
    1. Look up or create customer
    2. Create call record
    3. Trigger AI callback task
    """
    logger.info(f"Processing missed call from {call_data.get('from', 'unknown')}")

    from_number = call_data.get("from", "")
    to_number = call_data.get("to", "")
    business_id = call_data.get("business_id")
    
    if not business_id:
        # Fallback to a default business if none supplied (for sandbox setup)
        from app.models.business import Business
        with SyncSessionLocal() as db:
            default_biz = db.query(Business).first()
            if default_biz:
                business_id = str(default_biz.id)
            else:
                logger.error("No business found in database. Cannot process call.")
                return {"status": "failed", "reason": "no_business"}

    try:
        with SyncSessionLocal() as db:
            # 1. Look up or create customer
            customer = db.query(Customer).filter_by(
                phone_number=from_number, business_id=uuid.UUID(business_id)
            ).first()
            
            if not customer:
                customer = Customer(
                    phone_number=from_number,
                    business_id=uuid.UUID(business_id),
                    category="new",
                    first_contact_at=datetime.now(timezone.utc),
                    last_contact_at=datetime.now(timezone.utc),
                )
                db.add(customer)
                db.commit()
                db.refresh(customer)

            # 2. Create inbound missed call record
            call = Call(
                business_id=uuid.UUID(business_id),
                customer_id=customer.id,
                twilio_call_sid=call_data.get("call_sid", f"missed-{uuid.uuid4().hex[:12]}"),
                direction=CallDirection.INBOUND,
                status=CallStatus.MISSED,
                from_number=from_number,
                to_number=to_number,
                started_at=datetime.now(timezone.utc),
                ended_at=datetime.now(timezone.utc),
            )
            db.add(call)
            db.commit()
            db.refresh(call)

            # 3. Trigger callback task
            initiate_ai_callback.delay(str(call.id))

            logger.info(f"Missed call processed and logged: Call ID={call.id}")
            return {"call_id": str(call.id), "status": "processed"}

    except Exception as exc:
        logger.error(f"Failed to process missed call: {exc}")
        self.retry(countdown=60, exc=exc)


@celery_app.task(name="app.worker.tasks.call_tasks.initiate_ai_callback", bind=True, max_retries=2)
def initiate_ai_callback(self, call_id: str) -> dict:
    """Initiate AI-powered callback to customer."""
    logger.info(f"Initiating AI callback for call {call_id}")
    
    try:
        with SyncSessionLocal() as db:
            # Fetch original call record
            original_call = db.query(Call).filter_by(id=uuid.UUID(call_id)).first()
            if not original_call:
                logger.error(f"Original call record not found: {call_id}")
                return {"status": "failed", "reason": "call_not_found"}

            customer = original_call.customer
            business = original_call.business

            # Determine callback language from business settings
            language = business.settings.get("language", "en-IN")

            # Initiate call via VoiceHandler
            from app.voice.voice_handler import get_voice_handler
            vh = get_voice_handler()
            
            # Initiate call (returns new Twilio CallSid)
            new_call_sid = asyncio.run(
                vh.initiate_callback(customer_phone=customer.phone_number, language=language)
            )

            # Log outbound callback session
            outbound_call = Call(
                business_id=business.id,
                customer_id=customer.id,
                twilio_call_sid=new_call_sid,
                direction=CallDirection.OUTBOUND,
                status=CallStatus.CALLBACK_INITIATED,
                from_number=original_call.to_number, # Dial from business number
                to_number=customer.phone_number, # Dial to customer
                started_at=datetime.now(timezone.utc),
            )
            db.add(outbound_call)
            db.commit()

            logger.info(f"AI Callback call created: Outbound CallSid={new_call_sid}")
            return {"call_sid": new_call_sid, "status": "initiated"}

    except Exception as exc:
        logger.error(f"Failed to initiate AI callback: {exc}")
        self.retry(countdown=60, exc=exc)


@celery_app.task(name="app.worker.tasks.call_tasks.complete_voice_session", bind=True)
def complete_voice_session(self, call_sid: str, history: list[dict]) -> dict:
    """End the call session, compile AI summary, and queue qualification tasks."""
    logger.info(f"Completing voice session for CallSid: {call_sid}")
    
    try:
        with SyncSessionLocal() as db:
            # Retrieve Call record
            call = db.query(Call).filter_by(twilio_call_sid=call_sid).first()
            if not call:
                logger.error(f"Call record not found for SID: {call_sid}")
                return {"status": "failed", "reason": "call_not_found"}

            # Calculate call duration
            ended_at = datetime.now(timezone.utc)
            duration = int((ended_at - call.started_at).total_seconds())

            # Update call record
            call.status = CallStatus.CALLBACK_COMPLETED
            call.ended_at = ended_at
            call.duration_seconds = duration

            # Generate AI summary
            from app.ai.conversation_summarizer import summarize_conversation
            summary_output = asyncio.run(summarize_conversation(history))
            
            # Create or update conversation record
            conversation = db.query(Conversation).filter_by(call_id=call.id).first()
            if not conversation:
                conversation = Conversation(
                    call_id=call.id,
                    customer_id=call.customer_id,
                    business_id=call.business_id,
                    channel=ConversationChannel.VOICE,
                    status=ConversationStatus.COMPLETED,
                    messages=history,
                    language=call.business.settings.get("language", "en"),
                    ai_summary=summary_output.summary,
                    started_at=call.started_at,
                    ended_at=ended_at,
                )
                db.add(conversation)
            else:
                conversation.status = ConversationStatus.COMPLETED
                conversation.messages = history
                conversation.ai_summary = summary_output.summary
                conversation.ended_at = ended_at
            
            db.commit()
            db.refresh(conversation)

            # Trigger background lead qualification
            from app.worker.tasks.lead_tasks import qualify_lead
            qualify_lead.delay(str(conversation.id))

            logger.info(f"Voice session completed. Conversation ID={conversation.id} qualified.")
            return {"conversation_id": str(conversation.id), "status": "completed"}

    except Exception as exc:
        logger.error(f"Error completing voice session: {exc}")
        raise exc


@celery_app.task(name="app.worker.tasks.call_tasks.store_recording", bind=True, max_retries=3)
def store_recording(self, recording_sid: str, recording_url: str, call_sid: str) -> dict:
    """Download call recording from Twilio and store in Backblaze B2."""
    logger.info(f"Downloading recording {recording_sid} from Twilio...")

    try:
        with SyncSessionLocal() as db:
            # Retrieve Call record
            call = db.query(Call).filter_by(twilio_call_sid=call_sid).first()
            if not call:
                logger.error(f"Call record not found for SID: {call_sid}")
                return {"status": "failed", "reason": "call_not_found"}

            # Fetch recording metadata from Twilio API
            from app.communication.twilio_client import get_twilio_service
            twilio = get_twilio_service()
            rec_metadata = twilio.get_recording(recording_sid)

            # Download mp3 binary
            media_url = rec_metadata["media_url"]
            auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            response = requests.get(media_url, auth=auth)
            
            if response.status_code != 200:
                raise Exception(f"Failed to download audio from Twilio: status={response.status_code}")

            # Upload to Backblaze B2 S3 storage
            from app.services.storage_service import get_storage_service
            storage = get_storage_service()
            storage_key = asyncio.run(
                storage.upload_file(
                    file_content=response.content,
                    file_name=f"{recording_sid}.mp3",
                    content_type="audio/mpeg"
                )
            )

            # Save recording details to database
            recording = CallRecording(
                call_id=call.id,
                recording_sid=recording_sid,
                storage_url=f"{settings.BACKBLAZE_ENDPOINT_URL}/{settings.BACKLAZE_BUCKET_NAME}/{storage_key}",
                storage_key=storage_key,
                duration_seconds=rec_metadata["duration"],
                file_size_bytes=len(response.content),
                format="mp3",
            )
            db.add(recording)
            db.commit()

            logger.info(f"Recording stored successfully in B2. Storage Key={storage_key}")
            return {"storage_key": storage_key, "status": "stored"}

    except Exception as exc:
        logger.error(f"Failed to store recording: {exc}")
        self.retry(countdown=120, exc=exc)
