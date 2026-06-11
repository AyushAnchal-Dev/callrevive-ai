"""
CallRevive AI — Notification schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """Public notification representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID
    type: str
    title: str
    message: str
    channel: str
    is_read: bool
    metadata: Optional[dict] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated list of notifications with unread count."""

    items: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    pages: int
