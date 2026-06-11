"""CallRevive AI — Gemini API client wrapper."""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

from google import genai
from google.genai import types

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Production-grade wrapper around Google Gemini API."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.fast_model = settings.GEMINI_FAST_MODEL
        self.pro_model = settings.GEMINI_PRO_MODEL

    async def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        model: str | None = None,
        temperature: float = 0.3,
        response_schema: Any = None,
        max_output_tokens: int = 4096,
    ) -> str:
        """Generate content with Gemini API."""
        config_kwargs: dict[str, Any] = {
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if response_schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_schema

        config = types.GenerateContentConfig(**config_kwargs)

        try:
            response = self.client.models.generate_content(
                model=model or self.fast_model,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def generate_structured(
        self,
        prompt: str,
        schema: Any,
        system_instruction: str = "",
        model: str | None = None,
        temperature: float = 0.2,
    ) -> dict:
        """Generate structured JSON output using a Pydantic schema."""
        text = await self.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            model=model,
            temperature=temperature,
            response_schema=schema,
        )
        return json.loads(text)

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_instruction: str = "",
        model: str | None = None,
    ) -> str:
        """Multi-turn conversation with Gemini."""
        config_kwargs: dict[str, Any] = {"temperature": 0.5}
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        chat_session = self.client.chats.create(
            model=model or self.fast_model,
            config=types.GenerateContentConfig(**config_kwargs),
        )

        last_response = ""
        for msg in messages:
            last_response = chat_session.send_message(msg["content"]).text

        return last_response


@lru_cache(maxsize=1)
def get_gemini_client() -> GeminiClient:
    """Return a cached singleton GeminiClient."""
    return GeminiClient()
