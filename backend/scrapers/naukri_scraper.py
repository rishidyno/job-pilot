"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Naukri.com Scraper                                   ║
║                                                                   ║
║  Scrapes job listings from Naukri.com — India's largest          ║
║  job portal. Naukri has good search API-like URLs which           ║
║  makes scraping more reliable than most portals.                  ║
║                                                                   ║
║  NAUKRI URL STRUCTURE:                                            ║
║  https://www.naukri.com/backend-developer-jobs-in-bangalore       ║
║  ?experience=1-3&ctcFilter=6to10                                  ║
║  This makes it easy to construct targeted search URLs.            ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text, generate_job_hash


class NaukriScraper(BaseScraper):
    """
    Naukri.com job scraper.
    
    Naukri is particularly scraping-friendly because:
    - Job search pages have predictable URL patterns
    - Job data is often in structured script tags
    - Less aggressive anti-bot measures than LinkedIn
    """

    @property
    def portal_name(self) -> str:
        return "naukri"

    LOGIN_URL = "https://www.naukri.com/nlogin/login"
    BASE_URL = "https://www.naukri.com"

    async def login(self) -> bool:
        """
        Log into Naukri.com.
        
        Naukri login is straightforward — email/password form.
        Some searches work without login, but login gives access
        to more features and avoids CAPTCHA.
        """
        email = settings.NAUKRI_EMAIL
        password = settings.NAUKRI_PASSWORD

        if not email or not password:
            logger.info("[naukri] No credentials — will scrape without login (limited)")
            return True  # Can still search without login

        try:
            logger.info("[naukri] Logging in...")
            await self.safe_goto(self.LOGIN_URL)
            await self.random_delay(1, 2)

            # Enter email
            await self.human_type("input[placeholder*='Email']", email, delay_ms=70)
            await self.random_delay(0.5, 1)

            # Enter password
            await self.human_type("input[placeholder*='Password'], input[type='password']", password, delay_ms=80)
            await self.random_delay(0.5, 1)

            # Click login button
            await self._page.click("button[type='submit'], .loginButton")
            await self.random_delay(3, 5)

            # Check if login was successful (redirects to dashboard or homepage)
            if "nlogin" not in self._page.url:
                logger.info("[naukri] Login successful")
                return True
            else:
                logger.warning("[naukri] Login may have failed — proceeding anyway")
                return True  # Try to scrape anyway

        except Exception as e:
            logger.warning(f"[naukri] Login failed: {e} — proceeding without login")
            return True  # Naukri works partially without login

    async def search_jobs(
        self,
        roles: List[str],
        locations: List[str],
        experience_min: float,
        experience_max: float,
    ) -> List[JobCreate]:
        """
        Search Naukri.com for jobs matching the criteria.
        
        Naukri URLs follow a pattern:
        /[keyword]-jobs-in-[location]?experience=[min]-[max]
        """
        all_jobs = []
        exp_min = int(experience_min)
        exp_max = int(experience_max) + 1  # Round up

        for role in roles[:4]:  # Search top 4 roles
            for location in locations[:3]:  # Top 3 locations
                try:
                    # Build Naukri search URL
                    keyword = role.lower().replace(" ", "-")
                    loc = location.lower().replace(" ", "-")
                    search_url = (
                        f"{self.BASE_URL}/{keyword}-jobs-in-{loc}"
                        f"?experience={exp_min}-{exp_max}"
                        f"&jobAge=7"  # Jobs posted in last 7 days
                    )

                    jobs = await self._scrape_search_page(search_url)
                    all_jobs.extend(jobs)
                    await self.random_delay(2, 4)

                except Exception as e:
                    logger.warning(f"[naukri] Search failed for '{role}' in '{location}': {e}")

        logger.info(f"[naukri] Total jobs found: {len(all_jobs)}")
        return all_jobs

    async def _scrape_search_page(self, url: str) -> List[JobCreate]:
        """
        Scrape a single Naukri search results page.
        
        Naukri renders job cards with structured data that we can extract.
        """
        jobs = []

        await self.safe_goto(url)
        await self.random_delay(2, 3)

        # Scroll to load more results
        for _ in range(3):
            await self._page.evaluate("window.scrollBy(0, 1000)")
            await self.random_delay(1, 2)

        # Find job cards
        try:
            job_cards = await self._page.query_selector_all(
                "article.jobTuple, .srp-jobtuple-wrapper, .cust-job-tuple"
            )

            for card in job_cards[:20]:
                try:
                    job = await self._parse_naukri_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"[naukri] Card parse error: {e}")

        except Exception as e:
            logger.warning(f"[naukri] No job cards found on page: {e}")

        return jobs

    async def _parse_naukri_card(self, card) -> Optional[JobCreate]:
        """
        Parse a single Naukri job card.
        
        Naukri job cards typically contain:
        - Title (linked to job detail page)
        - Company name
        - Experience required
        - Salary range
        - Location
        - Skills tags
        - Posted date
        """
        try:
            # Title and URL
            title_el = await card.query_selector("a.title, a.subTitle, .row1 a")
            title = clean_text(await title_el.inner_text()) if title_el else None
            url = await title_el.get_attribute("href") if title_el else None

            if not title or not url:
                return None

            # Ensure full URL
            if url and not url.startswith("http"):
                url = f"https://www.naukri.com{url}"

            # Company
            company_el = await card.query_selector("a.comp-name, .subTitle a, .row2 a")
            company = clean_text(await company_el.inner_text()) if company_el else "Unknown"

            # Experience
            exp_el = await card.query_selector(".expwdth, .experience span, .row3 .exp")
            experience = clean_text(await exp_el.inner_text()) if exp_el else None

            # Location
            loc_el = await card.query_selector(".locWdth, .location span, .row3 .loc")
            location = clean_text(await loc_el.inner_text()) if loc_el else None

            # Skills
            skills = []
            skill_els = await card.query_selector_all(".tag-li, .tags .tag, .skills-tag")
            for el in skill_els:
                skill = clean_text(await el.inner_text())
                if skill:
                    skills.append(skill)

            # Extract external ID from URL
            # Naukri URLs often have job ID at the end: /job-detail/123456
            external_id = ""
            if url:
                parts = url.rstrip("/").split("/")
                # Try to find a numeric ID
                for part in reversed(parts):
                    cleaned = part.split("?")[0]
                    if cleaned.isdigit():
                        external_id = cleaned
                        break
                if not external_id:
                    external_id = generate_job_hash("naukri", url)

            return JobCreate(
                title=title,
                company=company,
                portal="naukri",
                external_id=external_id,
                url=url,
                location=location,
                experience_required=experience,
                skills=skills,
            )

        except Exception as e:
            logger.debug(f"[naukri] Parse error: {e}")
            return None

    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        """
        Extract full details from a Naukri job page.
        """
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)

            # Extract full description
            desc_el = await self._page.query_selector(
                ".job-desc, .dang-inner-html, .styles_JDC__dang-inner-html__h0K4t"
            )
            description = clean_text(await desc_el.inner_text()) if desc_el else None

            # Extract skills
            skills = []
            skill_els = await self._page.query_selector_all(
                ".chip_chip, .key-skill a, .styles_chip-item__kJcYz"
            )
            for el in skill_els:
                skill = clean_text(await el.inner_text())
                if skill:
                    skills.append(skill)

            # Extract salary
            salary_el = await self._page.query_selector(".salary, .styles_jhc__salary__jdfEC")
            salary_text = clean_text(await salary_el.inner_text()) if salary_el else None

            return {
                "description": description,
                "skills": skills,
                "salary_text": salary_text,
                "job_type": "Full-time",
            }

        except Exception as e:
            logger.warning(f"[naukri] Job detail parse failed: {e}")
            return None
