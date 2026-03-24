"""
JOBPILOT — Indeed Scraper

Scrapes jobs from Indeed.com / in.indeed.com.
STATUS: Template — update selectors based on current Indeed UI.
"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text, generate_job_hash


class IndeedScraper(BaseScraper):
    """Indeed job scraper — broad job search engine."""

    @property
    def portal_name(self) -> str:
        return "indeed"

    BASE_URL = "https://in.indeed.com"

    async def login(self) -> bool:
        # Indeed works well without login for search
        logger.info("[indeed] No login required for search")
        return True

    async def search_jobs(
        self, roles: List[str], locations: List[str],
        experience_min: float, experience_max: float,
    ) -> List[JobCreate]:
        all_jobs = []
        for role in roles[:3]:
            for location in locations[:2]:
                try:
                    url = (
                        f"{self.BASE_URL}/jobs"
                        f"?q={role.replace(' ', '+')}"
                        f"&l={location.replace(' ', '+')}"
                        f"&fromage=7"  # Last 7 days
                    )
                    await self.safe_goto(url)
                    await self.random_delay(2, 4)

                    cards = await self._page.query_selector_all(
                        ".job_seen_beacon, .jobsearch-ResultsList > li, .resultContent"
                    )
                    for card in cards[:15]:
                        try:
                            title_el = await card.query_selector("h2 a, .jobTitle a, a.jcs-JobTitle")
                            company_el = await card.query_selector(".company, [data-testid='company-name'], .companyName")
                            loc_el = await card.query_selector(".companyLocation, [data-testid='text-location']")

                            title = clean_text(await title_el.inner_text()) if title_el else None
                            href = await title_el.get_attribute("href") if title_el else None
                            company = clean_text(await company_el.inner_text()) if company_el else "Unknown"
                            loc = clean_text(await loc_el.inner_text()) if loc_el else location

                            if title and href:
                                if not href.startswith("http"):
                                    href = f"{self.BASE_URL}{href}"
                                all_jobs.append(JobCreate(
                                    title=title, company=company, portal="indeed",
                                    external_id=generate_job_hash("indeed", href),
                                    url=href, location=loc,
                                ))
                        except Exception:
                            continue
                    await self.random_delay(3, 5)
                except Exception as e:
                    logger.warning(f"[indeed] Search error: {e}")
        return all_jobs

    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)
            desc_el = await self._page.query_selector("#jobDescriptionText, .jobsearch-JobComponent-description")
            description = clean_text(await desc_el.inner_text()) if desc_el else None
            return {"description": description, "skills": [], "job_type": "Full-time"}
        except Exception as e:
            logger.warning(f"[indeed] Detail parse failed: {e}")
            return None
