"""CallRevive AI — Global search endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUser, DBSession
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.conversation import Conversation

router = APIRouter()


@router.get("/")
async def global_search(
    db: DBSession, current_user: CurrentUser,
    q: str = Query(..., min_length=2, max_length=100),
):
    """Search across customers, leads, and conversations."""
    bid = current_user.business_id
    like_q = f"%{q}%"

    # Search customers
    cust_result = await db.execute(
        select(Customer)
        .where(
            Customer.business_id == bid,
            or_(
                Customer.name.ilike(like_q),
                Customer.phone_number.ilike(like_q),
                Customer.email.ilike(like_q),
            ),
        )
        .limit(5)
    )
    customers = [
        {"id": str(c.id), "name": c.name or c.phone_number, "phone": c.phone_number, "type": "customer"}
        for c in cust_result.scalars().all()
    ]

    # Search leads via customer
    lead_result = await db.execute(
        select(Lead)
        .options(joinedload(Lead.customer))
        .where(Lead.business_id == bid)
        .join(Customer, Lead.customer_id == Customer.id)
        .where(
            or_(
                Customer.name.ilike(like_q),
                Customer.phone_number.ilike(like_q),
                Lead.service_requested.ilike(like_q),
            ),
        )
        .limit(5)
    )
    leads = [
        {"id": str(l.id), "name": l.customer_name or "Unknown", "service": l.service_requested or "", "category": l.category, "type": "lead"}
        for l in lead_result.unique().scalars().all()
    ]

    # Search conversations by AI summary
    conv_result = await db.execute(
        select(Conversation)
        .options(joinedload(Conversation.customer))
        .where(
            Conversation.business_id == bid,
            Conversation.ai_summary.ilike(like_q),
        )
        .limit(5)
    )
    conversations = [
        {"id": str(c.id), "summary": c.ai_summary or "", "channel": c.channel, "customer_name": c.customer_name or "Unknown", "type": "conversation"}
        for c in conv_result.unique().scalars().all()
    ]

    return {"customers": customers, "leads": leads, "conversations": conversations}
