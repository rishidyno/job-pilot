"""
JOBPILOT — Scraper Manager with live event logging.
"""

from datetime import datetime
from typing import Dict, List, Optional, Callable

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
from utils.helpers import utc_now, generate_job_hash, clean_url


SCRAPERS: Dict[str, type] = {
    "linkedin": LinkedInScraper,
    "naukri": NaukriScraper,
    "wellfound": WellfoundScraper,
    "instahyre": InstahyreScraper,
    "indeed": IndeedScraper,
    "glassdoor": GlassdoorScraper,
}


class ScraperManager:

    async def scrape_all(self, portals: Optional[List[str]] = None, user_id: Optional[str] = None, on_event: Optional[Callable] = None) -> dict:
        target_portals = portals or list(SCRAPERS.keys())
        emit = on_event or (lambda *a: None)

        stats = {
            "started_at": utc_now(),
            "total_found": 0, "new_jobs": 0, "duplicates": 0,
            "errors": 0, "high_matches": 0, "portal_stats": {},
        }

        for portal_name in target_portals:
            if portal_name not in SCRAPERS:
                emit("warn", f"Unknown portal: {portal_name}")
                continue

            portal_stats = await self._scrape_portal(portal_name, user_id=user_id, on_event=emit)
            stats["portal_stats"][portal_name] = portal_stats
            stats["total_found"] += portal_stats["found"]
            stats["new_jobs"] += portal_stats["new"]
            stats["duplicates"] += portal_stats["duplicates"]
            stats["errors"] += portal_stats["errors"]
            stats["high_matches"] += portal_stats["high_matches"]

        stats["completed_at"] = utc_now()
        stats["duration_seconds"] = (stats["completed_at"] - stats["started_at"]).total_seconds()

        scrape_logs = get_collection("scrape_logs")
        log_data = {**stats, "user_id": user_id}
        await scrape_logs.insert_one(log_data)

        return stats

    async def _scrape_portal(self, portal_name: str, user_id: Optional[str] = None, on_event: Optional[Callable] = None) -> dict:
        emit = on_event or (lambda *a: None)
        portal_stats = {"found": 0, "new": 0, "duplicates": 0, "errors": 0, "high_matches": 0}

        try:
            scraper_class = SCRAPERS[portal_name]
            scraper: BaseScraper = scraper_class()

            # ── Launch browser ──
            emit("step", f"[{portal_name}] Launching browser...")
            try:
                await scraper.launch_browser()
                emit("ok", f"[{portal_name}] Browser ready")
            except Exception as e:
                emit("error", f"[{portal_name}] Browser launch failed: {e}")
                portal_stats["errors"] += 1
                return portal_stats

            try:
                # ── Login ──
                emit("step", f"[{portal_name}] Logging in...")
                logged_in = await scraper.login()
                if not logged_in:
                    emit("error", f"[{portal_name}] Login failed — skipping portal")
                    portal_stats["errors"] += 1
                    return portal_stats
                emit("ok", f"[{portal_name}] Login successful")

                # ── Search ──
                emit("step", f"[{portal_name}] Searching for jobs...")
                jobs = await scraper.search_jobs(
                    roles=settings.target_roles_list,
                    locations=settings.target_locations_list,
                    experience_min=settings.TARGET_EXPERIENCE_MIN,
                    experience_max=settings.TARGET_EXPERIENCE_MAX,
                )
                portal_stats["found"] = len(jobs)

                if len(jobs) == 0:
                    emit("warn", f"[{portal_name}] No jobs found on search pages — portal may be blocking or selectors outdated")
                else:
                    emit("ok", f"[{portal_name}] Found {len(jobs)} jobs on search pages")

                # ── Process each job ──
                jobs_collection = get_collection("jobs")

                for i, job_data in enumerate(jobs):
                    try:
                        job_hash = generate_job_hash(job_data.portal, job_data.external_id)
                        job_doc = job_data.model_dump()
                        job_doc["job_hash"] = job_hash
                        job_doc["user_id"] = user_id
                        job_doc["url"] = clean_url(job_doc.get("url", ""))
                        job_doc["created_at"] = utc_now()
                        job_doc["updated_at"] = utc_now()
                        job_doc["status"] = "new"

                        quick_score = await job_matcher.quick_score(
                            job_title=job_data.title,
                            job_skills=job_data.skills,
                            job_location=job_data.location or "",
                            user_skills=settings.target_skills_list,
                            user_target_locations=settings.target_locations_list,
                        )
                        job_doc["match_score"] = quick_score

                        try:
                            await jobs_collection.insert_one(job_doc)
                            portal_stats["new"] += 1
                            score_label = f"score={quick_score}" if quick_score else ""
                            emit("new_job", f"[{portal_name}] ✚ {job_data.title} @ {job_data.company} — NEW ({score_label})")

                            if quick_score >= settings.MIN_MATCH_SCORE_TO_APPLY:
                                portal_stats["high_matches"] += 1
                                emit("match", f"[{portal_name}] ★ HIGH MATCH: {job_data.title} @ {job_data.company} ({quick_score}/100)")
                                await telegram_service.notify_new_job(
                                    title=job_data.title, company=job_data.company,
                                    location=job_data.location or "Not specified",
                                    match_score=quick_score, url=job_data.url, portal=portal_name,
                                )

                        except DuplicateKeyError:
                            portal_stats["duplicates"] += 1
                            emit("skip", f"[{portal_name}] ↩ {job_data.title} @ {job_data.company} — already exists")
                            await jobs_collection.update_one(
                                {"user_id": user_id, "portal": job_data.portal, "external_id": job_data.external_id},
                                {"$set": {"updated_at": utc_now()}},
                            )

                    except Exception as e:
                        portal_stats["errors"] += 1
                        emit("error", f"[{portal_name}] Error processing job: {str(e)[:80]}")

                # ── Summary ──
                emit("done", f"[{portal_name}] Done: {portal_stats['found']} found, {portal_stats['new']} new, {portal_stats['duplicates']} duplicates, {portal_stats['errors']} errors")

                await telegram_service.notify_scrape_complete(
                    portal=portal_name, jobs_found=portal_stats["found"],
                    new_jobs=portal_stats["new"], high_matches=portal_stats["high_matches"],
                )

            finally:
                emit("step", f"[{portal_name}] Closing browser...")
                await scraper.close_browser()

        except Exception as e:
            portal_stats["errors"] += 1
            emit("error", f"[{portal_name}] Scraper crashed: {str(e)[:100]}")
            logger.error(f"[{portal_name}] Scraper failed: {e}")

        return portal_stats

    async def scrape_single(self, portal_name: str, user_id: Optional[str] = None, on_event: Optional[Callable] = None) -> dict:
        return await self.scrape_all(portals=[portal_name], user_id=user_id, on_event=on_event)


scraper_manager = ScraperManager()
