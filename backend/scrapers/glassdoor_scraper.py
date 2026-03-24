"""
JOBPILOT — Glassdoor Scraper

Scrapes jobs from Glassdoor. Note: Glassdoor has aggressive anti-bot
measures. This scraper may need frequent selector updates.
STATUS: Template — update selectors based on current Glassdoor UI.
"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text, generate_job_hash


class GlassdoorScraper(BaseScraper):
    """Glassdoor job scraper — includes company reviews + salary data."""

    @property
    def portal_name(self) -> str:
        return "glassdoor"

    async def login(self) -> bool:
        email = settings.GLASSDOOR_EMAIL
        password = settings.GLASSDOOR_PASSWORD
        if not email or not password:
            logger.info("[glassdoor] No credentials — browsing publicly")
            return True
        try:
            await self.safe_goto("https://www.glassdoor.co.in/profile/login_input.htm")
            await self.random_delay(1, 2)
            await self.human_type("input[name='username']", email)
            await self.human_type("input[name='password']", password)
            await self._page.click("button[type='submit']")
            await self.random_delay(3, 5)
            return True
        except Exception as e:
            logger.warning(f"[glassdoor] Login failed: {e}")
            return True

    async def search_jobs(
        self, roles: List[str], locations: List[str],
        experience_min: float, experience_max: float,
    ) -> List[JobCreate]:
        all_jobs = []
        for role in roles[:2]:
            try:
                url = f"https://www.glassdoor.co.in/Job/india-{role.lower().replace(' ', '-')}-jobs-SRCH_IL.0,5_IN115_KO6,{6+len(role)}.htm"
                await self.safe_goto(url)
                await self.random_delay(2, 4)

                cards = await self._page.query_selector_all(
                    "li.react-job-listing, [data-test='jobListing']"
                )
                for card in cards[:15]:
                    try:
                        title_el = await card.query_selector("a[data-test='job-link'], .jobLink")
                        company_el = await card.query_selector(".job-search-key-l2hmjt, .employerName")
                        loc_el = await card.query_selector(".job-search-key-location, .location")

                        title = clean_text(await title_el.inner_text()) if title_el else None
                        href = await title_el.get_attribute("href") if title_el else None
                        company = clean_text(await company_el.inner_text()) if company_el else "Unknown"
                        loc = clean_text(await loc_el.inner_text()) if loc_el else None

                        if title and href:
                            if not href.startswith("http"):
                                href = f"https://www.glassdoor.co.in{href}"
                            all_jobs.append(JobCreate(
                                title=title, company=company, portal="glassdoor",
                                external_id=generate_job_hash("glassdoor", href),
                                url=href, location=loc,
                            ))
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"[glassdoor] Search error: {e}")
        return all_jobs

    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)
            desc_el = await self._page.query_selector(".jobDescriptionContent, [data-test='jobDescription']")
            description = clean_text(await desc_el.inner_text()) if desc_el else None
            return {"description": description, "skills": [], "job_type": "Full-time"}
        except Exception as e:
            logger.warning(f"[glassdoor] Detail parse failed: {e}")
            return None
