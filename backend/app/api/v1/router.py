"""CallRevive AI — API v1 router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    businesses,
    customers,
    calls,
    conversations,
    leads,
    appointments,
    analytics,
    notifications,
    webhooks,
    voice,
    settings,
    search,
)

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_v1_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_v1_router.include_router(calls.router, prefix="/calls", tags=["Calls"])
api_v1_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_v1_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_v1_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_v1_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_v1_router.include_router(voice.router, prefix="/voice", tags=["Voice AI"])
api_v1_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_v1_router.include_router(search.router, prefix="/search", tags=["Search"])
