#!/usr/bin/env python3
"""Test script to verify resume parsing with proper session management."""

import asyncio
import logging
from agent_engine import OrchestratorAgentRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_resume_parsing():
    """Test resume parsing with session management."""
    logger.info("🔄 Testing resume parsing with session management...")
    
    # Create agent engine
    engine = OrchestratorAgentRunner()

    # Test resume text
    resume_text = """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    
    EXPERIENCE:
    Senior Software Engineer at Tech Corp (2020-2024)
    - Developed web applications using Python and React
    - Led a team of 5 developers
    - Implemented CI/CD pipelines
    
    EDUCATION:
    Bachelor of Science in Computer Science
    University of Technology (2016-2020)
    
    SKILLS:
    Python, JavaScript, React, Docker, AWS
    """
    
    # Test with session ID
    session_id = "resume_test_session_123"
    user_id = "test_user_resume"
    
    logger.info("📝 First resume parsing request")
    response1 = await engine.run_async(
        user_id=user_id,
        session_id=session_id,
        query=f"parse this: {resume_text}"
    )
    logger.info(f"First response length: {len(response1)}")
    
    logger.info("📝 Second resume parsing request (same session)")
    response2 = await engine.run_async(
        user_id=user_id,
        session_id=session_id,
        query=f"parse this: {resume_text}"
    )
    logger.info(f"Second response length: {len(response2)}")
    
    logger.info("✅ Resume parsing test completed. Check logs for interaction counts.")

if __name__ == "__main__":
    asyncio.run(test_resume_parsing())