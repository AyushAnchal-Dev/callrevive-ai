"""
CallRevive AI — Lead service.

CRUD, qualification, and revenue integration for leads.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.lead import Lead, LeadCategory, LeadStatus, LeadUrgency
from app.models.revenue_prediction import RevenuePrediction

logger = logging.getLogger(__name__)


async def create_lead(db: AsyncSession, data: dict) -> Lead:
    """
    Create a new lead record.

    ``data`` keys align with Lead model columns.
    """
    lead = Lead(**data)
    db.add(lead)
    await db.flush()
    await db.refresh(lead)

    logger.info("Created lead id=%s score=%s category=%s", lead.id, lead.lead_score, lead.category.value)
    return lead


async def get_lead(db: AsyncSession, lead_id: UUID) -> Lead:
    """Fetch a lead by ID. Raises NotFoundException if not found."""
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()
    if lead is None:
        raise NotFoundException(
            message="Lead not found",
            resource="Lead",
            resource_id=str(lead_id),
        )
    return lead


async def list_leads(
    db: AsyncSession,
    business_id: UUID,
    page: int = 1,
    page_size: int = 20,
    category: str | None = None,
    status: str | None = None,
    urgency: str | None = None,
) -> tuple[list[Lead], int]:
    """
    List leads for a business with optional filters and pagination.

    Returns (leads_list, total_count).
    """
    base_query = select(Lead).where(Lead.business_id == business_id)
    count_query = select(func.count(Lead.id)).where(Lead.business_id == business_id)

    if category is not None:
        try:
            lc = LeadCategory(category)
            base_query = base_query.where(Lead.category == lc)
            count_query = count_query.where(Lead.category == lc)
        except ValueError:
            pass

    if status is not None:
        try:
            ls = LeadStatus(status)
            base_query = base_query.where(Lead.status == ls)
            count_query = count_query.where(Lead.status == ls)
        except ValueError:
            pass

    if urgency is not None:
        try:
            lu = LeadUrgency(urgency)
            base_query = base_query.where(Lead.urgency == lu)
            count_query = count_query.where(Lead.urgency == lu)
        except ValueError:
            pass

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    stmt = base_query.order_by(Lead.lead_score.desc(), Lead.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    leads = list(result.scalars().all())

    return leads, total


async def update_lead(db: AsyncSession, lead_id: UUID, data: dict) -> Lead:
    """Partially update a lead. Only non-None fields in data are applied."""
    lead = await get_lead(db, lead_id)

    for field, value in data.items():
        if value is not None and hasattr(lead, field):
            setattr(lead, field, value)

    await db.flush()
    await db.refresh(lead)

    logger.info("Updated lead id=%s fields=%s", lead_id, list(data.keys()))
    return lead


async def update_lead_status(db: AsyncSession, lead_id: UUID, status: str) -> Lead:
    """Update a lead's status with timestamp tracking."""
    from datetime import datetime, timezone

    lead = await get_lead(db, lead_id)
    lead.status = LeadStatus(status)

    if status == LeadStatus.QUALIFIED.value:
        lead.qualified_at = datetime.now(timezone.utc)
    elif status == LeadStatus.CONVERTED.value:
        lead.converted_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(lead)

    logger.info("Updated lead id=%s status=%s", lead_id, status)
    return lead


async def get_hot_leads(db: AsyncSession, business_id: UUID) -> list[Lead]:
    """Fetch all hot leads for a business, sorted by score descending."""
    stmt = (
        select(Lead)
        .where(
            Lead.business_id == business_id,
            Lead.category == LeadCategory.HOT,
            Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.QUALIFIED]),
        )
        .order_by(Lead.lead_score.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_lead_with_revenue(db: AsyncSession, lead_id: UUID) -> dict:
    """
    Fetch a lead along with its latest revenue prediction.

    Returns a dict with lead data and revenue_prediction.
    """
    lead = await get_lead(db, lead_id)

    stmt = (
        select(RevenuePrediction)
        .where(RevenuePrediction.lead_id == lead_id)
        .order_by(RevenuePrediction.predicted_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    prediction = result.scalar_one_or_none()

    return {
        "lead": lead,
        "revenue_prediction": prediction,
    }
