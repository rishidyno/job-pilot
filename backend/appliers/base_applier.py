"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Base Applier (Abstract Base Class)                   ║
║                                                                   ║
║  All auto-apply modules extend this class. Each portal has       ║
║  its own application flow (Easy Apply, form filling, etc.)       ║
║                                                                   ║
║  TO ADD A NEW APPLIER:                                            ║
║  1. Create: appliers/myportal_applier.py                         ║
║  2. Extend BaseApplier, implement apply_to_job()                 ║
║  3. Register in applier_manager.py                                ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from abc import ABC, abstractmethod
from typing import Optional
from scrapers.base_scraper import BaseScraper


class BaseApplier(BaseScraper, ABC):
    """
    Abstract base class for auto-apply modules.
    
    Extends BaseScraper because it needs the same browser
    automation capabilities (Playwright, anti-detection, etc.).
    
    Subclasses must implement:
    - apply_to_job(): Submit an application to a specific job
    
    Inherited from BaseScraper:
    - launch_browser(), close_browser()
    - login()
    - random_delay(), human_type(), safe_goto()
    """

    @abstractmethod
    async def apply_to_job(
        self,
        job_url: str,
        resume_path: Optional[str] = None,
        cover_letter_path: Optional[str] = None,
        additional_data: Optional[dict] = None,
    ) -> dict:
        """
        Apply to a specific job listing.
        
        Args:
            job_url: Direct URL to the job posting
            resume_path: Path to the tailored resume PDF to upload
            cover_letter_path: Path to the cover letter PDF (optional)
            additional_data: Extra fields some portals require
                            (e.g., phone, current CTC, notice period)
        
        Returns:
            dict with keys:
                - success (bool): Whether application was submitted
                - confirmation_id (str): Portal's confirmation ID if available
                - error (str): Error message if failed
                - method (str): How it was applied (easy_apply, form, email)
        """
        ...

    # BaseApplier doesn't need search_jobs or parse_job_detail
    # (it's an applier, not a scraper) — provide no-op implementations

    async def search_jobs(self, *args, **kwargs):
        """Not used by appliers — returns empty list."""
        return []

    async def parse_job_detail(self, *args, **kwargs):
        """Not used by appliers — returns None."""
        return None
