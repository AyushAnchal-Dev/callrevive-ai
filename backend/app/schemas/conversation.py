"""CallRevive AI — Conversation Pydantic schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ConversationMessage(BaseModel):
    role: str  # "customer", "ai", "system"
    content: str
    timestamp: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    call_id: Optional[uuid.UUID] = None
    customer_id: uuid.UUID
    business_id: uuid.UUID
    channel: str
    status: str
    messages: list[dict]
    language: str
    ai_summary: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int
    pages: int
