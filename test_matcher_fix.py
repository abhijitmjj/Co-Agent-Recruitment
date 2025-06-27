#!/usr/bin/env python3
"""
Test script to verify the matcher agent fixes work correctly.
"""

import asyncio
import logging
from co_agent_recruitment.agent_engine import get_agent_runner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_compatibility_generation():
    """Test generating compatibility scores with the fixed matcher agent."""
    
    # Sample resume data
    resume_data = {
        "name": "John Doe",
        "skills": ["Python", "Machine Learning", "TensorFlow", "Data Analysis"],
        "experience_years": 5,
        "education": "MS Computer Science"
    }
    
    # Sample job posting data  
    job_posting_data = {
        "title": "Senior ML Engineer",
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
        "experience_required": "3-7 years",
        "education_required": "Bachelor's or Master's in CS/related field"
    }
    
    # Create the query for the matcher agent
    query = f"""Generate a compatibility score between this resume and job posting:

Resume: {resume_data}

Job Posting: {job_posting_data}

Please analyze the compatibility and provide a structured score."""

    try:
        runner = get_agent_runner()
        logger.info("Testing compatibility score generation...")
        
        response = await runner.run_async(
            user_id="test_user_matcher",
            query=query,
            session_id="test_session_matcher"
        )
        
        logger.info(f"Matcher response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error testing matcher: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    asyncio.run(test_compatibility_generation())