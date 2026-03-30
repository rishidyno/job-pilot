"""
JOBPILOT — Jobs API Router with detailed scrape event logging.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from bson import ObjectId
from database import get_collection
from models.job import JobUpdate, JobStatus
from services.job_matcher import job_matcher
from services.auth_service import get_current_user_id
from scrapers.scraper_manager import scraper_manager
from config import settings
from utils.logger import logger
from utils.helpers import utc_now, generate_job_hash

# ── In-memory scrape status tracker ──
_scrape_status = {
    "running": False,
    "stop_requested": False,
    "current_portal": None,
    "portals_done": [],
    "portals_remaining": [],
    "jobs_found": 0,
    "new_jobs": 0,
    "duplicates": 0,
    "errors": 0,
    "high_matches": 0,
    "started_at": None,
    "logs": [],
}


def _log(level: str, msg: str):
    """Add a structured log entry."""
    from datetime import datetime
    _scrape_status["logs"].append({
        "time": datetime.now().isoformat(),
        "level": level,
        "message": msg,
    })
    # Keep last 200 entries
    if len(_scrape_status["logs"]) > 200:
        _scrape_status["logs"] = _scrape_status["logs"][-200:]


def _on_scrape_event(level: str, msg: str):
    """Callback passed to scraper_manager — receives granular events."""
    _log(level, msg)

    # Update counters from event types
    if level == "new_job":
        _scrape_status["new_jobs"] += 1
    elif level == "skip":
        _scrape_status["duplicates"] += 1
    elif level == "match":
        _scrape_status["high_matches"] += 1
    elif level == "error":
        _scrape_status["errors"] += 1

    # Track current portal from message
    if msg.startswith("["):
        portal = msg[1:msg.index("]")] if "]" in msg else None
        if portal and portal != _scrape_status.get("current_portal"):
            _scrape_status["current_portal"] = portal


router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("")
async def list_jobs(
    status: Optional[str] = Query(None),
    portal: Optional[str] = Query(None),
    bookmarked: Optional[bool] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("match_score"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user_id),
):
    jobs_col = get_collection("jobs")
    query = {"user_id": user_id}
    if status:
        query["status"] = status
    if portal:
        query["portal"] = portal
    if bookmarked is not None:
        query["bookmarked"] = bookmarked
    if min_score is not None:
        query["match_score"] = {"$gte": min_score}
    if search:
        pattern = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"title": pattern},
            {"company": pattern},
            {"skills": pattern},
            {"location": pattern},
            {"description": pattern},
        ]

    sort_dir = -1 if sort_order == "desc" else 1
    cursor = jobs_col.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
    jobs = await cursor.to_list(limit)
    total = await jobs_col.count_documents(query)

    for job in jobs:
        job["_id"] = str(job["_id"])

    return {"jobs": jobs, "total": total, "skip": skip, "limit": limit, "has_more": (skip + limit) < total}


@router.post("/scrape")
async def trigger_scrape(portals: Optional[str] = None, user_id: str = Depends(get_current_user_id)):
    """Trigger a manual scrape with detailed live event logging."""
    import asyncio

    if _scrape_status["running"]:
        raise HTTPException(status_code=409, detail="Scrape already running")

    target = [p.strip() for p in portals.split(",") if p.strip()] if portals else ["linkedin", "indeed", "glassdoor", "google", "naukri"]

    _scrape_status.update({
        "running": True,
        "stop_requested": False,
        "current_portal": None,
        "portals_done": [],
        "portals_remaining": list(target),
        "jobs_found": 0,
        "new_jobs": 0,
        "duplicates": 0,
        "errors": 0,
        "high_matches": 0,
        "started_at": utc_now().isoformat(),
        "logs": [],
    })
    _log("info", f"Scrape started for: {', '.join(target)}")

    async def run_scrape():
        try:
            for portal_name in target:
                if _scrape_status["stop_requested"]:
                    _log("warn", "Stop requested — aborting remaining portals")
                    break

                _scrape_status["current_portal"] = portal_name
                _scrape_status["portals_remaining"] = [
                    p for p in target if p not in _scrape_status["portals_done"] and p != portal_name
                ]

                try:
                    result = await scraper_manager._scrape_portal(portal_name, user_id=user_id, on_event=_on_scrape_event)
                    _scrape_status["jobs_found"] += result["found"]
                except Exception as e:
                    _log("error", f"[{portal_name}] Fatal: {str(e)[:100]}")

                _scrape_status["portals_done"].append(portal_name)

        finally:
            _scrape_status["running"] = False
            _scrape_status["current_portal"] = None
            _scrape_status["portals_remaining"] = []
            _log("info", f"Scrape complete: {_scrape_status['jobs_found']} found, {_scrape_status['new_jobs']} new, {_scrape_status['duplicates']} duplicates, {_scrape_status['high_matches']} high matches")

    task = asyncio.create_task(run_scrape())
    _scrape_status["_task"] = task

    return {"success": True, "message": f"Scrape started for: {', '.join(target)}"}


@router.get("/scrape/status")
async def get_scrape_status(user_id: str = Depends(get_current_user_id)):
    """Get live scrape status with full event log."""
    return {k: v for k, v in _scrape_status.items() if k != "_task"}


@router.post("/scrape/stop")
async def stop_scrape(user_id: str = Depends(get_current_user_id)):
    if not _scrape_status["running"]:
        raise HTTPException(status_code=400, detail="No scrape running")
    _scrape_status["stop_requested"] = True
    if _scrape_status.get("_task"):
        _scrape_status["_task"].cancel()
    _scrape_status["running"] = False
    _scrape_status["current_portal"] = None
    _scrape_status["portals_remaining"] = []
    _log("warn", "Force stopped by user")
    return {"success": True, "message": "Scrape stopped"}


@router.get("/{job_id}")
async def get_job(job_id: str, user_id: str = Depends(get_current_user_id)):
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
    jobs_col = get_collection("jobs")
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    update_data["updated_at"] = utc_now()
    try:
        result = await jobs_col.update_one({"_id": ObjectId(job_id), "user_id": user_id}, {"$set": update_data})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"success": True, "modified": result.modified_count}


@router.get("/export")
async def export_jobs(format: str = "csv", user_id: str = Depends(get_current_user_id)):
    """Export all jobs as CSV."""
    import csv, io
    from starlette.responses import Response

    jobs_col = get_collection("jobs")
    cursor = jobs_col.find({"user_id": user_id}).sort("match_score", -1)
    jobs = await cursor.to_list(5000)

    output = io.StringIO()
    fields = ["title", "company", "location", "portal", "match_score", "status", "bookmarked", "skills", "salary", "url", "notes", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for j in jobs:
        writer.writerow({
            "title": j.get("title", ""),
            "company": j.get("company", ""),
            "location": j.get("location", ""),
            "portal": j.get("portal", ""),
            "match_score": j.get("match_score", ""),
            "status": j.get("status", ""),
            "bookmarked": "Yes" if j.get("bookmarked") else "",
            "skills": ", ".join(j.get("skills", [])),
            "salary": j.get("salary", ""),
            "url": j.get("url", ""),
            "notes": j.get("notes", ""),
            "created_at": str(j.get("created_at", "")),
        })

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=jobpilot_jobs.csv"},
    )


class ManualJobInput(BaseModel):
    url: str
    title: str = ""
    company: str = ""
    location: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    salary: Optional[str] = None


@router.post("/fetch-details")
async def fetch_job_from_url(data: dict, user_id: str = Depends(get_current_user_id)):
    """Fetch job details from a URL — extracts title, company, location, description, skills."""
    from services.job_parser import fetch_job_details
    url = data.get("url", "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    result = await fetch_job_details(url)
    return result


@router.post("/manual")
async def add_manual_job(data: ManualJobInput, user_id: str = Depends(get_current_user_id)):
    """Add a job manually. Title and company are required."""
    if not data.title.strip() or not data.company.strip():
        raise HTTPException(status_code=400, detail="Title and company are required")

    from services.user_prefs import get_user_prefs

    jobs_col = get_collection("jobs")
    prefs = await get_user_prefs()

    # Quick score
    quick_score = await job_matcher.quick_score(
        job_title=data.title,
        job_skills=data.skills or [],
        job_location=data.location or "",
        user_skills=prefs["primary_skills"],
        user_target_locations=prefs["target_locations"],
    )

    job_doc = {
        "title": data.title.strip(),
        "company": data.company.strip(),
        "url": data.url.strip(),
        "portal": "manual",
        "external_id": generate_job_hash("manual", data.url),
        "job_hash": generate_job_hash("manual", data.url),
        "location": data.location or "",
        "description": data.description or "",
        "skills": data.skills or [],
        "salary": data.salary or "",
        "match_score": quick_score,
        "status": "new",
        "is_manual": True,
        "user_id": user_id,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }

    try:
        result = await jobs_col.insert_one(job_doc)
    except Exception:
        raise HTTPException(status_code=400, detail="Job with this URL already exists")

    return {"success": True, "job_id": str(result.inserted_id), "match_score": quick_score}


@router.delete("/{job_id}")
async def delete_job(job_id: str, user_id: str = Depends(get_current_user_id)):
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

    from services.user_prefs import get_user_prefs
    prefs = await get_user_prefs()

    score_data = await job_matcher.score_job(
        job_title=job["title"], job_description=job.get("description", ""),
        job_skills=job.get("skills", []), job_location=job.get("location", ""),
        job_experience=job.get("experience_required", ""),
        resume_text=resume_text, user_target_roles=prefs["target_roles"],
        user_target_locations=prefs["target_locations"],
        user_skills=prefs["primary_skills"], user_experience_years=prefs["target_experience_min"],
    )

    await jobs_col.update_one(
        {"_id": ObjectId(job_id), "user_id": user_id},
        {"$set": {"match_score": score_data["score"], "match_reasoning": score_data.get("reasoning", ""), "updated_at": utc_now()}}
    )
    return {"success": True, "score": score_data}
