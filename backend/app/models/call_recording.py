"""
CallRevive AI — CallRecording model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.call import Call


class CallRecording(Base, UUIDMixin, TimestampMixin):
    """Audio recording stored in Backblaze B2."""

    __tablename__ = "call_recordings"

    call_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("calls.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    recording_sid: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    storage_url: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    format: Mapped[str] = mapped_column(String(10), default="mp3", nullable=False)

    # ── Relationships ──────────────────────────────────────────────
    call: Mapped[Call] = relationship("Call", back_populates="recording")

    def __repr__(self) -> str:
        return f"<CallRecording id={self.id} call_id={self.call_id}>"
