"""CallRevive AI — Intent detection using Gemini."""
from __future__ import annotations

import logging
from typing import Literal
from pydantic import BaseModel, Field

from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import INTENT_DETECTION_SYSTEM

logger = logging.getLogger(__name__)


class IntentResult(BaseModel):
    intent: Literal["service_request", "product_inquiry", "complaint", "appointment_request", "general_inquiry"]
    confidence: float = Field(ge=0, le=1)
    entities: dict = Field(default_factory=dict, description="Extracted entities like service type, dates")


async def detect_intent(text: str) -> IntentResult:
    """Classify customer intent from message text using Gemini AI."""
    client = get_gemini_client()
    result = await client.generate_structured(
        prompt=f"Customer message: \"{text}\"\n\nClassify the intent.",
        schema=IntentResult,
        system_instruction=INTENT_DETECTION_SYSTEM,
        temperature=0.1,
    )
    return IntentResult(**result)
