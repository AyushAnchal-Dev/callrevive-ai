"""CallRevive AI — Analytics Pydantic schemas."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class OverviewStatsResponse(BaseModel):
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    total_calls: int
    missed_calls: int
    recovered_calls: int
    recovery_rate: float
    total_revenue_recovered: Decimal
    currency: str
    conversion_rate: float
    appointment_success_rate: float
    active_conversations: int
    total_leads_trend: float = 0.0
    hot_leads_trend: float = 0.0
    revenue_recovered_trend: float = 0.0
    recovery_rate_trend: float = 0.0


class LeadAnalyticsResponse(BaseModel):
    leads_by_category: dict[str, int]
    leads_by_status: dict[str, int]
    leads_by_intent: dict[str, int]
    avg_lead_score: float
    top_services: list[dict]


class TrendDataPoint(BaseModel):
    date: str
    leads: int = 0
    calls: int = 0
    conversions: int = 0
    revenue: Decimal = Decimal("0")


class RevenueAnalyticsResponse(BaseModel):
    total_potential_revenue: Decimal
    total_recovered_revenue: Decimal
    recovery_rate: float
    currency: str
    monthly_data: list[dict]
    avg_deal_value: Decimal


class ConversionFunnelResponse(BaseModel):
    missed_calls: int
    contacted: int
    qualified: int
    converted: int
    contact_rate: float
    qualification_rate: float
    conversion_rate: float
