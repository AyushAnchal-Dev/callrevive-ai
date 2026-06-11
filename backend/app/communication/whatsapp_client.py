"""CallRevive AI — WhatsApp messaging via Twilio Sandbox."""
from __future__ import annotations

import logging
from functools import lru_cache

from twilio.rest import Client

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """WhatsApp messaging via Twilio Sandbox."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER or "whatsapp:+14155238886"

    def send_message(self, to: str, body: str) -> str:
        """Send a WhatsApp message."""
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"
        message = self.client.messages.create(
            from_=self.from_number, to=to, body=body,
        )
        logger.info(f"WhatsApp sent: {message.sid} to {to}")
        return message.sid

    def send_appointment_confirmation(self, to: str, details: dict) -> str:
        """Send appointment confirmation via WhatsApp."""
        body = (
            f"✅ *Appointment Confirmed*\n\n"
            f"📋 *Service:* {details.get('title', 'Appointment')}\n"
            f"📅 *Date:* {details.get('date', 'TBD')}\n"
            f"⏰ *Time:* {details.get('time', 'TBD')}\n"
            f"⏱ *Duration:* {details.get('duration', 30)} minutes\n\n"
            f"Reply CANCEL to cancel or RESCHEDULE to change."
        )
        return self.send_message(to, body)

    def send_lead_summary(self, to: str, summary: dict) -> str:
        """Send lead summary to business owner via WhatsApp."""
        body = (
            f"🔔 *New Lead Alert*\n\n"
            f"👤 *Customer:* {summary.get('customer_name', 'Unknown')}\n"
            f"📞 *Phone:* {summary.get('phone', 'N/A')}\n"
            f"🎯 *Service:* {summary.get('service', 'N/A')}\n"
            f"⚡ *Score:* {summary.get('score', 0)}/100\n"
            f"💰 *Est. Revenue:* {summary.get('revenue', 'N/A')}\n"
            f"🏷 *Category:* {summary.get('category', 'warm').upper()}\n\n"
            f"Reply CALL to initiate callback."
        )
        return self.send_message(to, body)

    def send_followup_reminder(self, to: str, reminder_text: str) -> str:
        """Send follow-up reminder."""
        body = f"⏰ *Reminder*\n\n{reminder_text}"
        return self.send_message(to, body)


@lru_cache(maxsize=1)
def get_whatsapp_service() -> WhatsAppService:
    return WhatsAppService()
