"""Tests for /api/resumes endpoints."""

import pytest
from bson import ObjectId
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.asyncio


async def test_get_latex_empty(client):
    r = await client.get("/api/resumes/latex")
    assert r.status_code == 200
    assert r.json()["content"] == ""


async def test_put_and_get_latex(client):
    latex = r"\documentclass{article}\begin{document}Test\end{document}"
    r = await client.put("/api/resumes/latex", json={"content": latex})
    assert r.status_code == 200
    assert r.json()["success"] is True

    r = await client.get("/api/resumes/latex")
    assert r.json()["content"] == latex


async def test_put_latex_upserts(client):
    """Second PUT should update, not create duplicate."""
    await client.put("/api/resumes/latex", json={"content": "v1"})
    await client.put("/api/resumes/latex", json={"content": "v2"})

    r = await client.get("/api/resumes/latex")
    assert r.json()["content"] == "v2"


async def test_list_resumes_empty(client):
    r = await client.get("/api/resumes")
    assert r.status_code == 200
    assert r.json()["resumes"] == []


async def test_list_resumes_with_base(client, base_resume):
    r = await client.get("/api/resumes")
    assert r.json()["total"] == 1
    assert r.json()["resumes"][0]["is_base"] is True


async def test_list_resumes_filter_base(client, base_resume):
    r = await client.get("/api/resumes", params={"is_base": True})
    assert r.json()["total"] == 1

    r = await client.get("/api/resumes", params={"is_base": False})
    assert r.json()["total"] == 0


async def test_get_resume(client, base_resume):
    r = await client.get(f"/api/resumes/{base_resume}")
    assert r.status_code == 200
    assert r.json()["is_base"] is True


async def test_get_resume_not_found(client):
    fake_id = str(ObjectId())
    r = await client.get(f"/api/resumes/{fake_id}")
    assert r.status_code == 404


async def test_tailor_resume(client, sample_job, base_resume):
    mock_result = {
        "latex_source": r"\documentclass{article}\begin{document}Tailored\end{document}",
        "changes_made": ["Reworded summary"],
    }
    with patch("routers.resumes.resume_tailor.tailor_resume", AsyncMock(return_value=mock_result)):
        r = await client.post("/api/resumes/tailor", params={"job_id": sample_job})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "resume_id" in data
    assert data["changes_made"] == ["Reworded summary"]


async def test_tailor_resume_no_base(client, sample_job):
    r = await client.post("/api/resumes/tailor", params={"job_id": sample_job})
    assert r.status_code == 400
    assert "no base" in r.json()["detail"].lower()


async def test_tailor_resume_job_not_found(client, base_resume):
    fake_id = str(ObjectId())
    r = await client.post("/api/resumes/tailor", params={"job_id": fake_id})
    assert r.status_code == 404


async def test_cover_letter(client, sample_job, base_resume):
    mock_letter = {
        "subject_line": "Application for Backend Engineer",
        "greeting": "Dear Hiring Manager,",
        "body": "I am excited...",
        "closing": "Best regards,\nTest User",
        "full_text": "Dear Hiring Manager,\n\nI am excited...\n\nBest regards,\nTest User",
        "_ai_metadata": {"model": "test", "input_tokens": 0, "output_tokens": 0, "tone": "professional"},
    }
    with patch("routers.resumes.cover_letter_service.generate", AsyncMock(return_value=mock_letter)):
        r = await client.post("/api/resumes/cover-letter", params={"job_id": sample_job})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "cover_letter_id" in data
    assert "Dear Hiring Manager" in data["content"]


async def test_cover_letter_job_not_found(client, base_resume):
    fake_id = str(ObjectId())
    r = await client.post("/api/resumes/cover-letter", params={"job_id": fake_id})
    assert r.status_code == 404
