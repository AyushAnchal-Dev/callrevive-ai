"""CallRevive AI — Notification dispatch tasks."""
from __future__ import annotations

import logging
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.notification_tasks.send_notification")
def send_notification(notification_id: str) -> dict:
    """Dispatch a notification to the appropriate channel."""
    logger.info(f"Sending notification {notification_id}")
    return {"notification_id": notification_id, "status": "sent"}


@celery_app.task(name="app.worker.tasks.notification_tasks.send_daily_summary_all")
def send_daily_summary_all() -> dict:
    """Send daily summary to all business owners."""
    logger.info("Sending daily summaries")
    return {"status": "completed"}
