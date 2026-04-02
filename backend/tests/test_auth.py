"""Tests for /api/auth endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def anon_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_register(anon_client):
    r = await anon_client.post("/api/auth/register", json={
        "email": "new@example.com", "password": "Secret123", "full_name": "New User",
    })
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["full_name"] == "New User"


async def test_register_duplicate(anon_client):
    payload = {"email": "dup@example.com", "password": "Secret123", "full_name": "Dup"}
    await anon_client.post("/api/auth/register", json=payload)
    r = await anon_client.post("/api/auth/register", json=payload)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert "already registered" in str(detail).lower()


async def test_login_success(anon_client):
    await anon_client.post("/api/auth/register", json={
        "email": "login@example.com", "password": "Secret123", "full_name": "Login User",
    })
    r = await anon_client.post("/api/auth/login", json={
        "email": "login@example.com", "password": "Secret123",
    })
    assert r.status_code == 200
    assert "token" in r.json()


async def test_login_wrong_password(anon_client):
    await anon_client.post("/api/auth/register", json={
        "email": "wrong@example.com", "password": "Secret123", "full_name": "Wrong",
    })
    r = await anon_client.post("/api/auth/login", json={
        "email": "wrong@example.com", "password": "badpassword",
    })
    assert r.status_code == 401


async def test_login_nonexistent(anon_client):
    r = await anon_client.post("/api/auth/login", json={
        "email": "ghost@example.com", "password": "Secret123",
    })
    assert r.status_code == 401


async def test_me(client):
    r = await client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"


async def test_me_no_token(anon_client):
    r = await anon_client.get("/api/auth/me")
    assert r.status_code == 403  # HTTPBearer returns 403 when no token
