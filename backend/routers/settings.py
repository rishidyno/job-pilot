"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Settings API Router                                  ║
║                                                                   ║
║  Endpoints for managing user profile and app settings:            ║
║  GET    /api/settings/profile     → Get user profile             ║
║  PUT    /api/settings/profile     → Update user profile          ║
║  GET    /api/settings/scheduler   → Get scheduler status         ║
║  POST   /api/settings/scheduler   → Toggle scheduler on/off     ║
║  GET    /api/settings/portals     → Get portal connection status ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_collection
from config import settings
from services.auth_service import get_current_user_id
from schedulers.job_scheduler import get_scheduler
from utils.helpers import utc_now
from utils.logger import logger

router = APIRouter(prefix="/api/settings", tags=["Settings"])

# Paths for editable markdown files
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
RULES_PATH = os.path.join(DATA_DIR, "rules.md")
PROFILE_PATH = os.path.join(DATA_DIR, "profile.md")


class MarkdownContent(BaseModel):
    content: str


@router.get("/rules")
async def get_rules(user_id: str = Depends(get_current_user_id)):
    """Get the resume/cover letter generation rules."""
    try:
        with open(RULES_PATH, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"content": ""}


@router.put("/rules")
async def update_rules(data: MarkdownContent, user_id: str = Depends(get_current_user_id)):
    """Update the resume/cover letter generation rules."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RULES_PATH, "w") as f:
        f.write(data.content)
    return {"success": True}


@router.get("/profile-md")
async def get_profile_md(user_id: str = Depends(get_current_user_id)):
    """Get the candidate profile markdown."""
    try:
        with open(PROFILE_PATH, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"content": ""}


@router.put("/profile-md")
async def update_profile_md(data: MarkdownContent, user_id: str = Depends(get_current_user_id)):
    """Update the candidate profile markdown."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        f.write(data.content)
    return {"success": True}


@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """Get the user profile and preferences."""
    profile_col = get_collection("user_profile")
    profile = await profile_col.find_one({"user_id": user_id})

    if not profile:
        # Create default profile from settings
        users_col = get_collection("users")
        from bson import ObjectId
        user = await users_col.find_one({"_id": ObjectId(user_id)})
        profile = {
            "user_id": user_id,
            "full_name": user["full_name"] if user else "",
            "email": user["email"] if user else "",
            "phone": "",
            "current_role": "",
            "current_company": "",
            "total_experience_years": 0,
            "target_roles": settings.target_roles_list,
            "target_locations": settings.target_locations_list,
            "primary_skills": settings.target_skills_list,
            "target_experience_min": settings.TARGET_EXPERIENCE_MIN,
            "target_experience_max": settings.TARGET_EXPERIENCE_MAX,
            "auto_apply_enabled": settings.AUTO_APPLY_ENABLED,
            "auto_apply_mode": settings.AUTO_APPLY_MODE,
            "min_match_score": settings.MIN_MATCH_SCORE_TO_APPLY,
            "scrape_interval_hours": settings.SCRAPE_INTERVAL_HOURS,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        await profile_col.insert_one(profile)

    profile["_id"] = str(profile["_id"])
    return profile


@router.put("/profile")
async def update_profile(data: dict, user_id: str = Depends(get_current_user_id)):
    """Update user profile and preferences."""
    profile_col = get_collection("user_profile")
    data["updated_at"] = utc_now()

    # Remove _id if present (can't update _id)
    data.pop("_id", None)
    data.pop("user_id", None)

    result = await profile_col.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True,
    )

    return {"success": True, "modified": result.modified_count}


@router.get("/scheduler")
async def get_scheduler_status(user_id: str = Depends(get_current_user_id)):
    """Get current scheduler status and upcoming jobs."""
    scheduler = get_scheduler()

    if not scheduler or not scheduler.running:
        return {"running": False, "jobs": []}

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {
        "running": True,
        "jobs": jobs,
        "scrape_interval_hours": settings.SCRAPE_INTERVAL_HOURS,
        "auto_apply_enabled": settings.AUTO_APPLY_ENABLED,
    }


@router.post("/scheduler")
async def update_scheduler(data: dict, user_id: str = Depends(get_current_user_id)):
    """Update scheduler interval from user preferences."""
    from apscheduler.triggers.interval import IntervalTrigger
    scheduler = get_scheduler()
    if not scheduler or not scheduler.running:
        raise HTTPException(status_code=400, detail="Scheduler not running")

    hours = data.get("scrape_interval_hours")
    if hours and isinstance(hours, (int, float)) and hours >= 1:
        try:
            scheduler.reschedule_job("scrape_all_portals", trigger=IntervalTrigger(hours=int(hours)))
            # Also save to user profile
            profile_col = get_collection("user_profile")
            await profile_col.update_one({"user_id": user_id}, {"$set": {"scrape_interval_hours": int(hours)}}, upsert=True)
            return {"success": True, "message": f"Scrape interval updated to {hours}h"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    raise HTTPException(status_code=400, detail="Invalid interval")


@router.get("/portals")
async def get_portal_status(user_id: str = Depends(get_current_user_id)):
    """
    Get connection status for all supported portals.
    Shows which portals have credentials configured.
    """
    portals = {
        "linkedin": {
            "name": "LinkedIn",
            "configured": bool(settings.LINKEDIN_EMAIL and settings.LINKEDIN_PASSWORD),
            "features": ["scraping", "easy_apply"],
        },
        "naukri": {
            "name": "Naukri",
            "configured": bool(settings.NAUKRI_EMAIL and settings.NAUKRI_PASSWORD),
            "features": ["scraping", "auto_apply"],
        },
        "wellfound": {
            "name": "Wellfound",
            "configured": bool(settings.WELLFOUND_EMAIL and settings.WELLFOUND_PASSWORD),
            "features": ["scraping", "auto_apply"],
        },
        "instahyre": {
            "name": "Instahyre",
            "configured": bool(settings.INSTAHYRE_EMAIL and settings.INSTAHYRE_PASSWORD),
            "features": ["scraping", "auto_apply"],
        },
        "indeed": {
            "name": "Indeed",
            "configured": True,  # Works without login
            "features": ["scraping"],
        },
        "glassdoor": {
            "name": "Glassdoor",
            "configured": bool(settings.GLASSDOOR_EMAIL and settings.GLASSDOOR_PASSWORD),
            "features": ["scraping"],
        },
    }

    return {"portals": portals}


@router.get("/health")
async def health_check(user_id: str = Depends(get_current_user_id)):
    """Simple health check endpoint."""
    from services.ai_service import ai_service
    return {
        "status": "healthy",
        "ai_tokens_used": ai_service.get_token_usage(),
        "telegram_configured": settings.telegram_enabled,
    }
