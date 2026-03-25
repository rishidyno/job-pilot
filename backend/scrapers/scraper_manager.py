"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Scraper Manager                                      ║
║                                                                   ║
║  Orchestrates all job portal scrapers. This is the single entry   ║
║  point for scraping — it runs all enabled scrapers, deduplicates  ║
║  results, scores jobs, and saves to MongoDB.                      ║
║                                                                   ║
║  FLOW:                                                            ║
║  1. ScraperManager.scrape_all() is called (by scheduler or API)  ║
║  2. Each enabled scraper runs in sequence (not parallel, to       ║
║     avoid overwhelming the machine with multiple browsers)        ║
║  3. Results are deduplicated against existing DB entries          ║
║  4. New jobs get a quick match score                              ║
║  5. High-scoring jobs get full AI scoring                         ║
║  6. Results saved to MongoDB                                      ║
║  7. Telegram notifications sent for high matches                  ║
║                                                                   ║
║  TO ADD A NEW SCRAPER:                                            ║
║  1. Create the scraper class (extend BaseScraper)                ║
║  2. Import it here                                                ║
║  3. Add it to the SCRAPERS dict                                  ║
║  That's it! The manager handles the rest.                         ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Dict, List, Optional
from pymongo.errors import DuplicateKeyError

from scrapers.base_scraper import BaseScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.naukri_scraper import NaukriScraper
from scrapers.wellfound_scraper import WellfoundScraper
from scrapers.instahyre_scraper import InstahyreScraper
from scrapers.indeed_scraper import IndeedScraper
from scrapers.glassdoor_scraper import GlassdoorScraper

from services.job_matcher import job_matcher
from services.telegram_service import telegram_service
from database import get_collection
from config import settings
from utils.logger import logger
from utils.helpers import utc_now, generate_job_hash


# ─────────────────────────────────────
# SCRAPER REGISTRY
# Add new scrapers here!
# ─────────────────────────────────────
SCRAPERS: Dict[str, type] = {
    "linkedin": LinkedInScraper,
    "naukri": NaukriScraper,
    "wellfound": WellfoundScraper,
    "instahyre": InstahyreScraper,
    "indeed": IndeedScraper,
    "glassdoor": GlassdoorScraper,
}


class ScraperManager:
    """
    Orchestrates all scrapers and manages the scraping pipeline.
    
    This is the top-level class that the scheduler and API call
    to trigger scraping operations.
    """

    async def scrape_all(self, portals: Optional[List[str]] = None, user_id: Optional[str] = None) -> dict:
        """
        Run all enabled scrapers and process results.
        
        Args:
            portals: Specific portals to scrape (None = all registered)
        
        Returns:
            dict: Summary stats of the scrape run
                  {total_found, new_jobs, duplicates, errors, high_matches}
        """
        # Determine which scrapers to run
        target_portals = portals or list(SCRAPERS.keys())

        stats = {
            "started_at": utc_now(),
            "total_found": 0,
            "new_jobs": 0,
            "duplicates": 0,
            "errors": 0,
            "high_matches": 0,
            "portal_stats": {},
        }

        logger.info(f"🔍 Starting scrape run for portals: {', '.join(target_portals)}")

        for portal_name in target_portals:
            if portal_name not in SCRAPERS:
                logger.warning(f"Unknown portal: {portal_name}")
                continue

            portal_stats = await self._scrape_portal(portal_name, user_id=user_id)
            stats["portal_stats"][portal_name] = portal_stats
            stats["total_found"] += portal_stats["found"]
            stats["new_jobs"] += portal_stats["new"]
            stats["duplicates"] += portal_stats["duplicates"]
            stats["errors"] += portal_stats["errors"]
            stats["high_matches"] += portal_stats["high_matches"]

        stats["completed_at"] = utc_now()
        stats["duration_seconds"] = (
            stats["completed_at"] - stats["started_at"]
        ).total_seconds()

        # Save scrape log to database
        scrape_logs = get_collection("scrape_logs")
        log_data = {**stats}
        log_data["user_id"] = user_id
        log_data["started_at"] = stats["started_at"]
        log_data["completed_at"] = stats["completed_at"]
        await scrape_logs.insert_one(log_data)

        logger.info(
            f"✅ Scrape complete: {stats['total_found']} found, "
            f"{stats['new_jobs']} new, {stats['high_matches']} high matches"
        )

        return stats

    async def _scrape_portal(self, portal_name: str, user_id: Optional[str] = None) -> dict:
        """
        Run a single portal scraper and process its results.
        
        Args:
            portal_name: Name of the portal to scrape
        
        Returns:
            dict: Stats for this portal's scrape run
        """
        portal_stats = {"found": 0, "new": 0, "duplicates": 0, "errors": 0, "high_matches": 0}

        try:
            # Create scraper instance and run
            scraper_class = SCRAPERS[portal_name]
            scraper: BaseScraper = scraper_class()

            logger.info(f"[{portal_name}] Starting scrape...")
            jobs = await scraper.scrape()
            portal_stats["found"] = len(jobs)

            # Process each job: deduplicate, score, save
            jobs_collection = get_collection("jobs")

            for job_data in jobs:
                try:
                    # Generate dedup hash
                    job_hash = generate_job_hash(job_data.portal, job_data.external_id)

                    # Build the document to insert
                    job_doc = job_data.model_dump()
                    job_doc["job_hash"] = job_hash
                    job_doc["user_id"] = user_id
                    job_doc["created_at"] = utc_now()
                    job_doc["updated_at"] = utc_now()
                    job_doc["status"] = "new"

                    # Quick score (heuristic, no API call)
                    quick_score = await job_matcher.quick_score(
                        job_title=job_data.title,
                        job_skills=job_data.skills,
                        job_location=job_data.location or "",
                        user_skills=settings.target_skills_list,
                        user_target_locations=settings.target_locations_list,
                    )
                    job_doc["match_score"] = quick_score

                    # Try to insert (unique index on portal+external_id prevents dupes)
                    try:
                        await jobs_collection.insert_one(job_doc)
                        portal_stats["new"] += 1

                        # Notify via Telegram if high match
                        if quick_score >= settings.MIN_MATCH_SCORE_TO_APPLY:
                            portal_stats["high_matches"] += 1
                            await telegram_service.notify_new_job(
                                title=job_data.title,
                                company=job_data.company,
                                location=job_data.location or "Not specified",
                                match_score=quick_score,
                                url=job_data.url,
                                portal=portal_name,
                            )

                    except DuplicateKeyError:
                        # Job already exists for this user — update last_seen timestamp
                        portal_stats["duplicates"] += 1
                        await jobs_collection.update_one(
                            {"user_id": user_id, "portal": job_data.portal, "external_id": job_data.external_id},
                            {"$set": {"updated_at": utc_now()}},
                        )

                except Exception as e:
                    portal_stats["errors"] += 1
                    logger.warning(f"[{portal_name}] Error processing job: {e}")

            # Send scrape completion notification
            await telegram_service.notify_scrape_complete(
                portal=portal_name,
                jobs_found=portal_stats["found"],
                new_jobs=portal_stats["new"],
                high_matches=portal_stats["high_matches"],
            )

        except Exception as e:
            portal_stats["errors"] += 1
            logger.error(f"[{portal_name}] Scraper failed: {e}")

        return portal_stats

    async def scrape_single(self, portal_name: str, user_id: Optional[str] = None) -> dict:
        """Convenience method to scrape a single portal."""
        return await self.scrape_all(portals=[portal_name], user_id=user_id)


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
scraper_manager = ScraperManager()
