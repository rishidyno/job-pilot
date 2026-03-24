# JobPilot — Adding a New Job Portal Scraper

## Overview

Adding a new job portal scraper is designed to be straightforward. You create a single Python file, implement 3 methods, and register it. The manager handles everything else (deduplication, scoring, notifications, DB storage).

## Step-by-Step Guide

### Step 1: Create the scraper file

Create `backend/scrapers/myportal_scraper.py`:

```python
"""JOBPILOT — MyPortal Scraper"""

from typing import List, Optional
from scrapers.base_scraper import BaseScraper
from models.job import JobCreate
from config import settings
from utils.logger import logger
from utils.helpers import clean_text, generate_job_hash


class MyPortalScraper(BaseScraper):
    """Scraper for MyPortal job listings."""

    @property
    def portal_name(self) -> str:
        """Unique identifier — used in DB, logs, and UI."""
        return "myportal"

    async def login(self) -> bool:
        """
        Authenticate with the portal.
        Return True if login succeeded (or if login isn't needed).
        """
        # Option A: Portal requires login
        email = settings.MYPORTAL_EMAIL  # Add to config.py first!
        password = settings.MYPORTAL_PASSWORD
        if not email or not password:
            return False
        
        await self.safe_goto("https://myportal.com/login")
        await self.human_type("input[name='email']", email)
        await self.human_type("input[name='password']", password)
        await self._page.click("button[type='submit']")
        await self.random_delay(3, 5)
        return True
        
        # Option B: No login needed
        # return True

    async def search_jobs(
        self,
        roles: List[str],
        locations: List[str],
        experience_min: float,
        experience_max: float,
    ) -> List[JobCreate]:
        """Search the portal and return JobCreate objects."""
        all_jobs = []
        
        for role in roles[:3]:
            url = f"https://myportal.com/search?q={role}"
            await self.safe_goto(url)
            await self.random_delay(2, 4)
            
            # Find job cards (update these selectors!)
            cards = await self._page.query_selector_all(".job-card")
            
            for card in cards[:15]:
                title_el = await card.query_selector("h2")
                company_el = await card.query_selector(".company")
                link_el = await card.query_selector("a")
                
                title = clean_text(await title_el.inner_text()) if title_el else None
                company = clean_text(await company_el.inner_text()) if company_el else "Unknown"
                url = await link_el.get_attribute("href") if link_el else None
                
                if title and url:
                    all_jobs.append(JobCreate(
                        title=title,
                        company=company,
                        portal="myportal",
                        external_id=generate_job_hash("myportal", url),
                        url=url,
                    ))
        
        return all_jobs

    async def parse_job_detail(self, job_url: str) -> Optional[dict]:
        """Fetch full details from a job page."""
        await self.safe_goto(job_url)
        await self.random_delay(2, 3)
        
        desc_el = await self._page.query_selector(".job-description")
        description = clean_text(await desc_el.inner_text()) if desc_el else None
        
        return {"description": description, "skills": [], "job_type": "Full-time"}
```

### Step 2: Add credentials to config (if needed)

In `backend/config.py`, add:
```python
MYPORTAL_EMAIL: str = ""
MYPORTAL_PASSWORD: str = ""
```

And in `.env.example`:
```
MYPORTAL_EMAIL=
MYPORTAL_PASSWORD=
```

### Step 3: Register the scraper

In `backend/scrapers/scraper_manager.py`, add:
```python
from scrapers.myportal_scraper import MyPortalScraper

SCRAPERS: Dict[str, type] = {
    # ... existing scrapers ...
    "myportal": MyPortalScraper,
}
```

### Step 4: (Optional) Add an auto-applier

Follow the same pattern in `backend/appliers/` — extend `BaseApplier`.

## Tips for Writing Scrapers

1. **Use `self.random_delay()`** between every action — this is critical for avoiding detection
2. **Use `self.human_type()`** instead of `page.fill()` for text inputs
3. **CSS selectors change** — check the portal's current DOM before writing selectors
4. **Handle errors gracefully** — return empty lists/None instead of crashing
5. **Limit results** — don't scrape 1000 jobs per run; 15-20 per search is fine
6. **Test with `PLAYWRIGHT_HEADLESS=false`** to watch the browser and debug
