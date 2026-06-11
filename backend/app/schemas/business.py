"""
CallRevive AI — Business schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class BusinessCreate(BaseModel):
    """Create a new business tenant."""

    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    phone_number: str = Field(max_length=20)
    whatsapp_number: str | None = Field(default=None, max_length=20)
    email: EmailStr
    address: str | None = None
    settings: dict | None = Field(default_factory=dict)
    timezone: str = Field(default="Asia/Kolkata", max_length=50)
    default_currency: str = Field(default="INR", min_length=3, max_length=3)
    supported_currencies: list[str] = Field(default_factory=lambda: ["INR"])


class BusinessUpdate(BaseModel):
    """Partial update for a business."""

    name: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)
    whatsapp_number: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    settings: dict | None = None
    timezone: str | None = Field(default=None, max_length=50)
    default_currency: str | None = Field(default=None, min_length=3, max_length=3)
    supported_currencies: list[str] | None = None
    is_active: bool | None = None


class BusinessResponse(BaseModel):
    """Public business representation."""

    id: UUID
    name: str
    category: str
    phone_number: str
    whatsapp_number: str | None = None
    email: str
    address: str | None = None
    settings: dict
    timezone: str
    default_currency: str
    supported_currencies: list[str]
    owner_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BusinessStatsResponse(BaseModel):
    """Aggregated business statistics."""

    business_id: UUID
    total_customers: int = 0
    total_calls: int = 0
    total_missed_calls: int = 0
    total_leads: int = 0
    hot_leads: int = 0
    total_appointments: int = 0
    total_revenue_estimated: float = 0.0
    currency: str = "INR"
    conversion_rate: float = 0.0
    avg_lead_score: float = 0.0
