"""CallRevive AI — Settings endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.models.business import Business

router = APIRouter()


@router.get("/")
async def get_settings(db: DBSession, current_user: CurrentUser):
    """Get business settings."""
    if not current_user.business_id:
        raise HTTPException(status_code=404, detail="No business configured")
    result = await db.execute(select(Business).where(Business.id == current_user.business_id))
    biz = result.scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    return {
        "business_name": biz.name,
        "category": biz.category,
        "phone_number": biz.phone_number,
        "whatsapp_number": biz.whatsapp_number,
        "email": biz.email,
        "address": biz.address,
        "timezone": biz.timezone,
        "default_currency": biz.default_currency,
        "settings": biz.settings or {},
    }


@router.put("/")
async def update_settings(data: dict, db: DBSession, current_user: CurrentUser):
    """Update business settings."""
    result = await db.execute(select(Business).where(Business.id == current_user.business_id))
    biz = result.scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    allowed_fields = {"name", "category", "phone_number", "whatsapp_number", "email",
                      "address", "timezone", "default_currency"}
    for key, val in data.items():
        if key in allowed_fields:
            setattr(biz, key, val)

    await db.commit()
    await db.refresh(biz)
    return {"message": "Settings updated"}


@router.put("/notifications")
async def update_notification_prefs(data: dict, db: DBSession, current_user: CurrentUser):
    """Update notification preferences."""
    result = await db.execute(select(Business).where(Business.id == current_user.business_id))
    biz = result.scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    current_settings = biz.settings or {}
    current_settings["notification_preferences"] = data
    biz.settings = current_settings
    await db.commit()
    return {"message": "Notification preferences updated"}
