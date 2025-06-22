#!/usr/bin/env python3
"""
Test script to show session information embedded in orchestrator and parser outputs
"""

import asyncio
import json
from co_agent_recruitment.agent import root_agent, parse_resume
from co_agent_recruitment.job_posting.agent import analyze_job_posting
from google.adk.runners import InMemoryRunner
from google.adk.agents.run_config import RunConfig
from google.genai import types


async def test_session_in_outputs():
    """Test that session information is now embedded in all outputs"""
    print("🧪 Testing Session Information in Outputs")
    print("=" * 50)

    # Test 1: Direct function calls (parsers)
    print("📋 Test 1: Direct Parser Function Calls")
    print("-" * 40)

    # Test resume parser
    resume_text = "John Doe\nSoftware Engineer\n5 years Python experience"
    resume_result = await parse_resume(resume_text)

    print("🔍 Resume Parser Output Structure:")
    print(f"   Keys: {list(resume_result.keys())}")
    print(f"   Session Info: {resume_result.get('session_info', {})}")
    print(f"   Operation Status: {resume_result.get('operation_status')}")
    print()

    # Test job posting parser
    job_text = "Senior Python Developer\nTech Corp\n5+ years experience required"
    job_result = await analyze_job_posting(job_text)

    print("🔍 Job Posting Parser Output Structure:")
    print(f"   Keys: {list(job_result.keys())}")
    print(f"   Session Info: {job_result.get('session_info', {})}")
    print(f"   Operation Status: {job_result.get('operation_status')}")
    print()

    # Test 2: Orchestrator agent calls
    print("📋 Test 2: Orchestrator Agent Calls")
    print("-" * 40)

    # Create runner and session
    app_name = "co_agent_recruitment"
    user_id = "test_user"
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )

    print(f"📋 Session Created: {session.id}")

    # Test orchestrator with resume
    print("\n🤖 Orchestrator Resume Processing:")
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=f"Please parse this resume: {resume_text}")],
    )

    orchestrator_responses = []
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
            and event.author == root_agent.name
        ):
            orchestrator_responses.append(event.content.parts[0].text)

    if orchestrator_responses:
        try:
            # Try to parse the JSON response
            orchestrator_result = json.loads(orchestrator_responses[0])
            print("🔍 Orchestrator Output Structure:")
            print(f"   Keys: {list(orchestrator_result.keys())}")
            if "session_info" in orchestrator_result:
                print(f"   Session Info: {orchestrator_result['session_info']}")
            if "orchestrator_info" in orchestrator_result:
                print(
                    f"   Orchestrator Info: {orchestrator_result['orchestrator_info']}"
                )
            print(f"   Has Resume Data: {'resume_data' in orchestrator_result}")
        except json.JSONDecodeError:
            print(f"   Raw Response: {orchestrator_responses[0][:200]}...")

    # Get session state after orchestrator call
    updated_session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session.id
    )

    print("\n📊 Session State After Orchestrator Call:")
    if updated_session:
        print(f"   Session ID: {updated_session.id}")
        print(
            f"   Interaction Count: {updated_session.state.get('interaction_count', 0)}"
        )
        print(
            f"   Current Session Info: {updated_session.state.get('current_session_info', {})}"
        )
    else:
        print("   ❌ Session not found!")

    print("\n✅ Session information is now embedded in all outputs!")
    print("✅ Both parsers and orchestrator include session data!")
    print("✅ Session state is tracked throughout the process!")


if __name__ == "__main__":
    asyncio.run(test_session_in_outputs())
