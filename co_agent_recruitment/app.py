"""Main entry point for the Co-Agent Recruitment system.

This module provides both a FastAPI web interface and CLI interface for the resume parsing functionality.
"""

import asyncio
import sys
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from co_agent_recruitment.agent import parse_resume, sanitize_input


class ResumeRequest(BaseModel):
    """Request model for resume parsing."""
    resume_text: str = Field(..., description="The raw resume text to parse", max_length=50000)


class ResumeResponse(BaseModel):
    """Response model for resume parsing."""
    success: bool = Field(..., description="Whether the parsing was successful")
    data: Dict[str, Any] = Field(..., description="The parsed resume data")
    message: str = Field(default="Resume parsed successfully", description="Response message")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(default=False, description="Whether the parsing was successful")
    error: str = Field(..., description="Error message")


# Create FastAPI app instance
app = FastAPI(
    title="Co-Agent Recruitment API",
    description="API for parsing resumes and extracting structured data",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Co-Agent Recruitment API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "co-agent-recruitment"}


@app.post("/parse-resume", response_model=ResumeResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
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
        # Parse the resume
        result = await parse_resume(request.resume_text)
        
        return ResumeResponse(
            success=True,
            data=result,
            message="Resume parsed successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": f"Invalid input: {str(e)}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to parse resume"}
        )


async def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) != 2:
        print("Usage: python -m co_agent_recruitment <resume_text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        result = await parse_resume(resume_text)
        print(result)
    except Exception as e:
        print(f"Error processing resume: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())