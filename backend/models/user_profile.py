"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — User Profile Model                                   ║
║                                                                   ║
║  Stores your profile data and job search preferences.             ║
║  This is a singleton document — only one profile exists.          ║
║  Populated from .env defaults + can be updated via dashboard.     ║
║                                                                   ║
║  MongoDB Collection: "user_profile"                               ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from utils.helpers import utc_now


class UserProfile(BaseModel):
    """
    Your professional profile and job search preferences.
    
    The AI uses this data (along with your base resume) to:
    - Score how well a job matches your profile
    - Tailor resumes to emphasize relevant experience
    - Generate personalized cover letters
    """
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = Field(None, description="Owner user ID")
    
    # ── Personal Info ──
    full_name: str = Field("", description="Your full name")
    email: str = Field("", description="Primary email")
    phone: str = Field("", description="Phone number")
    linkedin_url: str = Field("", description="LinkedIn profile URL")
    github_url: str = Field("", description="GitHub profile URL")
    location: str = Field("", description="Current location")
    
    # ── Professional Summary ──
    current_role: str = Field("", description="Current job title")
    current_company: str = Field("", description="Current employer")
    total_experience_years: float = Field(0, description="Total years of experience")
    
    # ── Job Search Preferences ──
    target_roles: List[str] = Field(
        default_factory=lambda: [
            "Backend Engineer", "Full Stack Developer", "SDE-1", "SDE-2",
            "Software Engineer", "Software Developer", "Backend Developer"
        ],
        description="Job titles you're interested in"
    )
    target_locations: List[str] = Field(
        default_factory=lambda: [
            "Bengaluru", "Bangalore", "Remote", "Hyderabad", "Noida", "Gurgaon", "Gurugram"
        ],
        description="Preferred locations"
    )
    min_salary: Optional[float] = Field(None, description="Minimum acceptable salary (annual)")
    max_notice_period_days: int = Field(90, description="Maximum acceptable notice period in days")
    
    # ── Skills (ordered by proficiency) ──
    primary_skills: List[str] = Field(
        default_factory=lambda: [
            "Java", "Spring Boot", "Node.js", "JavaScript", "Python",
            "MongoDB", "PostgreSQL", "REST API", "Microservices"
        ],
        description="Your strongest skills"
    )
    secondary_skills: List[str] = Field(
        default_factory=lambda: [
            "Docker", "React", "Kotlin", "C/C++", "Git", "Linux",
            "Redis", "AWS", "Playwright"
        ],
        description="Skills you have but aren't primary"
    )
    
    # ── Preferences ──
    preferred_company_sizes: List[str] = Field(
        default_factory=lambda: ["startup", "mid", "large"],
        description="Company size preference: startup, mid, large, enterprise"
    )
    industries_to_avoid: List[str] = Field(
        default_factory=list,
        description="Industries you don't want to work in"
    )
    companies_to_avoid: List[str] = Field(
        default_factory=list,
        description="Specific companies to skip"
    )
    
    # ── Auto-apply settings ──
    auto_apply_enabled: bool = Field(False, description="Master switch for auto-apply")
    auto_apply_mode: str = Field("semi", description="'auto' or 'semi'")
    min_match_score: int = Field(70, description="Min score to auto-apply")
    max_daily_applications: int = Field(20, description="Max applications per day (safety limit)")
    
    # ── Timestamps ──
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
