"""CallRevive AI — Call & CallRecording Pydantic schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CallCreate(BaseModel):
    business_id: uuid.UUID
    customer_id: uuid.UUID
    twilio_call_sid: str
    direction: str = "inbound"
    status: str = "missed"
    from_number: str
    to_number: str
    duration_seconds: int = 0
    started_at: Optional[datetime] = None


class CallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    customer_id: uuid.UUID
    twilio_call_sid: str
    direction: str
    status: str
    from_number: str
    to_number: str
    duration_seconds: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    has_recording: bool = False


class CallListResponse(BaseModel):
    items: list[CallResponse]
    total: int
    page: int
    page_size: int
    pages: int


class CallRecordingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    call_id: uuid.UUID
    recording_sid: str
    storage_url: str
    duration_seconds: int
    file_size_bytes: int
    format: str
    created_at: datetime
