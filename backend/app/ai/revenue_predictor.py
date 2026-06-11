"""CallRevive AI — Revenue Recovery Score prediction using Gemini (FLAGSHIP FEATURE)."""
from __future__ import annotations

import logging
from typing import Literal
from pydantic import BaseModel, Field

from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import REVENUE_PREDICTION_SYSTEM

logger = logging.getLogger(__name__)


class ScoringFactorsOutput(BaseModel):
    urgency_score: float = Field(ge=0, le=1)
    service_type_score: float = Field(ge=0, le=1)
    estimated_value_score: float = Field(ge=0, le=1)
    business_category_score: float = Field(ge=0, le=1)
    sentiment_score: float = Field(ge=0, le=1)
    buying_intent_score: float = Field(ge=0, le=1)


class RevenuePredictionOutput(BaseModel):
    revenue_score: int = Field(ge=0, le=100)
    estimated_revenue: float
    conversion_probability: float = Field(ge=0, le=1)
    competitor_risk: Literal["low", "medium", "high"]
    urgency: Literal["high", "medium", "low"]
    recommendation: str
    scoring_factors: ScoringFactorsOutput


async def predict_revenue(
    conversation_text: str,
    business_category: str,
    service_type: str,
    currency: str = "INR",
) -> RevenuePredictionOutput:
    """Generate Revenue Recovery Score using Gemini Pro for deep analysis."""
    client = get_gemini_client()
    prompt = (
        f"Business category: {business_category}\n"
        f"Service type: {service_type}\n"
        f"Currency: {currency}\n\n"
        f"Customer conversation:\n{conversation_text}\n\n"
        "Predict the revenue opportunity for this lead."
    )
    result = await client.generate_structured(
        prompt=prompt,
        schema=RevenuePredictionOutput,
        system_instruction=REVENUE_PREDICTION_SYSTEM,
        model=client.pro_model,  # Use Pro model for complex analysis
        temperature=0.2,
    )
    return RevenuePredictionOutput(**result)
