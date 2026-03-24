"""JOBPILOT — Wellfound Applier (Template)"""

from typing import Optional
from appliers.base_applier import BaseApplier
from config import settings
from utils.logger import logger


class WellfoundApplier(BaseApplier):
    """Wellfound auto-apply — template implementation."""

    @property
    def portal_name(self) -> str:
        return "wellfound"

    async def login(self) -> bool:
        email = settings.WELLFOUND_EMAIL
        password = settings.WELLFOUND_PASSWORD
        if not email or not password:
            return False
        try:
            await self.safe_goto("https://wellfound.com/login")
            await self.human_type("input[name='email']", email)
            await self.human_type("input[name='password']", password)
            await self._page.click("button[type='submit']")
            await self.random_delay(3, 5)
            return True
        except Exception as e:
            logger.error(f"[wellfound-applier] Login failed: {e}")
            return False

    async def apply_to_job(
        self, job_url: str, resume_path: Optional[str] = None,
        cover_letter_path: Optional[str] = None, additional_data: Optional[dict] = None,
    ) -> dict:
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)
            apply_btn = await self._page.query_selector("button[class*='apply'], .apply-btn")
            if apply_btn:
                await apply_btn.click()
                await self.random_delay(2, 3)
                return {"success": True, "confirmation_id": None, "error": None, "method": "wellfound"}
            return {"success": False, "error": "No apply button found", "method": "wellfound"}
        except Exception as e:
            return {"success": False, "error": str(e), "method": "wellfound"}
