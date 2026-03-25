"""Tests for /api/applications endpoints."""

import pytest
from bson import ObjectId

pytestmark = pytest.mark.asyncio


async def test_list_applications_empty(client):
    r = await client.get("/api/applications")
    assert r.status_code == 200
    assert r.json()["applications"] == []
    assert r.json()["total"] == 0


async def test_create_application(client, sample_job):
    r = await client.post("/api/applications", params={"job_id": sample_job})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "application_id" in data
    assert data["job_url"] == "https://linkedin.com/jobs/ext123"


async def test_create_application_sets_job_status(client, sample_job):
    await client.post("/api/applications", params={"job_id": sample_job})
    r = await client.get(f"/api/jobs/{sample_job}")
    assert r.json()["status"] == "applied"


async def test_create_application_duplicate(client, sample_job):
    await client.post("/api/applications", params={"job_id": sample_job})
    r = await client.post("/api/applications", params={"job_id": sample_job})
    assert r.status_code == 400
    assert "already applied" in r.json()["detail"].lower()


async def test_create_application_job_not_found(client):
    fake_id = str(ObjectId())
    r = await client.post("/api/applications", params={"job_id": fake_id})
    assert r.status_code == 404


async def test_list_applications_with_data(client, sample_job):
    await client.post("/api/applications", params={"job_id": sample_job})
    r = await client.get("/api/applications")
    data = r.json()
    assert data["total"] == 1
    assert data["applications"][0]["job_title"] == "Backend Engineer"


async def test_list_applications_filter_status(client, sample_job):
    await client.post("/api/applications", params={"job_id": sample_job})
    r = await client.get("/api/applications", params={"status": "pending"})
    assert r.json()["total"] == 1

    r = await client.get("/api/applications", params={"status": "submitted"})
    assert r.json()["total"] == 0


async def test_get_application(client, sample_job):
    create_r = await client.post("/api/applications", params={"job_id": sample_job})
    app_id = create_r.json()["application_id"]

    r = await client.get(f"/api/applications/{app_id}")
    assert r.status_code == 200
    assert r.json()["job_title"] == "Backend Engineer"
    assert r.json()["status"] == "pending"


async def test_get_application_not_found(client):
    fake_id = str(ObjectId())
    r = await client.get(f"/api/applications/{fake_id}")
    assert r.status_code == 404


async def test_update_application_status(client, sample_job):
    create_r = await client.post("/api/applications", params={"job_id": sample_job})
    app_id = create_r.json()["application_id"]

    r = await client.patch(f"/api/applications/{app_id}", params={"status": "interview"})
    assert r.status_code == 200
    assert r.json()["success"] is True

    r = await client.get(f"/api/applications/{app_id}")
    assert r.json()["status"] == "interview"
    # Should have event in timeline
    events = r.json().get("events", [])
    assert any("interview" in e.get("description", "").lower() for e in events)


async def test_update_application_notes(client, sample_job):
    create_r = await client.post("/api/applications", params={"job_id": sample_job})
    app_id = create_r.json()["application_id"]

    r = await client.patch(f"/api/applications/{app_id}", params={"notes": "Great interview"})
    assert r.status_code == 200

    r = await client.get(f"/api/applications/{app_id}")
    assert r.json()["notes"] == "Great interview"


async def test_retry_application_not_failed(client, sample_job):
    """Can only retry failed applications."""
    create_r = await client.post("/api/applications", params={"job_id": sample_job})
    app_id = create_r.json()["application_id"]

    r = await client.post(f"/api/applications/{app_id}/retry")
    assert r.status_code == 400
    assert "failed" in r.json()["detail"].lower()
