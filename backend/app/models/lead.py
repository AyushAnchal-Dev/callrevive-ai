"""
CallRevive AI — Lead model.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.business import Business
    from app.models.conversation import Conversation
    from app.models.appointment import Appointment
    from app.models.revenue_prediction import RevenuePrediction


class LeadCategory(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class LeadUrgency(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PurchaseReadiness(str, enum.Enum):
    READY = "ready"
    CONSIDERING = "considering"
    BROWSING = "browsing"


class CustomerIntent(str, enum.Enum):
    SERVICE = "service"
    PRODUCT = "product"
    COMPLAINT = "complaint"
    APPOINTMENT = "appointment"
    GENERAL = "general"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class Lead(Base, UUIDMixin, TimestampMixin):
    """A qualified lead extracted from a customer conversation."""

    __tablename__ = "leads"

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
    conversation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    service_requested: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[LeadCategory] = mapped_column(
        Enum(LeadCategory, name="lead_category", create_constraint=True),
        default=LeadCategory.WARM,
        nullable=False,
    )
    lead_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    urgency: Mapped[LeadUrgency] = mapped_column(
        Enum(LeadUrgency, name="lead_urgency", create_constraint=True),
        default=LeadUrgency.MEDIUM,
        nullable=False,
    )
    budget_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_readiness: Mapped[PurchaseReadiness] = mapped_column(
        Enum(PurchaseReadiness, name="purchase_readiness", create_constraint=True),
        default=PurchaseReadiness.BROWSING,
        nullable=False,
    )
    customer_intent: Mapped[CustomerIntent] = mapped_column(
        Enum(CustomerIntent, name="customer_intent", create_constraint=True),
        default=CustomerIntent.GENERAL,
        nullable=False,
    )
    qualification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status", create_constraint=True),
        default=LeadStatus.NEW,
        nullable=False,
    )
    estimated_revenue: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    qualified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    converted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────────────
    customer: Mapped[Customer] = relationship("Customer", back_populates="leads")
    business: Mapped[Business] = relationship("Business", back_populates="leads")
    conversation: Mapped[Conversation | None] = relationship("Conversation")
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment", back_populates="lead", cascade="all, delete-orphan"
    )
    revenue_predictions: Mapped[list[RevenuePrediction]] = relationship(
        "RevenuePrediction", back_populates="lead", cascade="all, delete-orphan"
    )

    @property
    def customer_name(self) -> str | None:
        return self.customer.name if self.customer else None

    @property
    def customer_phone(self) -> str | None:
        return self.customer.phone_number if self.customer else None

    def __repr__(self) -> str:
        return f"<Lead id={self.id} score={self.lead_score} status={self.status.value}>"
