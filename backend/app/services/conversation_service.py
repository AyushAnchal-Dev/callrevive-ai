"""
CallRevive AI — Conversation service.

Manage AI conversations with customers across voice, WhatsApp, and SMS.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.conversation import Conversation, ConversationStatus

logger = logging.getLogger(__name__)


async def create_conversation(db: AsyncSession, data: dict) -> Conversation:
    """
    Create a new conversation record.

    ``data`` keys: call_id, customer_id, business_id, channel, language, started_at.
    """
    conversation = Conversation(
        call_id=data.get("call_id"),
        customer_id=data["customer_id"],
        business_id=data["business_id"],
        channel=data["channel"],
        language=data.get("language", "en"),
        messages=data.get("messages", []),
        status=ConversationStatus.ACTIVE,
        started_at=data.get("started_at", datetime.now(timezone.utc)),
    )
    db.add(conversation)
    await db.flush()
    await db.refresh(conversation)

    logger.info(
        "Created conversation id=%s channel=%s business=%s",
        conversation.id,
        conversation.channel.value,
        conversation.business_id,
    )
    return conversation


async def get_conversation(db: AsyncSession, conv_id: UUID) -> Conversation:
    """Fetch a conversation by ID. Raises NotFoundException if not found."""
    stmt = select(Conversation).where(Conversation.id == conv_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise NotFoundException(
            message="Conversation not found",
            resource="Conversation",
            resource_id=str(conv_id),
        )
    return conversation


async def list_conversations(
    db: AsyncSession,
    business_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Conversation], int]:
    """
    List conversations for a business with pagination.

    Returns (conversations_list, total_count).
    """
    count_query = select(func.count(Conversation.id)).where(
        Conversation.business_id == business_id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    stmt = (
        select(Conversation)
        .where(Conversation.business_id == business_id)
        .order_by(Conversation.started_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    conversations = list(result.scalars().all())

    return conversations, total


async def add_message(
    db: AsyncSession,
    conv_id: UUID,
    role: str,
    content: str,
) -> Conversation:
    """
    Append a message to a conversation's JSON messages array.

    ``role`` is one of: 'customer', 'ai', 'system'.
    """
    conversation = await get_conversation(db, conv_id)

    new_message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Create a new list to trigger SQLAlchemy's change detection on JSON column
    updated_messages = list(conversation.messages) + [new_message]
    conversation.messages = updated_messages

    await db.flush()
    await db.refresh(conversation)

    logger.debug(
        "Added message to conversation id=%s role=%s length=%d",
        conv_id,
        role,
        len(content),
    )
    return conversation


async def complete_conversation(
    db: AsyncSession,
    conv_id: UUID,
    ai_summary: str,
) -> Conversation:
    """
    Mark a conversation as completed with an AI-generated summary.
    """
    conversation = await get_conversation(db, conv_id)

    conversation.status = ConversationStatus.COMPLETED
    conversation.ai_summary = ai_summary
    conversation.ended_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(conversation)

    logger.info("Completed conversation id=%s", conv_id)
    return conversation
