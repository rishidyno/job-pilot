"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Wellfound (AngelList) Scraper                        ║
║                                                                   ║
║  Scrapes startup jobs from Wellfound (formerly AngelList Talent). ║
║  Great for finding startup/growth-stage company roles.            ║
║                                                                   ║
║  STATUS: Template implementation — extend with actual selectors   ║
║  based on current Wellfound UI.                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text, generate_job_hash


class WellfoundScraper(BaseScraper):
    """Wellfound (AngelList) job scraper — startup-focused roles."""

    @property
    def portal_name(self) -> str:
        return "wellfound"

    LOGIN_URL = "https://wellfound.com/login"
    SEARCH_URL = "https://wellfound.com/jobs"

    async def login(self) -> bool:
        email = settings.WELLFOUND_EMAIL
        password = settings.WELLFOUND_PASSWORD
        if not email or not password:
            logger.info("[wellfound] No credentials — will browse publicly")
            return True

        try:
            await self.safe_goto(self.LOGIN_URL)
            await self.random_delay(1, 2)
            await self.human_type("input[name='email']", email)
            await self.random_delay(0.5, 1)
            await self.human_type("input[name='password']", password)
            await self._page.click("button[type='submit']")
            await self.random_delay(3, 5)
            logger.info("[wellfound] Login attempted")
            return True
        except Exception as e:
            logger.warning(f"[wellfound] Login failed: {e}")
            return True

    async def search_jobs(
        self, roles: List[str], locations: List[str],
        experience_min: float, experience_max: float,
    ) -> List[JobCreate]:
        """
        Search Wellfound for jobs.
        
        TODO: Update CSS selectors based on current Wellfound UI.
        Wellfound frequently redesigns their pages.
        """
        all_jobs = []
        for role in roles[:2]:
            try:
                search_url = f"{self.SEARCH_URL}?role={role.replace(' ', '+')}"
                await self.safe_goto(search_url)
                await self.random_delay(2, 4)

                # Scroll to load more
                for _ in range(3):
                    await self._page.evaluate("window.scrollBy(0, 800)")
                    await self.random_delay(1, 2)

                # Extract job cards — UPDATE SELECTORS AS NEEDED
                cards = await self._page.query_selector_all(
                    "[data-test='StartupResult'], .styles_result__card"
                )
                for card in cards[:15]:
                    try:
                        title_el = await card.query_selector("h2, .styles_title, a[href*='/jobs/']")
                        company_el = await card.query_selector("h3, .styles_company, a[href*='/company/']")
                        link_el = await card.query_selector("a[href*='/jobs/']")

                        title = clean_text(await title_el.inner_text()) if title_el else None
                        company = clean_text(await company_el.inner_text()) if company_el else "Unknown"
                        url = await link_el.get_attribute("href") if link_el else None

                        if title and url:
                            if not url.startswith("http"):
                                url = f"https://wellfound.com{url}"
                            all_jobs.append(JobCreate(
                                title=title, company=company, portal="wellfound",
                                external_id=generate_job_hash("wellfound", url),
                                url=url,
                            ))
                    except Exception:
                        continue

            except Exception as e:
                logger.warning(f"[wellfound] Search error for '{role}': {e}")

        return all_jobs

    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        """Extract full details from a Wellfound job page."""
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)
            desc_el = await self._page.query_selector(
                ".styles_description, .job-description, [data-test='JobDescription']"
            )
            description = clean_text(await desc_el.inner_text()) if desc_el else None
            return {"description": description, "skills": [], "job_type": "Full-time"}
        except Exception as e:
            logger.warning(f"[wellfound] Detail parse failed: {e}")
            return None
