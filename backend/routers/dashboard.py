"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Dashboard API Router                                 ║
║                                                                   ║
║  Aggregation endpoints for the dashboard overview:                ║
║  GET /api/dashboard/stats    → Key metrics                       ║
║  GET /api/dashboard/timeline → Jobs found over time              ║
║  GET /api/dashboard/portals  → Per-portal breakdown              ║
║  GET /api/dashboard/pipeline → Application pipeline counts       ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime, timedelta
import time
from fastapi import APIRouter, Depends
from database import get_collection
from services.auth_service import get_current_user_id
from services.user_prefs import get_user_prefs

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# Simple per-user TTL cache for dashboard queries
_cache = {}
CACHE_TTL = 60  # seconds

def _get_cached(key):
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < CACHE_TTL:
        return entry["data"]
    return None

def _set_cached(key, data):
    _cache[key] = {"data": data, "ts": time.time()}


@router.get("/stats")
async def get_dashboard_stats(user_id: str = Depends(get_current_user_id)):
    """Get key metrics for the dashboard overview cards."""
    cached = _get_cached(f"stats:{user_id}")
    if cached:
        return cached

    jobs_col = get_collection("jobs")
    apps_col = get_collection("applications")

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    prefs = await get_user_prefs(user_id)
    uf = {"user_id": user_id}

    total_jobs = await jobs_col.count_documents(uf)
    new_today = await jobs_col.count_documents({**uf, "created_at": {"$gte": today_start}})
    new_this_week = await jobs_col.count_documents({**uf, "created_at": {"$gte": week_start}})
    high_matches = await jobs_col.count_documents({
        **uf,
        "match_score": {"$gte": prefs["min_match_score"]},
        "status": {"$in": ["new", "reviewed", "shortlisted"]},
    })

    total_applied = await apps_col.count_documents({**uf, "status": {"$ne": "failed"}})
    applied_today = await apps_col.count_documents({
        **uf,
        "applied_at": {"$gte": today_start},
        "status": {"$ne": "failed"},
    })
    interviews = await apps_col.count_documents({**uf, "status": "interview"})
    offers = await apps_col.count_documents({**uf, "status": "offered"})
    failed = await apps_col.count_documents({**uf, "status": "failed"})

    # Average match score
    pipeline = [{"$match": uf}, {"$group": {"_id": None, "avg_score": {"$avg": "$match_score"}}}]
    avg_result = await jobs_col.aggregate(pipeline).to_list(1)
    avg_score = round(avg_result[0]["avg_score"], 1) if avg_result and avg_result[0]["avg_score"] else 0

    result = {
        "total_jobs": total_jobs,
        "new_today": new_today,
        "new_this_week": new_this_week,
        "high_matches": high_matches,
        "total_applied": total_applied,
        "applied_today": applied_today,
        "interviews": interviews,
        "offers": offers,
        "failed_applications": failed,
        "avg_match_score": avg_score,
    }
    _set_cached(f"stats:{user_id}", result)
    return result


@router.get("/pipeline")
async def get_pipeline(user_id: str = Depends(get_current_user_id)):
    """
    Get application pipeline data for the Kanban-style view.
    
    Returns counts per status:
    pending → submitted → reviewing → interview → offered → accepted
    """
    apps_col = get_collection("applications")

    statuses = ["pending", "submitted", "reviewing", "interview", "offered", "accepted", "rejected", "withdrawn"]
    pipeline_data = {}

    for status in statuses:
        count = await apps_col.count_documents({"status": status, "user_id": user_id})
        pipeline_data[status] = count

    return {"pipeline": pipeline_data}


@router.get("/portals")
async def get_portal_stats(user_id: str = Depends(get_current_user_id)):
    """Get per-portal breakdown of jobs and applications."""
    jobs_col = get_collection("jobs")
    prefs = await get_user_prefs(user_id)

    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$portal",
            "total": {"$sum": 1},
            "avg_score": {"$avg": "$match_score"},
            "high_matches": {
                "$sum": {"$cond": [{"$gte": ["$match_score", prefs["min_match_score"]]}, 1, 0]}
            },
        }},
        {"$sort": {"total": -1}},
    ]

    results = await jobs_col.aggregate(pipeline).to_list(20)

    portals = []
    for r in results:
        portals.append({
            "portal": r["_id"],
            "total_jobs": r["total"],
            "avg_score": round(r["avg_score"] or 0, 1),
            "high_matches": r["high_matches"],
        })

    return {"portals": portals}


@router.get("/timeline")
async def get_timeline(user_id: str = Depends(get_current_user_id)):
    """
    Get daily job counts for the past 30 days.
    Used for the timeline chart on the dashboard.
    """
    jobs_col = get_collection("jobs")
    start_date = datetime.utcnow() - timedelta(days=30)

    pipeline = [
        {"$match": {"created_at": {"$gte": start_date}, "user_id": user_id}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$match_score"},
        }},
        {"$sort": {"_id": 1}},
    ]

    results = await jobs_col.aggregate(pipeline).to_list(31)

    return {
        "timeline": [
            {"date": r["_id"], "jobs": r["count"], "avg_score": round(r["avg_score"] or 0, 1)}
            for r in results
        ]
    }


@router.get("/recent-activity")
async def get_recent_activity(user_id: str = Depends(get_current_user_id)):
    """Get the 10 most recent actions (new jobs, applications, status changes)."""
    jobs_col = get_collection("jobs")
    apps_col = get_collection("applications")

    # Recent jobs
    recent_jobs = await jobs_col.find({"user_id": user_id}).sort("created_at", -1).limit(5).to_list(5)
    # Recent applications
    recent_apps = await apps_col.find({"user_id": user_id}).sort("applied_at", -1).limit(5).to_list(5)

    activity = []
    for job in recent_jobs:
        activity.append({
            "type": "job_found",
            "title": job.get("title"),
            "company": job.get("company"),
            "portal": job.get("portal"),
            "score": job.get("match_score"),
            "timestamp": job.get("created_at"),
        })
    for app in recent_apps:
        activity.append({
            "type": "application",
            "title": app.get("job_title"),
            "company": app.get("company"),
            "status": app.get("status"),
            "timestamp": app.get("applied_at"),
        })

    # Sort by timestamp descending
    activity.sort(key=lambda x: x.get("timestamp") or datetime.min, reverse=True)

    return {"activity": activity[:10]}


@router.get("/salary-insights")
async def get_salary_insights(user_id: str = Depends(get_current_user_id)):
    """Aggregate salary data from scraped jobs."""
    jobs_col = get_collection("jobs")

    # Get jobs with salary data
    cursor = jobs_col.find(
        {"user_id": user_id, "salary": {"$exists": True, "$ne": ""}},
        {"title": 1, "company": 1, "location": 1, "salary": 1, "match_score": 1}
    ).limit(500)
    jobs = await cursor.to_list(500)

    # Get top skills demand
    pipeline = [
        {"$match": {"user_id": user_id, "skills": {"$exists": True, "$ne": []}}},
        {"$unwind": "$skills"},
        {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]
    skills = await jobs_col.aggregate(pipeline).to_list(15)

    return {
        "jobs_with_salary": len(jobs),
        "salary_jobs": [{"title": j["title"], "company": j["company"], "salary": j["salary"], "score": j.get("match_score")} for j in jobs[:20]],
        "top_skills": [{"skill": s["_id"], "count": s["count"]} for s in skills],
    }
