"""
CallRevive AI — Notification model.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.business import Business


class NotificationType(str, enum.Enum):
    NEW_LEAD = "new_lead"
    HOT_LEAD = "hot_lead"
    APPOINTMENT = "appointment"
    DAILY_SUMMARY = "daily_summary"
    REVENUE_ALERT = "revenue_alert"
    MISSED_CALL = "missed_call"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"


class Notification(Base, UUIDMixin, TimestampMixin):
    """User notification dispatched via various channels."""

    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type", create_constraint=True),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, name="notification_channel", create_constraint=True),
        default=NotificationChannel.IN_APP,
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, default=dict, nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────────────
    user: Mapped[User] = relationship("User", back_populates="notifications")
    business: Mapped[Business] = relationship("Business", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.type.value} read={self.is_read}>"
