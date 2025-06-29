"""
Vertex AI Agent Engine specific agent implementation.

This module provides a clean agent implementation for Vertex AI Agent Engine deployment
without Firestore session dependencies, as Vertex AI handles session management natively.
"""

import os
import logging
from typing import Any, Optional
from google.adk.agents import Agent
from co_agent_recruitment.resume_parser.agent import create_resume_parser_agent
from co_agent_recruitment.job_posting.agent import create_job_posting_agent
from co_agent_recruitment.matcher.agent import create_matcher_agent
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


def get_project_id() -> str:
    """Get Google Cloud project ID from environment variable."""
    project_id = os.getenv("PROJECT_ID", "gen-lang-client-0249131775")
    if not project_id:
        raise ValueError("PROJECT_ID environment variable not set.")
    return project_id


def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("MODEL_NAME", "gemini-2.5-flash")


def create_vertex_orchestrator_agent() -> Agent:
    """
    Create an orchestrator agent optimized for Vertex AI Agent Engine deployment.

    This agent does not use Firestore session management as Vertex AI Agent Engine
    provides its own session management capabilities.

    Returns:
        Agent: Configured agent ready for Vertex AI deployment
    """
    # Create new instances of sub-agents for Vertex AI deployment
    vertex_resume_parser = create_resume_parser_agent()
    vertex_job_posting_agent = create_job_posting_agent()
    vertex_matcher_agent = create_matcher_agent()

    return Agent(
        name="vertex_orchestrator_agent",
        model=get_model_name(),
        description=(
            "Vertex AI orchestrator agent for Co-Agent Recruitment system. "
            "Handles resume parsing, job posting analysis, and compatibility matching "
            "with native Vertex AI session management."
        ),
        instruction=(
            "You are the Co-Agent Recruitment orchestrator agent deployed on Vertex AI Agent Engine. "
            "Your role is to:\n\n"
            "1. Parse resumes and extract structured data\n"
            "2. Analyze job postings and extract requirements\n"
            "3. Generate compatibility scores between candidates and positions\n"
            "4. Return structured JSON responses for API consumption\n\n"
            "PROCESSING WORKFLOW:\n"
            "- For resume content: Extract personal info, experience, skills, education\n"
            "- For job postings: Extract requirements, responsibilities, qualifications\n"
            "- For matching requests: Calculate compatibility scores and provide insights\n\n"
            "CONTENT IDENTIFICATION:\n"
            "- Resume indicators: personal details, work experience, education, skills, contact information\n"
            "- Job posting indicators: job title, company description, requirements, responsibilities, qualifications\n\n"
            "PROCESSING WORKFLOW:\n"
            "When the user provides a RESUME:\n"
            "1. Transfer to resume_parser_agent\n"
            "2. Call parse_resume with the resume text\n"
            "3. Return the complete structured JSON\n\n"
            "When the user provides a JOB POSTING:\n"
            "1. Transfer to job_posting_agent\n"
            "2. Call analyze_job_posting with the job posting text\n"
            "3. Return the complete structured JSON\n\n"
            "When the user requests MATCHING:\n"
            "1. Transfer to matcher_agent\n"
            "2. Call generate_compatibility_score with both resume and job posting data\n"
            "3. Return the compatibility analysis\n\n"
            "RESPONSE FORMAT:\n"
            "Always return structured JSON responses suitable for API consumption. "
            "Session management is handled natively by Vertex AI Agent Engine."
        ),
        sub_agents=[
            vertex_resume_parser,
            vertex_job_posting_agent,
            vertex_matcher_agent,
        ],
        output_key="result",
        # No session callbacks - Vertex AI handles sessions natively
    )


# Create the Vertex AI specific agent
vertex_orchestrator_agent = create_vertex_orchestrator_agent()

# Export for deployment
__all__ = [
    "vertex_orchestrator_agent",
    "create_vertex_orchestrator_agent",
    "get_project_id",
    "get_model_name",
]
