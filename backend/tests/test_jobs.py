"""Tests for /api/jobs endpoints."""

import pytest
from bson import ObjectId

pytestmark = pytest.mark.asyncio


async def test_list_jobs_empty(client):
    r = await client.get("/api/jobs")
    assert r.status_code == 200
    data = r.json()
    assert data["jobs"] == []
    assert data["total"] == 0


async def test_list_jobs_with_data(client, sample_job):
    r = await client.get("/api/jobs")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["jobs"][0]["title"] == "Backend Engineer"


async def test_list_jobs_filter_status(client, sample_job):
    r = await client.get("/api/jobs", params={"status": "new"})
    assert r.json()["total"] == 1

    r = await client.get("/api/jobs", params={"status": "applied"})
    assert r.json()["total"] == 0


async def test_list_jobs_filter_portal(client, sample_job):
    r = await client.get("/api/jobs", params={"portal": "linkedin"})
    assert r.json()["total"] == 1

    r = await client.get("/api/jobs", params={"portal": "naukri"})
    assert r.json()["total"] == 0


async def test_list_jobs_filter_min_score(client, sample_job):
    r = await client.get("/api/jobs", params={"min_score": 70})
    assert r.json()["total"] == 1

    r = await client.get("/api/jobs", params={"min_score": 90})
    assert r.json()["total"] == 0


async def test_list_jobs_pagination(client, test_user):
    """Insert multiple jobs and test skip/limit."""
    from tests.conftest import _mock_db
    uid, _ = test_user
    from utils.helpers import utc_now
    jobs_col = _mock_db["jobs"]
    for i in range(5):
        await jobs_col.insert_one({
            "user_id": uid, "title": f"Job {i}", "company": "Co",
            "portal": "linkedin", "external_id": f"pag{i}",
            "url": f"https://example.com/{i}", "status": "new",
            "match_score": 50 + i, "created_at": utc_now(), "updated_at": utc_now(),
        })

    r = await client.get("/api/jobs", params={"limit": 2, "skip": 0})
    data = r.json()
    assert len(data["jobs"]) == 2
    assert data["total"] == 5
    assert data["has_more"] is True

    r = await client.get("/api/jobs", params={"limit": 2, "skip": 4})
    data = r.json()
    assert len(data["jobs"]) == 1
    assert data["has_more"] is False


async def test_get_job(client, sample_job):
    r = await client.get(f"/api/jobs/{sample_job}")
    assert r.status_code == 200
    assert r.json()["title"] == "Backend Engineer"


async def test_get_job_not_found(client):
    fake_id = str(ObjectId())
    r = await client.get(f"/api/jobs/{fake_id}")
    assert r.status_code == 404


async def test_get_job_invalid_id(client):
    r = await client.get("/api/jobs/not-an-objectid")
    assert r.status_code == 400


async def test_update_job_status(client, sample_job):
    r = await client.patch(f"/api/jobs/{sample_job}", json={"status": "shortlisted"})
    assert r.status_code == 200
    assert r.json()["success"] is True

    r = await client.get(f"/api/jobs/{sample_job}")
    assert r.json()["status"] == "shortlisted"


async def test_update_job_notes(client, sample_job):
    r = await client.patch(f"/api/jobs/{sample_job}", json={"notes": "Looks good"})
    assert r.status_code == 200

    r = await client.get(f"/api/jobs/{sample_job}")
    assert r.json()["notes"] == "Looks good"


async def test_update_job_empty_body(client, sample_job):
    r = await client.patch(f"/api/jobs/{sample_job}", json={})
    assert r.status_code == 400


async def test_update_job_not_found(client):
    fake_id = str(ObjectId())
    r = await client.patch(f"/api/jobs/{fake_id}", json={"status": "applied"})
    assert r.status_code == 404


async def test_delete_job(client, sample_job):
    r = await client.delete(f"/api/jobs/{sample_job}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True

    r = await client.get(f"/api/jobs/{sample_job}")
    assert r.status_code == 404


async def test_delete_job_not_found(client):
    fake_id = str(ObjectId())
    r = await client.delete(f"/api/jobs/{fake_id}")
    assert r.status_code == 404


async def test_score_job(client, sample_job, base_resume):
    """Score endpoint calls AI — mock it."""
    from unittest.mock import patch, AsyncMock
    mock_score = {
        "score": 85, "reasoning": "Great match",
        "matching_skills": ["Python"], "missing_skills": [],
        "experience_fit": "good", "key_strengths": [], "concerns": [],
    }
    with patch("routers.jobs.job_matcher.score_job", AsyncMock(return_value=mock_score)):
        r = await client.post(f"/api/jobs/{sample_job}/score")
    assert r.status_code == 200
    assert r.json()["score"]["score"] == 85

    # Verify score persisted
    r = await client.get(f"/api/jobs/{sample_job}")
    assert r.json()["match_score"] == 85


async def test_score_job_not_found(client):
    fake_id = str(ObjectId())
    r = await client.post(f"/api/jobs/{fake_id}/score")
    assert r.status_code == 404
