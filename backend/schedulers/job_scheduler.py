"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Background Job Scheduler                             ║
║                                                                   ║
║  Uses APScheduler to run periodic tasks in the background:        ║
║  - Job scraping (every N hours, configurable)                    ║
║  - Auto-apply queue processing                                   ║
║  - Daily summary notifications                                   ║
║                                                                   ║
║  The scheduler starts with the FastAPI app and runs tasks         ║
║  in the background without blocking the API.                     ║
║                                                                   ║
║  USAGE:                                                           ║
║    from schedulers.job_scheduler import start_scheduler           ║
║    start_scheduler()  # Called in main.py lifespan                ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from config import settings
from utils.logger import logger

# The global scheduler instance
_scheduler: AsyncIOScheduler | None = None


async def _scrape_all_portals():
    """Background task: Scrape all registered job portals for all users."""
    logger.info("⏰ Scheduled scrape starting...")
    try:
        from scrapers.scraper_manager import scraper_manager
        from database import get_collection
        users = await get_collection("users").find({}, {"_id": 1}).to_list(1000)
        for user in users:
            uid = str(user["_id"])
            try:
                stats = await scraper_manager.scrape_all(user_id=uid)
                logger.info(f"⏰ Scrape for user {uid}: {stats['new_jobs']} new jobs")
            except Exception as e:
                logger.error(f"⏰ Scrape failed for user {uid}: {e}")
    except Exception as e:
        logger.error(f"⏰ Scheduled scrape failed: {e}")


async def _process_auto_apply():
    """Background task: Process the auto-apply queue for all users."""
    logger.info("⏰ Processing auto-apply queue...")
    try:
        from appliers.applier_manager import applier_manager
        from database import get_collection
        users = await get_collection("users").find({}, {"_id": 1}).to_list(1000)
        for user in users:
            uid = str(user["_id"])
            try:
                results = await applier_manager.process_auto_apply_queue(user_id=uid)
                logger.info(f"⏰ Auto-apply for user {uid}: {results.get('applied', 0)} submitted")
            except Exception as e:
                logger.error(f"⏰ Auto-apply failed for user {uid}: {e}")
    except Exception as e:
        logger.error(f"⏰ Auto-apply processing failed: {e}")


async def _send_daily_summary():
    """Background task: Send daily summary via Telegram (aggregated across all users)."""
    try:
        from database import get_collection
        from services.telegram_service import telegram_service
        from datetime import datetime, timedelta

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)

        jobs_col = get_collection("jobs")
        apps_col = get_collection("applications")

        total_jobs = await jobs_col.count_documents({})
        new_today = await jobs_col.count_documents({"created_at": {"$gte": today_start}})
        applied_today = await apps_col.count_documents({"applied_at": {"$gte": today_start}})
        high_matches = await jobs_col.count_documents({
            "status": {"$in": ["new", "shortlisted"]},
            "match_score": {"$gte": settings.MIN_MATCH_SCORE_TO_APPLY},
        })

        await telegram_service.notify_daily_summary(
            total_jobs=total_jobs,
            new_today=new_today,
            applied_today=applied_today,
            high_matches=high_matches,
        )
    except Exception as e:
        logger.error(f"⏰ Daily summary failed: {e}")


def start_scheduler() -> AsyncIOScheduler:
    """
    Initialize and start the background scheduler.
    
    Registers all periodic tasks and starts the scheduler.
    Called once during app startup (main.py lifespan).
    
    Returns:
        AsyncIOScheduler: The running scheduler instance
    """
    global _scheduler

    _scheduler = AsyncIOScheduler(
        job_defaults={
            "coalesce": True,     # If a job was missed, only run it once (not once per miss)
            "max_instances": 1,   # Don't allow the same job to run concurrently
            "misfire_grace_time": 3600,  # Allow 1 hour grace for missed jobs
        }
    )

    # ── Task 1: Scrape all portals periodically ──
    _scheduler.add_job(
        _scrape_all_portals,
        trigger=IntervalTrigger(hours=settings.SCRAPE_INTERVAL_HOURS),
        id="scrape_all_portals",
        name="Scrape all job portals",
        replace_existing=True,
    )

    # ── Task 2: Process auto-apply queue (every 2 hours) ──
    if settings.AUTO_APPLY_ENABLED:
        _scheduler.add_job(
            _process_auto_apply,
            trigger=IntervalTrigger(hours=2),
            id="process_auto_apply",
            name="Process auto-apply queue",
            replace_existing=True,
        )

    # ── Task 3: Daily summary notification (every day at 8 PM IST) ──
    if settings.telegram_enabled:
        _scheduler.add_job(
            _send_daily_summary,
            trigger=CronTrigger(hour=14, minute=30),  # 8 PM IST = 2:30 PM UTC
            id="daily_summary",
            name="Send daily summary via Telegram",
            replace_existing=True,
        )

    _scheduler.start()
    logger.info(
        f"✅ Scheduler started — scraping every {settings.SCRAPE_INTERVAL_HOURS}h, "
        f"auto-apply: {'enabled' if settings.AUTO_APPLY_ENABLED else 'disabled'}"
    )

    return _scheduler


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
    _scheduler = None


def get_scheduler() -> AsyncIOScheduler | None:
    """Get the current scheduler instance (for status checks)."""
    return _scheduler
