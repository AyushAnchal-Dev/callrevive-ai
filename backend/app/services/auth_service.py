"""
CallRevive AI — Authentication service.

Handles user registration, login, and token refresh with JWT management.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest

logger = logging.getLogger(__name__)


async def register_user(
    db: AsyncSession,
    data: RegisterRequest,
) -> tuple[User, str, str]:
    """
    Register a new user account.

    Returns the created user, access token, and refresh token.
    Raises ConflictException if email already exists.
    """
    # Check for existing email
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise ConflictException(message=f"User with email {data.email} already exists")

    # Create user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole(data.role),
        phone_number=data.phone_number,
        business_id=data.business_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    logger.info("Registered new user id=%s email=%s role=%s", user.id, user.email, user.role.value)

    # Generate tokens
    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
        email=user.email,
        business_id=user.business_id,
    )
    refresh_token = create_refresh_token(
        user_id=user.id,
        role=user.role.value,
        email=user.email,
        business_id=user.business_id,
    )

    return user, access_token, refresh_token


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> tuple[User, str, str]:
    """
    Authenticate a user by email and password.

    Returns the user, access token, and refresh token.
    Raises UnauthorizedException on invalid credentials.
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException(message="Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise UnauthorizedException(message="Invalid email or password")

    if not user.is_active:
        raise UnauthorizedException(message="Account is deactivated. Contact your administrator.")

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    logger.info("User authenticated id=%s email=%s", user.id, user.email)

    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
        email=user.email,
        business_id=user.business_id,
    )
    refresh_token = create_refresh_token(
        user_id=user.id,
        role=user.role.value,
        email=user.email,
        business_id=user.business_id,
    )

    return user, access_token, refresh_token


async def refresh_access_token(
    db: AsyncSession,
    refresh_token: str,
) -> tuple[str, str]:
    """
    Exchange a valid refresh token for a new token pair.

    Returns new access token and refresh token.
    Raises UnauthorizedException on invalid/expired refresh tokens.
    """
    try:
        payload = verify_token(refresh_token, expected_type="refresh")
    except Exception:
        raise UnauthorizedException(message="Invalid or expired refresh token")

    user_id = UUID(payload.sub)
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException(message="User no longer exists")

    if not user.is_active:
        raise UnauthorizedException(message="Account is deactivated")

    logger.info("Token refreshed for user id=%s", user.id)

    new_access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
        email=user.email,
        business_id=user.business_id,
    )
    new_refresh_token = create_refresh_token(
        user_id=user.id,
        role=user.role.value,
        email=user.email,
        business_id=user.business_id,
    )

    return new_access_token, new_refresh_token
