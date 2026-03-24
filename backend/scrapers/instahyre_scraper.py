"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Instahyre Scraper                                    ║
║                                                                   ║
║  Scrapes jobs from Instahyre — an invite-based hiring platform.  ║
║  Instahyre requires login for most functionality.                 ║
║                                                                   ║
║  STATUS: Template — update selectors based on current UI.         ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text, generate_job_hash


class InstahyreScraper(BaseScraper):
    """Instahyre job scraper."""

    @property
    def portal_name(self) -> str:
        return "instahyre"

    async def login(self) -> bool:
        email = settings.INSTAHYRE_EMAIL
        password = settings.INSTAHYRE_PASSWORD
        if not email or not password:
            logger.warning("[instahyre] No credentials configured")
            return False
        try:
            await self.safe_goto("https://www.instahyre.com/login/")
            await self.random_delay(1, 2)
            await self.human_type("input[name='email']", email)
            await self.human_type("input[name='password']", password)
            await self._page.click("button[type='submit']")
            await self.random_delay(3, 5)
            logger.info("[instahyre] Login attempted")
            return True
        except Exception as e:
            logger.warning(f"[instahyre] Login failed: {e}")
            return False

    async def search_jobs(
        self, roles: List[str], locations: List[str],
        experience_min: float, experience_max: float,
    ) -> List[JobCreate]:
        """Search Instahyre — update selectors based on current UI."""
        all_jobs = []
        try:
            await self.safe_goto("https://www.instahyre.com/candidate/opportunities/")
            await self.random_delay(2, 4)

            # Instahyre shows recommended jobs after login
            cards = await self._page.query_selector_all(".opportunity-card, .job-card")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector("h3, .title")
                    company_el = await card.query_selector(".company-name, h4")
                    link_el = await card.query_selector("a")

                    title = clean_text(await title_el.inner_text()) if title_el else None
                    company = clean_text(await company_el.inner_text()) if company_el else "Unknown"
                    url = await link_el.get_attribute("href") if link_el else ""

                    if title:
                        if url and not url.startswith("http"):
                            url = f"https://www.instahyre.com{url}"
                        all_jobs.append(JobCreate(
                            title=title, company=company, portal="instahyre",
                            external_id=generate_job_hash("instahyre", url or title),
                            url=url or "https://www.instahyre.com",
                        ))
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"[instahyre] Search error: {e}")

        return all_jobs

    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)
            desc_el = await self._page.query_selector(".job-description, .description")
            description = clean_text(await desc_el.inner_text()) if desc_el else None
            return {"description": description, "skills": [], "job_type": "Full-time"}
        except Exception as e:
            logger.warning(f"[instahyre] Detail parse failed: {e}")
            return None
