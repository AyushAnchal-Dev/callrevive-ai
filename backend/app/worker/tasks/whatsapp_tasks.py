"""CallRevive AI — WhatsApp processing and template message notification tasks."""
from __future__ import annotations

import logging
import uuid
import asyncio
from datetime import datetime, timezone

from app.worker.celery_app import celery_app
from app.db.session import SyncSessionLocal
from app.models.customer import Customer
from app.models.appointment import Appointment
from app.models.conversation import Conversation, ConversationChannel, ConversationStatus
from app.communication.whatsapp_client import get_whatsapp_service
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import VOICE_CONVERSATION_SYSTEM

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.whatsapp_tasks.send_whatsapp_followup")
def send_whatsapp_followup(customer_phone: str, message: str) -> dict:
    """Send a WhatsApp follow-up message."""
    wa = get_whatsapp_service()
    sid = wa.send_message(customer_phone, message)
    return {"message_sid": sid, "status": "sent"}


@celery_app.task(name="app.worker.tasks.whatsapp_tasks.send_appointment_confirmation", bind=True, max_retries=3)
def send_appointment_confirmation(self, appointment_id: str) -> dict:
    """Send appointment confirmation details to a customer via WhatsApp."""
    logger.info(f"Sending WhatsApp appointment confirmation for {appointment_id}")
    
    try:
        with SyncSessionLocal() as db:
            appt = db.query(Appointment).filter_by(id=uuid.UUID(appointment_id)).first()
            if not appt:
                logger.error(f"Appointment record not found: {appointment_id}")
                return {"status": "failed", "reason": "appointment_not_found"}

            customer = appt.customer
            
            # Format appointment details
            details = {
                "title": appt.title,
                "date": appt.scheduled_at.strftime("%Y-%m-%d"),
                "time": appt.scheduled_at.strftime("%I:%M %p"),
                "duration": appt.duration_minutes
            }

            # Send template via WhatsApp client
            whatsapp = get_whatsapp_service()
            msg_sid = whatsapp.send_appointment_confirmation(customer.phone_number, details)

            # Record confirmation status in database
            appt.confirmation_sent_via = "whatsapp"
            db.commit()

            logger.info(f"WhatsApp Confirmation sent: SID={msg_sid}")
            return {"message_sid": msg_sid, "status": "sent"}

    except Exception as exc:
        logger.error(f"Failed to send WhatsApp confirmation: {exc}")
        self.retry(countdown=60, exc=exc)


@celery_app.task(name="app.worker.tasks.whatsapp_tasks.send_appointment_reminder", bind=True, max_retries=3)
def send_appointment_reminder(self, appointment_id: str) -> dict:
    """Send appointment reminder alert prior to scheduled slot."""
    logger.info(f"Sending WhatsApp appointment reminder for {appointment_id}")
    
    try:
        with SyncSessionLocal() as db:
            appt = db.query(Appointment).filter_by(id=uuid.UUID(appointment_id)).first()
            if not appt:
                logger.error(f"Appointment record not found: {appointment_id}")
                return {"status": "failed", "reason": "appointment_not_found"}

            customer = appt.customer
            
            reminder_text = (
                f"Friendly reminder for your upcoming appointment:\n"
                f"*Service:* {appt.title}\n"
                f"*Time:* {appt.scheduled_at.strftime('%I:%M %p')} tomorrow.\n"
                f"We look forward to serving you!"
            )

            # Send via WhatsApp client
            whatsapp = get_whatsapp_service()
            msg_sid = whatsapp.send_followup_reminder(customer.phone_number, reminder_text)

            appt.reminder_sent = True
            db.commit()

            logger.info(f"WhatsApp Reminder sent: SID={msg_sid}")
            return {"message_sid": msg_sid, "status": "sent"}

    except Exception as exc:
        logger.error(f"Failed to send WhatsApp reminder: {exc}")
        self.retry(countdown=60, exc=exc)


@celery_app.task(name="app.worker.tasks.whatsapp_tasks.process_whatsapp_message", bind=True, max_retries=3)
def process_whatsapp_message(self, from_number: str, body: str) -> dict:
    """Chatbot pipeline: process incoming WhatsApp message through Gemini and reply."""
    logger.info(f"Processing incoming WhatsApp message from {from_number}")

    try:
        with SyncSessionLocal() as db:
            # 1. Look up customer by phone number
            customer = db.query(Customer).filter(
                (Customer.phone_number == from_number) | 
                (Customer.whatsapp_number == from_number)
            ).first()

            if not customer:
                # If unknown customer, let's create a placeholder link with the first active business
                from app.models.business import Business
                default_biz = db.query(Business).first()
                if not default_biz:
                    logger.error("No active business found in database. Cannot resolve customer link.")
                    return {"status": "failed", "reason": "no_business"}

                customer = Customer(
                    phone_number=from_number,
                    whatsapp_number=from_number,
                    business_id=default_biz.id,
                    category="new",
                    first_contact_at=datetime.now(timezone.utc),
                    last_contact_at=datetime.now(timezone.utc),
                )
                db.add(customer)
                db.commit()
                db.refresh(customer)

            # 2. Look up or create active WhatsApp Conversation session
            conversation = db.query(Conversation).filter_by(
                customer_id=customer.id,
                channel=ConversationChannel.WHATSAPP,
                status=ConversationStatus.ACTIVE
            ).first()

            if not conversation:
                conversation = Conversation(
                    customer_id=customer.id,
                    business_id=customer.business_id,
                    channel=ConversationChannel.WHATSAPP,
                    status=ConversationStatus.ACTIVE,
                    messages=[],
                    language=customer.business.settings.get("language", "en"),
                    started_at=datetime.now(timezone.utc),
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            # 3. Append customer message to transcript
            messages = list(conversation.messages)
            messages.append({
                "role": "user",
                "content": body,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            # 4. Generate dialogue response via Gemini
            transcript_lines = []
            for msg in messages:
                speaker = "Customer" if msg["role"] == "user" else "AI"
                transcript_lines.append(f"{speaker}: {msg['content']}")

            prompt = (
                "Conversation history so far:\n"
                + "\n".join(transcript_lines)
                + "\n\nAI Next Response (be friendly and concise, suitable for WhatsApp chat):"
                + "\n(Note: If the conversation is complete or customer says goodbye, append '[END]' at the very end)."
            )

            gemini = get_gemini_client()
            ai_reply = asyncio.run(
                gemini.generate(
                    prompt=prompt,
                    system_instruction=VOICE_CONVERSATION_SYSTEM,
                    model=gemini.fast_model,
                    temperature=0.5
                )
            )
            ai_reply = ai_reply.strip()

            # 5. Check if session has resolved
            is_completed = "[END]" in ai_reply
            clean_reply = ai_reply.replace("[END]", "").strip()

            # 6. Send the reply via WhatsApp
            whatsapp = get_whatsapp_service()
            msg_sid = whatsapp.send_message(customer.phone_number, clean_reply)

            # 7. Save AI message to DB
            messages.append({
                "role": "assistant",
                "content": clean_reply,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            conversation.messages = messages
            conversation.last_contact_at = datetime.now(timezone.utc)

            if is_completed:
                conversation.status = ConversationStatus.COMPLETED
                conversation.ended_at = datetime.now(timezone.utc)
                
                # Trigger lead qualification asynchronously
                from app.worker.tasks.lead_tasks import qualify_lead
                qualify_lead.delay(str(conversation.id))
                
                logger.info(f"WhatsApp session complete. Triggered qualification for {conversation.id}.")

            db.commit()
            return {"message_sid": msg_sid, "status": "processed"}

    except Exception as exc:
        logger.error(f"Failed to process WhatsApp message: {exc}")
        self.retry(countdown=60, exc=exc)
