"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Jobs API Router                                      ║
║                                                                   ║
║  Endpoints for managing job listings:                             ║
║  GET    /api/jobs           → List all jobs (with filters)       ║
║  GET    /api/jobs/:id       → Get a single job                   ║
║  PATCH  /api/jobs/:id       → Update job (status, notes, etc.)   ║
║  DELETE /api/jobs/:id       → Remove a job                       ║
║  POST   /api/jobs/scrape    → Trigger a scrape run               ║
║  POST   /api/jobs/:id/score → Re-score a job with AI            ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from bson import ObjectId
from database import get_collection
from models.job import JobUpdate, JobStatus
from services.job_matcher import job_matcher
from services.auth_service import get_current_user_id
from scrapers.scraper_manager import scraper_manager
from config import settings
from utils.logger import logger
from utils.helpers import utc_now

# ── In-memory scrape status tracker ──
_scrape_status = {
    "running": False,
    "stop_requested": False,
    "current_portal": None,
    "portals_done": [],
    "portals_remaining": [],
    "jobs_found": 0,
    "new_jobs": 0,
    "errors": 0,
    "started_at": None,
    "logs": [],  # last N log messages
}

def _log(msg: str):
    """Add a log entry to scrape status."""
    from datetime import datetime
    _scrape_status["logs"].append({"time": datetime.now().isoformat(), "message": msg})
    if len(_scrape_status["logs"]) > 50:
        _scrape_status["logs"] = _scrape_status["logs"][-50:]

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("")
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status: new, reviewed, shortlisted, applied, etc."),
    portal: Optional[str] = Query(None, description="Filter by portal: linkedin, naukri, etc."),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum match score"),
    search: Optional[str] = Query(None, description="Search in title, company, description"),
    sort_by: str = Query("match_score", description="Sort field: match_score, created_at, title"),
    sort_order: str = Query("desc", description="Sort direction: asc or desc"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    user_id: str = Depends(get_current_user_id),
):
    """
    List all jobs with optional filtering, sorting, and pagination.
    
    This is the main endpoint the dashboard's Jobs page calls.
    Supports flexible filtering to find exactly what you need.
    """
    jobs_col = get_collection("jobs")

    # Build the query filter
    query = {"user_id": user_id}
    if status:
        query["status"] = status
    if portal:
        query["portal"] = portal
    if min_score is not None:
        query["match_score"] = {"$gte": min_score}
    if search:
        query["$text"] = {"$search": search}

    # Determine sort direction
    sort_dir = -1 if sort_order == "desc" else 1

    # Execute query
    cursor = jobs_col.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
    jobs = await cursor.to_list(limit)

    # Get total count for pagination
    total = await jobs_col.count_documents(query)

    # Convert ObjectId to string for JSON serialization
    for job in jobs:
        job["_id"] = str(job["_id"])

    return {
        "jobs": jobs,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


@router.post("/scrape")
async def trigger_scrape(portals: Optional[str] = None, user_id: str = Depends(get_current_user_id)):
    """Trigger a manual scrape run with live status tracking."""
    import asyncio

    if _scrape_status["running"]:
        raise HTTPException(status_code=409, detail="Scrape already running")

    target = [p.strip() for p in portals.split(",") if p.strip()] if portals else ["linkedin", "naukri", "wellfound", "instahyre", "indeed", "glassdoor"]

    # Reset status
    _scrape_status.update({
        "running": True,
        "stop_requested": False,
        "current_portal": None,
        "portals_done": [],
        "portals_remaining": list(target),
        "jobs_found": 0,
        "new_jobs": 0,
        "errors": 0,
        "started_at": utc_now().isoformat(),
        "logs": [],
    })
    _log(f"Scrape started for: {', '.join(target)}")

    async def run_scrape():
        try:
            for portal_name in target:
                if _scrape_status["stop_requested"]:
                    _log("Stop requested — aborting remaining portals")
                    break

                _scrape_status["current_portal"] = portal_name
                _scrape_status["portals_remaining"] = [
                    p for p in target if p not in _scrape_status["portals_done"] and p != portal_name
                ]
                _log(f"Scraping {portal_name}...")

                try:
                    result = await scraper_manager._scrape_portal(portal_name, user_id=user_id)
                    _scrape_status["jobs_found"] += result["found"]
                    _scrape_status["new_jobs"] += result["new"]
                    _scrape_status["errors"] += result["errors"]
                    _log(f"{portal_name}: {result['found']} found, {result['new']} new, {result['errors']} errors")
                except Exception as e:
                    _scrape_status["errors"] += 1
                    _log(f"{portal_name}: failed — {str(e)[:100]}")

                _scrape_status["portals_done"].append(portal_name)

        finally:
            _scrape_status["running"] = False
            _scrape_status["current_portal"] = None
            _scrape_status["portals_remaining"] = []
            _log(f"Scrape complete: {_scrape_status['jobs_found']} found, {_scrape_status['new_jobs']} new")

    task = asyncio.create_task(run_scrape())
    _scrape_status["_task"] = task

    return {"success": True, "message": f"Scrape started for: {', '.join(target)}", "status": "running"}


@router.get("/scrape/status")
async def get_scrape_status(user_id: str = Depends(get_current_user_id)):
    """Get live scrape status."""
    return {k: v for k, v in _scrape_status.items() if k != "_task"}


@router.post("/scrape/stop")
async def stop_scrape(user_id: str = Depends(get_current_user_id)):
    """Force stop the scraper immediately."""
    if not _scrape_status["running"]:
        raise HTTPException(status_code=400, detail="No scrape running")
    _scrape_status["stop_requested"] = True
    # Cancel the running task
    if _scrape_status.get("_task"):
        _scrape_status["_task"].cancel()
    _scrape_status["running"] = False
    _scrape_status["current_portal"] = None
    _scrape_status["portals_remaining"] = []
    _log("Force stopped by user")
    return {"success": True, "message": "Scrape stopped"}


@router.get("/{job_id}")
async def get_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """Get a single job by ID with full details."""
    jobs_col = get_collection("jobs")

    try:
        job = await jobs_col.find_one({"_id": ObjectId(job_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job["_id"] = str(job["_id"])
    return job


@router.patch("/{job_id}")
async def update_job(job_id: str, update: JobUpdate, user_id: str = Depends(get_current_user_id)):
    """
    Update a job's status, notes, apply mode, etc.
    
    Used when:
    - User reviews a job and changes status (new → shortlisted)
    - User adds personal notes
    - User changes apply mode for a specific job
    """
    jobs_col = get_collection("jobs")

    # Build update dict (only include non-None fields)
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_data["updated_at"] = utc_now()

    try:
        result = await jobs_col.update_one(
            {"_id": ObjectId(job_id), "user_id": user_id},
            {"$set": update_data}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"success": True, "modified": result.modified_count}


@router.delete("/{job_id}")
async def delete_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """Remove a job from the database."""
    jobs_col = get_collection("jobs")
    try:
        result = await jobs_col.delete_one({"_id": ObjectId(job_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"success": True, "deleted": True}


@router.post("/{job_id}/score")
async def score_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """Re-score a job using AI matching."""
    jobs_col = get_collection("jobs")
    resumes_col = get_collection("resumes")

    try:
        job = await jobs_col.find_one({"_id": ObjectId(job_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    base_resume = await resumes_col.find_one({"is_base": True, "user_id": user_id})
    resume_text = base_resume.get("raw_text", "") if base_resume else ""

    score_data = await job_matcher.score_job(
        job_title=job["title"],
        job_description=job.get("description", ""),
        job_skills=job.get("skills", []),
        job_location=job.get("location", ""),
        job_experience=job.get("experience_required", ""),
        resume_text=resume_text,
        user_target_roles=settings.target_roles_list,
        user_target_locations=settings.target_locations_list,
        user_skills=settings.target_skills_list,
        user_experience_years=settings.TARGET_EXPERIENCE_MIN,
    )

    await jobs_col.update_one(
        {"_id": ObjectId(job_id), "user_id": user_id},
        {"$set": {
            "match_score": score_data["score"],
            "match_reasoning": score_data.get("reasoning", ""),
            "updated_at": utc_now(),
        }}
    )

    return {"success": True, "score": score_data}
