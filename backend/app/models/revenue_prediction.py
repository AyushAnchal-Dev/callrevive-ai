"""
CallRevive AI — RevenuePrediction model.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.lead import Lead
    from app.models.business import Business


class CompetitorRisk(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PredictionUrgency(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RevenuePrediction(Base, UUIDMixin, TimestampMixin):
    """AI-generated revenue prediction for a lead."""

    __tablename__ = "revenue_predictions"

    lead_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revenue_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_revenue: Mapped[float] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    conversion_probability: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    competitor_risk: Mapped[CompetitorRisk] = mapped_column(
        Enum(CompetitorRisk, name="competitor_risk", create_constraint=True),
        default=CompetitorRisk.LOW,
        nullable=False,
    )
    urgency: Mapped[PredictionUrgency] = mapped_column(
        Enum(PredictionUrgency, name="prediction_urgency", create_constraint=True),
        default=PredictionUrgency.MEDIUM,
        nullable=False,
    )
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    scoring_factors: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────────
    lead: Mapped[Lead] = relationship("Lead", back_populates="revenue_predictions")
    business: Mapped[Business] = relationship("Business", back_populates="revenue_predictions")

    def __repr__(self) -> str:
        return f"<RevenuePrediction id={self.id} score={self.revenue_score} prob={self.conversion_probability}>"
