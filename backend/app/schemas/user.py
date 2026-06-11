"""
CallRevive AI — User schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Admin-initiated user creation."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: str = Field(default="agent", pattern="^(admin|manager|agent)$")
    phone_number: str | None = Field(default=None, max_length=20)
    business_id: UUID | None = None
    is_active: bool = True


class UserUpdate(BaseModel):
    """Partial update for a user profile."""

    full_name: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=20)
    role: str | None = Field(default=None, pattern="^(admin|manager|agent)$")
    business_id: UUID | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """Public user representation."""

    id: UUID
    email: str
    full_name: str
    role: str
    business_id: UUID | None = None
    is_active: bool
    phone_number: str | None = None
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Paginated list of users."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
