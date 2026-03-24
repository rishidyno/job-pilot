"""
JOBPILOT — Naukri.com Applier

Automates job applications on Naukri.com.
STATUS: Template — update selectors based on current Naukri apply flow.
"""

from typing import Optional
from appliers.base_applier import BaseApplier
from config import settings
from utils.logger import logger


class NaukriApplier(BaseApplier):
    """Naukri.com auto-apply module."""

    @property
    def portal_name(self) -> str:
        return "naukri"

    async def login(self) -> bool:
        email = settings.NAUKRI_EMAIL
        password = settings.NAUKRI_PASSWORD
        if not email or not password:
            return False
        try:
            await self.safe_goto("https://www.naukri.com/nlogin/login")
            await self.random_delay(1, 2)
            await self.human_type("input[placeholder*='Email']", email)
            await self.human_type("input[type='password']", password)
            await self._page.click("button[type='submit']")
            await self.random_delay(3, 5)
            return True
        except Exception as e:
            logger.error(f"[naukri-applier] Login failed: {e}")
            return False

    async def apply_to_job(
        self, job_url: str, resume_path: Optional[str] = None,
        cover_letter_path: Optional[str] = None, additional_data: Optional[dict] = None,
    ) -> dict:
        """
        Apply on Naukri — most jobs have a one-click "Apply" button.
        Some require filling additional questions.
        """
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)

            # Look for apply button
            apply_btn = await self._page.query_selector(
                "button.apply-button, #apply-button, "
                ".styles_jhc__apply-button, button[id*='apply']"
            )

            if not apply_btn:
                return {"success": False, "error": "No apply button found", "method": "naukri"}

            await apply_btn.click()
            await self.random_delay(2, 3)

            # Check for chatbot/questionnaire popup
            chatbot = await self._page.query_selector(".chatbot_container, .apply-questionnaire")
            if chatbot:
                # Handle common questions — extend as needed
                logger.info("[naukri-applier] Questionnaire detected — attempting to fill")
                # Try to click through common questions
                submit_btns = await self._page.query_selector_all(
                    "button[type='submit'], .chatbot_submit"
                )
                for btn in submit_btns:
                    try:
                        await btn.click()
                        await self.random_delay(1, 2)
                    except Exception:
                        pass

            # Upload resume if possible
            if resume_path:
                file_input = await self._page.query_selector("input[type='file']")
                if file_input:
                    await file_input.set_input_files(resume_path)
                    await self.random_delay(1, 2)

            logger.info(f"[naukri-applier] Applied to {job_url}")
            return {"success": True, "confirmation_id": None, "error": None, "method": "naukri"}

        except Exception as e:
            logger.error(f"[naukri-applier] Apply failed: {e}")
            return {"success": False, "error": str(e), "method": "naukri"}
