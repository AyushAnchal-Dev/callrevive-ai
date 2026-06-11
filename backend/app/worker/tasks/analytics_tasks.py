"""CallRevive AI — Analytics event recording tasks."""
from __future__ import annotations

import logging
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.analytics_tasks.record_analytics_event")
def record_analytics_event(business_id: str, event_type: str, event_data: dict) -> dict:
    """Record an analytics event."""
    logger.info(f"Recording analytics event: {event_type} for business {business_id}")
    return {"status": "recorded"}


@celery_app.task(name="app.worker.tasks.analytics_tasks.generate_daily_report")
def generate_daily_report(business_id: str) -> dict:
    """Generate daily analytics report for a business."""
    logger.info(f"Generating daily report for business {business_id}")
    return {"business_id": business_id, "status": "generated"}
