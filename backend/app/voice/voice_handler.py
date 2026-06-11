"""CallRevive AI — Voice call flow handler with Redis session memory and Gemini dynamic dialogue."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from redis.asyncio import Redis

from app.core.config import get_settings
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import VOICE_CONVERSATION_SYSTEM
from app.voice.twiml_generator import generate_greeting, generate_response, generate_gather, generate_goodbye

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceHandler:
    """Manages the complete voice call flow with stateful AI dialogue."""

    async def _get_session_history(self, call_sid: str) -> list[dict[str, str]]:
        """Retrieve conversation history from Redis cache."""
        r = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            history_json = await r.get(f"call:session:{call_sid}")
            if history_json:
                return json.loads(history_json)
            return []
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return []
        finally:
            await r.close()

    async def _save_session_history(self, call_sid: str, history: list[dict[str, str]]) -> None:
        """Persist conversation history to Redis with a 2-hour expiry."""
        r = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            # Expire in 2 hours (7200 seconds)
            await r.set(f"call:session:{call_sid}", json.dumps(history), ex=7200)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
        finally:
            await r.close()

    async def initiate_callback(self, customer_phone: str, language: str = "en-IN") -> str:
        """Start outbound call to customer via Twilio."""
        from app.communication.twilio_client import get_twilio_service

        twilio = get_twilio_service()
        
        # Point the webhook callback url to our backend TwiML endpoints
        call_sid = twilio.make_call(
            to=customer_phone,
            from_=settings.TWILIO_PHONE_NUMBER,
            twiml_url=f"{settings.BACKEND_URL}/api/v1/voice/twiml/greeting?language={language}",
            status_callback_url=f"{settings.BACKEND_URL}/api/v1/webhooks/twilio/voice",
        )
        logger.info(f"Callback initiated to {customer_phone}, Twilio SID: {call_sid}")
        return call_sid

    async def handle_speech_input(self, speech_text: str, call_sid: str, language: str = "en-IN") -> str:
        """Process speech input through Gemini, update state, and return the TwiML response."""
        # 1. Fetch conversation history from Redis
        history = await self._get_session_history(call_sid)
        
        # 2. Append new user message
        timestamp = datetime.now(timezone.utc).isoformat()
        history.append({"role": "user", "content": speech_text, "timestamp": timestamp})

        # 3. Format prompt context for Gemini
        transcript_lines = []
        for turn in history:
            speaker = "Customer" if turn["role"] == "user" else "AI"
            transcript_lines.append(f"{speaker}: {turn['content']}")
        
        prompt = (
            "Conversation history so far:\n"
            + "\n".join(transcript_lines)
            + "\n\nAI Next Response (limit to 1-2 sentences):"
            + "\n(Note: If the customer's request is resolved, they say goodbye, or we have collected their details, "
              "conclude the conversation. Add '[END]' at the very end of your response to signal completion)."
        )

        try:
            # 4. Generate dynamic response via Gemini Client
            gemini = get_gemini_client()
            ai_response = await gemini.generate(
                prompt=prompt,
                system_instruction=VOICE_CONVERSATION_SYSTEM,
                model=gemini.fast_model,
                temperature=0.4
            )
            ai_response = ai_response.strip()
        except Exception as e:
            logger.error(f"Gemini generation error in voice loop: {e}")
            ai_response = "I understand. Let me get our team to call you back shortly. Have a nice day! [END]"

        # 5. Check if conversation has completed
        is_completed = "[END]" in ai_response
        clean_response = ai_response.replace("[END]", "").strip()

        # 6. Append AI message to history
        history.append({"role": "assistant", "content": clean_response, "timestamp": datetime.now(timezone.utc).isoformat()})
        await self._save_session_history(call_sid, history)

        if is_completed:
            logger.info(f"Voice call session completed for CallSid: {call_sid}. Triggering qualification.")
            # Trigger background Celery tasks to save transcript and qualify lead
            from app.worker.tasks.call_tasks import complete_voice_session
            complete_voice_session.delay(call_sid, history)
            return generate_goodbye(language)
        
        # 7. Otherwise, play AI reply and gather next user response
        return generate_gather(clean_response, language)


def get_voice_handler() -> VoiceHandler:
    return VoiceHandler()
