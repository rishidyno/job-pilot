"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Job Model                                            ║
║                                                                   ║
║  Represents a job listing scraped from any portal.                ║
║  This is the CORE entity of the system — everything revolves      ║
║  around jobs: matching, tailoring, applying, tracking.            ║
║                                                                   ║
║  MongoDB Collection: "jobs"                                       ║
║                                                                   ║
║  LIFECYCLE:                                                       ║
║    new → reviewed → shortlisted → applied → interviewing →       ║
║    offered → accepted / rejected / expired / skipped              ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from utils.helpers import utc_now


class JobStatus(str, Enum):
    """
    All possible states a job can be in.
    
    Flow:
    ┌──────┐    ┌──────────┐    ┌─────────────┐    ┌─────────┐
    │ NEW  │───►│ REVIEWED  │───►│ SHORTLISTED │───►│ APPLIED │───► ...
    └──────┘    └──────────┘    └─────────────┘    └─────────┘
                     │                                    │
                     ▼                                    ▼
                 ┌─────────┐                     ┌──────────────┐
                 │ SKIPPED │                     │ INTERVIEWING │
                 └─────────┘                     └──────────────┘
                                                        │
                                            ┌───────────┼───────────┐
                                            ▼           ▼           ▼
                                      ┌─────────┐ ┌──────────┐ ┌──────────┐
                                      │ OFFERED │ │ REJECTED │ │ EXPIRED  │
                                      └─────────┘ └──────────┘ └──────────┘
                                            │
                                      ┌─────┴──────┐
                                      ▼            ▼
                                ┌──────────┐ ┌──────────┐
                                │ ACCEPTED │ │ DECLINED │
                                └──────────┘ └──────────┘
    """
    NEW = "new"                    # Just scraped, not reviewed yet
    REVIEWED = "reviewed"          # Seen on dashboard but no action taken
    SHORTLISTED = "shortlisted"    # Marked as interesting, pending apply
    APPLIED = "applied"            # Application submitted
    INTERVIEWING = "interviewing"  # In interview process
    OFFERED = "offered"            # Received an offer
    ACCEPTED = "accepted"          # Accepted the offer
    REJECTED = "rejected"          # Rejected by company
    EXPIRED = "expired"            # Job listing expired/closed
    SKIPPED = "skipped"            # User chose to skip this job
    DECLINED = "declined"          # User declined the offer


class JobCreate(BaseModel):
    """
    Schema for creating a new job entry (used by scrapers).
    
    When a scraper finds a job, it creates a JobCreate object
    with whatever data it could extract. Not all fields are
    required because different portals provide different data.
    """
    # ── Required fields (every scraper must provide these) ──
    title: str = Field(..., description="Job title (e.g., 'SDE-2 Backend')")
    company: str = Field(..., description="Company name")
    portal: str = Field(..., description="Source portal (e.g., 'linkedin', 'naukri')")
    external_id: str = Field(..., description="Portal's unique ID for this job")
    url: str = Field(..., description="Direct URL to the job posting")

    # ── Optional fields (scrapers fill what they can) ──
    description: Optional[str] = Field(None, description="Full job description text")
    location: Optional[str] = Field(None, description="Job location (city/remote)")
    experience_required: Optional[str] = Field(None, description="Required experience (e.g., '1-3 years')")
    experience_min_years: Optional[float] = Field(None, description="Parsed minimum years of experience")
    salary_min: Optional[float] = Field(None, description="Minimum salary (annual)")
    salary_max: Optional[float] = Field(None, description="Maximum salary (annual)")
    salary_currency: str = Field("INR", description="Salary currency code")
    skills: List[str] = Field(default_factory=list, description="Required skills mentioned")
    job_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract, etc.")
    company_logo_url: Optional[str] = Field(None, description="URL to company logo image")
    posted_date: Optional[str] = Field(None, description="When the job was posted (raw text)")
    apply_method: Optional[str] = Field(None, description="How to apply: 'easy_apply', 'external', 'email'")


class JobUpdate(BaseModel):
    """
    Schema for updating an existing job.
    All fields are optional — only provided fields will be updated.
    """
    status: Optional[JobStatus] = None
    match_score: Optional[int] = Field(None, ge=0, le=100, description="AI match score 0-100")
    match_reasoning: Optional[str] = Field(None, description="AI explanation for the match score")
    notes: Optional[str] = Field(None, description="User's personal notes about this job")
    apply_mode: Optional[str] = Field(None, description="'auto' or 'semi' for this specific job")


class Job(BaseModel):
    """
    Full job document as stored in MongoDB.
    
    This extends JobCreate with system-managed fields like
    _id, status, match_score, timestamps, etc.
    """
    # ── System fields ──
    id: Optional[str] = Field(None, alias="_id", description="MongoDB ObjectId as string")
    user_id: Optional[str] = Field(None, description="Owner user ID")
    status: JobStatus = Field(JobStatus.NEW, description="Current job status")
    match_score: Optional[int] = Field(None, ge=0, le=100, description="AI-computed match score")
    match_reasoning: Optional[str] = Field(None, description="Why the AI gave this score")
    notes: Optional[str] = Field(None, description="User's notes")
    apply_mode: str = Field("semi", description="Apply mode for this job: 'auto' or 'semi'")
    
    # ── Job details (from scraper) ──
    title: str
    company: str
    portal: str
    external_id: str
    url: str
    description: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[str] = None
    experience_min_years: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "INR"
    skills: List[str] = Field(default_factory=list)
    job_type: Optional[str] = None
    company_logo_url: Optional[str] = None
    posted_date: Optional[str] = None
    apply_method: Optional[str] = None
    
    # ── Deduplication ──
    job_hash: Optional[str] = Field(None, description="SHA-256 hash for deduplication")
    
    # ── Timestamps ──
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        # Allow both "id" and "_id" when parsing from MongoDB
        populate_by_name = True
        # Allow arbitrary types (for ObjectId handling)
        arbitrary_types_allowed = True
        # Use enum values (not names) when serializing
        use_enum_values = True
