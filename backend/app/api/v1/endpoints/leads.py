"""CallRevive AI — Lead management endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DBSession
from app.models.lead import Lead
from app.models.revenue_prediction import RevenuePrediction
from app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadStatusUpdate, LeadResponse,
    LeadListResponse, LeadWithRevenueResponse,
)
from app.schemas.revenue import RevenueScoreResponse

router = APIRouter()


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    db: DBSession,
    current_user: CurrentUser,
    page: int = 1,
    page_size: int = 20,
    category: str | None = None,
    status: str | None = None,
    urgency: str | None = None,
):
    """List leads with filters."""
    query = select(Lead).options(joinedload(Lead.customer)).where(Lead.business_id == current_user.business_id)
    if category:
        query = query.where(Lead.category == category)
    if status:
        query = query.where(Lead.status == status)
    if urgency:
        query = query.where(Lead.urgency == urgency)
    query = query.order_by(Lead.lead_score.desc())

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return LeadListResponse(
        items=result.scalars().all(), total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/hot", response_model=list[LeadResponse])
async def get_hot_leads(db: DBSession, current_user: CurrentUser):
    """Get hot leads requiring immediate action."""
    result = await db.execute(
        select(Lead)
        .options(joinedload(Lead.customer))
        .where(Lead.business_id == current_user.business_id, Lead.category == "hot")
        .where(Lead.status.in_(["new", "contacted"]))
        .order_by(Lead.lead_score.desc())
        .limit(20)
    )
    return result.scalars().all()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get lead details."""
    result = await db.execute(select(Lead).options(joinedload(Lead.customer)).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: uuid.UUID, data: LeadUpdate, db: DBSession, current_user: CurrentUser
):
    """Update lead information."""
    result = await db.execute(select(Lead).options(joinedload(Lead.customer)).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(lead, key, val)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.put("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: uuid.UUID, data: LeadStatusUpdate, db: DBSession, current_user: CurrentUser
):
    """Update lead status."""
    result = await db.execute(select(Lead).options(joinedload(Lead.customer)).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    from datetime import datetime, timezone
    lead.status = data.status
    if data.status == "qualified":
        lead.qualified_at = datetime.now(timezone.utc)
    elif data.status == "converted":
        lead.converted_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/{lead_id}/revenue-score", response_model=RevenueScoreResponse)
async def get_lead_revenue_score(lead_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get the Revenue Recovery Score for a lead."""
    result = await db.execute(
        select(RevenuePrediction).where(RevenuePrediction.lead_id == lead_id)
        .order_by(RevenuePrediction.created_at.desc())
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=404, detail="Revenue score not yet calculated")
    return prediction
