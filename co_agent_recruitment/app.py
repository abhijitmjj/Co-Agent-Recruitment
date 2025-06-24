"""Main entry point for the Co-Agent Recruitment system.

This module provides both a FastAPI web interface and CLI interface for the resume parsing functionality.
"""

import asyncio
import sys
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .agent import parse_resume
from .json_agents import (
    parse_resume_json,
    analyze_job_posting_json,
    process_document_json,
)
from .matcher.json_matcher import generate_compatibility_score_json
from .tools.pubsub import emit_event
from .agent_engine import get_agent_runner


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

class OrchestratorResponse(BaseModel):
    """Response model for the orchestrator agent, expecting a dictionary which is the parsed JSON from agent."""
    success: bool = Field(..., description="Indicates if the orchestrator call was successful.")
    response: Dict[str, Any] = Field(..., description="The structured JSON response from the orchestrator agent.")
    error: Optional[str] = Field(None, description="Error message if the call failed.")


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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Co-Agent Recruitment API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "co-agent-recruitment"}


@app.post(
    "/parse-resume",
    response_model=ResumeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def parse_resume_endpoint(request: ResumeRequest):
    """
    Parse a resume from raw text and return structured data.

    Args:
        request: ResumeRequest containing the resume text

    Returns:
        ResumeResponse with parsed resume data

    Raises:
        HTTPException: If parsing fails or input is invalid
    """
    try:
        # Use the JSON-focused function to ensure proper JSON output
        result = await parse_resume_json(request.resume_text)

        # Check if there was an error in the result
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": result["error"]},
            )

        return ResumeResponse(
            success=True, data=result, message="Resume parsed successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": f"Invalid input: {str(e)}"},
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to parse resume"},
        )


@app.post(
    "/analyze-job-posting",
    response_model=JobPostingResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def analyze_job_posting_endpoint(request: JobPostingRequest):
    """
    Analyze a job posting from raw text and return structured data.

    Args:
        request: JobPostingRequest containing the job posting text

    Returns:
        JobPostingResponse with analyzed job posting data

    Raises:
        HTTPException: If analysis fails or input is invalid
    """
    try:
        # Use the JSON-focused function to ensure proper JSON output
        result = await analyze_job_posting_json(request.job_posting_text)

        # Check if there was an error in the result
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": result["error"]},
            )

        return JobPostingResponse(
            success=True, data=result, message="Job posting analyzed successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": f"Invalid input: {str(e)}"},
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to analyze job posting"},
        )


@app.post(
    "/process-document",
    response_model=DocumentResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def process_document_endpoint(request: DocumentRequest):
    """
    Process a document (resume or job posting) with auto-detection or explicit type.

    Args:
        request: DocumentRequest containing the document text and optional type

    Returns:
        DocumentResponse with processed document data

    Raises:
        HTTPException: If processing fails or input is invalid
    """
    try:
        # Use the unified document processing function
        result = await process_document_json(
            request.document_text, request.document_type
        )

        # Check if there was an error in the result
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": result["error"]},
            )

        return DocumentResponse(
            success=result.get("success", True),
            document_type=result.get("document_type", "unknown"),
            data=result.get("data", {}),
            detection_confidence=result.get("detection_confidence"),
            message="Document processed successfully",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": f"Invalid input: {str(e)}"},
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to process document"},
        )


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
            query=request.query,
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


async def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) != 2:
        print("Usage: python -m co_agent_recruitment <resume_text_file>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            resume_text = f.read()

        result = await parse_resume(resume_text)
        print(result)
    except Exception as e:
        print(f"Error processing resume: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
