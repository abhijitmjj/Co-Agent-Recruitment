"""Main entry point for the Co-Agent Recruitment system.

This module provides both a FastAPI web interface and CLI interface for the resume parsing functionality.
"""

import asyncio
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from co_agent_recruitment.agent import parse_resume, sanitize_input
from co_agent_recruitment.json_agents import (
    parse_resume_json,
    analyze_job_posting_json,
    process_document_json,
)


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


# Create FastAPI app instance
app = FastAPI(
    title="Co-Agent Recruitment API",
    description="API for parsing resumes and extracting structured data",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to process document"},
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
