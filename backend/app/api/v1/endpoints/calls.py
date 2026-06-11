"""CallRevive AI — Call management endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DBSession
from app.models.call import Call
from app.models.call_recording import CallRecording
from app.schemas.call import CallResponse, CallListResponse, CallRecordingResponse

router = APIRouter()


@router.get("/", response_model=CallListResponse)
async def list_calls(
    db: DBSession,
    current_user: CurrentUser,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    direction: str | None = None,
):
    """List calls with optional filters."""
    query = select(Call).options(joinedload(Call.customer)).where(Call.business_id == current_user.business_id)
    if status:
        query = query.where(Call.status == status)
    if direction:
        query = query.where(Call.direction == direction)
    query = query.order_by(Call.created_at.desc())

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return CallListResponse(
        items=result.scalars().all(), total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(call_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get call details."""
    result = await db.execute(select(Call).options(joinedload(Call.customer)).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.get("/{call_id}/recording", response_model=CallRecordingResponse)
async def get_call_recording(call_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get call recording info."""
    result = await db.execute(select(CallRecording).where(CallRecording.call_id == call_id))
    recording = result.scalar_one_or_none()
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@router.post("/{call_id}/callback", status_code=202)
async def initiate_callback(call_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Initiate a manual callback for a missed call."""
    result = await db.execute(select(Call).options(joinedload(Call.customer)).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    call.status = "callback_initiated"
    await db.commit()
    # Trigger Celery task to dial
    from app.worker.tasks.call_tasks import initiate_ai_callback
    initiate_ai_callback.delay(str(call_id))
    return {"message": "Callback initiated", "call_id": str(call_id)}
