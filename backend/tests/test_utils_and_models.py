"""Tests for utility functions and models."""

import pytest
from utils.helpers import (
    generate_job_hash, clean_text, truncate_text, parse_experience_years,
    format_salary, sanitize_filename, clean_url, extract_domain, to_object_id,
)
from bson import ObjectId


def test_generate_job_hash():
    h1 = generate_job_hash("linkedin", "123")
    h2 = generate_job_hash("linkedin", "123")
    h3 = generate_job_hash("naukri", "123")
    assert h1 == h2  # Same input → same hash
    assert h1 != h3  # Different portal → different hash
    assert len(h1) == 64  # SHA-256 hex


def test_clean_text():
    assert clean_text("  hello   world  \n\n  ") == "hello world"
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_truncate_text():
    assert truncate_text("short", 100) == "short"
    assert truncate_text("a" * 200, 100) == "a" * 97 + "..."
    assert truncate_text(None) == ""
    assert truncate_text("") == ""


def test_parse_experience_years():
    assert parse_experience_years("1-3 years") == 1.0
    assert parse_experience_years("2+ years") == 2.0
    assert parse_experience_years("1.5 to 3 yrs") == 1.5
    assert parse_experience_years("fresher") == 0.0
    assert parse_experience_years("entry level") == 0.0
    assert parse_experience_years(None) is None
    assert parse_experience_years("") is None


def test_format_salary():
    assert format_salary(None) == "Not disclosed"
    assert "15" in format_salary(1500000)  # ₹15.0L
    assert "1.5" in format_salary(15000000)  # ₹1.5Cr
    assert "$" in format_salary(150000, "USD")


def test_sanitize_filename():
    assert sanitize_filename("SDE-2 @ Google (Backend)") == "SDE-2_Google_Backend"
    assert len(sanitize_filename("a" * 200)) <= 100


def test_clean_url():
    assert clean_url("https://example.com/jobs/123?ref=abc#top") == "https://example.com/jobs/123"
    assert clean_url("") == ""


def test_extract_domain():
    assert extract_domain("https://www.linkedin.com/jobs/123") == "linkedin.com"
    assert extract_domain("https://naukri.com/job/456") == "naukri.com"


def test_to_object_id():
    oid = ObjectId()
    assert to_object_id(str(oid)) == oid
    with pytest.raises(ValueError):
        to_object_id("not-valid")


# ── Model validation tests ──

def test_job_status_enum():
    from models.job import JobStatus
    assert JobStatus.NEW == "new"
    assert JobStatus.APPLIED == "applied"


def test_application_status_enum():
    from models.application import ApplicationStatus
    assert ApplicationStatus.PENDING == "pending"
    assert ApplicationStatus.SUBMITTED == "submitted"


def test_job_create_validation():
    from models.job import JobCreate
    job = JobCreate(
        title="SDE", company="Google", portal="linkedin",
        external_id="123", url="https://example.com",
    )
    assert job.title == "SDE"
    assert job.skills == []  # Default empty list


def test_job_update_partial():
    from models.job import JobUpdate
    update = JobUpdate(status="applied")
    dump = update.model_dump(exclude_none=True)
    assert dump == {"status": "applied"}


def test_user_create_validation():
    from models.user import UserCreate
    with pytest.raises(Exception):
        UserCreate(email="x", password="12345", full_name="")  # password too short
