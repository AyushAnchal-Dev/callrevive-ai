"""CallRevive AI — Business management endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DBSession
from app.models.business import Business
from app.models.lead import Lead
from app.models.call import Call
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse, BusinessStatsResponse

router = APIRouter()


@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(data: BusinessCreate, db: DBSession, current_user: CurrentUser):
    """Create a new business."""
    business = Business(
        name=data.name,
        category=data.category,
        phone_number=data.phone_number,
        email=data.email,
        whatsapp_number=getattr(data, "whatsapp_number", None),
        address=getattr(data, "address", None),
        timezone=getattr(data, "timezone", "Asia/Kolkata"),
        default_currency=getattr(data, "default_currency", "INR"),
        owner_id=current_user.id,
        is_active=True,
    )
    db.add(business)
    await db.commit()
    await db.refresh(business)

    current_user.business_id = business.id
    await db.commit()
    return business


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get business details."""
    result = await db.execute(select(Business).where(Business.id == business_id))
    biz = result.scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    return biz


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: uuid.UUID, data: BusinessUpdate, db: DBSession, current_user: CurrentUser
):
    """Update business details."""
    result = await db.execute(select(Business).where(Business.id == business_id))
    biz = result.scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    if biz.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(biz, key, val)
    await db.commit()
    await db.refresh(biz)
    return biz


@router.get("/{business_id}/stats", response_model=BusinessStatsResponse)
async def get_business_stats(business_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get business-level statistics."""
    total_leads = (await db.execute(
        select(func.count()).where(Lead.business_id == business_id)
    )).scalar() or 0
    hot_leads = (await db.execute(
        select(func.count()).where(Lead.business_id == business_id, Lead.category == "hot")
    )).scalar() or 0
    total_calls = (await db.execute(
        select(func.count()).where(Call.business_id == business_id)
    )).scalar() or 0
    missed_calls = (await db.execute(
        select(func.count()).where(Call.business_id == business_id, Call.status == "missed")
    )).scalar() or 0

    return BusinessStatsResponse(
        total_leads=total_leads,
        hot_leads=hot_leads,
        total_calls=total_calls,
        missed_calls=missed_calls,
        recovery_rate=round(((total_calls - missed_calls) / max(total_calls, 1)) * 100, 1),
    )
