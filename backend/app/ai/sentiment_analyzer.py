"""CallRevive AI — Sentiment analysis using Gemini."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import SENTIMENT_ANALYSIS_SYSTEM


class SentimentResult(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    emotion: str
    confidence: float = Field(ge=0, le=1)


async def analyze_sentiment(text: str) -> SentimentResult:
    """Analyze customer sentiment from text."""
    client = get_gemini_client()
    result = await client.generate_structured(
        prompt=f"Analyze sentiment: \"{text}\"",
        schema=SentimentResult,
        system_instruction=SENTIMENT_ANALYSIS_SYSTEM,
        temperature=0.1,
    )
    return SentimentResult(**result)
