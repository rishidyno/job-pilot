"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Base Scraper (Abstract Base Class)                   ║
║                                                                   ║
║  All job portal scrapers MUST extend this class.                  ║
║  It provides the common interface and shared utilities.           ║
║                                                                   ║
║  TO ADD A NEW SCRAPER:                                            ║
║  1. Create a new file: scrapers/myportal_scraper.py              ║
║  2. Create a class that extends BaseScraper                       ║
║  3. Implement: login(), search_jobs(), parse_job_detail()        ║
║  4. Register in scraper_manager.py                                ║
║                                                                   ║
║  See docs/SCRAPER_GUIDE.md for detailed instructions.             ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from models.job import JobCreate
from config import settings
from utils.logger import logger


class BaseScraper(ABC):
    """
    Abstract base class for all job portal scrapers.
    
    Provides:
    - Playwright browser management (launch, close, new page)
    - Anti-detection measures (random delays, user-agent rotation)
    - Common cookie/session handling
    - Logging and error handling patterns
    
    Subclasses must implement:
    - portal_name (property): unique identifier for this portal
    - login(): authenticate with the portal
    - search_jobs(): find job listings matching criteria
    - parse_job_detail(): extract full details from a job page
    """

    # ─────────────────────────────────────
    # User-Agent pool for rotation
    # Rotating UAs helps avoid bot detection
    # ─────────────────────────────────────
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]

    def __init__(self):
        """Initialize scraper state (browser not launched yet)."""
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    # ─────────────────────────────────────
    # Abstract properties & methods
    # Subclasses MUST implement these
    # ─────────────────────────────────────

    @property
    @abstractmethod
    def portal_name(self) -> str:
        """
        Unique identifier for this portal (e.g., 'linkedin', 'naukri').
        Used for logging, database entries, and deduplication.
        """
        ...

    @abstractmethod
    async def login(self) -> bool:
        """
        Authenticate with the job portal.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        ...

    @abstractmethod
    async def search_jobs(
        self,
        roles: List[str],
        locations: List[str],
        experience_min: float,
        experience_max: float,
    ) -> List[JobCreate]:
        """
        Search the portal for matching jobs.
        
        Args:
            roles: Job titles to search for
            locations: Preferred locations
            experience_min: Minimum years of experience
            experience_max: Maximum years of experience
        
        Returns:
            List of JobCreate objects with scraped data
        """
        ...

    @abstractmethod
    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        """
        Extract full details from a specific job listing page.
        
        Called after search_jobs() to enrich job data with full
        description, requirements, etc.
        
        Args:
            job_url: Direct URL to the job posting
        
        Returns:
            dict with additional job details, or None if parsing fails
        """
        ...

    # ─────────────────────────────────────
    # Browser Management
    # ─────────────────────────────────────

    async def launch_browser(self) -> None:
        """
        Launch browser for scraping.
        Uses system Chrome (channel='chrome') which is more stable
        than bundled Chromium inside server processes.
        """
        logger.info(f"[{self.portal_name}] Launching browser...")

        self._playwright = await async_playwright().start()

        # Use system Chrome — bundled Chromium crashes inside uvicorn
        self._browser = await self._playwright.chromium.launch(
            headless=settings.PLAYWRIGHT_HEADLESS,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        self._context = await self._browser.new_context(
            user_agent=random.choice(self.USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="Asia/Kolkata",
        )

        self._page = await self._context.new_page()

        await self._page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        logger.info(f"[{self.portal_name}] Browser launched")

    async def close_browser(self) -> None:
        """
        Close the browser and clean up resources.
        
        Always call this when done scraping, even on error.
        Use try/finally or the context manager pattern.
        """
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            logger.info(f"[{self.portal_name}] Browser closed")
        except Exception as e:
            logger.warning(f"[{self.portal_name}] Error closing browser: {e}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

    # ─────────────────────────────────────
    # Anti-Detection Utilities
    # ─────────────────────────────────────

    async def random_delay(self, min_sec: Optional[float] = None, max_sec: Optional[float] = None) -> None:
        """
        Wait a random amount of time between actions.
        
        This is CRITICAL for avoiding bot detection. Job portals
        track request timing and will block or CAPTCHA you if
        requests come in too fast or at regular intervals.
        
        Args:
            min_sec: Minimum wait (defaults to config SCRAPE_DELAY_MIN)
            max_sec: Maximum wait (defaults to config SCRAPE_DELAY_MAX)
        """
        min_s = min_sec or settings.SCRAPE_DELAY_MIN
        max_s = max_sec or settings.SCRAPE_DELAY_MAX
        delay = random.uniform(min_s, max_s)
        await asyncio.sleep(delay)

    async def human_type(self, selector: str, text: str, delay_ms: int = 100) -> None:
        """
        Type text into an input field with human-like delays.
        
        Instead of instantly setting the value (which is detectable),
        this types each character with a random delay.
        
        Args:
            selector: CSS selector for the input field
            text: Text to type
            delay_ms: Average milliseconds between keystrokes
        """
        if self._page:
            await self._page.click(selector)
            await self._page.type(selector, text, delay=delay_ms)

    async def safe_goto(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """
        Navigate to a URL with error handling.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation done:
                        "domcontentloaded", "load", "networkidle"
        
        Returns:
            bool: True if navigation successful
        """
        try:
            if self._page:
                await self._page.goto(url, wait_until=wait_until, timeout=30000)
                return True
        except Exception as e:
            logger.warning(f"[{self.portal_name}] Navigation failed to {url}: {e}")
        return False

    # ─────────────────────────────────────
    # Main Scrape Orchestrator
    # ─────────────────────────────────────

    async def scrape(self) -> List[JobCreate]:
        """
        Full scraping pipeline: launch → login → search → close.
        
        This is the main entry point called by the ScraperManager.
        It handles the full lifecycle including error handling
        and browser cleanup.
        
        Returns:
            List of JobCreate objects (can be empty on failure)
        """
        jobs = []
        try:
            # Step 1: Launch browser
            await self.launch_browser()

            # Step 2: Login
            logged_in = await self.login()
            if not logged_in:
                logger.warning(f"[{self.portal_name}] Login failed — skipping")
                return []

            # Step 3: Search for jobs
            jobs = await self.search_jobs(
                roles=settings.target_roles_list,
                locations=settings.target_locations_list,
                experience_min=settings.TARGET_EXPERIENCE_MIN,
                experience_max=settings.TARGET_EXPERIENCE_MAX,
            )

            logger.info(f"[{self.portal_name}] Scrape complete: {len(jobs)} jobs found")

        except Exception as e:
            logger.error(f"[{self.portal_name}] Scrape failed: {e}")

        finally:
            # Always clean up browser resources
            await self.close_browser()

        return jobs
