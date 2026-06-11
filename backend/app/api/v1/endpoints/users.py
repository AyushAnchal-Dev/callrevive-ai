"""CallRevive AI — User management endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DBSession
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserListResponse

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def list_users(
    db: DBSession,
    current_user: CurrentUser,
    page: int = 1,
    page_size: int = 20,
):
    """List users in the same business. Admin/manager only."""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    offset = (page - 1) * page_size
    query = select(User).where(User.business_id == current_user.business_id)
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    result = await db.execute(query.offset(offset).limit(page_size))
    users = result.scalars().all()
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update user profile."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Cannot update other users")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user
