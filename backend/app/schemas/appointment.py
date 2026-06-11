"""CallRevive AI — Appointment Pydantic schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AppointmentCreate(BaseModel):
    lead_id: Optional[uuid.UUID] = None
    customer_id: uuid.UUID
    business_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=480)


class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=15, le=480)
    status: Optional[str] = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lead_id: Optional[uuid.UUID] = None
    customer_id: uuid.UUID
    business_id: uuid.UUID
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int
    status: str
    confirmation_sent_via: Optional[str] = None
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime


class AvailableSlotResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: int
