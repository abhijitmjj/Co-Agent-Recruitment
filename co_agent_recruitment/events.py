"""
Defines the data contracts (Pydantic models) for events used in Pub/Sub.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .resume_parser.agent import Resume
from .job_posting.agent import JobPosting
from .matcher.agent import CompatibilityScore


class EventPayload(BaseModel):
    """Base model for all event payloads."""
    user_id: str = Field(..., description="The user ID associated with the event.")
    session_id: str = Field(..., description="The session ID associated with the event.")

class ParseResumeEvent(EventPayload):
    """Payload for when a resume has been parsed."""
    resume_data: Resume = Field(..., description="The structured resume data.")

class ParseJobPostingEvent(EventPayload):
    """Payload for when a job posting has been analyzed."""
    job_posting_data: JobPosting = Field(..., description="The structured job posting data.")

class CompatibilityScoreEvent(EventPayload):
    """Payload for when a compatibility score has been generated."""
    compatibility_data: CompatibilityScore = Field(..., description="The compatibility score data.")
