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
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_collection
from config import settings
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
async def get_rules():
    """Get the resume/cover letter generation rules."""
    try:
        with open(RULES_PATH, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"content": ""}


@router.put("/rules")
async def update_rules(data: MarkdownContent):
    """Update the resume/cover letter generation rules."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(RULES_PATH, "w") as f:
        f.write(data.content)
    return {"success": True}


@router.get("/profile-md")
async def get_profile_md():
    """Get the candidate profile markdown."""
    try:
        with open(PROFILE_PATH, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        return {"content": ""}


@router.put("/profile-md")
async def update_profile_md(data: MarkdownContent):
    """Update the candidate profile markdown."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        f.write(data.content)
    return {"success": True}


@router.get("/profile")
async def get_profile():
    """Get the user profile and preferences."""
    profile_col = get_collection("user_profile")
    profile = await profile_col.find_one({})

    if not profile:
        # Create default profile from settings
        profile = {
            "full_name": "Rishi Raj",
            "email": "rishiraj727909.work@gmail.com",
            "phone": "+91-8210239176",
            "current_role": "SDE-1",
            "current_company": "Amazon",
            "total_experience_years": 1.5,
            "target_roles": settings.target_roles_list,
            "target_locations": settings.target_locations_list,
            "primary_skills": settings.target_skills_list,
            "auto_apply_enabled": settings.AUTO_APPLY_ENABLED,
            "auto_apply_mode": settings.AUTO_APPLY_MODE,
            "min_match_score": settings.MIN_MATCH_SCORE_TO_APPLY,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        await profile_col.insert_one(profile)

    profile["_id"] = str(profile["_id"])
    return profile


@router.put("/profile")
async def update_profile(data: dict):
    """Update user profile and preferences."""
    profile_col = get_collection("user_profile")
    data["updated_at"] = utc_now()

    # Remove _id if present (can't update _id)
    data.pop("_id", None)

    result = await profile_col.update_one(
        {},  # Update the single profile document
        {"$set": data},
        upsert=True,
    )

    return {"success": True, "modified": result.modified_count}


@router.get("/scheduler")
async def get_scheduler_status():
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


@router.get("/portals")
async def get_portal_status():
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
async def health_check():
    """Simple health check endpoint."""
    from services.ai_service import ai_service
    return {
        "status": "healthy",
        "ai_tokens_used": ai_service.get_token_usage(),
        "telegram_configured": settings.telegram_enabled,
    }
