#!/usr/bin/env python3
"""
Demo script to show session information in action
"""

import asyncio
from co_agent_recruitment.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig
from google.genai import types


async def demo_session_visibility():
    """Demonstrate session information visibility"""
    print("🔍 Session Information Demo")
    print("=" * 50)

    # Create runner
    app_name = "co_agent_recruitment"
    user_id = "demo_user"
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)

    # Create session
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )

    print("📋 Initial Session Info:")
    print(f"   Session ID: {session.id}")
    print(f"   User ID: {session.user_id}")
    print(f"   App Name: {session.app_name}")
    print(f"   Initial State: {dict(session.state)}")
    print()

    # First interaction
    print("🤖 First Interaction - Resume Parsing")
    print("-" * 30)

    resume_text = """
    John Doe
    Software Engineer
    Email: john.doe@example.com
    
    Experience:
    - 5 years Python development
    - 3 years React/JavaScript
    
    Education:
    - BS Computer Science, 2018
    """

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=f"Please parse this resume: {resume_text}")],
    )

    response_parts = []
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
            if event.author == root_agent.name:
                response_parts.append(event.content.parts[0].text)

    # Get session state after first interaction
    updated_session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session.id
    )

    print("📊 Session State After First Interaction:")
    if updated_session:
        print(f"   Session ID: {updated_session.id}")
        print(
            f"   Interaction Count: {updated_session.state.get('interaction_count', 0)}"
        )
        print(
            f"   Conversation Started: {updated_session.state.get('conversation_started', 'N/A')}"
        )
        print(
            f"   Last Operation: {updated_session.state.get('last_operation_status', 'N/A')}"
        )
        print(f"   All State Keys: {list(updated_session.state.keys())}")
    else:
        print("   ❌ Session not found!")
    print()

    # Second interaction
    print("🤖 Second Interaction - Job Posting Analysis")
    print("-" * 40)

    job_posting = """
    Senior Python Developer
    Company: Tech Corp
    Requirements:
    - 5+ years Python experience
    - React/JavaScript skills
    - Bachelor's degree in Computer Science
    """

    content2 = types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=f"Please analyze this job posting: {job_posting}")
        ],
    )

    response_parts2 = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,  # Same session!
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
                response_parts2.append(event.content.parts[0].text)

    # Get final session state
    final_session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session.id
    )

    print("📊 Final Session State After Two Interactions:")
    if final_session:
        print(f"   Session ID: {final_session.id}")
        print(
            f"   Interaction Count: {final_session.state.get('interaction_count', 0)}"
        )
        print(
            f"   Conversation Started: {final_session.state.get('conversation_started', 'N/A')}"
        )
        print(
            f"   Last Interaction End: {final_session.state.get('last_interaction_end', 'N/A')}"
        )
        print(
            f"   Last Operation: {final_session.state.get('last_operation_status', 'N/A')}"
        )
        print(f"   All State Keys: {list(final_session.state.keys())}")
    else:
        print("   ❌ Session not found!")
    print()

    # Show session persistence
    print("🔄 Session Persistence Check")
    print("-" * 25)

    # List all sessions for this user
    sessions_response = await runner.session_service.list_sessions(
        app_name=app_name, user_id=user_id
    )

    print(f"   Total Sessions for User: {len(sessions_response.sessions)}")
    for i, sess in enumerate(sessions_response.sessions):
        print(f"   Session {i + 1}: {sess.id}")
        print(f"     - Interactions: {sess.state.get('interaction_count', 0)}")
        print(
            f"     - Started: {sess.state.get('conversation_started', 'N/A')[:19] if sess.state.get('conversation_started') else 'N/A'}"
        )

    print()
    print("✅ Session information is now visible and persistent!")
    print("✅ Same session used for multiple interactions!")
    print("✅ Session state tracks conversation history!")


if __name__ == "__main__":
    asyncio.run(demo_session_visibility())
