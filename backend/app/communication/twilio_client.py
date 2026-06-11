"""CallRevive AI — Twilio REST client wrapper."""
from __future__ import annotations

import logging
from functools import lru_cache

from twilio.rest import Client
from twilio.request_validator import RequestValidator

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TwilioService:
    """Production wrapper for Twilio Voice and SMS."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER

    def make_call(self, to: str, from_: str, twiml_url: str, status_callback_url: str = "") -> str:
        """Initiate an outbound call and return the Call SID."""
        kwargs = {"url": twiml_url, "to": to, "from_": from_ or self.phone_number}
        if status_callback_url:
            kwargs["status_callback"] = status_callback_url
            kwargs["status_callback_event"] = ["initiated", "ringing", "answered", "completed"]
        call = self.client.calls.create(**kwargs)
        logger.info(f"Call initiated: {call.sid} to {to}")
        return call.sid

    def send_sms(self, to: str, body: str, from_: str = "") -> str:
        """Send an SMS message."""
        message = self.client.messages.create(
            to=to, from_=from_ or self.phone_number, body=body,
        )
        logger.info(f"SMS sent: {message.sid} to {to}")
        return message.sid

    def get_recording(self, recording_sid: str) -> dict:
        """Get recording details."""
        recording = self.client.recordings(recording_sid).fetch()
        return {
            "sid": recording.sid,
            "duration": recording.duration,
            "uri": recording.uri,
            "media_url": f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}",
        }

    def validate_signature(self, url: str, params: dict, signature: str) -> bool:
        """Validate Twilio webhook signature."""
        return self.validator.validate(url, params, signature)


@lru_cache(maxsize=1)
def get_twilio_service() -> TwilioService:
    return TwilioService()
