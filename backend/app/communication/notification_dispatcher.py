"""CallRevive AI — Multi-channel notification dispatcher."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """Routes notifications to appropriate channels."""

    async def dispatch(self, channel: str, recipient: str, title: str, message: str, metadata: dict | None = None) -> bool:
        """Dispatch a notification to the specified channel."""
        try:
            if channel == "whatsapp":
                from app.communication.whatsapp_client import get_whatsapp_service
                wa = get_whatsapp_service()
                wa.send_message(recipient, f"*{title}*\n\n{message}")
            elif channel == "sms":
                from app.communication.twilio_client import get_twilio_service
                twilio = get_twilio_service()
                twilio.send_sms(recipient, f"{title}: {message}")
            elif channel == "in_app":
                logger.info(f"In-app notification: {title} -> {recipient}")
            else:
                logger.warning(f"Unknown channel: {channel}")
                return False
            return True
        except Exception as e:
            logger.error(f"Notification dispatch failed: {e}")
            return False


def get_notification_dispatcher() -> NotificationDispatcher:
    return NotificationDispatcher()
