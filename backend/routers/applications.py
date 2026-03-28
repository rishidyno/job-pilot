"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Applications API Router                              ║
║                                                                   ║
║  Endpoints for managing job applications:                         ║
║  GET    /api/applications           → List all applications      ║
║  GET    /api/applications/:id       → Get application details    ║
║  POST   /api/applications           → Create (apply to a job)   ║
║  PATCH  /api/applications/:id       → Update status/notes       ║
║  POST   /api/applications/:id/retry → Retry a failed apply      ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from bson import ObjectId
from database import get_collection
from services.auth_service import get_current_user_id
from utils.helpers import utc_now
from utils.logger import logger

router = APIRouter(prefix="/api/applications", tags=["Applications"])


@router.get("")
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("applied_at", description="Sort field"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user_id),
):
    """List all applications with optional filtering."""
    apps_col = get_collection("applications")
    query = {"user_id": user_id}
    if status:
        query["status"] = status

    sort_dir = -1 if sort_order == "desc" else 1
    cursor = apps_col.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
    apps = await cursor.to_list(limit)
    total = await apps_col.count_documents(query)

    for app in apps:
        app["_id"] = str(app["_id"])

    return {"applications": apps, "total": total, "skip": skip, "limit": limit}


@router.get("/{app_id}")
async def get_application(app_id: str, user_id: str = Depends(get_current_user_id)):
    """Get a single application with full details and event timeline."""
    apps_col = get_collection("applications")
    try:
        app = await apps_col.find_one({"_id": ObjectId(app_id), "user_id": user_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid application ID")
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app["_id"] = str(app["_id"])
    return app


@router.post("")
async def create_application(job_id: str, force: bool = False, user_id: str = Depends(get_current_user_id)):
    """
    Track a job application — creates an application record.
    Opens the job URL for manual apply.
    """
    jobs_col = get_collection("jobs")
    apps_col = get_collection("applications")

    job = await jobs_col.find_one({"_id": ObjectId(job_id), "user_id": user_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = await apps_col.find_one({"job_id": job_id, "user_id": user_id})
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    app_doc = {
        "job_id": job_id,
        "user_id": user_id,
        "status": "pending",
        "portal": job.get("portal", "unknown"),
        "job_title": job["title"],
        "company": job["company"],
        "job_url": job.get("url", ""),
        "events": [{
            "timestamp": utc_now(),
            "event_type": "created",
            "description": "Application created",
        }],
        "applied_at": utc_now(),
        "updated_at": utc_now(),
    }
    result = await apps_col.insert_one(app_doc)

    await jobs_col.update_one(
        {"_id": ObjectId(job_id), "user_id": user_id},
        {"$set": {"status": "applied", "updated_at": utc_now()}},
    )

    return {
        "success": True,
        "application_id": str(result.inserted_id),
        "job_url": job.get("url", ""),
    }


@router.patch("/{app_id}")
async def update_application(app_id: str, status: Optional[str] = None, notes: Optional[str] = None, user_id: str = Depends(get_current_user_id)):
    """
    Update an application's status or notes.
    
    Used when manually tracking progress:
    - Mark as "interview" when you get a call
    - Mark as "offered" when you receive an offer
    - Add notes about interviews, contacts, etc.
    """
    apps_col = get_collection("applications")
    update_data = {"updated_at": utc_now()}

    if status:
        update_data["status"] = status
        # Add event to timeline
        event = {
            "timestamp": utc_now(),
            "event_type": "status_change",
            "description": f"Status changed to {status}",
        }
        await apps_col.update_one(
            {"_id": ObjectId(app_id), "user_id": user_id},
            {"$push": {"events": event}}
        )

    if notes is not None:
        update_data["notes"] = notes

    result = await apps_col.update_one(
        {"_id": ObjectId(app_id), "user_id": user_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")

    return {"success": True}


@router.post("/{app_id}/retry")
async def retry_application(app_id: str, user_id: str = Depends(get_current_user_id)):
    """Retry a failed application — resets status to pending."""
    apps_col = get_collection("applications")
    app = await apps_col.find_one({"_id": ObjectId(app_id), "user_id": user_id})

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.get("status") != "failed":
        raise HTTPException(status_code=400, detail="Can only retry failed applications")

    await apps_col.update_one(
        {"_id": ObjectId(app_id)},
        {"$set": {"status": "pending", "error_message": None, "updated_at": utc_now()},
         "$push": {"events": {"timestamp": utc_now(), "event_type": "retry", "description": "Application retried"}}},
    )
    return {"success": True}
