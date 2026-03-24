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
from fastapi import APIRouter
from database import get_collection
from config import settings

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    """
    Get key metrics for the dashboard overview cards.
    
    Returns counts for: total jobs, new today, applied,
    high matches, interviews, offers.
    """
    jobs_col = get_collection("jobs")
    apps_col = get_collection("applications")

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Run all counts in parallel-ish (Motor handles this efficiently)
    total_jobs = await jobs_col.count_documents({})
    new_today = await jobs_col.count_documents({"created_at": {"$gte": today_start}})
    new_this_week = await jobs_col.count_documents({"created_at": {"$gte": week_start}})
    high_matches = await jobs_col.count_documents({
        "match_score": {"$gte": settings.MIN_MATCH_SCORE_TO_APPLY},
        "status": {"$in": ["new", "reviewed", "shortlisted"]},
    })

    total_applied = await apps_col.count_documents({"status": {"$ne": "failed"}})
    applied_today = await apps_col.count_documents({
        "applied_at": {"$gte": today_start},
        "status": {"$ne": "failed"},
    })
    interviews = await apps_col.count_documents({"status": "interview"})
    offers = await apps_col.count_documents({"status": "offered"})
    failed = await apps_col.count_documents({"status": "failed"})

    # Average match score
    pipeline = [{"$group": {"_id": None, "avg_score": {"$avg": "$match_score"}}}]
    avg_result = await jobs_col.aggregate(pipeline).to_list(1)
    avg_score = round(avg_result[0]["avg_score"], 1) if avg_result and avg_result[0]["avg_score"] else 0

    return {
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


@router.get("/pipeline")
async def get_pipeline():
    """
    Get application pipeline data for the Kanban-style view.
    
    Returns counts per status:
    pending → submitted → reviewing → interview → offered → accepted
    """
    apps_col = get_collection("applications")

    statuses = ["pending", "submitted", "reviewing", "interview", "offered", "accepted", "rejected", "withdrawn"]
    pipeline_data = {}

    for status in statuses:
        count = await apps_col.count_documents({"status": status})
        pipeline_data[status] = count

    return {"pipeline": pipeline_data}


@router.get("/portals")
async def get_portal_stats():
    """
    Get per-portal breakdown of jobs and applications.
    
    Shows which portals are yielding the most and best results.
    """
    jobs_col = get_collection("jobs")

    pipeline = [
        {"$group": {
            "_id": "$portal",
            "total": {"$sum": 1},
            "avg_score": {"$avg": "$match_score"},
            "high_matches": {
                "$sum": {"$cond": [{"$gte": ["$match_score", settings.MIN_MATCH_SCORE_TO_APPLY]}, 1, 0]}
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
async def get_timeline():
    """
    Get daily job counts for the past 30 days.
    Used for the timeline chart on the dashboard.
    """
    jobs_col = get_collection("jobs")
    start_date = datetime.utcnow() - timedelta(days=30)

    pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
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
async def get_recent_activity():
    """Get the 10 most recent actions (new jobs, applications, status changes)."""
    jobs_col = get_collection("jobs")
    apps_col = get_collection("applications")

    # Recent jobs
    recent_jobs = await jobs_col.find().sort("created_at", -1).limit(5).to_list(5)
    # Recent applications
    recent_apps = await apps_col.find().sort("applied_at", -1).limit(5).to_list(5)

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
