"""CallRevive AI — Analytics endpoints (optimized)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import select, func, case, cast, Date, text

from app.api.deps import CurrentUser, DBSession
from app.models.lead import Lead
from app.models.call import Call
from app.models.appointment import Appointment
from app.models.conversation import Conversation
from app.schemas.analytics import (
    OverviewStatsResponse, LeadAnalyticsResponse,
    RevenueAnalyticsResponse, TrendDataPoint, ConversionFunnelResponse,
)

router = APIRouter()


@router.get("/overview", response_model=OverviewStatsResponse)
async def get_overview(db: DBSession, current_user: CurrentUser):
    """Get dashboard overview statistics with trend calculation."""
    bid = current_user.business_id
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=30)
    prev_start = now - timedelta(days=60)

    # Single consolidated lead query
    lead_stats = (await db.execute(
        select(
            func.count().label("total"),
            func.count().filter(Lead.category == "hot").label("hot"),
            func.count().filter(Lead.category == "warm").label("warm"),
            func.count().filter(Lead.category == "cold").label("cold"),
            func.count().filter(Lead.status == "converted").label("converted"),
            func.coalesce(
                func.sum(Lead.estimated_revenue).filter(Lead.status == "converted"), 0
            ).label("revenue"),
        ).where(Lead.business_id == bid)
    )).one()

    # Single consolidated call query
    call_stats = (await db.execute(
        select(
            func.count().label("total"),
            func.count().filter(Call.status == "missed").label("missed"),
            func.count().filter(Call.status == "callback_completed").label("recovered"),
        ).where(Call.business_id == bid)
    )).one()

    # Appointment + conversation counts
    total_appts = (await db.execute(select(func.count()).where(Appointment.business_id == bid))).scalar() or 0
    completed_appts = (await db.execute(select(func.count()).where(Appointment.business_id == bid, Appointment.status == "completed"))).scalar() or 0
    active_convs = (await db.execute(select(func.count()).where(Conversation.business_id == bid, Conversation.status == "active"))).scalar() or 0

    # Trend: leads created in current vs previous 30-day period
    current_leads = (await db.execute(
        select(func.count()).where(Lead.business_id == bid, Lead.created_at >= period_start)
    )).scalar() or 0
    prev_leads = (await db.execute(
        select(func.count()).where(Lead.business_id == bid, Lead.created_at >= prev_start, Lead.created_at < period_start)
    )).scalar() or 0
    leads_trend = round(((current_leads - prev_leads) / max(prev_leads, 1)) * 100, 1)

    # Trend: hot leads
    current_hot = (await db.execute(
        select(func.count()).where(Lead.business_id == bid, Lead.category == "hot", Lead.created_at >= period_start)
    )).scalar() or 0
    prev_hot = (await db.execute(
        select(func.count()).where(Lead.business_id == bid, Lead.category == "hot", Lead.created_at >= prev_start, Lead.created_at < period_start)
    )).scalar() or 0
    hot_trend = current_hot - prev_hot

    # Trend: revenue
    current_rev = (await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0))
        .where(Lead.business_id == bid, Lead.status == "converted", Lead.converted_at >= period_start)
    )).scalar() or Decimal("0")
    prev_rev = (await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0))
        .where(Lead.business_id == bid, Lead.status == "converted", Lead.converted_at >= prev_start, Lead.converted_at < period_start)
    )).scalar() or Decimal("0")
    rev_trend = round(float((current_rev - prev_rev) / max(prev_rev, Decimal("1"))) * 100, 1)

    # Trend: recovery rate
    current_recovered = (await db.execute(
        select(func.count()).where(Call.business_id == bid, Call.status == "callback_completed", Call.created_at >= period_start)
    )).scalar() or 0
    current_missed = (await db.execute(
        select(func.count()).where(Call.business_id == bid, Call.status == "missed", Call.created_at >= period_start)
    )).scalar() or 0
    prev_recovered = (await db.execute(
        select(func.count()).where(Call.business_id == bid, Call.status == "callback_completed", Call.created_at >= prev_start, Call.created_at < period_start)
    )).scalar() or 0
    prev_missed = (await db.execute(
        select(func.count()).where(Call.business_id == bid, Call.status == "missed", Call.created_at >= prev_start, Call.created_at < period_start)
    )).scalar() or 0
    curr_rate = round((current_recovered / max(current_missed, 1)) * 100, 1)
    prev_rate = round((prev_recovered / max(prev_missed, 1)) * 100, 1)
    rate_trend = round(curr_rate - prev_rate, 1)

    missed = call_stats.missed or 0
    recovered = call_stats.recovered or 0
    total_leads_count = lead_stats.total or 0
    converted_count = lead_stats.converted or 0

    return OverviewStatsResponse(
        total_leads=total_leads_count,
        hot_leads=lead_stats.hot or 0,
        warm_leads=lead_stats.warm or 0,
        cold_leads=lead_stats.cold or 0,
        total_calls=call_stats.total or 0,
        missed_calls=missed,
        recovered_calls=recovered,
        recovery_rate=round((recovered / max(missed, 1)) * 100, 1),
        total_revenue_recovered=lead_stats.revenue or Decimal("0"),
        currency="INR",
        conversion_rate=round((converted_count / max(total_leads_count, 1)) * 100, 1),
        appointment_success_rate=round((completed_appts / max(total_appts, 1)) * 100, 1),
        active_conversations=active_convs,
        total_leads_trend=leads_trend,
        hot_leads_trend=hot_trend,
        revenue_recovered_trend=rev_trend,
        recovery_rate_trend=rate_trend,
    )


@router.get("/leads", response_model=LeadAnalyticsResponse)
async def get_lead_analytics(db: DBSession, current_user: CurrentUser):
    """Get lead analytics breakdown using GROUP BY."""
    bid = current_user.business_id

    # Single GROUP BY query for categories
    cat_rows = (await db.execute(
        select(Lead.category, func.count().label("cnt"))
        .where(Lead.business_id == bid)
        .group_by(Lead.category)
    )).all()
    by_category = {row.category: row.cnt for row in cat_rows}

    # Single GROUP BY query for statuses
    status_rows = (await db.execute(
        select(Lead.status, func.count().label("cnt"))
        .where(Lead.business_id == bid)
        .group_by(Lead.status)
    )).all()
    by_status = {row.status: row.cnt for row in status_rows}

    # Single GROUP BY query for intents
    intent_rows = (await db.execute(
        select(Lead.customer_intent, func.count().label("cnt"))
        .where(Lead.business_id == bid)
        .group_by(Lead.customer_intent)
    )).all()
    by_intent = {(row.customer_intent or "general"): row.cnt for row in intent_rows}

    avg_score = (await db.execute(
        select(func.coalesce(func.avg(Lead.lead_score), 0)).where(Lead.business_id == bid)
    )).scalar() or 0

    return LeadAnalyticsResponse(
        leads_by_category=by_category, leads_by_status=by_status,
        leads_by_intent=by_intent, avg_lead_score=round(float(avg_score), 1),
        top_services=[],
    )


@router.get("/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(db: DBSession, current_user: CurrentUser):
    """Get revenue recovery analytics."""
    bid = current_user.business_id
    potential = (await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0)).where(Lead.business_id == bid)
    )).scalar() or Decimal("0")
    recovered = (await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0))
        .where(Lead.business_id == bid, Lead.status == "converted")
    )).scalar() or Decimal("0")

    rate = float(recovered / max(potential, Decimal("1"))) * 100
    total_converted = (await db.execute(
        select(func.count()).where(Lead.business_id == bid, Lead.status == "converted")
    )).scalar() or 0
    avg_deal = recovered / max(total_converted, 1)

    # Monthly breakdown using GROUP BY
    monthly_rows = (await db.execute(
        select(
            func.date_trunc(text("'month'"), Lead.created_at).label("month"),
            func.coalesce(func.sum(Lead.estimated_revenue), 0).label("potential"),
            func.coalesce(
                func.sum(Lead.estimated_revenue).filter(Lead.status == "converted"), 0
            ).label("recovered"),
        ).where(Lead.business_id == bid)
        .group_by(func.date_trunc(text("'month'"), Lead.created_at))
        .order_by(func.date_trunc(text("'month'"), Lead.created_at))
        .limit(12)
    )).all()

    monthly_data = [
        {
            "month": row.month.strftime("%b") if row.month else "N/A",
            "potential": float(row.potential),
            "recovered": float(row.recovered),
        }
        for row in monthly_rows
    ]

    return RevenueAnalyticsResponse(
        total_potential_revenue=potential, total_recovered_revenue=recovered,
        recovery_rate=round(rate, 1), currency="INR",
        monthly_data=monthly_data, avg_deal_value=avg_deal,
    )


@router.get("/trends", response_model=list[TrendDataPoint])
async def get_trends(db: DBSession, current_user: CurrentUser, days: int = 30):
    """Get daily trend data using GROUP BY date (optimized from 120 queries to 4)."""
    bid = current_user.business_id
    start_date = datetime.now(timezone.utc).date() - timedelta(days=days - 1)
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)

    # Leads per day
    lead_rows = (await db.execute(
        select(
            cast(Lead.created_at, Date).label("day"),
            func.count().label("cnt"),
        ).where(Lead.business_id == bid, Lead.created_at >= start_dt)
        .group_by(cast(Lead.created_at, Date))
    )).all()
    leads_by_day = {row.day: row.cnt for row in lead_rows}

    # Calls per day
    call_rows = (await db.execute(
        select(
            cast(Call.created_at, Date).label("day"),
            func.count().label("cnt"),
        ).where(Call.business_id == bid, Call.created_at >= start_dt)
        .group_by(cast(Call.created_at, Date))
    )).all()
    calls_by_day = {row.day: row.cnt for row in call_rows}

    # Conversions per day
    conv_rows = (await db.execute(
        select(
            cast(Lead.converted_at, Date).label("day"),
            func.count().label("cnt"),
        ).where(
            Lead.business_id == bid,
            Lead.status == "converted",
            Lead.converted_at >= start_dt,
            Lead.converted_at.is_not(None),
        )
        .group_by(cast(Lead.converted_at, Date))
    )).all()
    convs_by_day = {row.day: row.cnt for row in conv_rows}

    # Revenue per day
    rev_rows = (await db.execute(
        select(
            cast(Lead.converted_at, Date).label("day"),
            func.coalesce(func.sum(Lead.estimated_revenue), 0).label("rev"),
        ).where(
            Lead.business_id == bid,
            Lead.status == "converted",
            Lead.converted_at >= start_dt,
            Lead.converted_at.is_not(None),
        )
        .group_by(cast(Lead.converted_at, Date))
    )).all()
    rev_by_day = {row.day: row.rev for row in rev_rows}

    # Build result
    data = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        data.append(TrendDataPoint(
            date=day.isoformat(),
            leads=leads_by_day.get(day, 0),
            calls=calls_by_day.get(day, 0),
            conversions=convs_by_day.get(day, 0),
            revenue=rev_by_day.get(day, Decimal("0")),
        ))
    return data


@router.get("/conversion-funnel", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(db: DBSession, current_user: CurrentUser):
    """Get conversion funnel data."""
    bid = current_user.business_id
    missed = (await db.execute(select(func.count()).where(Call.business_id == bid, Call.status == "missed"))).scalar() or 0
    contacted = (await db.execute(select(func.count()).where(Lead.business_id == bid, Lead.status.in_(["contacted", "qualified", "converted"])))).scalar() or 0
    qualified = (await db.execute(select(func.count()).where(Lead.business_id == bid, Lead.status.in_(["qualified", "converted"])))).scalar() or 0
    converted = (await db.execute(select(func.count()).where(Lead.business_id == bid, Lead.status == "converted"))).scalar() or 0

    return ConversionFunnelResponse(
        missed_calls=missed, contacted=contacted, qualified=qualified, converted=converted,
        contact_rate=round((contacted / max(missed, 1)) * 100, 1),
        qualification_rate=round((qualified / max(contacted, 1)) * 100, 1),
        conversion_rate=round((converted / max(qualified, 1)) * 100, 1),
    )


@router.post("/ai-insights")
async def generate_ai_insights(db: DBSession, current_user: CurrentUser):
    """Generate AI-powered business insights using Gemini."""
    bid = current_user.business_id

    # Gather current metrics
    total_leads = (await db.execute(select(func.count()).where(Lead.business_id == bid))).scalar() or 0
    hot_leads = (await db.execute(select(func.count()).where(Lead.business_id == bid, Lead.category == "hot"))).scalar() or 0
    missed_calls = (await db.execute(select(func.count()).where(Call.business_id == bid, Call.status == "missed"))).scalar() or 0
    recovered = (await db.execute(select(func.count()).where(Call.business_id == bid, Call.status == "callback_completed"))).scalar() or 0
    total_revenue = (await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_revenue), 0))
        .where(Lead.business_id == bid, Lead.status == "converted")
    )).scalar() or 0
    converted = (await db.execute(select(func.count()).where(Lead.business_id == bid, Lead.status == "converted"))).scalar() or 0
    conversion_rate = round((converted / max(total_leads, 1)) * 100, 1)
    recovery_rate = round((recovered / max(missed_calls, 1)) * 100, 1)

    # Try to use Gemini for real AI insights
    try:
        from app.core.config import get_settings
        settings = get_settings()
        if settings.GEMINI_API_KEY:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"""You are a business analytics AI. Based on these metrics for a service business, generate exactly 4 actionable recommendations.

Metrics:
- Total Leads: {total_leads} (Hot: {hot_leads})
- Missed Calls: {missed_calls}, Recovered: {recovered} (Recovery Rate: {recovery_rate}%)
- Converted: {converted} (Conversion Rate: {conversion_rate}%)
- Revenue Recovered: ₹{total_revenue:,}

Return a JSON array of exactly 4 objects, each with: title, impact (string like "High Impact" or "Medium Impact"), category (one of: Lead Recovery, Operational, Appointment Booking, Customer Experience), description (2-3 sentences), status (one of: Action Needed, Configure Auto-Reply, Send WhatsApp, Review Transcripts).
Return ONLY valid JSON, no markdown."""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            import json
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            recommendations = json.loads(text)
            return {
                "revenue_recovered": float(total_revenue),
                "conversion_rate": conversion_rate,
                "recovery_rate": recovery_rate,
                "recommendations": recommendations,
            }
    except Exception:
        pass

    # Fallback: generate data-driven insights without Gemini
    recommendations = []
    if hot_leads > 0:
        recommendations.append({
            "title": f"Prioritize {hot_leads} Hot Lead{'s' if hot_leads > 1 else ''}",
            "impact": "High Impact",
            "category": "Lead Recovery",
            "description": f"You have {hot_leads} hot leads awaiting action. These leads have the highest conversion probability. Reach out within 15 minutes for best results.",
            "status": "Action Needed",
        })
    if recovery_rate < 70:
        recommendations.append({
            "title": "Improve Call Recovery Rate",
            "impact": "High Impact",
            "category": "Operational",
            "description": f"Your recovery rate is {recovery_rate}%. Setting up evening auto-response sequences could help recover more missed calls during off-hours.",
            "status": "Configure Auto-Reply",
        })
    if conversion_rate < 30:
        recommendations.append({
            "title": "Boost Lead Conversion",
            "impact": "Medium Impact",
            "category": "Appointment Booking",
            "description": f"Conversion rate is at {conversion_rate}%. Send personalized WhatsApp follow-ups to warm leads with scheduling links to improve bookings.",
            "status": "Send WhatsApp",
        })
    recommendations.append({
        "title": "Review Recent Conversations",
        "impact": "Medium Impact",
        "category": "Customer Experience",
        "description": "Regularly reviewing AI conversation transcripts helps identify customer pain points and improve the voice agent's responses.",
        "status": "Review Transcripts",
    })

    return {
        "revenue_recovered": float(total_revenue),
        "conversion_rate": conversion_rate,
        "recovery_rate": recovery_rate,
        "recommendations": recommendations[:4],
    }
