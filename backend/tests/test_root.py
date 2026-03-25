"""Tests for the root endpoint and CORS."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_root_endpoint(client):
    r = await client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "JobPilot API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


async def test_scrape_status_not_running(client):
    r = await client.get("/api/jobs/scrape/status")
    assert r.status_code == 200
    assert r.json()["running"] is False


async def test_stop_scrape_when_not_running(client):
    r = await client.post("/api/jobs/scrape/stop")
    assert r.status_code == 400
