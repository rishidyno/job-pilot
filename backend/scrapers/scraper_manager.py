"""
JOBPILOT — Scraper Manager (powered by python-jobspy)

Uses python-jobspy for the actual scraping (LinkedIn, Indeed, Glassdoor,
Google, Naukri — no login required). We handle:
  - User preferences → search parameters
  - Keyword expansion for better coverage
  - Deduplication against existing DB entries
  - Quick match scoring
  - Live event logging to the UI
  - MongoDB persistence
  - Telegram notifications for high matches
"""

import asyncio
from typing import List, Optional, Callable
from pymongo.errors import DuplicateKeyError

from services.job_matcher import job_matcher
from services.telegram_service import telegram_service
from services.user_prefs import get_user_prefs
from database import get_collection
from utils.logger import logger
from utils.helpers import utc_now, generate_job_hash


# Portals supported by python-jobspy
SUPPORTED_PORTALS = ["linkedin", "indeed", "glassdoor", "google", "naukri"]


def _expand_keywords(target_roles: list) -> list:
    """
    Generate keyword variations from target roles for broader search coverage.
    E.g. "Backend Engineer" → also search "Software Engineer", "Java Developer", etc.
    """
    base = list(target_roles) if target_roles else ["Software Engineer"]

    # Common synonyms/variations in the SDE job market
    expansions = {
        "backend engineer": ["software engineer backend", "java developer", "server side engineer"],
        "full stack developer": ["fullstack developer", "full stack engineer"],
        "software engineer": ["software developer", "SDE"],
        "sde-1": ["SDE 1", "software development engineer"],
        "sde-2": ["SDE 2", "software development engineer II"],
        "backend developer": ["backend engineer", "java backend developer"],
    }

    expanded = set()
    for role in base:
        expanded.add(role)
        key = role.lower().strip()
        if key in expansions:
            expanded.update(expansions[key])

    return list(expanded)


class ScraperManager:

    async def scrape_all(
        self,
        portals: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        on_event: Optional[Callable] = None,
    ) -> dict:
        target_portals = portals or list(SUPPORTED_PORTALS)
        emit = on_event or (lambda *a: None)

        stats = {
            "started_at": utc_now(),
            "total_found": 0, "new_jobs": 0, "duplicates": 0,
            "errors": 0, "high_matches": 0, "portal_stats": {},
        }

        emit("info", f"Starting scrape for: {', '.join(target_portals)}")

        for portal_name in target_portals:
            if portal_name not in SUPPORTED_PORTALS:
                emit("warn", f"Unsupported portal: {portal_name}")
                continue

            portal_stats = await self._scrape_portal(
                portal_name, user_id=user_id, on_event=emit,
            )
            stats["portal_stats"][portal_name] = portal_stats
            stats["total_found"] += portal_stats["found"]
            stats["new_jobs"] += portal_stats["new"]
            stats["duplicates"] += portal_stats["duplicates"]
            stats["errors"] += portal_stats["errors"]
            stats["high_matches"] += portal_stats["high_matches"]

        stats["completed_at"] = utc_now()
        stats["duration_seconds"] = (stats["completed_at"] - stats["started_at"]).total_seconds()

        # Save scrape log
        scrape_logs = get_collection("scrape_logs")
        await scrape_logs.insert_one({**stats, "user_id": user_id})

        return stats

    async def _scrape_portal(
        self,
        portal_name: str,
        user_id: Optional[str] = None,
        on_event: Optional[Callable] = None,
    ) -> dict:
        emit = on_event or (lambda *a: None)
        portal_stats = {"found": 0, "new": 0, "duplicates": 0, "errors": 0, "high_matches": 0}

        prefs = await get_user_prefs()
        keywords = _expand_keywords(prefs["target_roles"])
        locations = prefs["target_locations"]
        # Use first location as primary (jobspy takes a single location string)
        location = locations[0] if locations else "India"

        emit("step", f"[{portal_name}] Starting scrape...")
        emit("step", f"[{portal_name}] Keywords: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
        emit("step", f"[{portal_name}] Location: {location}")

        try:
            # Run jobspy in a thread to avoid blocking the event loop
            # (jobspy uses synchronous requests internally)
            from jobspy import scrape_jobs

            for keyword in keywords[:6]:  # Cap at 6 keywords to avoid rate limits
                emit("step", f"[{portal_name}] Searching: '{keyword}'...")

                try:
                    df = await asyncio.to_thread(
                        scrape_jobs,
                        site_name=[portal_name],
                        search_term=keyword,
                        location=location,
                        results_wanted=30,
                        hours_old=720,  # 30 days
                        country_indeed="India" if portal_name in ("indeed", "glassdoor") else None,
                        linkedin_fetch_description=True if portal_name == "linkedin" else False,
                        verbose=0,
                    )
                except Exception as e:
                    emit("error", f"[{portal_name}] Search failed for '{keyword}': {str(e)[:80]}")
                    portal_stats["errors"] += 1
                    continue

                if df is None or df.empty:
                    emit("warn", f"[{portal_name}] No results for '{keyword}'")
                    continue

                emit("ok", f"[{portal_name}] Found {len(df)} results for '{keyword}'")
                portal_stats["found"] += len(df)

                # Process each job
                await self._process_jobs(
                    df, portal_name, user_id, prefs, portal_stats, emit,
                )

                # Small delay between keyword searches
                await asyncio.sleep(1)

        except Exception as e:
            emit("error", f"[{portal_name}] Fatal error: {str(e)[:100]}")
            portal_stats["errors"] += 1
            logger.error(f"[{portal_name}] Scrape failed: {e}")

        emit("done", f"[{portal_name}] Done — {portal_stats['found']} found, {portal_stats['new']} new, {portal_stats['duplicates']} dupes")
        return portal_stats

    async def _process_jobs(self, df, portal_name, user_id, prefs, portal_stats, emit):
        """Process a DataFrame of jobs from jobspy — dedup, score, save."""
        jobs_col = get_collection("jobs")

        for _, row in df.iterrows():
            try:
                title = str(row.get("title", "")).strip()
                company = str(row.get("company", "")).strip()
                job_url = str(row.get("job_url", "")).strip()

                if not title or not job_url or title == "nan":
                    continue

                # Generate external ID from URL or job_url hash
                external_id = str(row.get("id", "")) or generate_job_hash(portal_name, job_url)

                # Build job document
                job_doc = {
                    "title": title,
                    "company": company if company != "nan" else "Unknown",
                    "portal": portal_name,
                    "external_id": external_id,
                    "url": job_url,
                    "location": _clean_field(row.get("location")),
                    "description": _clean_field(row.get("description")),
                    "job_type": _clean_field(row.get("job_type")),
                    "date_posted": _clean_field(row.get("date_posted")),
                    "salary": _format_salary(row),
                    "is_remote": bool(row.get("is_remote", False)),
                    "company_url": _clean_field(row.get("company_url")),
                    "skills": _extract_skills(row),
                    "experience_required": _clean_field(row.get("experience_range")),
                    "job_hash": generate_job_hash(portal_name, external_id),
                    "user_id": user_id,
                    "status": "new",
                    "created_at": utc_now(),
                    "updated_at": utc_now(),
                }

                # Quick score
                quick_score = await job_matcher.quick_score(
                    job_title=title,
                    job_skills=job_doc["skills"],
                    job_location=job_doc["location"] or "",
                    user_skills=prefs["primary_skills"],
                    user_target_locations=prefs["target_locations"],
                )
                job_doc["match_score"] = quick_score

                # Try insert (dedup via unique index on job_hash)
                try:
                    await jobs_col.insert_one(job_doc)
                    portal_stats["new"] += 1
                    emit("new_job", f"[{portal_name}] ✚ {title} @ {company} (score={quick_score})")

                    if quick_score >= prefs["min_match_score"]:
                        portal_stats["high_matches"] += 1
                        emit("match", f"[{portal_name}] ★ HIGH MATCH: {title} @ {company} ({quick_score}/100)")
                        await telegram_service.notify_new_job(
                            title=title, company=company,
                            location=job_doc["location"] or "Not specified",
                            match_score=quick_score, url=job_url, portal=portal_name,
                        )

                except DuplicateKeyError:
                    portal_stats["duplicates"] += 1

            except Exception as e:
                portal_stats["errors"] += 1
                emit("error", f"[{portal_name}] Error processing job: {str(e)[:60]}")


def _clean_field(val) -> str:
    """Clean a DataFrame field value — handle NaN, None, etc."""
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s in ("nan", "None", "NaT") else s


def _format_salary(row) -> str:
    """Format salary from jobspy's min/max/interval fields."""
    min_amt = row.get("min_amount")
    max_amt = row.get("max_amount")
    interval = row.get("interval")
    currency = row.get("currency", "")

    if min_amt and str(min_amt) != "nan":
        parts = []
        if currency and str(currency) != "nan":
            parts.append(str(currency))
        parts.append(f"{int(float(min_amt)):,}")
        if max_amt and str(max_amt) != "nan":
            parts.append(f"- {int(float(max_amt)):,}")
        if interval and str(interval) != "nan":
            parts.append(f"/{interval}")
        return " ".join(parts)
    return ""


def _extract_skills(row) -> list:
    """Extract skills from jobspy row."""
    skills = row.get("skills")
    if skills and str(skills) != "nan":
        if isinstance(skills, list):
            return skills
        return [s.strip() for s in str(skills).split(",") if s.strip()]
    return []


# Singleton
scraper_manager = ScraperManager()
