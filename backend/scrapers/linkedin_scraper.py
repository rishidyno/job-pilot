"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — LinkedIn Scraper                                     ║
║                                                                   ║
║  Scrapes job listings from LinkedIn Jobs.                         ║
║  Uses Playwright for browser automation (handles JS rendering).   ║
║                                                                   ║
║  NOTE ON LINKEDIN SCRAPING:                                       ║
║  LinkedIn actively fights scraping. This scraper:                 ║
║  - Uses your real account credentials                             ║
║  - Mimics human behavior (delays, scrolling, typing speed)        ║
║  - Respects rate limits to avoid account restrictions             ║
║  - May need periodic updates as LinkedIn changes their DOM        ║
║                                                                   ║
║  IMPORTANT: Use responsibly. Excessive scraping may result         ║
║  in account restrictions. Keep SCRAPE_INTERVAL_HOURS >= 6.        ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text, generate_job_hash


class LinkedInScraper(BaseScraper):
    """
    LinkedIn Jobs scraper.
    
    Navigates to LinkedIn, logs in, searches for jobs using
    the configured criteria, and extracts listing data.
    
    CSS selectors may need updating as LinkedIn changes their UI.
    Last verified: March 2026.
    """

    @property
    def portal_name(self) -> str:
        return "linkedin"

    # ─────────────────────────────────────
    # LinkedIn-specific URLs
    # ─────────────────────────────────────
    LOGIN_URL = "https://www.linkedin.com/login"
    JOBS_URL = "https://www.linkedin.com/jobs/search/"

    async def login(self) -> bool:
        """
        Log into LinkedIn with credentials from .env.
        
        Flow:
        1. Navigate to login page
        2. Enter email and password with human-like typing
        3. Click sign-in
        4. Wait for redirect to feed (confirms login success)
        
        Returns:
            bool: True if login succeeded
        """
        email = settings.LINKEDIN_EMAIL
        password = settings.LINKEDIN_PASSWORD

        if not email or not password:
            logger.warning("[linkedin] No credentials configured — skipping")
            return False

        try:
            logger.info("[linkedin] Logging in...")

            # Navigate to login page
            await self.safe_goto(self.LOGIN_URL)
            await self.random_delay(1, 2)

            # Enter email
            await self.human_type("#username", email, delay_ms=80)
            await self.random_delay(0.5, 1)

            # Enter password
            await self.human_type("#password", password, delay_ms=90)
            await self.random_delay(0.5, 1.5)

            # Click sign in
            await self._page.click('button[type="submit"]')

            # Wait for navigation to feed or jobs page
            await self._page.wait_for_url("**/feed/**", timeout=30000)

            logger.info("[linkedin] Login successful")
            return True

        except Exception as e:
            logger.error(f"[linkedin] Login failed: {e}")
            # Check if there's a security challenge (CAPTCHA, verification)
            current_url = self._page.url if self._page else ""
            if "challenge" in current_url or "checkpoint" in current_url:
                logger.error(
                    "[linkedin] Security challenge detected. "
                    "Login manually once, then try again."
                )
            return False

    async def search_jobs(
        self,
        roles: List[str],
        locations: List[str],
        experience_min: float,
        experience_max: float,
    ) -> List[JobCreate]:
        """
        Search LinkedIn Jobs with the given criteria.
        
        LinkedIn's search supports keyword + location + filters.
        We search for each role separately and combine results.
        
        Args:
            roles: Job titles to search for
            locations: Preferred locations
            experience_min: Min years of experience
            experience_max: Max years of experience
        
        Returns:
            List of JobCreate objects
        """
        all_jobs = []

        # LinkedIn experience level mapping
        # f_E=2 → Entry level, f_E=3 → Associate, f_E=4 → Mid-Senior
        experience_filter = "2,3"  # Entry + Associate for 1.5-2 YOE

        for role in roles[:3]:  # Limit to 3 roles to avoid rate limiting
            for location in locations[:2]:  # Top 2 locations per role
                try:
                    jobs = await self._search_single(role, location, experience_filter)
                    all_jobs.extend(jobs)
                    await self.random_delay(3, 6)  # Extra delay between searches
                except Exception as e:
                    logger.warning(f"[linkedin] Search failed for '{role}' in '{location}': {e}")

        logger.info(f"[linkedin] Total jobs found: {len(all_jobs)}")
        return all_jobs

    async def _search_single(
        self,
        role: str,
        location: str,
        experience_filter: str,
    ) -> List[JobCreate]:
        """
        Execute a single search query on LinkedIn.
        
        Args:
            role: Job title to search
            location: Location to search in
            experience_filter: LinkedIn experience level codes
        
        Returns:
            List of JobCreate objects from this search
        """
        jobs = []

        # Build search URL with query params
        search_url = (
            f"{self.JOBS_URL}"
            f"?keywords={role.replace(' ', '%20')}"
            f"&location={location.replace(' ', '%20')}"
            f"&f_E={experience_filter}"  # Experience level filter
            f"&f_TPR=r604800"  # Posted in last week
            f"&sortBy=R"  # Sort by relevance
        )

        await self.safe_goto(search_url)
        await self.random_delay(2, 4)

        # Scroll to load more results (LinkedIn uses lazy loading)
        for _ in range(3):
            await self._page.evaluate("window.scrollBy(0, 800)")
            await self.random_delay(1, 2)

        # Extract job cards from the search results
        # NOTE: These selectors may change as LinkedIn updates their UI
        try:
            job_cards = await self._page.query_selector_all(
                ".jobs-search-results__list-item, .job-card-container"
            )

            for card in job_cards[:15]:  # Max 15 per search
                try:
                    job = await self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"[linkedin] Failed to parse a job card: {e}")

        except Exception as e:
            logger.warning(f"[linkedin] Failed to find job cards: {e}")

        return jobs

    async def _parse_job_card(self, card) -> Optional[JobCreate]:
        """
        Parse a single job card element from search results.
        
        Extracts: title, company, location, URL, external ID.
        Full description is fetched later via parse_job_detail().
        
        Args:
            card: Playwright ElementHandle for the job card
        
        Returns:
            JobCreate or None if parsing fails
        """
        try:
            # Extract title
            title_el = await card.query_selector(
                ".job-card-list__title, .artdeco-entity-lockup__title"
            )
            title = clean_text(await title_el.inner_text()) if title_el else None

            # Extract company name
            company_el = await card.query_selector(
                ".job-card-container__primary-description, .artdeco-entity-lockup__subtitle"
            )
            company = clean_text(await company_el.inner_text()) if company_el else "Unknown"

            # Extract location
            location_el = await card.query_selector(
                ".job-card-container__metadata-item, .artdeco-entity-lockup__caption"
            )
            location = clean_text(await location_el.inner_text()) if location_el else None

            # Extract job URL and ID
            link_el = await card.query_selector("a[href*='/jobs/view/']")
            url = await link_el.get_attribute("href") if link_el else None

            if not title or not url:
                return None

            # Clean URL and extract job ID
            if url and not url.startswith("http"):
                url = f"https://www.linkedin.com{url}"

            # Extract external ID from URL (e.g., /jobs/view/3847291056/)
            external_id = ""
            if "/jobs/view/" in url:
                external_id = url.split("/jobs/view/")[1].split("/")[0].split("?")[0]

            return JobCreate(
                title=title,
                company=company,
                portal="linkedin",
                external_id=external_id or generate_job_hash("linkedin", url),
                url=url,
                location=location,
                apply_method="easy_apply",  # Most LinkedIn jobs support Easy Apply
            )

        except Exception as e:
            logger.debug(f"[linkedin] Job card parse error: {e}")
            return None

    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        """
        Fetch full details from a LinkedIn job posting page.
        
        Navigates to the job URL and extracts the full description,
        skills, experience requirements, etc.
        
        Args:
            job_url: Direct URL to the job posting
        
        Returns:
            dict with additional job details:
            - description: Full job description text
            - skills: List of required skills
            - experience_required: Experience text
            - job_type: Full-time, contract, etc.
        """
        try:
            await self.safe_goto(job_url)
            await self.random_delay(2, 3)

            # Click "Show more" to expand full description
            try:
                show_more = await self._page.query_selector(
                    "button.show-more-less-html__button--more"
                )
                if show_more:
                    await show_more.click()
                    await self.random_delay(0.5, 1)
            except Exception:
                pass  # Description might already be expanded

            # Extract description
            desc_el = await self._page.query_selector(
                ".show-more-less-html__markup, .jobs-description-content__text"
            )
            description = clean_text(await desc_el.inner_text()) if desc_el else None

            # Extract skills from the skills section
            skills = []
            try:
                skill_elements = await self._page.query_selector_all(
                    ".job-details-skill-match-status-list li, "
                    ".jobs-unified-top-card__job-insight span"
                )
                for el in skill_elements:
                    text = clean_text(await el.inner_text())
                    if text and len(text) < 50:  # Filter out non-skill text
                        skills.append(text)
            except Exception:
                pass

            # Extract experience/seniority level
            experience = None
            try:
                criteria_items = await self._page.query_selector_all(
                    ".description__job-criteria-item"
                )
                for item in criteria_items:
                    header = await item.query_selector("h3")
                    value = await item.query_selector("span")
                    if header and value:
                        h_text = clean_text(await header.inner_text())
                        v_text = clean_text(await value.inner_text())
                        if "seniority" in h_text.lower() or "experience" in h_text.lower():
                            experience = v_text
            except Exception:
                pass

            return {
                "description": description,
                "skills": skills,
                "experience_required": experience,
                "job_type": "Full-time",  # Default for LinkedIn
            }

        except Exception as e:
            logger.warning(f"[linkedin] Failed to parse job detail {job_url}: {e}")
            return None
