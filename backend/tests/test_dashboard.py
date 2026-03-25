"""Tests for /api/dashboard endpoints."""

import pytest
from bson import ObjectId
from utils.helpers import utc_now

pytestmark = pytest.mark.asyncio


async def test_dashboard_stats_empty(client):
    r = await client.get("/api/dashboard/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_jobs"] == 0
    assert data["total_applied"] == 0
    assert data["interviews"] == 0
    assert data["avg_match_score"] == 0


async def test_dashboard_stats_with_data(client, sample_job):
    r = await client.get("/api/dashboard/stats")
    data = r.json()
    assert data["total_jobs"] == 1
    assert data["new_today"] == 1
    assert data["avg_match_score"] == 75


async def test_dashboard_pipeline_empty(client):
    r = await client.get("/api/dashboard/pipeline")
    assert r.status_code == 200
    pipeline = r.json()["pipeline"]
    assert all(v == 0 for v in pipeline.values())


async def test_dashboard_pipeline_with_app(client, sample_job):
    await client.post("/api/applications", params={"job_id": sample_job})
    r = await client.get("/api/dashboard/pipeline")
    assert r.json()["pipeline"]["pending"] == 1


async def test_dashboard_portals_empty(client):
    r = await client.get("/api/dashboard/portals")
    assert r.status_code == 200
    assert r.json()["portals"] == []


async def test_dashboard_portals_with_data(client, sample_job):
    r = await client.get("/api/dashboard/portals")
    portals = r.json()["portals"]
    assert len(portals) == 1
    assert portals[0]["portal"] == "linkedin"
    assert portals[0]["total_jobs"] == 1


async def test_dashboard_timeline(client, sample_job):
    r = await client.get("/api/dashboard/timeline")
    assert r.status_code == 200
    timeline = r.json()["timeline"]
    assert len(timeline) >= 1
    assert timeline[0]["jobs"] == 1


async def test_dashboard_recent_activity_empty(client):
    r = await client.get("/api/dashboard/recent-activity")
    assert r.status_code == 200
    assert r.json()["activity"] == []


async def test_dashboard_recent_activity(client, sample_job):
    r = await client.get("/api/dashboard/recent-activity")
    activity = r.json()["activity"]
    assert len(activity) == 1
    assert activity[0]["type"] == "job_found"
    assert activity[0]["title"] == "Backend Engineer"
