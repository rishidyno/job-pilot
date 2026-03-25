"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Application Model                                    ║
║                                                                   ║
║  Tracks the application lifecycle for each job you apply to.      ║
║  Links a Job → Resume → Cover Letter → Application Status.       ║
║                                                                   ║
║  MongoDB Collection: "applications"                               ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from utils.helpers import utc_now


class ApplicationStatus(str, Enum):
    """
    Application pipeline stages.
    
    PENDING    → Queued for auto-apply, waiting to be submitted
    SUBMITTED  → Successfully submitted to the portal
    FAILED     → Auto-apply failed (will show error details)
    REVIEWING  → Company is reviewing the application
    INTERVIEW  → Got an interview call
    OFFERED    → Received an offer
    ACCEPTED   → Accepted the offer
    REJECTED   → Rejected by the company
    WITHDRAWN  → You withdrew the application
    """
    PENDING = "pending"
    SUBMITTED = "submitted"
    FAILED = "failed"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationEvent(BaseModel):
    """
    A single event in the application timeline.
    
    Every status change, note, or action is recorded as an event.
    This gives a full history of what happened with each application.
    
    Example events:
    - "Application submitted via LinkedIn Easy Apply"
    - "Status changed from submitted to interview"
    - "Interview scheduled for 2025-03-15"
    """
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: str = Field(..., description="Type: status_change, note, error, action")
    description: str = Field(..., description="Human-readable event description")
    metadata: Optional[dict] = Field(None, description="Extra data (error details, etc.)")


class ApplicationCreate(BaseModel):
    """
    Schema for creating a new application record.
    
    Created when the user clicks "Apply" or when auto-apply
    picks up a shortlisted job.
    """
    job_id: str = Field(..., description="MongoDB ObjectId of the job")
    resume_id: Optional[str] = Field(None, description="ID of the tailored resume used")
    cover_letter_id: Optional[str] = Field(None, description="ID of the generated cover letter")
    apply_mode: str = Field("semi", description="Was this 'auto' or 'semi' (manual trigger)?")


class Application(BaseModel):
    """
    Full application document as stored in MongoDB.
    """
    # ── System fields ──
    id: Optional[str] = Field(None, alias="_id")
    
    # ── Owner ──
    user_id: Optional[str] = Field(None, description="Owner user ID")
    
    # ── References ──
    job_id: str = Field(..., description="Reference to the job document")
    resume_id: Optional[str] = Field(None, description="Tailored resume used for this application")
    cover_letter_id: Optional[str] = Field(None, description="Cover letter used")
    
    # ── Status tracking ──
    status: ApplicationStatus = Field(ApplicationStatus.PENDING)
    apply_mode: str = Field("semi", description="'auto' or 'semi'")
    
    # ── Portal-specific data ──
    portal: Optional[str] = Field(None, description="Which portal was used to apply")
    confirmation_id: Optional[str] = Field(None, description="Portal's confirmation/tracking ID")
    
    # ── Error tracking (for failed applications) ──
    error_message: Optional[str] = Field(None, description="Why the application failed")
    retry_count: int = Field(0, description="Number of retry attempts")
    
    # ── Timeline ──
    events: List[ApplicationEvent] = Field(
        default_factory=list,
        description="Chronological list of all events for this application"
    )
    
    # ── User notes ──
    notes: Optional[str] = Field(None, description="Personal notes about this application")
    
    # ── Timestamps ──
    applied_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    # ── Denormalized job data for dashboard display ──
    # (So we don't have to join on every dashboard load)
    job_title: Optional[str] = None
    company: Optional[str] = None
    job_url: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        use_enum_values = True
