"""
Standalone FastAPI server for testing the JSON agents.
This bypasses any environment issues with the main app.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from co_agent_recruitment.json_agents import (
    parse_resume_json,
    analyze_job_posting_json,
    process_document_json,
)


# Request models
class DocumentRequest(BaseModel):
    """Request model for unified document processing."""

    document_text: str = Field(
        ..., description="The raw document text to process", max_length=50000
    )
    document_type: str = Field(
        default="auto",
        description="Type of document: 'resume', 'job_posting', or 'auto' for auto-detection",
    )


class JobPostingRequest(BaseModel):
    """Request model for job posting analysis."""

    job_posting_text: str = Field(
        ..., description="The raw job posting text to analyze", max_length=50000
    )


class ResumeRequest(BaseModel):
    """Request model for resume parsing."""

    resume_text: str = Field(
        ..., description="The raw resume text to parse", max_length=50000
    )


# Response models
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
        default=False, description="Whether the processing was successful"
    )
    error: str = Field(..., description="Error message")


# Create FastAPI app
app = FastAPI(
    title="Co-Agent Recruitment JSON API",
    description="Standalone API for testing resume parsing and job posting analysis with guaranteed JSON output",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Co-Agent Recruitment JSON API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/process-document",
            "/analyze-job-posting",
            "/parse-resume",
            "/docs",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "co-agent-recruitment-json"}


@app.post(
    "/process-document",
    response_model=DocumentResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def process_document_endpoint(request: DocumentRequest):
    """
    Process a document (resume or job posting) with auto-detection or explicit type.

    This is the main endpoint that handles both resumes and job postings.
    """
    try:
        print(f"📄 Processing document: {request.document_text[:100]}...")
        print(f"🔍 Document type: {request.document_type}")

        # Use the unified document processing function
        result = await process_document_json(
            request.document_text, request.document_type
        )

        print(f"✅ Processing result: {result.get('success', True)}")

        # Check if there was an error in the result
        if isinstance(result, dict) and "error" in result:
            print(f"❌ Error in processing: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": result["error"]},
            )

        response = DocumentResponse(
            success=result.get("success", True),
            document_type=result.get("document_type", "unknown"),
            data=result.get("data", {}),
            detection_confidence=result.get("detection_confidence"),
            message="Document processed successfully",
        )

        print(f"📋 Returning response for {response.document_type}")
        return response

    except ValueError as e:
        print(f"❌ ValueError: {e}")
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": f"Invalid input: {str(e)}"},
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Exception: {e}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to process document"},
        )


@app.post("/analyze-job-posting")
async def analyze_job_posting_endpoint(request: JobPostingRequest):
    """Analyze a job posting and return structured JSON data."""
    try:
        result = await analyze_job_posting_json(request.job_posting_text)

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": result["error"]},
            )

        return {
            "success": True,
            "data": result,
            "message": "Job posting analyzed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to analyze job posting"},
        )


@app.post("/parse-resume")
async def parse_resume_endpoint(request: ResumeRequest):
    """Parse a resume and return structured JSON data."""
    try:
        result = await parse_resume_json(request.resume_text)

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "error": result["error"]},
            )

        return {
            "success": True,
            "data": result,
            "message": "Resume parsed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to parse resume"},
        )


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting standalone Co-Agent Recruitment JSON API server...")
    print("📋 Available endpoints:")
    print("  - POST /process-document (main endpoint)")
    print("  - POST /analyze-job-posting")
    print("  - POST /parse-resume")
    print("  - GET /docs (API documentation)")
    print("  - GET /health")
    print()
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs will be available at: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
