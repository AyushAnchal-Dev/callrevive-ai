"""
CallRevive AI — Auth schemas.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    """Email + password login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class RegisterRequest(BaseModel):
    """New user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)
    role: str = Field(default="admin", pattern="^(admin|manager|agent)$")
    phone_number: str | None = Field(default=None, max_length=20)
    business_id: UUID | None = None

    # Frontend signup fields
    name: str | None = None
    phone: str | None = None
    businessName: str | None = None
    businessCategory: str | None = None

    @model_validator(mode="after")
    def populate_fields(self) -> RegisterRequest:
        if not self.full_name and self.name:
            self.full_name = self.name
        if not self.phone_number and self.phone:
            self.phone_number = self.phone
        if not self.full_name:
            raise ValueError("full_name is required")
        return self


class TokenResponse(BaseModel):
    """JWT token pair returned on login/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=1800, description="Access token lifetime in seconds")


class RefreshTokenRequest(BaseModel):
    """Request to exchange a refresh token for a new access token."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Initiate password reset."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Complete password reset with token."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class PasswordChangeRequest(BaseModel):
    """Authenticated password change."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
