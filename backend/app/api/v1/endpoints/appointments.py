"""CallRevive AI — Appointment management endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DBSession
from app.models.appointment import Appointment
from app.schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, AppointmentResponse, AvailableSlotResponse,
)

router = APIRouter()


@router.get("/", response_model=list[AppointmentResponse])
async def list_appointments(
    db: DBSession, current_user: CurrentUser,
    status: str | None = None, page: int = 1, page_size: int = 20,
):
    """List appointments."""
    query = select(Appointment).options(joinedload(Appointment.customer)).where(Appointment.business_id == current_user.business_id)
    if status:
        query = query.where(Appointment.status == status)
    query = query.order_by(Appointment.scheduled_at.desc())
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return result.scalars().all()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(data: AppointmentCreate, db: DBSession, current_user: CurrentUser):
    """Create a new appointment."""
    appt = Appointment(
        lead_id=data.lead_id,
        customer_id=data.customer_id,
        business_id=data.business_id,
        title=data.title,
        description=data.description,
        scheduled_at=data.scheduled_at,
        duration_minutes=data.duration_minutes,
        status="scheduled",
    )
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt


@router.get("/available-slots", response_model=list[AvailableSlotResponse])
async def get_available_slots(
    db: DBSession, current_user: CurrentUser,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    duration: int = 30,
):
    """Get available time slots for a date."""
    from datetime import date as date_type
    target_date = datetime.strptime(date, "%Y-%m-%d").date()
    start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = start_of_day + timedelta(days=1)

    result = await db.execute(
        select(Appointment).where(
            Appointment.business_id == current_user.business_id,
            Appointment.scheduled_at >= start_of_day,
            Appointment.scheduled_at < end_of_day,
            Appointment.status.in_(["scheduled", "confirmed"]),
        )
    )
    booked = result.scalars().all()
    booked_ranges = [
        (a.scheduled_at, a.scheduled_at + timedelta(minutes=a.duration_minutes))
        for a in booked
    ]

    slots = []
    slot_start = start_of_day.replace(hour=9)  # Business hours: 9 AM
    slot_end_limit = start_of_day.replace(hour=18)  # Until 6 PM

    while slot_start + timedelta(minutes=duration) <= slot_end_limit:
        slot_end = slot_start + timedelta(minutes=duration)
        is_available = not any(
            slot_start < be and slot_end > bs for bs, be in booked_ranges
        )
        if is_available:
            slots.append(AvailableSlotResponse(
                start_time=slot_start, end_time=slot_end, duration_minutes=duration,
            ))
        slot_start += timedelta(minutes=30)  # 30-min increments

    return slots


@router.get("/slots", response_model=list[AvailableSlotResponse])
async def get_slots(
    db: DBSession, current_user: CurrentUser,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    duration: int = 30,
):
    """Get available time slots (alias for /available-slots)."""
    return await get_available_slots(db, current_user, date, duration)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get appointment details."""
    result = await db.execute(
        select(Appointment).options(joinedload(Appointment.customer)).where(Appointment.id == appointment_id)
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: uuid.UUID, data: AppointmentUpdate, db: DBSession, current_user: CurrentUser
):
    """Update appointment."""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(appt, key, val)
    await db.commit()
    await db.refresh(appt)
    return appt


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_patch(
    appointment_id: uuid.UUID, data: AppointmentUpdate, db: DBSession, current_user: CurrentUser
):
    """Update appointment (PATCH alias)."""
    return await update_appointment(appointment_id, data, db, current_user)


@router.delete("/{appointment_id}", status_code=200)
async def cancel_appointment(appointment_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Cancel an appointment."""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = "cancelled"
    await db.commit()
    return {"message": "Appointment cancelled"}
