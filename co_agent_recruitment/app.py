"""Main entry point for the Co-Agent Recruitment system.

This module provides both a FastAPI web interface and CLI interface for the resume parsing functionality.
"""

import asyncio
import sys
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
from pydantic import BaseModel, Field
# parse_resume is not directly used by endpoints, parse_resume_json is used.
# from co_agent_recruitment.agent import parse_resume 
from co_agent_recruitment.json_agents import (
    parse_resume_json, # Ensured this is imported for main()
    analyze_job_posting_json,
    process_document_json, 
)
# Added import for get_agent_runner
from co_agent_recruitment.agent_engine import get_agent_runner
from co_agent_recruitment.agent import root_agent, get_or_create_session_for_user, _shared_session_service, sanitize_input
# Added import for pubsub
from co_agent_recruitment.tools.pubsub import emit_event
import dotenv
import json # Import the json module

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
dotenv.load_dotenv()
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


class OrchestratorRequest(BaseModel):
    """Request model for the orchestrator agent."""

    text: str = Field(
        ...,
        description="The text to be processed by the orchestrator agent",
        max_length=50000,
    )
    user_id: str = Field(..., description="User identifier for session management")
    session_id: Optional[str] = Field(
        None, description="Existing session ID (optional)"
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
    document_type: Optional[str] = Field(None, description="Detected or specified document type") # Made Optional
    data: Optional[Dict[str, Any]] = Field(None, description="The processed document data") # Made Optional
    detection_confidence: Optional[Dict[str, Any]] = Field(
        default=None, description="Auto-detection confidence scores (if applicable)"
    )
    message: str = Field(
        default="Document processed successfully", description="Response message"
    )
    # Added field for direct agent string response for the /orchestrator endpoint
    agent_response: Optional[str] = Field(None, description="Direct string response from the agent")


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

# Add CORS middleware
# TODO: For production, restrict origins to your actual frontend domain(s)
origins = [
    "http://localhost:3000",  # Common Next.js dev origin
    "http://127.0.0.1:3000",
    # Add any other origins your frontend might be served from during development or production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allows cookies to be included in cross-origin requests
    allow_methods=["GET", "POST", "OPTIONS"], # Crucially, OPTIONS must be allowed for preflight
    allow_headers=["Content-Type", "accept", "Authorization"], # Add other headers your frontend might send
)


'''@app.post("/orchestrate/", response_model=Dict[str, Any])  # This is the existing /orchestrate/ endpoint
async def orchestrate_document_endpoint(request: OrchestratorRequest):
    """
    Processes a document (resume or job posting) using the orchestrator agent.
    Manages session and returns a comprehensive JSON response from the agent.
    """
    #add logger
    print(f"Inside orchestrate_document_endpoint with request: {request}")
      
    # Sanitize input text to prevent injection attacks
    sanitized_text = sanitize_input(request.text)   
    if not sanitized_text:
        raise HTTPException(
            status_code=400, detail="Input text cannot be empty or invalid."
        )
    
    print(f"request.session_id :{request.session_id}")  # Log first 100 chars for brevity
    try:
        # Get or create the session ID
        actual_session_id = await get_or_create_session_for_user(
            user_id=request.user_id, session_id=request.session_id
        )
        print(f"session id {actual_session_id}")
      
   
        # Retrieve the actual Session object using the session ID
        session_object = await _shared_session_service.get_session(
            app_name="co_agent_recruitment", # Consistent with app_name used in agent.py
            user_id=request.user_id,    
            session_id=actual_session_id
        )


        if not session_object:
            # This case should ideally not happen if get_or_create_session_for_user works correctly
            # and _shared_session_service is consistent.
            print(f"Error: Could not retrieve session object for session_id: {actual_session_id}")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve session object."
            )

        print(f"Calling root_agent.run with session_id: {session_object.id}")
    
        # Call root_agent.run with the Session object and sanitized user input
        raw_agent_response = await root_agent.run(
            session=session_object,
            user_input=sanitized_text,
        )
        
        print(f"Raw agent response: {raw_agent_response}")
        
        # Ensure the response is a dictionary before checking for output_key
        if not isinstance(raw_agent_response, dict):
            print(
                f"Error: Agent response is not a dictionary. Type: {type(raw_agent_response)}"
            )
            # Attempt to provide more context from the agent's instruction if it's a string
            error_detail = "Agent returned an unexpected response format."
            if isinstance(raw_agent_response, str):
                error_detail = f"Agent returned a string, expected a dictionary. Agent output: {raw_agent_response[:200]}..."
            
            # Check if the orchestrator agent's instruction mentions a specific output structure
            # This part is more for debugging insight; the actual fix is in the agent's return value
            agent_instruction = getattr(root_agent, 'instruction', '')
            if "Example response format:" in agent_instruction or "output_key" in agent_instruction:
                 print(f"Hint: Orchestrator agent instruction mentions specific output format. Review agent's instruction and implementation.")

            raise HTTPException(
                status_code=500,
                detail=error_detail,
            )

        if root_agent.output_key not in raw_agent_response:
            print(
                f"Error: Agent response missing output key '{root_agent.output_key}'. Available keys: {list(raw_agent_response.keys())}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Agent response did not contain expected output key '{root_agent.output_key}'.",
            )

        final_response_data = raw_agent_response[root_agent.output_key]
        return final_response_data

    except ValueError as ve:
        # Log the exception for debugging if needed
        # print(f"Validation error in /orchestrate endpoint: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        # Re-raise HTTPExceptions directly
        raise he
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in /orchestrate endpoint: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}"
        )'''


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

'''
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
        )'''

@app.post(
    "/orchestrator", 
    response_model=DocumentResponse, 
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def orchestrator_endpoint(request: OrchestratorRequest): # Changed request model to OrchestratorRequest
    """
    Processes text using the OrchestratorAgentRunner and returns its string response.
    """
    try:
        runner = get_agent_runner() # Get the OrchestratorAgentRunner instance
        
        # Call the runner's run_async method
        agent_response_str = await runner.run_async(
            user_id=request.user_id,
            query=request.text, # 'text' from OrchestratorRequest maps to 'query' for run_async
            session_id=request.session_id
        )

        logger.info(f"\\n--- Agent Response ---\\n{agent_response_str}")
        #trigger event
        await emit_event(name="TestEvent1", payload={"response": agent_response_str})
      
        # The OrchestratorAgentRunner returns a string.
        # We adapt it to the DocumentResponse model,
        # placing the string in the 'agent_response' field.
        return DocumentResponse(
            success=True,
            agent_response=agent_response_str, # Populate the new field
            message="Text processed successfully by orchestrator agent."
            # document_type, data, detection_confidence will be None by default as they are Optional
        )

    except HTTPException as he:
        # Re-raise HTTPExceptions directly
        raise he
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in /orchestrator endpoint: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {type(e).__name__}"
        )

async def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) != 2:
        print("Usage: python -m co_agent_recruitment <resume_text_file>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            resume_text = f.read()

        result = await parse_resume_json(resume_text)
        print(result)
    except Exception as e:
        print(f"Error processing resume: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
