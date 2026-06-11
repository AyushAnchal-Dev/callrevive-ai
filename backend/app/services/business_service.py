"""
CallRevive AI — Business service.

CRUD and stats for multi-tenant business management.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.appointment import Appointment
from app.models.business import Business
from app.models.call import Call, CallStatus
from app.models.customer import Customer
from app.models.lead import Lead, LeadCategory, LeadStatus
from app.schemas.business import BusinessCreate, BusinessUpdate

logger = logging.getLogger(__name__)


async def create_business(
    db: AsyncSession,
    owner_id: UUID,
    data: BusinessCreate,
) -> Business:
    """Create a new business tenant owned by owner_id."""
    business = Business(
        name=data.name,
        category=data.category,
        phone_number=data.phone_number,
        whatsapp_number=data.whatsapp_number,
        email=data.email,
        address=data.address,
        settings=data.settings or {},
        timezone=data.timezone,
        default_currency=data.default_currency,
        supported_currencies=data.supported_currencies,
        owner_id=owner_id,
        is_active=True,
    )
    db.add(business)
    await db.flush()
    await db.refresh(business)

    logger.info("Created business id=%s name=%s owner=%s", business.id, business.name, owner_id)
    return business


async def get_business(db: AsyncSession, business_id: UUID) -> Business:
    """Fetch a business by ID. Raises NotFoundException if not found."""
    stmt = select(Business).where(Business.id == business_id)
    result = await db.execute(stmt)
    business = result.scalar_one_or_none()
    if business is None:
        raise NotFoundException(
            message="Business not found",
            resource="Business",
            resource_id=str(business_id),
        )
    return business


async def update_business(
    db: AsyncSession,
    business_id: UUID,
    data: BusinessUpdate,
) -> Business:
    """Partially update a business. Only non-None fields are applied."""
    business = await get_business(db, business_id)

    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        if hasattr(business, field):
            setattr(business, field, value)

    await db.flush()
    await db.refresh(business)

    logger.info("Updated business id=%s fields=%s", business_id, list(update_fields.keys()))
    return business


async def get_business_stats(db: AsyncSession, business_id: UUID) -> dict:
    """
    Compute aggregated statistics for a business dashboard.

    Returns a dict matching BusinessStatsResponse fields.
    """
    # Verify business exists
    business = await get_business(db, business_id)

    # Total customers
    r = await db.execute(
        select(func.count(Customer.id)).where(Customer.business_id == business_id)
    )
    total_customers = r.scalar_one()

    # Total calls
    r = await db.execute(
        select(func.count(Call.id)).where(Call.business_id == business_id)
    )
    total_calls = r.scalar_one()

    # Total missed calls
    r = await db.execute(
        select(func.count(Call.id)).where(
            Call.business_id == business_id,
            Call.status == CallStatus.MISSED,
        )
    )
    total_missed_calls = r.scalar_one()

    # Total leads
    r = await db.execute(
        select(func.count(Lead.id)).where(Lead.business_id == business_id)
    )
    total_leads = r.scalar_one()

    # Hot leads
    r = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.business_id == business_id,
            Lead.category == LeadCategory.HOT,
        )
    )
    hot_leads = r.scalar_one()

    # Total appointments
    r = await db.execute(
        select(func.count(Appointment.id)).where(Appointment.business_id == business_id)
    )
    total_appointments = r.scalar_one()

    # Total estimated revenue
    r = await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0)).where(
            Lead.business_id == business_id
        )
    )
    total_revenue_estimated = float(r.scalar_one())

    # Conversion rate
    r = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.business_id == business_id,
            Lead.status == LeadStatus.CONVERTED,
        )
    )
    converted_leads = r.scalar_one()
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0.0

    # Average lead score
    r = await db.execute(
        select(func.coalesce(func.avg(Lead.lead_score), 0)).where(
            Lead.business_id == business_id
        )
    )
    avg_lead_score = float(r.scalar_one())

    return {
        "business_id": business_id,
        "total_customers": total_customers,
        "total_calls": total_calls,
        "total_missed_calls": total_missed_calls,
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "total_appointments": total_appointments,
        "total_revenue_estimated": total_revenue_estimated,
        "currency": business.default_currency,
        "conversion_rate": round(conversion_rate, 2),
        "avg_lead_score": round(avg_lead_score, 2),
    }
