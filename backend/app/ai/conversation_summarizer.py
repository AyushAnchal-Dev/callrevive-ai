"""CallRevive AI — Conversation summarization using Gemini."""
from __future__ import annotations
from pydantic import BaseModel
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import CONVERSATION_SUMMARY_SYSTEM


class ConversationSummary(BaseModel):
    summary: str
    key_points: list[str]
    customer_need: str
    action_items: list[str]
    next_steps: str


async def summarize_conversation(messages: list[dict]) -> ConversationSummary:
    """Summarize a multi-turn conversation."""
    client = get_gemini_client()
    transcript = "\n".join(f"{m.get('role', 'unknown')}: {m.get('content', '')}" for m in messages)
    result = await client.generate_structured(
        prompt=f"Conversation transcript:\n{transcript}\n\nSummarize this conversation.",
        schema=ConversationSummary,
        system_instruction=CONVERSATION_SUMMARY_SYSTEM,
    )
    return ConversationSummary(**result)
