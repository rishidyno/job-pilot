"""
Shared test fixtures — mongomock-motor for DB, FastAPI TestClient with auth.
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import patch, AsyncMock

# Ensure backend is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mongomock_motor import AsyncMongoMockClient
from httpx import AsyncClient, ASGITransport
from bson import ObjectId

# Patch database BEFORE importing app
_mock_client = AsyncMongoMockClient()
_mock_db = _mock_client["jobpilot_test"]


def _mock_get_db():
    return _mock_db


def _mock_get_collection(name):
    return _mock_db[name]


# Patch database module at import time
patch("database._database", _mock_db).start()
patch("database.get_db", _mock_get_db).start()
patch("database.get_collection", _mock_get_collection).start()
patch("database.connect_db", AsyncMock()).start()
patch("database.close_db", AsyncMock()).start()

# Patch scheduler so it doesn't start real jobs
patch("schedulers.job_scheduler.start_scheduler", lambda: None).start()
patch("schedulers.job_scheduler.stop_scheduler", lambda: None).start()

from main import app
from services.auth_service import create_access_token, hash_password
from utils.helpers import utc_now


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def clean_db():
    """Drop all collections before each test."""
    for name in await _mock_db.list_collection_names():
        await _mock_db.drop_collection(name)
    yield


@pytest.fixture
async def test_user():
    """Create a test user and return (user_id, token)."""
    users = _mock_db["users"]
    doc = {
        "email": "test@example.com",
        "password_hash": hash_password("password123"),
        "full_name": "Test User",
        "created_at": utc_now(),
    }
    result = await users.insert_one(doc)
    uid = str(result.inserted_id)
    token = create_access_token(uid)
    return uid, token


@pytest.fixture
async def client(test_user):
    """Authenticated async HTTP client."""
    uid, token = test_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.headers["Authorization"] = f"Bearer {token}"
        ac._test_user_id = uid
        yield ac


@pytest.fixture
async def sample_job(test_user):
    """Insert a sample job and return its ID."""
    uid, _ = test_user
    jobs = _mock_db["jobs"]
    doc = {
        "user_id": uid,
        "title": "Backend Engineer",
        "company": "TestCorp",
        "portal": "linkedin",
        "external_id": "ext123",
        "url": "https://linkedin.com/jobs/ext123",
        "description": "Build APIs with Python and FastAPI",
        "location": "Bengaluru",
        "experience_required": "1-3 years",
        "skills": ["Python", "FastAPI", "MongoDB"],
        "status": "new",
        "match_score": 75,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    result = await jobs.insert_one(doc)
    return str(result.inserted_id)


@pytest.fixture
async def base_resume(test_user):
    """Insert a base resume and return its ID."""
    uid, _ = test_user
    resumes = _mock_db["resumes"]
    doc = {
        "user_id": uid,
        "is_base": True,
        "latex_source": r"\documentclass{article}\begin{document}Hello\end{document}",
        "raw_text": "Test User - Backend Engineer - Python, FastAPI, MongoDB",
        "created_at": utc_now(),
    }
    result = await resumes.insert_one(doc)
    return str(result.inserted_id)
