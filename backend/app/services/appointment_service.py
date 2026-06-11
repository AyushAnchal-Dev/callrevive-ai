"""
CallRevive AI — Appointment service.

Scheduling, availability slots, and appointment lifecycle management.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.appointment import Appointment, AppointmentStatus

logger = logging.getLogger(__name__)


async def create_appointment(db: AsyncSession, data: dict) -> Appointment:
    """
    Create a new appointment.

    ``data`` keys: lead_id, customer_id, business_id, title, description,
    scheduled_at, duration_minutes, status.
    """
    appointment = Appointment(
        lead_id=data.get("lead_id"),
        customer_id=data["customer_id"],
        business_id=data["business_id"],
        title=data["title"],
        description=data.get("description"),
        scheduled_at=data["scheduled_at"],
        duration_minutes=data.get("duration_minutes", 30),
        status=AppointmentStatus(data.get("status", "scheduled")),
    )
    db.add(appointment)
    await db.flush()
    await db.refresh(appointment)

    logger.info(
        "Created appointment id=%s at=%s business=%s",
        appointment.id,
        appointment.scheduled_at,
        appointment.business_id,
    )
    return appointment


async def get_appointment(db: AsyncSession, appt_id: UUID) -> Appointment:
    """Fetch an appointment by ID. Raises NotFoundException if not found."""
    stmt = select(Appointment).where(Appointment.id == appt_id)
    result = await db.execute(stmt)
    appt = result.scalar_one_or_none()
    if appt is None:
        raise NotFoundException(
            message="Appointment not found",
            resource="Appointment",
            resource_id=str(appt_id),
        )
    return appt


async def list_appointments(
    db: AsyncSession,
    business_id: UUID,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    date_start: date | None = None,
    date_end: date | None = None,
) -> tuple[list[Appointment], int]:
    """
    List appointments for a business with optional filters.

    Returns (appointments_list, total_count).
    """
    base_query = select(Appointment).where(Appointment.business_id == business_id)
    count_query = select(func.count(Appointment.id)).where(
        Appointment.business_id == business_id
    )

    if status is not None:
        try:
            ast = AppointmentStatus(status)
            base_query = base_query.where(Appointment.status == ast)
            count_query = count_query.where(Appointment.status == ast)
        except ValueError:
            pass

    if date_start is not None:
        start_dt = datetime.combine(date_start, time.min, tzinfo=timezone.utc)
        base_query = base_query.where(Appointment.scheduled_at >= start_dt)
        count_query = count_query.where(Appointment.scheduled_at >= start_dt)

    if date_end is not None:
        end_dt = datetime.combine(date_end, time.max, tzinfo=timezone.utc)
        base_query = base_query.where(Appointment.scheduled_at <= end_dt)
        count_query = count_query.where(Appointment.scheduled_at <= end_dt)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    stmt = base_query.order_by(Appointment.scheduled_at.asc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    appointments = list(result.scalars().all())

    return appointments, total


async def update_appointment(
    db: AsyncSession,
    appt_id: UUID,
    data: dict,
) -> Appointment:
    """Partially update an appointment."""
    appt = await get_appointment(db, appt_id)

    for field, value in data.items():
        if value is not None and hasattr(appt, field):
            setattr(appt, field, value)

    await db.flush()
    await db.refresh(appt)

    logger.info("Updated appointment id=%s fields=%s", appt_id, list(data.keys()))
    return appt


async def cancel_appointment(db: AsyncSession, appt_id: UUID) -> Appointment:
    """Cancel an appointment. Raises ValidationException if already completed."""
    appt = await get_appointment(db, appt_id)

    if appt.status == AppointmentStatus.COMPLETED:
        raise ValidationException(
            message="Cannot cancel a completed appointment",
        )

    appt.status = AppointmentStatus.CANCELLED
    await db.flush()
    await db.refresh(appt)

    logger.info("Cancelled appointment id=%s", appt_id)
    return appt


async def get_available_slots(
    db: AsyncSession,
    business_id: UUID,
    target_date: date,
) -> list[dict]:
    """
    Return available appointment slots for a business on a specific date.

    Business hours: 09:00 – 18:00 in 30-minute slots.
    Existing appointments block their time + duration.
    """
    # Fetch existing appointments for that day
    day_start = datetime.combine(target_date, time(9, 0), tzinfo=timezone.utc)
    day_end = datetime.combine(target_date, time(18, 0), tzinfo=timezone.utc)

    stmt = select(Appointment).where(
        and_(
            Appointment.business_id == business_id,
            Appointment.scheduled_at >= day_start,
            Appointment.scheduled_at < day_end,
            Appointment.status.in_([
                AppointmentStatus.SCHEDULED,
                AppointmentStatus.CONFIRMED,
            ]),
        )
    )
    result = await db.execute(stmt)
    existing = result.scalars().all()

    # Build set of blocked 30-min slots
    blocked_slots: set[datetime] = set()
    for appt in existing:
        slot_start = appt.scheduled_at
        num_blocks = max(1, appt.duration_minutes // 30)
        for i in range(num_blocks):
            blocked_slots.add(slot_start + timedelta(minutes=30 * i))

    # Generate all 30-min slots from 09:00 to 17:30
    available: list[dict] = []
    current_slot = day_start
    while current_slot < day_end:
        if current_slot not in blocked_slots:
            available.append({
                "start_time": current_slot.isoformat(),
                "end_time": (current_slot + timedelta(minutes=30)).isoformat(),
                "duration_minutes": 30,
            })
        current_slot += timedelta(minutes=30)

    return available
