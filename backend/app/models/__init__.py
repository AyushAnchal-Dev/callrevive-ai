"""
CallRevive AI — Model registry.

All SQLAlchemy models are imported here for convenient access.
"""

from __future__ import annotations

from app.models.user import User
from app.models.business import Business
from app.models.customer import Customer
from app.models.call import Call
from app.models.call_recording import CallRecording
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.appointment import Appointment
from app.models.notification import Notification
from app.models.revenue_prediction import RevenuePrediction
from app.models.analytics_event import AnalyticsEvent
from app.models.audit_log import AuditLog

__all__ = [
    "User",
    "Business",
    "Customer",
    "Call",
    "CallRecording",
    "Conversation",
    "Lead",
    "Appointment",
    "Notification",
    "RevenuePrediction",
    "AnalyticsEvent",
    "AuditLog",
]
