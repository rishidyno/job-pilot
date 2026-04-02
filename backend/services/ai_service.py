"""
JOBPILOT — AI Service (Google Gemini) — Production Grade

Handles all AI operations with:
  - Type-safe response parsing (inspected SDK types, not guessed)
  - Error isolation (metrics never crash the main operation)
  - Retry with exponential backoff (429, 503)
  - Response validation (empty, safety-blocked, malformed)
  - Timeout handling
  - Robust JSON extraction (direct, fenced, brace-search)
  - Graceful degradation with clear error messages
"""

import json
import re
import asyncio
from typing import Optional
from utils.logger import logger


# ── Constants ──
MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
RETRY_DELAYS = [1, 3, 8]  # exponential backoff seconds
TIMEOUT_SECONDS = 120

# Finish reasons that indicate blocked/failed content
BLOCKED_REASONS = {"SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII"}


# ── Response Parsing (type-safe) ──

def _extract_text(response) -> str:
    """Safely extract text from Gemini response. Never throws."""
    try:
        text = response.text
        if text:
            return text
    except Exception:
        pass

    # Fallback: dig into candidates manually
    try:
        for candidate in response.candidates or []:
            for part in (candidate.content.parts or []):
                if hasattr(part, 'text') and part.text:
                    return part.text
    except Exception:
        pass

    return ""


def _extract_usage(response) -> dict:
    """Safely extract token usage. Never throws."""
    try:
        um = response.usage_metadata
        if um:
            return {
                "input_tokens": getattr(um, 'prompt_token_count', 0) or 0,
                "output_tokens": getattr(um, 'candidates_token_count', 0) or 0,
                "total_tokens": getattr(um, 'total_token_count', 0) or 0,
            }
    except Exception:
        pass
    return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}


def _check_blocked(response) -> Optional[str]:
    """Check if response was blocked by safety filters. Returns reason or None."""
    try:
        for candidate in response.candidates or []:
            reason = getattr(candidate, 'finish_reason', None)
            if reason and hasattr(reason, 'name') and reason.name in BLOCKED_REASONS:
                return reason.name
    except Exception:
        pass
    return None


def _extract_json(raw: str) -> dict:
    """
    Robust JSON extraction from AI response.
    Handles: raw JSON, markdown fences, text before/after JSON.
    """
    raw = raw.strip()

    # 1. Direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2. Extract from markdown fences: ```json ... ``` or ``` ... ```
    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', raw, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Find first { ... } block (handles text before/after)
    brace_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in AI response: {raw[:200]}")


# ── Retry Logic ──

def _is_retryable(error) -> bool:
    """Check if an error is transient and worth retrying."""
    err_str = str(error)
    return any(code in err_str for code in ["429", "503", "500", "RESOURCE_EXHAUSTED", "UNAVAILABLE"])


# ── Main Service ──

class AIService:
    """
    Production-grade Gemini AI service.
    Thread-safe, retry-capable, error-isolated.
    """

    def __init__(self):
        self._client = None
        self._request_count = 0

    def _get_client(self):
        if self._client is None:
            from config import settings
            if not settings.GEMINI_API_KEY:
                raise RuntimeError(
                    "AI features require a Gemini API key. "
                    "Get one free at https://aistudio.google.com/apikey "
                    "and set GEMINI_API_KEY in your .env file."
                )
            from google import genai
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> dict:
        """
        Send a message to Gemini with retry and validation.

        Returns: {"content": str, "input_tokens": int, "output_tokens": int, "model": str}
        Raises: RuntimeError with clear message on failure.
        """
        client = self._get_client()

        config = {"temperature": temperature, "max_output_tokens": max_tokens}
        if system_prompt:
            config["system_instruction"] = system_prompt

        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                # Call with timeout
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=MODEL,
                        contents=user_message,
                        config=config,
                    ),
                    timeout=TIMEOUT_SECONDS,
                )

                # Check if blocked
                blocked = _check_blocked(response)
                if blocked:
                    raise RuntimeError(f"AI response blocked by safety filter: {blocked}")

                # Extract text
                content = _extract_text(response)
                if not content:
                    raise RuntimeError("AI returned empty response")

                # Extract usage (never crashes main flow)
                usage = _extract_usage(response)

                self._request_count += 1
                logger.debug(f"Gemini OK: {len(content)} chars, {usage['total_tokens']} tokens (attempt {attempt + 1})")

                return {
                    "content": content,
                    "input_tokens": usage["input_tokens"],
                    "output_tokens": usage["output_tokens"],
                    "model": MODEL,
                }

            except asyncio.TimeoutError:
                last_error = RuntimeError(f"AI request timed out after {TIMEOUT_SECONDS}s")
                logger.warning(f"Gemini timeout (attempt {attempt + 1}/{MAX_RETRIES})")

            except Exception as e:
                last_error = e
                if _is_retryable(e) and attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                    logger.warning(f"Gemini retryable error (attempt {attempt + 1}), retrying in {delay}s: {str(e)[:80]}")
                    await asyncio.sleep(delay)
                    continue
                break

        # All retries exhausted
        error_msg = str(last_error)[:200] if last_error else "Unknown error"
        logger.error(f"Gemini failed after {MAX_RETRIES} attempts: {error_msg}")
        raise RuntimeError(f"AI service error: {error_msg}")

    async def chat_json(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> dict:
        """
        Send a message and parse response as JSON with robust extraction.

        Returns: {"data": dict, "input_tokens": int, "output_tokens": int, "model": str}
        """
        json_instruction = (
            "\n\nIMPORTANT: Respond ONLY with valid JSON. "
            "No markdown, no backticks, no explanatory text. Just pure JSON."
        )

        result = await self.chat(
            user_message=user_message,
            system_prompt=(system_prompt or "") + json_instruction,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        try:
            parsed = _extract_json(result["content"])
        except ValueError as e:
            logger.error(f"JSON extraction failed: {e}")
            raise RuntimeError(f"AI returned invalid JSON: {str(e)[:100]}")

        return {
            "data": parsed,
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
            "model": result["model"],
        }

    def get_token_usage(self) -> dict:
        return {
            "total_requests": self._request_count,
            "engine": f"gemini ({MODEL})",
        }


# Singleton
ai_service = AIService()
