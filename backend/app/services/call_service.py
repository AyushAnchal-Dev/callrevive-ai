"""
CallRevive AI — Call service.

CRUD for telephone call records and recordings.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.call import Call, CallDirection, CallStatus
from app.models.call_recording import CallRecording

logger = logging.getLogger(__name__)


async def create_call(db: AsyncSession, data: dict) -> Call:
    """
    Create a new call record.

    ``data`` keys: business_id, customer_id, twilio_call_sid, direction,
    status, from_number, to_number, duration_seconds, started_at, ended_at.
    """
    call = Call(**data)
    db.add(call)
    await db.flush()
    await db.refresh(call)

    logger.info("Created call id=%s sid=%s status=%s", call.id, call.twilio_call_sid, call.status.value)
    return call


async def get_call(db: AsyncSession, call_id: UUID) -> Call:
    """Fetch a call by ID. Raises NotFoundException if not found."""
    stmt = select(Call).where(Call.id == call_id)
    result = await db.execute(stmt)
    call = result.scalar_one_or_none()
    if call is None:
        raise NotFoundException(
            message="Call not found",
            resource="Call",
            resource_id=str(call_id),
        )
    return call


async def list_calls(
    db: AsyncSession,
    business_id: UUID,
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    direction_filter: str | None = None,
) -> tuple[list[Call], int]:
    """
    List calls for a business with optional filters and pagination.

    Returns (calls_list, total_count).
    """
    base_query = select(Call).where(Call.business_id == business_id)
    count_query = select(func.count(Call.id)).where(Call.business_id == business_id)

    if status_filter is not None:
        try:
            cs = CallStatus(status_filter)
            base_query = base_query.where(Call.status == cs)
            count_query = count_query.where(Call.status == cs)
        except ValueError:
            pass  # Ignore invalid filter

    if direction_filter is not None:
        try:
            cd = CallDirection(direction_filter)
            base_query = base_query.where(Call.direction == cd)
            count_query = count_query.where(Call.direction == cd)
        except ValueError:
            pass

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    stmt = base_query.order_by(Call.started_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    calls = list(result.scalars().all())

    return calls, total


async def update_call_status(
    db: AsyncSession,
    call_id: UUID,
    status: str,
) -> Call:
    """Update a call's status. Returns the updated call."""
    call = await get_call(db, call_id)
    call.status = CallStatus(status)
    await db.flush()
    await db.refresh(call)

    logger.info("Updated call id=%s status=%s", call_id, status)
    return call


async def get_call_recording(db: AsyncSession, call_id: UUID) -> CallRecording:
    """Fetch the recording associated with a call."""
    stmt = select(CallRecording).where(CallRecording.call_id == call_id)
    result = await db.execute(stmt)
    recording = result.scalar_one_or_none()
    if recording is None:
        raise NotFoundException(
            message="Call recording not found",
            resource="CallRecording",
            resource_id=str(call_id),
        )
    return recording
