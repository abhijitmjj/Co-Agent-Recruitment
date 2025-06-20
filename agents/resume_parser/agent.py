"""Resume Parser ADK Agent implementation."""

import os
import sys
import datetime
from typing import Any

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from google.adk.agents import Agent
from co_agent_recruitment.agent import parse_resume, get_model_name

def get_resume_parser_agent() -> Agent:
    """Create and return the resume parser agent for ADK."""
    model_name = get_model_name()
    
    return Agent(
        name="resume_parser",
        model=model_name,
        description="Expert AI agent for parsing unstructured resume text and transforming it into structured JSON data suitable for Applicant Tracking Systems (ATS).",
        instruction=(
            "You are an expert AI resume parser. Your task is to transform unstructured resume text "
            "into a single, structured, and comprehensive JSON object suitable for a modern Applicant "
            "Tracking System (ATS). Only extract information explicitly present in the text.\n\n"
            "When a user provides resume text, call the parse_resume function to process it. "
            "Return the structured JSON data with session information included.\n\n"
            "Always provide helpful, accurate parsing results and include session metadata."
        ),
        tools=[parse_resume],
        output_key="parsed_resume",
    )

# Create the agent instance for ADK discovery
agent = get_resume_parser_agent()
root_agent = agent  # ADK looks for root_agent