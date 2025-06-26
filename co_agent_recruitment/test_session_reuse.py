#!/usr/bin/env python3
"""
Test script to verify session reuse is working correctly.
"""

import asyncio
import logging
from agent_engine import get_agent_runner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_session_reuse():
    """Test that sessions are reused correctly for the same user."""
    logger.info("🔄 Testing session reuse...")
    runner = get_agent_runner()
    
    user_id = "test_session_user"
    session_id = "test_session_reuse"
    
    # First request - should create new session
    logger.info("📝 First request - should create new session")
    response1 = await runner.run_async(
        user_id=user_id,
        query="who are you?",
        session_id=session_id
    )
    logger.info(f"First response length: {len(response1)}")
    
    # Second request - should reuse existing session
    logger.info("📝 Second request - should reuse existing session")
    response2 = await runner.run_async(
        user_id=user_id,
        query="who are you?",
        session_id=session_id
    )
    logger.info(f"Second response length: {len(response2)}")
    
    # Third request - should reuse existing session
    logger.info("📝 Third request - should reuse existing session")
    response3 = await runner.run_async(
        user_id=user_id,
        query="who are you?",
        session_id=session_id
    )
    logger.info(f"Third response length: {len(response3)}")
    
    # Test with different user but same session ID - should create new session
    logger.info("📝 Different user, same session ID - should create new session")
    response4 = await runner.run_async(
        user_id="different_user",
        query="who are you?",
        session_id=session_id
    )
    logger.info(f"Different user response length: {len(response4)}")
    
    # Test with no session ID - should create new session
    logger.info("📝 No session ID - should create new session")
    response5 = await runner.run_async(
        user_id=user_id,
        query="who are you?",
        session_id=None
    )
    logger.info(f"No session ID response length: {len(response5)}")
    
    logger.info("✅ Session reuse test completed. Check logs for 'Reusing existing session' vs 'Created session' messages.")

if __name__ == "__main__":
    asyncio.run(test_session_reuse())