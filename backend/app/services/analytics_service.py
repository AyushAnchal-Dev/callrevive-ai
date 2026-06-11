"""
CallRevive AI — Analytics service.

Dashboard stats, lead analytics, revenue analytics, trends, and conversion funnel.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.call import Call, CallStatus
from app.models.conversation import Conversation, ConversationStatus
from app.models.customer import Customer
from app.models.lead import Lead, LeadCategory, LeadStatus, LeadUrgency
from app.models.revenue_prediction import RevenuePrediction

logger = logging.getLogger(__name__)


async def get_overview_stats(db: AsyncSession, business_id: UUID) -> dict:
    """High-level dashboard overview numbers."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Today's calls
    r = await db.execute(
        select(func.count(Call.id)).where(
            Call.business_id == business_id,
            Call.started_at >= today_start,
        )
    )
    calls_today = r.scalar_one()

    # Today's missed calls
    r = await db.execute(
        select(func.count(Call.id)).where(
            Call.business_id == business_id,
            Call.started_at >= today_start,
            Call.status == CallStatus.MISSED,
        )
    )
    missed_today = r.scalar_one()

    # Weekly new leads
    r = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.business_id == business_id,
            Lead.created_at >= week_ago,
        )
    )
    leads_this_week = r.scalar_one()

    # Monthly revenue recovered (from converted leads)
    r = await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0)).where(
            Lead.business_id == business_id,
            Lead.status == LeadStatus.CONVERTED,
            Lead.converted_at >= month_ago,
        )
    )
    revenue_recovered_month = float(r.scalar_one())

    # Active conversations
    r = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.business_id == business_id,
            Conversation.status == ConversationStatus.ACTIVE,
        )
    )
    active_conversations = r.scalar_one()

    # Upcoming appointments (next 7 days)
    r = await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.business_id == business_id,
            Appointment.scheduled_at >= now,
            Appointment.scheduled_at <= now + timedelta(days=7),
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
        )
    )
    upcoming_appointments = r.scalar_one()

    # AI callbacks completed today
    r = await db.execute(
        select(func.count(Call.id)).where(
            Call.business_id == business_id,
            Call.started_at >= today_start,
            Call.status == CallStatus.CALLBACK_COMPLETED,
        )
    )
    callbacks_completed_today = r.scalar_one()

    return {
        "calls_today": calls_today,
        "missed_today": missed_today,
        "leads_this_week": leads_this_week,
        "revenue_recovered_month": revenue_recovered_month,
        "active_conversations": active_conversations,
        "upcoming_appointments": upcoming_appointments,
        "callbacks_completed_today": callbacks_completed_today,
    }


async def get_lead_analytics(db: AsyncSession, business_id: UUID) -> dict:
    """Lead breakdown by category, status, and urgency."""
    # By category
    r = await db.execute(
        select(Lead.category, func.count(Lead.id))
        .where(Lead.business_id == business_id)
        .group_by(Lead.category)
    )
    by_category = {row[0].value: row[1] for row in r.all()}

    # By status
    r = await db.execute(
        select(Lead.status, func.count(Lead.id))
        .where(Lead.business_id == business_id)
        .group_by(Lead.status)
    )
    by_status = {row[0].value: row[1] for row in r.all()}

    # By urgency
    r = await db.execute(
        select(Lead.urgency, func.count(Lead.id))
        .where(Lead.business_id == business_id)
        .group_by(Lead.urgency)
    )
    by_urgency = {row[0].value: row[1] for row in r.all()}

    # Average score
    r = await db.execute(
        select(func.coalesce(func.avg(Lead.lead_score), 0)).where(
            Lead.business_id == business_id
        )
    )
    avg_score = float(r.scalar_one())

    # Top-scoring leads
    r = await db.execute(
        select(Lead.id, Lead.lead_score, Lead.service_requested)
        .where(Lead.business_id == business_id)
        .order_by(Lead.lead_score.desc())
        .limit(5)
    )
    top_leads = [
        {"id": str(row[0]), "score": row[1], "service": row[2]}
        for row in r.all()
    ]

    return {
        "by_category": by_category,
        "by_status": by_status,
        "by_urgency": by_urgency,
        "avg_score": round(avg_score, 2),
        "top_leads": top_leads,
    }


async def get_revenue_analytics(
    db: AsyncSession,
    business_id: UUID,
    currency: str = "INR",
) -> dict:
    """Revenue analytics: total predicted, recovered, by category, avg score."""
    # Total estimated revenue (all leads)
    r = await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0)).where(
            Lead.business_id == business_id,
            Lead.currency == currency,
        )
    )
    total_estimated = float(r.scalar_one())

    # Recovered revenue (converted leads)
    r = await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0)).where(
            Lead.business_id == business_id,
            Lead.status == LeadStatus.CONVERTED,
            Lead.currency == currency,
        )
    )
    total_recovered = float(r.scalar_one())

    # Pipeline revenue (not yet converted or lost)
    r = await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0)).where(
            Lead.business_id == business_id,
            Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.QUALIFIED]),
            Lead.currency == currency,
        )
    )
    pipeline_revenue = float(r.scalar_one())

    # Revenue by category
    r = await db.execute(
        select(Lead.category, func.coalesce(func.sum(Lead.estimated_revenue), 0))
        .where(Lead.business_id == business_id, Lead.currency == currency)
        .group_by(Lead.category)
    )
    by_category = {row[0].value: float(row[1]) for row in r.all()}

    # Avg revenue score from predictions
    r = await db.execute(
        select(func.coalesce(func.avg(RevenuePrediction.revenue_score), 0)).where(
            RevenuePrediction.business_id == business_id,
            RevenuePrediction.currency == currency,
        )
    )
    avg_revenue_score = float(r.scalar_one())

    return {
        "total_estimated": total_estimated,
        "total_recovered": total_recovered,
        "pipeline_revenue": pipeline_revenue,
        "by_category": by_category,
        "avg_revenue_score": round(avg_revenue_score, 2),
        "currency": currency,
    }


async def get_trend_data(
    db: AsyncSession,
    business_id: UUID,
    days: int = 30,
) -> list[dict]:
    """
    Daily trend data for the last N days.

    Returns list of {date, calls, missed_calls, leads, revenue} per day.
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    trend_data: list[dict] = []

    for i in range(days):
        day = start_date + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        # Calls for this day
        r = await db.execute(
            select(func.count(Call.id)).where(
                Call.business_id == business_id,
                Call.started_at >= day_start,
                Call.started_at < day_end,
            )
        )
        total_calls = r.scalar_one()

        # Missed calls
        r = await db.execute(
            select(func.count(Call.id)).where(
                Call.business_id == business_id,
                Call.started_at >= day_start,
                Call.started_at < day_end,
                Call.status == CallStatus.MISSED,
            )
        )
        missed_calls = r.scalar_one()

        # New leads
        r = await db.execute(
            select(func.count(Lead.id)).where(
                Lead.business_id == business_id,
                Lead.created_at >= day_start,
                Lead.created_at < day_end,
            )
        )
        new_leads = r.scalar_one()

        # Revenue from conversions
        r = await db.execute(
            select(func.coalesce(func.sum(Lead.estimated_revenue), 0)).where(
                Lead.business_id == business_id,
                Lead.converted_at >= day_start,
                Lead.converted_at < day_end,
            )
        )
        revenue = float(r.scalar_one())

        trend_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "calls": total_calls,
            "missed_calls": missed_calls,
            "leads": new_leads,
            "revenue": revenue,
        })

    return trend_data


async def get_conversion_funnel(db: AsyncSession, business_id: UUID) -> dict:
    """
    Conversion funnel: missed calls → callbacks → conversations → leads → conversions.
    """
    # Total missed calls
    r = await db.execute(
        select(func.count(Call.id)).where(
            Call.business_id == business_id,
            Call.status == CallStatus.MISSED,
        )
    )
    missed_calls = r.scalar_one()

    # Callbacks initiated
    r = await db.execute(
        select(func.count(Call.id)).where(
            Call.business_id == business_id,
            Call.status.in_([CallStatus.CALLBACK_INITIATED, CallStatus.CALLBACK_COMPLETED]),
        )
    )
    callbacks = r.scalar_one()

    # Conversations completed
    r = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.business_id == business_id,
            Conversation.status == ConversationStatus.COMPLETED,
        )
    )
    conversations = r.scalar_one()

    # Total leads
    r = await db.execute(
        select(func.count(Lead.id)).where(Lead.business_id == business_id)
    )
    total_leads = r.scalar_one()

    # Qualified leads
    r = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.business_id == business_id,
            Lead.status.in_([LeadStatus.QUALIFIED, LeadStatus.CONVERTED]),
        )
    )
    qualified = r.scalar_one()

    # Conversions
    r = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.business_id == business_id,
            Lead.status == LeadStatus.CONVERTED,
        )
    )
    conversions = r.scalar_one()

    return {
        "missed_calls": missed_calls,
        "callbacks_initiated": callbacks,
        "conversations_completed": conversations,
        "leads_generated": total_leads,
        "leads_qualified": qualified,
        "conversions": conversions,
        "funnel_rates": {
            "callback_rate": round(callbacks / missed_calls * 100, 2) if missed_calls > 0 else 0,
            "conversation_rate": round(conversations / callbacks * 100, 2) if callbacks > 0 else 0,
            "lead_rate": round(total_leads / conversations * 100, 2) if conversations > 0 else 0,
            "qualification_rate": round(qualified / total_leads * 100, 2) if total_leads > 0 else 0,
            "conversion_rate": round(conversions / qualified * 100, 2) if qualified > 0 else 0,
        },
    }
