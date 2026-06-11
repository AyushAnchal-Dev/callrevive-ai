"""
CallRevive AI — AnalyticsEvent model.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.business import Business


class AnalyticsEvent(Base, UUIDMixin, TimestampMixin):
    """Generic analytics event for dashboards and reporting."""

    __tablename__ = "analytics_events"

    business_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    event_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────────
    business: Mapped[Business] = relationship("Business", back_populates="analytics_events")

    def __repr__(self) -> str:
        return f"<AnalyticsEvent id={self.id} type={self.event_type}>"
