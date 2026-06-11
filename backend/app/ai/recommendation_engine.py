"""CallRevive AI — Smart business recommendations using Gemini."""
from __future__ import annotations
from pydantic import BaseModel
from typing import Literal
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import RECOMMENDATION_SYSTEM


class Recommendation(BaseModel):
    title: str
    description: str
    priority: Literal["high", "medium", "low"]
    action_type: Literal["contact_lead", "review_analytics", "schedule_followup", "team_action"]


class RecommendationsOutput(BaseModel):
    recommendations: list[Recommendation]


async def generate_recommendations(business_data: dict) -> list[Recommendation]:
    """Generate daily smart business recommendations."""
    client = get_gemini_client()
    prompt = (
        f"Business data:\n"
        f"- Total leads: {business_data.get('total_leads', 0)}\n"
        f"- Hot leads uncontacted: {business_data.get('hot_uncontacted', 0)}\n"
        f"- Potential lost revenue: {business_data.get('potential_lost_revenue', 0)}\n"
        f"- Top service requests: {business_data.get('top_services', [])}\n"
        f"- Avg response time: {business_data.get('avg_response_time', 'N/A')}\n\n"
        "Generate actionable recommendations."
    )
    result = await client.generate_structured(
        prompt=prompt,
        schema=RecommendationsOutput,
        system_instruction=RECOMMENDATION_SYSTEM,
    )
    return [Recommendation(**r) for r in result.get("recommendations", [])]
