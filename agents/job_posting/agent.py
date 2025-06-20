"""Job Posting Analysis ADK Agent implementation."""

import os
import sys
import datetime
from typing import Any

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from google.adk.agents import Agent
from co_agent_recruitment.job_posting.agent import analyze_job_posting
from co_agent_recruitment.agent import get_model_name

def get_job_posting_agent() -> Agent:
    """Create and return the job posting analysis agent for ADK."""
    model_name = get_model_name()
    
    return Agent(
        name="job_posting_analyzer",
        model=model_name,
        description="Expert AI agent for analyzing job posting text and extracting structured information about requirements, responsibilities, and company details.",
        instruction=(
            "You are an expert AI job posting analyzer. Your task is to analyze job posting text "
            "and extract structured information including job requirements, responsibilities, "
            "company information, salary details, and other relevant job-related data.\n\n"
            "When a user provides job posting text, call the analyze_job_posting function to process it. "
            "Return the structured JSON data with comprehensive job analysis.\n\n"
            "Always provide helpful, accurate analysis results and include relevant metadata."
        ),
        tools=[analyze_job_posting],
        output_key="analyzed_job_posting",
    )

# Create the agent instance for ADK discovery
agent = get_job_posting_agent()
root_agent = agent  # ADK looks for root_agent