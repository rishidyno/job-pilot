"""Tests for /api/settings endpoints."""

import os
import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


async def test_get_profile_creates_default(client):
    r = await client.get("/api/settings/profile")
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "test@example.com"
    assert "target_roles" in data
    assert isinstance(data["target_roles"], list)


async def test_update_profile(client):
    # Ensure profile exists
    await client.get("/api/settings/profile")

    r = await client.put("/api/settings/profile", json={
        "full_name": "Updated Name",
        "current_role": "SDE-2",
        "min_match_score": 80,
    })
    assert r.status_code == 200
    assert r.json()["success"] is True

    r = await client.get("/api/settings/profile")
    assert r.json()["full_name"] == "Updated Name"
    assert r.json()["current_role"] == "SDE-2"
    assert r.json()["min_match_score"] == 80


async def test_get_scheduler_status(client):
    r = await client.get("/api/settings/scheduler")
    assert r.status_code == 200
    # Scheduler is mocked out, so it should report not running
    assert "running" in r.json()


async def test_get_portal_status(client):
    r = await client.get("/api/settings/portals")
    assert r.status_code == 200
    portals = r.json()["portals"]
    assert "linkedin" in portals
    assert "naukri" in portals
    assert portals["indeed"]["configured"] is True  # Indeed works without login


async def test_health(client):
    r = await client.get("/api/settings/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


async def test_rules_crud(client):
    # Initially empty
    r = await client.get("/api/settings/rules")
    assert r.status_code == 200

    # Update
    r = await client.put("/api/settings/rules", json={"content": "# My Rules\n- Be concise"})
    assert r.json()["success"] is True

    # Read back
    r = await client.get("/api/settings/rules")
    assert "My Rules" in r.json()["content"]


async def test_profile_md_crud(client):
    r = await client.get("/api/settings/profile-md")
    assert r.status_code == 200

    r = await client.put("/api/settings/profile-md", json={"content": "# Profile\nPython dev"})
    assert r.json()["success"] is True

    r = await client.get("/api/settings/profile-md")
    assert "Python dev" in r.json()["content"]
