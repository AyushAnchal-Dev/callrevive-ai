"""
CallRevive AI — Lead schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.revenue import RevenueScoreResponse


class LeadCreate(BaseModel):
    """Create a new lead."""

    customer_id: uuid.UUID
    business_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    service_requested: Optional[str] = None
    category: str = "warm"  # hot, warm, cold
    lead_score: int = Field(default=50, ge=0, le=100)
    urgency: str = "medium"
    budget_range: Optional[str] = None
    purchase_readiness: str = "considering"
    customer_intent: str = "general"
    qualification_notes: Optional[str] = None
    estimated_revenue: Optional[Decimal] = None
    currency: str = "INR"


class LeadUpdate(BaseModel):
    """Partial update for a lead."""

    service_requested: Optional[str] = None
    category: Optional[str] = None
    lead_score: Optional[int] = Field(default=None, ge=0, le=100)
    urgency: Optional[str] = None
    budget_range: Optional[str] = None
    purchase_readiness: Optional[str] = None
    customer_intent: Optional[str] = None
    qualification_notes: Optional[str] = None
    estimated_revenue: Optional[Decimal] = None
    currency: Optional[str] = None


class LeadStatusUpdate(BaseModel):
    """Update only the status of a lead."""

    status: str  # new, contacted, qualified, converted, lost


class LeadResponse(BaseModel):
    """Public lead representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID
    business_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    service_requested: Optional[str] = None
    category: str
    lead_score: int
    urgency: str
    budget_range: Optional[str] = None
    purchase_readiness: str
    customer_intent: str
    qualification_notes: Optional[str] = None
    status: str
    estimated_revenue: Optional[Decimal] = None
    currency: str
    qualified_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None


class LeadListResponse(BaseModel):
    """Paginated list of leads."""

    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
    pages: int


class LeadWithRevenueResponse(LeadResponse):
    """Lead response enriched with revenue prediction data."""

    revenue_score: Optional[RevenueScoreResponse] = None
