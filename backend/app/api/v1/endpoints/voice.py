"""CallRevive AI — Voice AI endpoints."""
from __future__ import annotations

import uuid
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.api.deps import CurrentUser, DBSession
from app.core.config import get_settings
from app.voice.voice_handler import get_voice_handler

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post("/initiate-callback", status_code=202)
async def initiate_callback(
    call_id: uuid.UUID, db: DBSession, current_user: CurrentUser
):
    """Start an AI-powered callback to a customer."""
    from sqlalchemy import select
    from app.models.call import Call
    from app.worker.tasks.call_tasks import initiate_ai_callback

    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Delegate the Twilio phone call dialer to Celery
    initiate_ai_callback.delay(str(call_id))

    call.status = "callback_initiated"
    await db.commit()
    return {"message": "AI callback initiated", "call_id": str(call_id)}


@router.post("/twiml/greeting", response_class=HTMLResponse)
async def twiml_greeting(request: Request):
    """Generate TwiML greeting with speech gather and initialize Redis history."""
    form = await request.form()
    params = dict(form)
    call_sid = params.get("CallSid", "")
    language = params.get("language", "en-IN")

    logger.info(f"Received Twilio callback answer. Initializing dialogue for CallSid: {call_sid}")

    # Initialize empty dialogue transcript in Redis cache
    handler = get_voice_handler()
    await handler._save_session_history(call_sid, [])

    # Return greeting gather
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        language=language,
        action=f"{settings.BACKEND_URL}/api/v1/voice/twiml/respond?language={language}",
        speech_timeout="auto",
        timeout=5,
    )
    gather.say(
        "Hello, we noticed we missed your call. How can we help you today?",
        voice="Polly.Aditi",
        language=language,
    )
    response.append(gather)
    
    # Goodbye fallback if they don't say anything
    response.say("We didn't hear a response. Goodbye!", voice="Polly.Aditi", language=language)
    
    return HTMLResponse(content=str(response), media_type="application/xml")


@router.post("/twiml/respond", response_class=HTMLResponse)
async def twiml_respond(request: Request):
    """Process speech input from Twilio Gather, query Gemini, and return the next turn's TwiML."""
    form = await request.form()
    params = dict(form)
    speech_result = params.get("SpeechResult", "")
    call_sid = params.get("CallSid", "")
    language = request.query_params.get("language", "en-IN")

    logger.info(f"Gathered speech from customer (CallSid: {call_sid}): '{speech_result}'")

    handler = get_voice_handler()
    
    if speech_result:
        # Pass input to the VoiceHandler to generate next response TwiML
        twiml_content = await handler.handle_speech_input(
            speech_text=speech_result,
            call_sid=call_sid,
            language=language
        )
    else:
        # Fallback if no speech detected
        response = VoiceResponse()
        response.say("I didn't catch that. Goodbye!", voice="Polly.Aditi", language=language)
        twiml_content = str(response)

    return HTMLResponse(content=twiml_content, media_type="application/xml")
