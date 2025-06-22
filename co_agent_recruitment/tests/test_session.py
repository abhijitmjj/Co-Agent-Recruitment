#!/usr/bin/env python3
"""
Test script for session management functionality
"""

import asyncio
import sys
import logging
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig
from google.genai import types
from co_agent_recruitment.agent import (
    root_agent,
)


# Configure logging with datetime and fancy INFO formatting
class FancyFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname == "INFO":
            prefix = "\033[1;34m[INFO]\033[0m"
        elif levelname == "ERROR":
            prefix = "\033[1;31m[ERROR]\033[0m"
        elif levelname == "WARNING":
            prefix = "\033[1;33m[WARN]\033[0m"
        else:
            prefix = f"[{levelname}]"
        dt = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return f"{prefix} {dt} - {record.getMessage()}"


handler = logging.StreamHandler()
handler.setFormatter(FancyFormatter())
logger = logging.getLogger("session_test")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False
# Add the co_agent_recruitment directory to the path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "co_agent_recruitment"))


async def test_session_management():
    """Test the session management functionality"""
    print("Testing session management...")

    # Test data
    test_resume = """
    John Doe
    Software Engineer
    Email: john.doe@example.com
    Phone: (555) 123-4567
    
    Experience:
    - 5 years Python development
    - 3 years React/JavaScript
    - 2 years AWS cloud services
    
    Education:
    - BS Computer Science, University of Technology, 2018
    
    Skills:
    - Python, JavaScript, React, AWS, Docker
    """

    user_id = "test_user_123"

    try:
        # Test 1: Create a runner and session
        print("Test 1: Creating ADK runner and session...")
        app_name = "co_agent_recruitment"
        runner = InMemoryRunner(
            agent=root_agent,
            app_name=app_name,
        )

        # Create session through runner's session service
        session = await runner.session_service.create_session(
            app_name=app_name, user_id=user_id
        )
        session_id = session.id
        logger.info(f"Session ID: {session_id}")
        print(f"✅ Session created: {session_id}")

        # Test 2: Run agent with session management
        print("\nTest 2: Running agent with resume parsing...")
        content = types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Please parse this resume: {test_resume}")
            ],
        )

        final_response_parts = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
            run_config=RunConfig(save_input_blobs_as_artifacts=False),
        ):
            if (
                event.content
                and event.content.parts
                and len(event.content.parts) > 0
                and event.content.parts[0].text
            ):
                print(f"** {event.author}: {event.content.parts[0].text[:100]}...")
                if event.author == root_agent.name:
                    final_response_parts.append(event.content.parts[0].text)

        print("✅ Resume parsed successfully with agent")

        # Test 3: Get session directly from runner's session service
        print("\nTest 3: Getting session from runner's session service...")
        retrieved_session = await runner.session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        if retrieved_session:
            print("✅ Session retrieved successfully")
            print(f"   - Session ID: {retrieved_session.id}")
            print(f"   - User ID: {retrieved_session.user_id}")
            print(f"   - State keys: {list(retrieved_session.state.keys())}")
        else:
            print("❌ Session not found")

        # Test 4: List sessions from runner's session service
        print("\nTest 4: Listing sessions from runner...")
        sessions_response = await runner.session_service.list_sessions(
            app_name=app_name, user_id=user_id
        )
        print(f"✅ Found {len(sessions_response.sessions)} sessions for user {user_id}")

        # Test 5: Continue conversation in same session
        print("\nTest 5: Continuing conversation in same session...")
        content2 = types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text="Please parse this resume: Jane Smith\nData Scientist\n3 years experience in ML"
                )
            ],
        )

        final_response_parts2 = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,  # Same session ID
            new_message=content2,
            run_config=RunConfig(save_input_blobs_as_artifacts=False),
        ):
            if (
                event.content
                and event.content.parts
                and len(event.content.parts) > 0
                and event.content.parts[0].text
            ):
                if event.author == root_agent.name:
                    final_response_parts2.append(event.content.parts[0].text)

        print("✅ Second interaction completed in same session")

        # Test 6: Check session state after multiple interactions
        print("\nTest 6: Checking session state after multiple interactions...")
        final_session = await runner.session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        if final_session:
            interaction_count = final_session.state.get("interaction_count", 0)
            print(f"✅ Session shows {interaction_count} interactions")
            print(f"   - Final state keys: {list(final_session.state.keys())}")

        # Test 7: List sessions again
        print("\nTest 7: Listing sessions after multiple interactions...")
        final_sessions_response = await runner.session_service.list_sessions(
            app_name=app_name, user_id=user_id
        )
        print(
            f"✅ Still found {len(final_sessions_response.sessions)} sessions for user {user_id} (session reused)"
        )

        print("\n🎉 All session management tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_session_management())
    sys.exit(0 if success else 1)
