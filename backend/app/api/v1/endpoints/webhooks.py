"""CallRevive AI — Twilio webhook endpoints."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models.call import Call
from app.models.customer import Customer
from app.voice.voice_handler import get_voice_handler

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


async def validate_twilio(request: Request) -> dict:
    """Validate incoming Twilio webhook signature and return form data."""
    if not settings.TWILIO_AUTH_TOKEN:
        # Skip validation in development
        form_data = await request.form()
        return dict(form_data)

    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    form_data = await request.form()
    params = dict(form_data)

    if not validator.validate(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    return params


@router.post("/twilio/voice", response_class=HTMLResponse)
async def twilio_voice_webhook(request: Request):
    """Handle incoming voice call status callbacks and inbound routing from Twilio."""
    params = await validate_twilio(request)
    call_status = params.get("CallStatus", "")
    call_sid = params.get("CallSid", "")
    from_number = params.get("From", "")
    to_number = params.get("To", "")

    logger.info(f"Voice webhook: {call_status} | SID: {call_sid} | From: {from_number}")

    # Missed call statuses (customer calls and hangs up without answer)
    if call_status in ("no-answer", "busy", "canceled", "failed"):
        logger.info(f"Missed call detected from {from_number}, triggering recovery task queue.")
        
        # Trigger Celery task to process the missed call and run the callback
        from app.worker.tasks.call_tasks import process_missed_call
        process_missed_call.delay({
            "call_sid": call_sid,
            "from": from_number,
            "to": to_number,
            # In production we associate it with the configured business by Twilio number
        })

    response = VoiceResponse()
    # If it is a new incoming call, say hello, hang up, and let the callback pipeline take over
    if call_status == "ringing":
        response.say("Thank you for calling. We are unable to answer right now, but our AI assistant will call you back immediately. Goodbye!", voice="Polly.Aditi", language="en-IN")
        response.hangup()
    else:
        response.say("Thank you. Goodbye!", voice="Polly.Aditi", language="en-IN")

    return HTMLResponse(content=str(response), media_type="application/xml")


@router.post("/twilio/voice/gather", response_class=HTMLResponse)
async def twilio_voice_gather(request: Request):
    """Handle speech input from Twilio Gather during inbound routing."""
    params = await validate_twilio(request)
    speech_result = params.get("SpeechResult", "")
    call_sid = params.get("CallSid", "")
    language = params.get("language", "en-IN")

    logger.info(f"Inbound Speech gathered: '{speech_result}' (CallSid: {call_sid})")

    handler = get_voice_handler()
    if speech_result:
        # Route speech processing to the unified VoiceHandler loop
        twiml_content = await handler.handle_speech_input(speech_result, call_sid, language)
    else:
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            language=language,
            action=f"{settings.BACKEND_URL}/api/v1/webhooks/twilio/voice/gather?language={language}",
            speech_timeout="auto",
            timeout=5
        )
        gather.say("I didn't catch that. Could you please repeat?", voice="Polly.Aditi", language=language)
        response.append(gather)
        twiml_content = str(response)

    return HTMLResponse(content=twiml_content, media_type="application/xml")


@router.post("/twilio/whatsapp", response_class=HTMLResponse)
async def twilio_whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from Twilio Sandbox."""
    params = await validate_twilio(request)
    from_number = params.get("From", "").replace("whatsapp:", "")
    body = params.get("Body", "")
    message_sid = params.get("MessageSid", "")

    logger.info(f"WhatsApp message from {from_number}: '{body}'")

    # Delegate WhatsApp message processing to Celery
    from app.worker.tasks.whatsapp_tasks import process_whatsapp_message
    process_whatsapp_message.delay(from_number, body)

    return HTMLResponse(content="<Response></Response>", media_type="application/xml")


@router.post("/twilio/recording")
async def twilio_recording_webhook(request: Request):
    """Handle recording status callbacks from Twilio."""
    params = await validate_twilio(request)
    recording_sid = params.get("RecordingSid", "")
    recording_url = params.get("RecordingUrl", "")
    call_sid = params.get("CallSid", "")
    recording_status = params.get("RecordingStatus", "")

    logger.info(f"Recording {recording_status}: SID={recording_sid} for CallSid={call_sid}")

    if recording_status == "completed":
        # Store recording in Backblaze B2 asynchronously
        from app.worker.tasks.call_tasks import store_recording
        store_recording.delay(recording_sid, recording_url, call_sid)

    return {"status": "ok"}
