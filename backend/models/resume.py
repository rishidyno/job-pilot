"""
JOBPILOT — Resume & Cover Letter Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from utils.helpers import utc_now


class Resume(BaseModel):
    """Resume document as stored in MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = Field(None, description="Owner user ID")

    is_base: bool = Field(False, description="True = original resume, False = tailored")
    job_id: Optional[str] = Field(None, description="Job this was tailored for")
    base_resume_id: Optional[str] = Field(None, description="Reference to base resume")

    # Content
    raw_text: Optional[str] = Field(None, description="Plain text extracted from PDF")
    content_json: Optional[dict] = Field(None, description="AI-tailored structured content")

    # Generated PDFs
    file_path_original_style: Optional[str] = Field(None, description="PDF in original format")
    file_path_clean_style: Optional[str] = Field(None, description="PDF in clean template")

    # AI metadata
    ai_model_used: Optional[str] = None
    changes_made: Optional[list] = Field(None, description="List of changes AI made")

    created_at: datetime = Field(default_factory=utc_now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CoverLetter(BaseModel):
    """Cover letter document as stored in MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = Field(None, description="Owner user ID")

    job_id: str
    content: str = Field(..., description="Full cover letter text")
    file_path: Optional[str] = None
    tone: str = Field("professional")

    created_at: datetime = Field(default_factory=utc_now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
