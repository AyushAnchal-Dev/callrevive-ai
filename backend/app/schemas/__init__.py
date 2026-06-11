"""
CallRevive AI — Schema registry.
"""

from __future__ import annotations

from app.schemas.common import (
    CurrencyAmount,
    DateRangeFilter,
    PaginatedResponse,
    PaginationParams,
    SortParams,
)
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.schemas.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessStatsResponse,
    BusinessUpdate,
)
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.schemas.call import CallCreate, CallListResponse, CallRecordingResponse, CallResponse
from app.schemas.conversation import (
    ConversationListResponse,
    ConversationMessage,
    ConversationResponse,
)
from app.schemas.lead import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadStatusUpdate,
    LeadUpdate,
    LeadWithRevenueResponse,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AvailableSlotResponse,
)
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.schemas.analytics import (
    ConversionFunnelResponse,
    LeadAnalyticsResponse,
    OverviewStatsResponse,
    RevenueAnalyticsResponse,
    TrendDataPoint,
)
from app.schemas.revenue import RevenuePredictionCreate, RevenueScoreResponse, ScoringFactors

__all__ = [
    # Common
    "CurrencyAmount",
    "DateRangeFilter",
    "PaginatedResponse",
    "PaginationParams",
    "SortParams",
    # Auth
    "ForgotPasswordRequest",
    "LoginRequest",
    "PasswordChangeRequest",
    "RefreshTokenRequest",
    "RegisterRequest",
    "ResetPasswordRequest",
    "TokenResponse",
    # User
    "UserCreate",
    "UserListResponse",
    "UserResponse",
    "UserUpdate",
    # Business
    "BusinessCreate",
    "BusinessResponse",
    "BusinessStatsResponse",
    "BusinessUpdate",
    # Customer
    "CustomerCreate",
    "CustomerListResponse",
    "CustomerResponse",
    "CustomerUpdate",
    # Call
    "CallCreate",
    "CallListResponse",
    "CallRecordingResponse",
    "CallResponse",
    # Conversation
    "ConversationListResponse",
    "ConversationMessage",
    "ConversationResponse",
    # Lead
    "LeadCreate",
    "LeadListResponse",
    "LeadResponse",
    "LeadStatusUpdate",
    "LeadUpdate",
    "LeadWithRevenueResponse",
    # Appointment
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentUpdate",
    "AvailableSlotResponse",
    # Notification
    "NotificationListResponse",
    "NotificationResponse",
    # Analytics
    "ConversionFunnelResponse",
    "LeadAnalyticsResponse",
    "OverviewStatsResponse",
    "RevenueAnalyticsResponse",
    "TrendDataPoint",
    # Revenue
    "RevenuePredictionCreate",
    "RevenueScoreResponse",
    "ScoringFactors",
]
