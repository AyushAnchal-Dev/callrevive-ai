"""CallRevive AI — Conversation endpoints."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DBSession
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationResponse, ConversationListResponse

router = APIRouter()


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    db: DBSession, current_user: CurrentUser, page: int = 1, page_size: int = 20
):
    """List conversations."""
    query = select(Conversation).options(joinedload(Conversation.customer)).where(
        Conversation.business_id == current_user.business_id
    ).order_by(Conversation.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    return ConversationListResponse(
        items=result.scalars().all(), total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: uuid.UUID, db: DBSession, current_user: CurrentUser):
    """Get full conversation transcript."""
    result = await db.execute(select(Conversation).options(joinedload(Conversation.customer)).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv
