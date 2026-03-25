"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — AI Service (Kiro CLI Local Engine)                   ║
║                                                                   ║
║  Uses kiro-cli running locally as the AI engine instead of        ║
║  the Anthropic API. This means no API key is needed — it          ║
║  leverages the user's existing Claude subscription via Kiro CLI.  ║
║                                                                   ║
║  HOW IT WORKS:                                                    ║
║  1. Constructs a prompt (system + user message)                   ║
║  2. Pipes it to `kiro-cli chat` via subprocess                    ║
║  3. Captures stdout as the AI response                            ║
║  4. Parses JSON if needed                                         ║
║                                                                   ║
║  USAGE:                                                           ║
║    from services.ai_service import ai_service                     ║
║    result = await ai_service.chat("Analyze this job...")          ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import json
import asyncio
import os
import re
from typing import Optional
from utils.logger import logger


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes and kiro-cli formatting from output."""
    # Remove ANSI escape sequences
    text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
    text = re.sub(r'\x1b\[\?25[hl]', '', text)
    # Remove non-ASCII decorative chars (emoji-like symbols kiro uses)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Remove kiro-cli chrome lines
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('WARNING:'):
            continue
        if stripped.startswith('Not all mcp servers'):
            continue
        if re.match(r'^Credits:', stripped):
            continue
        if stripped == '------':
            continue
        if stripped.startswith('error: Tool approva'):
            continue
        if stripped.startswith('error: MCP'):
            continue
        # Strip leading "> " prompt marker but keep the content
        if stripped.startswith('> '):
            stripped = stripped[2:]
        cleaned.append(stripped)
    return '\n'.join(cleaned).strip()


def _extract_json(text: str) -> dict:
    """Extract a JSON object from text that may contain surrounding prose."""
    # Try direct parse first
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown fences
    if '```' in text:
        m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass

    # Find first { ... last } 
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response: {text[:200]}")


class AIService:
    """
    Async wrapper that uses kiro-cli as the AI backend.

    Spawns kiro-cli as a subprocess, sends prompts via stdin,
    and captures the response from stdout.
    """

    def __init__(self):
        self.model = "kiro-cli (local)"
        self._total_requests = 0
        # Load rules.md if it exists
        self._rules_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "rules.md"
        )
        self._profile_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "profile.md"
        )

    def _load_file(self, path: str) -> str:
        """Load a text file, return empty string if not found."""
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @property
    def rules(self) -> str:
        return self._load_file(self._rules_path)

    @property
    def profile(self) -> str:
        return self._load_file(self._profile_path)

    async def _run_kiro(self, prompt: str) -> str:
        """
        Run kiro-cli chat with the given prompt.
        Writes long prompts to a temp file to avoid CLI arg length issues.
        Runs from project root so kiro-cli can access data/ files.
        """
        import tempfile

        project_root = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        try:
            # Write prompt to temp file to avoid CLI arg length limits
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, dir="/tmp"
            ) as f:
                f.write(prompt)
                prompt_file = f.name

            process = await asyncio.create_subprocess_exec(
                "kiro-cli", "chat",
                "--no-interactive",
                "--trust-tools=fs_read",
                f"Read the prompt from {prompt_file} and follow the instructions in it exactly.",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_root,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=120
            )

            # Clean up temp file
            try:
                os.unlink(prompt_file)
            except OSError:
                pass

            response = _strip_ansi(stdout.decode("utf-8"))

            if process.returncode != 0 and not response:
                err = stderr.decode("utf-8").strip()
                logger.error(f"kiro-cli error (exit {process.returncode}): {err}")
                raise RuntimeError(f"kiro-cli failed: {err}")

            if not response:
                logger.error("kiro-cli returned empty response")
                raise RuntimeError("AI returned empty response")

            self._total_requests += 1
            logger.debug(f"kiro-cli response ({len(response)} chars)")
            return response

        except asyncio.TimeoutError:
            logger.error("kiro-cli timed out after 120s")
            raise RuntimeError("AI request timed out")
        except FileNotFoundError:
            logger.error("kiro-cli not found in PATH")
            raise RuntimeError("kiro-cli not found. Install it or add it to PATH.")

    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> dict:
        """
        Send a message to the AI via kiro-cli and get a response.

        Args:
            user_message: The prompt/question to send
            system_prompt: Optional system prompt prepended to the message
            max_tokens: Unused (kiro-cli manages this)
            temperature: Unused (kiro-cli manages this)

        Returns:
            dict with keys: content, model
        """
        # Build combined prompt
        parts = []
        if system_prompt:
            parts.append(f"SYSTEM INSTRUCTIONS:\n{system_prompt}")

        parts.append(f"USER REQUEST:\n{user_message}")

        full_prompt = "\n\n---\n\n".join(parts)

        content = await self._run_kiro(full_prompt)

        return {
            "content": content,
            "input_tokens": 0,
            "output_tokens": 0,
            "model": self.model,
        }

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

        content = result.get("content", "")
        if not content:
            raise RuntimeError("AI returned empty response")

        try:
            parsed = _extract_json(content)
        except ValueError as e:
            logger.error(f"Failed to parse AI JSON response: {content[:300]}")
            raise RuntimeError(f"AI returned invalid JSON: {str(e)}")

        return {
            "data": parsed,
            "input_tokens": 0,
            "output_tokens": 0,
            "model": self.model,
        }

    def get_token_usage(self) -> dict:
        """Get usage stats."""
        return {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_requests": self._total_requests,
            "engine": "kiro-cli (local)",
        }


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
ai_service = AIService()
