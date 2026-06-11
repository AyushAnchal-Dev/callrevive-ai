"""CallRevive AI — Lead qualification using Gemini."""
from __future__ import annotations

import logging
from typing import Literal
from pydantic import BaseModel, Field

from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import LEAD_QUALIFICATION_SYSTEM

logger = logging.getLogger(__name__)


class LeadQualification(BaseModel):
    category: Literal["hot", "warm", "cold"]
    lead_score: int = Field(ge=0, le=100)
    urgency: Literal["high", "medium", "low"]
    purchase_readiness: Literal["ready", "considering", "browsing"]
    customer_intent: Literal["service", "product", "complaint", "appointment", "general"]
    service_requested: str = ""
    budget_range: str = ""
    qualification_notes: str = ""


async def qualify_lead(conversation_text: str, business_category: str = "") -> LeadQualification:
    """Analyze conversation to qualify a lead using Gemini AI."""
    client = get_gemini_client()
    prompt = f"Business category: {business_category}\n\nConversation:\n{conversation_text}\n\nQualify this lead."
    result = await client.generate_structured(
        prompt=prompt,
        schema=LeadQualification,
        system_instruction=LEAD_QUALIFICATION_SYSTEM,
        temperature=0.2,
    )
    return LeadQualification(**result)
