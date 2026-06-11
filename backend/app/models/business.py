"""
CallRevive AI — Business model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.call import Call
    from app.models.conversation import Conversation
    from app.models.lead import Lead
    from app.models.appointment import Appointment
    from app.models.notification import Notification
    from app.models.revenue_prediction import RevenuePrediction
    from app.models.analytics_event import AnalyticsEvent
    from app.models.audit_log import AuditLog


class Business(Base, UUIDMixin, TimestampMixin):
    """Business entity — the tenant that owns customers, calls, leads, etc."""

    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    whatsapp_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    timezone: Mapped[str] = mapped_column(
        String(50), default="Asia/Kolkata", nullable=False
    )
    default_currency: Mapped[str] = mapped_column(
        String(3), default="INR", nullable=False
    )
    supported_currencies: Mapped[list] = mapped_column(
        JSON, default=lambda: ["INR"], nullable=False
    )
    owner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Relationships ──────────────────────────────────────────────
    owner: Mapped[User] = relationship(
        "User", foreign_keys=[owner_id]
    )
    users: Mapped[list[User]] = relationship(
        "User", back_populates="business", foreign_keys="User.business_id"
    )
    customers: Mapped[list[Customer]] = relationship(
        "Customer", back_populates="business", cascade="all, delete-orphan"
    )
    calls: Mapped[list[Call]] = relationship(
        "Call", back_populates="business", cascade="all, delete-orphan"
    )
    conversations: Mapped[list[Conversation]] = relationship(
        "Conversation", back_populates="business", cascade="all, delete-orphan"
    )
    leads: Mapped[list[Lead]] = relationship(
        "Lead", back_populates="business", cascade="all, delete-orphan"
    )
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment", back_populates="business", cascade="all, delete-orphan"
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification", back_populates="business", cascade="all, delete-orphan"
    )
    revenue_predictions: Mapped[list[RevenuePrediction]] = relationship(
        "RevenuePrediction", back_populates="business", cascade="all, delete-orphan"
    )
    analytics_events: Mapped[list[AnalyticsEvent]] = relationship(
        "AnalyticsEvent", back_populates="business", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog", back_populates="business", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Business id={self.id} name={self.name}>"
