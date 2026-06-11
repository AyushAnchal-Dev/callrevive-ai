"""
CallRevive AI — Conversation model.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.call import Call
    from app.models.customer import Customer
    from app.models.business import Business


class ConversationChannel(str, enum.Enum):
    VOICE = "voice"
    WHATSAPP = "whatsapp"
    SMS = "sms"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Conversation(Base, UUIDMixin, TimestampMixin):
    """AI conversation with a customer across voice, WhatsApp, or SMS."""

    __tablename__ = "conversations"

    call_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("calls.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[ConversationChannel] = mapped_column(
        Enum(ConversationChannel, name="conversation_channel", create_constraint=True),
        nullable=False,
    )
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversation_status", create_constraint=True),
        default=ConversationStatus.ACTIVE,
        nullable=False,
    )
    messages: Mapped[list] = mapped_column(
        JSON, default=list, nullable=False
    )  # [{role, content, timestamp}]
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────────────
    call: Mapped[Call | None] = relationship("Call", back_populates="conversation")
    customer: Mapped[Customer] = relationship("Customer", back_populates="conversations")
    business: Mapped[Business] = relationship("Business", back_populates="conversations")

    @property
    def customer_name(self) -> str | None:
        return self.customer.name if self.customer else None

    @property
    def customer_phone(self) -> str | None:
        return self.customer.phone_number if self.customer else None

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} channel={self.channel.value} status={self.status.value}>"
