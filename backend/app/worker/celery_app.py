"""CallRevive AI — Celery application configuration."""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "callrevive",
    broker=settings.CLOUDAMQP_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.worker.tasks.call_tasks",
        "app.worker.tasks.lead_tasks",
        "app.worker.tasks.notification_tasks",
        "app.worker.tasks.whatsapp_tasks",
        "app.worker.tasks.analytics_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.worker.tasks.call_tasks.*": {"queue": "calls"},
        "app.worker.tasks.lead_tasks.*": {"queue": "leads"},
        "app.worker.tasks.notification_tasks.*": {"queue": "notifications"},
        "app.worker.tasks.whatsapp_tasks.*": {"queue": "whatsapp"},
        "app.worker.tasks.analytics_tasks.*": {"queue": "analytics"},
    },
    beat_schedule={
        "daily-recommendations": {
            "task": "app.worker.tasks.lead_tasks.generate_daily_recommendations_all",
            "schedule": crontab(hour=8, minute=0),
        },
        "daily-summary": {
            "task": "app.worker.tasks.notification_tasks.send_daily_summary_all",
            "schedule": crontab(hour=20, minute=0),
        },
    },
)
