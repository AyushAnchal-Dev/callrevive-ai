"""
CallRevive AI — Customer schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    """Create a new customer record."""

    phone_number: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = None
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    category: str = "new"  # new, returning, vip
    metadata: Optional[dict] = None


class CustomerUpdate(BaseModel):
    """Partial update for a customer."""

    name: Optional[str] = None
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[dict] = None


class CustomerResponse(BaseModel):
    """Public customer representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    business_id: uuid.UUID
    category: str
    first_contact_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    total_calls: int = 0
    total_revenue: Decimal = Decimal("0")


class CustomerListResponse(BaseModel):
    """Paginated list of customers."""

    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    pages: int
