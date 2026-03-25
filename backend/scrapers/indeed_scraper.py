"""
JOBPILOT — Indeed Scraper

Scrapes jobs from in.indeed.com.
Extracts real job URLs using the jk (job key) parameter.
"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text


class IndeedScraper(BaseScraper):

    @property
    def portal_name(self) -> str:
        return "indeed"

    BASE_URL = "https://in.indeed.com"

    async def login(self) -> bool:
        logger.info("[indeed] No login required for search")
        return True

    async def search_jobs(
        self, roles: List[str], locations: List[str],
        experience_min: float, experience_max: float,
    ) -> List[JobCreate]:
        all_jobs = []
        seen_ids = set()

        for role in roles[:3]:
            for location in locations[:2]:
                try:
                    url = (
                        f"{self.BASE_URL}/jobs"
                        f"?q={role.replace(' ', '+')}"
                        f"&l={location.replace(' ', '+')}"
                        f"&fromage=7"
                    )
                    await self.safe_goto(url)
                    await self.random_delay(2, 4)

                    # Extract job data from the page using JS to get jk (job key)
                    jobs_data = await self._page.evaluate('''() => {
                        const results = [];
                        // Indeed stores job keys in data attributes or href params
                        const cards = document.querySelectorAll(
                            '.job_seen_beacon, .resultContent, .jobsearch-ResultsList > li'
                        );
                        for (const card of cards) {
                            try {
                                const titleEl = card.querySelector('h2 a, .jobTitle a, a.jcs-JobTitle');
                                const companyEl = card.querySelector('.company, [data-testid="company-name"], .companyName');
                                const locEl = card.querySelector('.companyLocation, [data-testid="text-location"]');

                                if (!titleEl) continue;

                                const title = titleEl.innerText?.trim();
                                const href = titleEl.getAttribute('href') || '';
                                const company = companyEl?.innerText?.trim() || 'Unknown';
                                const loc = locEl?.innerText?.trim() || '';

                                // Extract job key from href (?jk=xxx) or data attribute
                                let jk = '';
                                const jkMatch = href.match(/[?&]jk=([a-f0-9]+)/);
                                if (jkMatch) {
                                    jk = jkMatch[1];
                                } else {
                                    // Try data-jk attribute on parent elements
                                    const parent = card.closest('[data-jk]') || card.querySelector('[data-jk]');
                                    if (parent) jk = parent.getAttribute('data-jk');
                                }

                                if (title && jk) {
                                    results.push({ title, company, loc, jk });
                                } else if (title && href) {
                                    results.push({ title, company, loc, href });
                                }
                            } catch {}
                        }
                        return results;
                    }''')

                    for item in jobs_data[:15]:
                        jk = item.get('jk', '')
                        if jk:
                            if jk in seen_ids:
                                continue
                            seen_ids.add(jk)
                            # Build the real viewjob URL using the job key
                            job_url = f"{self.BASE_URL}/viewjob?jk={jk}"
                            external_id = jk
                        else:
                            href = item.get('href', '')
                            if not href:
                                continue
                            if not href.startswith('http'):
                                href = f"{self.BASE_URL}{href}"
                            job_url = href
                            external_id = href

                        all_jobs.append(JobCreate(
                            title=clean_text(item['title']),
                            company=clean_text(item['company']),
                            portal="indeed",
                            external_id=external_id,
                            url=job_url,
                            location=clean_text(item.get('loc', '')) or location,
                        ))

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
