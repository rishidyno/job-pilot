"""
JOBPILOT — AI Service (Google Gemini)

Uses Google Gemini API for all AI operations:
  - Resume tailoring
  - Job-profile match scoring
  - Cover letter generation

USAGE:
    from services.ai_service import ai_service
    result = await ai_service.chat("Analyze this job...")
"""

import json
import asyncio
from typing import Optional
from utils.logger import logger


class AIService:
    """
    Wrapper around Google Gemini API.
    Same interface as the old Kiro CLI service — drop-in replacement.
    """

    def __init__(self):
        self.model_name = "gemini-2.0-flash"
        self._total_requests = 0
        self._client = None

    def _get_client(self):
        """Lazy-init the Gemini client."""
        if self._client is None:
            from config import settings
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY not set. Get one free at https://aistudio.google.com/apikey")
            from google import genai
            self._client = genai.Client(api_key=api_key)
        return self._client

    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> dict:
        """
        Send a message to Gemini and get a response.

        Returns:
            dict with keys: content, model
        """
        try:
            client = self._get_client()

            config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if system_prompt:
                config["system_instruction"] = system_prompt

            # Run sync API in thread to not block event loop
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=self.model_name,
                contents=user_message,
                config=config,
            )

            content = response.text or ""
            self._total_requests += 1

            logger.debug(f"Gemini response ({len(content)} chars)")

            return {
                "content": content,
                "input_tokens": getattr(response, 'usage_metadata', {}).get('prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                "output_tokens": getattr(response, 'usage_metadata', {}).get('candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                "model": self.model_name,
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def chat_json(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> dict:
        """
        Send a message and parse the response as JSON.
        """
        json_instruction = (
            "\n\nIMPORTANT: Respond ONLY with valid JSON. "
            "No markdown, no backticks, no explanatory text. Just pure JSON."
        )

        enhanced_system = (system_prompt or "") + json_instruction

        result = await self.chat(
            user_message=user_message,
            system_prompt=enhanced_system,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Parse JSON, stripping markdown fences if present
        raw = result["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        parsed = json.loads(raw)

        return {
            "data": parsed,
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
            "model": result["model"],
        }

    def get_token_usage(self) -> dict:
        """Get usage stats."""
        return {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_requests": self._total_requests,
            "engine": f"gemini ({self.model_name})",
        }


# Singleton
ai_service = AIService()
