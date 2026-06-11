"""
CallRevive AI — Call model.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.customer import Customer
    from app.models.call_recording import CallRecording
    from app.models.conversation import Conversation


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatus(str, enum.Enum):
    MISSED = "missed"
    ANSWERED = "answered"
    CALLBACK_INITIATED = "callback_initiated"
    CALLBACK_COMPLETED = "callback_completed"
    FAILED = "failed"


class Call(Base, UUIDMixin, TimestampMixin):
    """Telephone call record linked to Twilio."""

    __tablename__ = "calls"

    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    twilio_call_sid: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    direction: Mapped[CallDirection] = mapped_column(
        Enum(CallDirection, name="call_direction", create_constraint=True),
        nullable=False,
    )
    status: Mapped[CallStatus] = mapped_column(
        Enum(CallStatus, name="call_status", create_constraint=True),
        default=CallStatus.MISSED,
        nullable=False,
    )
    from_number: Mapped[str] = mapped_column(String(20), nullable=False)
    to_number: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────────────
    business: Mapped[Business] = relationship("Business", back_populates="calls")
    customer: Mapped[Customer] = relationship("Customer", back_populates="calls")
    recording: Mapped[CallRecording | None] = relationship(
        "CallRecording", back_populates="call", uselist=False, cascade="all, delete-orphan"
    )
    conversation: Mapped[Conversation | None] = relationship(
        "Conversation", back_populates="call", uselist=False
    )

    @property
    def customer_name(self) -> str | None:
        return self.customer.name if self.customer else None

    @property
    def customer_phone(self) -> str | None:
        return self.customer.phone_number if self.customer else None

    @property
    def has_recording(self) -> bool:
        return self.recording is not None

    def __repr__(self) -> str:
        return f"<Call id={self.id} sid={self.twilio_call_sid} status={self.status.value}>"
