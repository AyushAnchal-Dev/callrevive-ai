"""CallRevive AI — Appointment extraction using Gemini."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import APPOINTMENT_EXTRACTION_SYSTEM


class AppointmentIntent(BaseModel):
    has_appointment_intent: bool
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    service_type: str = ""
    duration_estimate: int = 30
    flexibility: str = "flexible"


async def extract_appointment(text: str) -> AppointmentIntent:
    """Detect appointment intent and extract details from conversation."""
    client = get_gemini_client()
    result = await client.generate_structured(
        prompt=f"Conversation: \"{text}\"\n\nExtract appointment details.",
        schema=AppointmentIntent,
        system_instruction=APPOINTMENT_EXTRACTION_SYSTEM,
        temperature=0.1,
    )
    return AppointmentIntent(**result)
