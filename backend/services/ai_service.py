"""
JOBPILOT — AI Service (Claude Code CLI)

Production-grade wrapper around `claude -p` for local AI operations.
Requires: Claude Pro subscription + `claude auth login`.

Architecture:
  - _run_claude(): subprocess layer — handles process lifecycle, timeout, ANSI stripping
  - _extract_json(): parsing layer — 3-tier JSON extraction (direct, fence, brace)
  - chat() / chat_json(): public API — retry, validation, error isolation
  - All layers independent, testable, never crash each other

Error handling:
  - Retry with backoff (2 attempts, 2s/5s delays) for transient failures
  - 180s timeout (Claude CLI can be slower than API)
  - FileNotFoundError → clear install instructions
  - Empty response → explicit error (not silent pass-through)
  - JSON parse failure → error with response preview for debugging
"""

import json
import re
import asyncio
from typing import Optional
from utils.logger import logger


# ── Configuration ──
MAX_RETRIES = 2
RETRY_DELAYS = [2, 5]
TIMEOUT_SECONDS = 180
MODEL_LABEL = "claude-code (local)"


# ═══════════════════════════════════════════
# Layer 1: Subprocess Management
# ═══════════════════════════════════════════

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes and terminal control sequences from CLI output."""
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
    text = re.sub(r'\x1b\[\?25[hl]', '', text)
    return text.strip()


async def _run_claude(prompt: str) -> str:
    """
    Execute `claude -p` as a subprocess.

    Returns: cleaned response text
    Raises:
      - RuntimeError on timeout, empty response, or process failure
      - RuntimeError with install instructions if claude binary not found
    """
    try:
        process = await asyncio.create_subprocess_exec(
            "claude", "-p", prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=TIMEOUT_SECONDS
        )

        response = _strip_ansi(stdout.decode("utf-8"))

        # Process failed with no output — surface the error
        if process.returncode != 0 and not response:
            err = _strip_ansi(stderr.decode("utf-8"))
            raise RuntimeError(f"Claude CLI exited with code {process.returncode}: {err[:200]}")

        if not response:
            raise RuntimeError("Claude returned empty response")

        return response

    except asyncio.TimeoutError:
        raise RuntimeError(f"Claude request timed out after {TIMEOUT_SECONDS}s")

    except FileNotFoundError:
        raise RuntimeError(
            "Claude Code CLI not found. "
            "Install: npm install -g @anthropic-ai/claude-code && claude auth login"
        )


# ═══════════════════════════════════════════
# Layer 2: Response Parsing
# ═══════════════════════════════════════════

def _extract_json(raw: str) -> dict:
    """
    Robust JSON extraction from AI response.

    Strategy (in order):
      1. Direct parse — response is pure JSON
      2. Markdown fence — ```json ... ``` or ``` ... ```
      3. Brace search — find first { ... } block in surrounding text

    Raises ValueError with response preview if all strategies fail.
    """
    raw = raw.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Markdown fence extraction
    fence_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', raw, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: First { ... } block
    brace_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response: {raw[:200]}")


# ═══════════════════════════════════════════
# Layer 3: Public API
# ═══════════════════════════════════════════

class AIService:
    """
    Production-grade Claude Code CLI wrapper.

    Public methods:
      - chat(message, system_prompt) → {"content": str, ...}
      - chat_json(message, system_prompt) → {"data": dict, ...}
      - get_token_usage() → {"total_requests": int, "engine": str}
    """

    def __init__(self):
        self._request_count = 0

    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> dict:
        """
        Send a message to Claude with retry and validation.

        Builds a combined prompt from system_prompt + user_message,
        retries on transient failures, and returns structured result.

        Returns: {"content": str, "input_tokens": int, "output_tokens": int, "model": str}
        Raises: RuntimeError with clear message on failure.
        """
        # Build prompt — system instructions first, then user request
        parts = []
        if system_prompt:
            parts.append(f"SYSTEM INSTRUCTIONS:\n{system_prompt}")
        parts.append(f"USER REQUEST:\n{user_message}")
        full_prompt = "\n\n---\n\n".join(parts)

        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                content = await _run_claude(full_prompt)

                self._request_count += 1
                logger.debug(f"Claude OK: {len(content)} chars (attempt {attempt + 1})")

                return {
                    "content": content,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "model": MODEL_LABEL,
                }

            except RuntimeError as e:
                last_error = e
                # Don't retry on "not found" or "install" errors
                if "not found" in str(e).lower():
                    break
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    logger.warning(f"Claude retry in {delay}s (attempt {attempt + 1}): {str(e)[:80]}")
                    await asyncio.sleep(delay)
                    continue
                break

            except Exception as e:
                last_error = e
                break

        error_msg = str(last_error)[:200]
        logger.error(f"Claude failed after {MAX_RETRIES} attempts: {error_msg}")
        raise RuntimeError(f"AI service error: {error_msg}")

    async def chat_json(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> dict:
        """
        Send a message and parse response as JSON.

        Appends JSON-only instruction to system prompt, then uses
        3-tier extraction to handle various response formats.

        Returns: {"data": dict, "input_tokens": int, "output_tokens": int, "model": str}
        Raises: RuntimeError if response can't be parsed as JSON.
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
            "input_tokens": 0,
            "output_tokens": 0,
            "model": MODEL_LABEL,
        }

    def get_token_usage(self) -> dict:
        """Return usage stats for the health endpoint."""
        return {
            "total_requests": self._request_count,
            "engine": MODEL_LABEL,
        }


# ── Singleton ──
ai_service = AIService()
