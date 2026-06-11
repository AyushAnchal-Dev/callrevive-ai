"""CallRevive AI — Notification endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func, update

from app.api.deps import CurrentUser, DBSession
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationListResponse

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(db: DBSession, current_user: CurrentUser, page: int = 1, page_size: int = 20):
    """List notifications for current user."""
    query = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    unread = (await db.execute(
        select(func.count()).where(Notification.user_id == current_user.id, Notification.is_read == False)
    )).scalar() or 0
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return NotificationListResponse(
        items=result.scalars().all(), total=total, unread_count=unread,
        page=page, page_size=page_size, pages=(total + page_size - 1) // page_size,
    )


@router.get("/unread-count")
async def get_unread_count(db: DBSession, current_user: CurrentUser):
    """Return the number of unread notifications for the current user."""
    count = (await db.execute(
        select(func.count()).where(Notification.user_id == current_user.id, Notification.is_read == False)
    )).scalar() or 0
    return {"count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(notification_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Mark a notification as read."""
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    notif.read_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(notif)
    return notif


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read_patch(notification_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Mark a notification as read (PATCH alias)."""
    return await mark_as_read(notification_id, db, current_user)


@router.put("/read-all", status_code=200)
async def mark_all_as_read(db: DBSession, current_user: CurrentUser):
    """Mark all notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"message": "All notifications marked as read"}


@router.patch("/read-all", status_code=200)
async def mark_all_as_read_patch(db: DBSession, current_user: CurrentUser):
    """Mark all notifications as read (PATCH alias)."""
    return await mark_all_as_read(db, current_user)


@router.delete("/{notification_id}", status_code=200)
async def delete_notification(notification_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Delete a notification."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.delete(notif)
    await db.commit()
    return {"message": "Notification deleted"}
