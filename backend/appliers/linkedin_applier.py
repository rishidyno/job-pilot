"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — LinkedIn Applier (Easy Apply)                        ║
║                                                                   ║
║  Automates LinkedIn Easy Apply applications using Playwright.     ║
║  Handles multi-step application forms.                            ║
║                                                                   ║
║  IMPORTANT: LinkedIn's Easy Apply flow changes frequently.        ║
║  You may need to update selectors and flow logic periodically.    ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from appliers.base_applier import BaseApplier
from config import settings
from utils.logger import logger


class LinkedInApplier(BaseApplier):
    """LinkedIn Easy Apply automation."""

    @property
    def portal_name(self) -> str:
        return "linkedin"

    async def login(self) -> bool:
        """Login to LinkedIn (same as scraper)."""
        email = settings.LINKEDIN_EMAIL
        password = settings.LINKEDIN_PASSWORD
        if not email or not password:
            return False
        try:
            await self.safe_goto("https://www.linkedin.com/login")
            await self.random_delay(1, 2)
            await self.human_type("#username", email, delay_ms=80)
            await self.human_type("#password", password, delay_ms=90)
            await self._page.click('button[type="submit"]')
            await self._page.wait_for_url("**/feed/**", timeout=30000)
            logger.info("[linkedin-applier] Logged in")
            return True
        except Exception as e:
            logger.error(f"[linkedin-applier] Login failed: {e}")
            return False

    async def apply_to_job(
        self,
        job_url: str,
        resume_path: Optional[str] = None,
        cover_letter_path: Optional[str] = None,
        additional_data: Optional[dict] = None,
    ) -> dict:
        """
        Apply to a LinkedIn job via Easy Apply.
        
        Flow:
        1. Navigate to job posting
        2. Click "Easy Apply" button
        3. Fill in required fields (phone, resume, etc.)
        4. Upload tailored resume if provided
        5. Navigate through multi-step form
        6. Submit application
        
        Returns:
            dict: {success, confirmation_id, error, method}
        """
        try:
            # Navigate to job page
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)

            # Look for Easy Apply button
            easy_apply_btn = await self._page.query_selector(
                "button.jobs-apply-button, "
                "button[aria-label*='Easy Apply'], "
                ".jobs-apply-button--top-card"
            )

            if not easy_apply_btn:
                return {
                    "success": False,
                    "error": "No Easy Apply button found — may require external application",
                    "method": "easy_apply",
                }

            # Click Easy Apply
            await easy_apply_btn.click()
            await self.random_delay(1, 2)

            # Handle the multi-step form
            max_steps = 5
            for step in range(max_steps):
                # Check if we're on the review/submit page
                submit_btn = await self._page.query_selector(
                    "button[aria-label*='Submit application'], "
                    "button[aria-label*='Review']"
                )

                if submit_btn:
                    btn_text = await submit_btn.inner_text()
                    if "submit" in btn_text.lower():
                        # Upload resume if available
                        if resume_path:
                            await self._try_upload_resume(resume_path)

                        # Submit!
                        await submit_btn.click()
                        await self.random_delay(2, 3)

                        logger.info(f"[linkedin-applier] Application submitted for {job_url}")
                        return {
                            "success": True,
                            "confirmation_id": None,
                            "error": None,
                            "method": "easy_apply",
                        }

                # Fill phone number if asked
                phone_input = await self._page.query_selector(
                    "input[name*='phoneNumber'], input[aria-label*='phone']"
                )
                if phone_input:
                    current_val = await phone_input.input_value()
                    if not current_val:
                        await phone_input.fill("+918210239176")

                # Upload resume if file input exists
                if resume_path:
                    await self._try_upload_resume(resume_path)

                # Click Next button to proceed to next step
                next_btn = await self._page.query_selector(
                    "button[aria-label*='Continue'], "
                    "button[aria-label*='Next'], "
                    "button[aria-label*='Review']"
                )
                if next_btn:
                    await next_btn.click()
                    await self.random_delay(1, 2)
                else:
                    break  # No more steps

            return {
                "success": False,
                "error": "Could not complete the application form",
                "method": "easy_apply",
            }

        except Exception as e:
            logger.error(f"[linkedin-applier] Apply failed for {job_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "easy_apply",
            }

    async def _try_upload_resume(self, resume_path: str) -> None:
        """Try to upload a resume file if a file input is present."""
        try:
            file_input = await self._page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(resume_path)
                await self.random_delay(1, 2)
                logger.debug("[linkedin-applier] Resume uploaded")
        except Exception as e:
            logger.debug(f"[linkedin-applier] Resume upload skipped: {e}")
