"""
CallRevive AI — Revenue prediction schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScoringFactors(BaseModel):
    """Individual scoring components used in revenue prediction."""

    urgency_score: float = Field(ge=0, le=1)
    service_type_score: float = Field(ge=0, le=1)
    estimated_value_score: float = Field(ge=0, le=1)
    business_category_score: float = Field(ge=0, le=1)
    sentiment_score: float = Field(ge=0, le=1)
    buying_intent_score: float = Field(ge=0, le=1)


class RevenueScoreResponse(BaseModel):
    """Public revenue score / prediction representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lead_id: uuid.UUID
    revenue_score: int = Field(ge=0, le=100)
    estimated_revenue: Decimal
    currency: str
    conversion_probability: float
    competitor_risk: str  # low, medium, high
    urgency: str
    recommendation: str
    scoring_factors: Optional[dict] = None
    predicted_at: datetime
    created_at: datetime


class RevenuePredictionCreate(BaseModel):
    """Payload to persist a new revenue prediction."""

    lead_id: uuid.UUID
    business_id: uuid.UUID
    revenue_score: int = Field(ge=0, le=100)
    estimated_revenue: Decimal
    currency: str = "INR"
    conversion_probability: float = Field(ge=0, le=1)
    competitor_risk: str = "medium"
    urgency: str = "medium"
    recommendation: str
    scoring_factors: Optional[dict] = None
