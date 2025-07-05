"""Main entry point for the Co-Agent Recruitment system.

This module provides both a FastAPI web interface and CLI interface for the resume parsing functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from co_agent_recruitment.agent import parse_resume
from co_agent_recruitment.matcher.json_matcher import generate_compatibility_score_json
from co_agent_recruitment.tools.pubsub import emit_event
from co_agent_recruitment.agent_engine import get_agent_runner
from co_agent_recruitment.utils import clean_text_to_ascii
import uvicorn

class ResumeRequest(BaseModel):
    """Request model for resume parsing."""

    resume_text: str = Field(
        ..., description="The raw resume text to parse", max_length=50000
    )


class JobPostingRequest(BaseModel):
    """Request model for job posting analysis."""

    job_posting_text: str = Field(
        ..., description="The raw job posting text to analyze", max_length=50000
    )


class DocumentRequest(BaseModel):
    """Request model for unified document processing."""

    document_text: str = Field(
        ..., description="The raw document text to process", max_length=50000
    )
    document_type: str = Field(
        default="auto",
        description="Type of document: 'resume', 'job_posting', or 'auto' for auto-detection",
    )


class ResumeResponse(BaseModel):
    """Response model for resume parsing."""

    success: bool = Field(..., description="Whether the parsing was successful")
    data: Dict[str, Any] = Field(..., description="The parsed resume data")
    message: str = Field(
        default="Resume parsed successfully", description="Response message"
    )


class JobPostingResponse(BaseModel):
    """Response model for job posting analysis."""

    success: bool = Field(..., description="Whether the analysis was successful")
    data: Dict[str, Any] = Field(..., description="The analyzed job posting data")
    message: str = Field(
        default="Job posting analyzed successfully", description="Response message"
    )


class DocumentResponse(BaseModel):
    """Response model for unified document processing."""

    success: bool = Field(..., description="Whether the processing was successful")
    document_type: str = Field(..., description="Detected or specified document type")
    data: Dict[str, Any] = Field(..., description="The processed document data")
    detection_confidence: Optional[Dict[str, Any]] = Field(
        default=None, description="Auto-detection confidence scores (if applicable)"
    )
    message: str = Field(
        default="Document processed successfully", description="Response message"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(
        default=False, description="Whether the parsing was successful"
    )
    error: str = Field(..., description="Error message")


class EventRequest(BaseModel):
    """Request model for publishing an event."""

    event_name: str = Field(..., description="The name of the event to publish")
    payload: Dict[str, Any] = Field(..., description="The event payload")


class OrchestratorRequest(BaseModel):
    """Request model for the orchestrator agent."""

    query: str = Field(..., description="The query to send to the orchestrator agent")
    user_id: str = Field(..., description="The user ID for the session")
    session_id: Optional[str] = Field(None, description="The session ID to use")


class MatcherRequest(BaseModel):
    """Request model for the matcher agent."""

    resume_data: Dict[str, Any] = Field(..., description="Structured resume data")
    job_posting_data: Dict[str, Any] = Field(
        ..., description="Structured job posting data"
    )


class MatcherResponse(BaseModel):
    """Response model for the matcher agent."""

    success: bool
    data: Dict[str, Any]
    message: str


# Create FastAPI app instance
app = FastAPI(
    title="Co-Agent Recruitment API",
    description="API for parsing resumes and extracting structured data",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS configuration
allowed_origins_str = os.getenv("CORS_ALLOWED_ORIGINS")
allowed_origin_regex = os.getenv("CORS_ALLOWED_ORIGIN_REGEX")

# Initialize with default values
cors_args: Dict[str, Any] = {
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
}

if allowed_origin_regex:
    # Use regex if provided
    cors_args["allow_origin_regex"] = allowed_origin_regex
elif allowed_origins_str:
    # Use the list of origins if provided
    cors_args["allow_origins"] = allowed_origins_str.split(",")
else:
    # Fallback to a default for local development
    cors_args["allow_origins"] = ["http://localhost:3000"]
    # allow all connections from https://a2a-githubaction--gen-lang-client-0249131775.us-central1.hosted.app/ and children
    cors_args["allow_origin_regex"] = r"https://a2a-githubaction--gen-lang-client-0249131775\.us-central1\.hosted\.app(/?.*)?$"


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore
    **cors_args,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Co-Agent Recruitment API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "co-agent-recruitment"}


@app.post("/publish-event")
async def publish_event_endpoint(request: EventRequest):
    """
    Publish an event to the Pub/Sub topic.
    """
    try:
        message_id = await emit_event(request.event_name, request.payload)
        return {"success": True, "message_id": message_id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Failed to publish event: {str(e)}"},
        )


@app.post("/orchestrator")
async def orchestrator_endpoint(request: OrchestratorRequest):
    """
    Route a query to the orchestrator agent.
    """
    try:
        runner = get_agent_runner()
        response = await runner.run_async(
            user_id=request.user_id,
            query=clean_text_to_ascii(request.query or "") or "",
            session_id=request.session_id,
        )
        return {"success": True, "response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Failed to run orchestrator: {str(e)}"},
        )


@app.post(
    "/generate-score",
    response_model=MatcherResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def generate_score_endpoint(request: MatcherRequest):
    """
    Generate a compatibility score between a resume and a job posting.
    """
    try:
        result = await generate_compatibility_score_json(
            request.resume_data, request.job_posting_data
        )

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": result["error"]},
            )

        return MatcherResponse(
            success=True,
            data=result,
            message="Compatibility score generated successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": f"Failed to generate score: {str(e)}",
            },
        )


# async def main():
#     """Main entry point for CLI usage."""
#     if len(sys.argv) != 2:
#         print("Usage: python -m co_agent_recruitment <resume_text_file>")
#         sys.exit(1)

#     try:
#         with open(sys.argv[1], "r", encoding="utf-8") as f:
#             resume_text = f.read()

#         result = await parse_resume(resume_text)
#         print(result)
#     except Exception as e:
#         print(f"Error processing resume: {e}")
#         sys.exit(1)


if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
