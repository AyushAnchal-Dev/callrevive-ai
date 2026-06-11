"""
CallRevive AI — Customer model.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.call import Call
    from app.models.conversation import Conversation
    from app.models.lead import Lead
    from app.models.appointment import Appointment


class CustomerCategory(str, enum.Enum):
    """Customer categorisation."""

    NEW = "new"
    RETURNING = "returning"
    VIP = "vip"


class Customer(Base, UUIDMixin, TimestampMixin):
    """A customer belonging to a specific business."""

    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("phone_number", "business_id", name="uq_customer_phone_business"),
    )

    phone_number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[CustomerCategory] = mapped_column(
        Enum(CustomerCategory, name="customer_category", create_constraint=True),
        default=CustomerCategory.NEW,
        nullable=False,
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, default=dict, nullable=True
    )
    first_contact_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_contact_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────────────
    business: Mapped[Business] = relationship("Business", back_populates="customers")
    calls: Mapped[list[Call]] = relationship(
        "Call", back_populates="customer", cascade="all, delete-orphan"
    )
    conversations: Mapped[list[Conversation]] = relationship(
        "Conversation", back_populates="customer", cascade="all, delete-orphan"
    )
    leads: Mapped[list[Lead]] = relationship(
        "Lead", back_populates="customer", cascade="all, delete-orphan"
    )
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment", back_populates="customer", cascade="all, delete-orphan"
    )

    @property
    def total_calls(self) -> int:
        return len(self.calls)

    @property
    def total_revenue(self) -> float:
        return sum(float(lead.estimated_revenue or 0.0) for lead in self.leads if lead.status.value == "converted")

    def __repr__(self) -> str:
        return f"<Customer id={self.id} phone={self.phone_number}>"
