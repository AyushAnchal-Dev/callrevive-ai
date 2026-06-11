"""
CallRevive AI — User service.

CRUD operations for user management.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.user import User

logger = logging.getLogger(__name__)


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User:
    """Fetch a user by their UUID. Raises NotFoundException if not found."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException(
            message="User not found",
            resource="User",
            resource_id=str(user_id),
        )
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User:
    """Fetch a user by their email. Raises NotFoundException if not found."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException(
            message="User not found",
            resource="User",
            resource_id=email,
        )
    return user


async def list_users(
    db: AsyncSession,
    business_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[User], int]:
    """
    List users with optional business filter and pagination.

    Returns a tuple of (users_list, total_count).
    """
    base_query = select(User)
    count_query = select(func.count(User.id))

    if business_id is not None:
        base_query = base_query.where(User.business_id == business_id)
        count_query = count_query.where(User.business_id == business_id)

    # Total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginated results
    offset = (page - 1) * page_size
    stmt = base_query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    users = list(result.scalars().all())

    return users, total


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    data: dict,
) -> User:
    """
    Update a user's fields. Only non-None fields in data are applied.

    Returns the updated user. Raises NotFoundException if user doesn't exist.
    """
    user = await get_user_by_id(db, user_id)

    for field, value in data.items():
        if value is not None and hasattr(user, field):
            setattr(user, field, value)

    await db.flush()
    await db.refresh(user)

    logger.info("Updated user id=%s fields=%s", user_id, list(data.keys()))
    return user
