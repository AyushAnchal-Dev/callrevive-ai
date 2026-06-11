"""
CallRevive AI — Notification service.

Create, list, and manage notification lifecycle.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.notification import (
    Notification,
    NotificationChannel,
    NotificationType,
)

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    business_id: UUID,
    type_: str,
    title: str,
    message: str,
    channel: str = "in_app",
    metadata: dict | None = None,
) -> Notification:
    """Create a new notification for a user."""
    notification = Notification(
        user_id=user_id,
        business_id=business_id,
        type=NotificationType(type_),
        title=title,
        message=message,
        channel=NotificationChannel(channel),
        is_read=False,
        metadata_=metadata or {},
        sent_at=datetime.now(timezone.utc),
    )
    db.add(notification)
    await db.flush()
    await db.refresh(notification)

    logger.info(
        "Created notification id=%s type=%s user=%s",
        notification.id,
        notification.type.value,
        user_id,
    )
    return notification


async def list_notifications(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Notification], int, int]:
    """
    List notifications for a user with pagination.

    Returns (notifications_list, total_count, unread_count).
    """
    count_query = select(func.count(Notification.id)).where(
        Notification.user_id == user_id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    unread_query = select(func.count(Notification.id)).where(
        Notification.user_id == user_id,
        Notification.is_read == False,  # noqa: E712
    )
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar_one()

    offset = (page - 1) * page_size
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    notifications = list(result.scalars().all())

    return notifications, total, unread_count


async def mark_as_read(db: AsyncSession, notification_id: UUID) -> Notification:
    """Mark a single notification as read."""
    stmt = select(Notification).where(Notification.id == notification_id)
    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()
    if notification is None:
        raise NotFoundException(
            message="Notification not found",
            resource="Notification",
            resource_id=str(notification_id),
        )

    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(notification)

    return notification


async def mark_all_as_read(db: AsyncSession, user_id: UUID) -> int:
    """
    Mark all unread notifications for a user as read.

    Returns the number of notifications updated.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True, read_at=now)
    )
    result = await db.execute(stmt)
    await db.flush()

    count = result.rowcount
    logger.info("Marked %d notifications as read for user %s", count, user_id)
    return count
