"""
Example demonstrating how to use output_key to pass data between agents.
This shows how the session state mechanism works with output_key.
"""

import asyncio
from co_agent_recruitment.agent import (
    create_resume_parser_agent,
    create_orchestrator_agent,
    get_or_create_session,
    _shared_session_service,
)
from co_agent_recruitment.job_posting.agent import create_job_posting_agent


async def demonstrate_output_key_concept():
    """Demonstrate the concept of how output_key works to pass data between agents."""

    print("=== Understanding output_key Usage ===")
    print()

    # Show the agents and their output_key settings
    resume_agent = create_resume_parser_agent()
    job_posting_agent = create_job_posting_agent()
    orchestrator_agent = create_orchestrator_agent()

    print("Agent Configuration:")
    print(f"1. Resume Parser Agent:")
    print(f"   - Name: {resume_agent.name}")
    print(f"   - output_key: 'resume_JSON'")
    print(f"   - Purpose: Stores parsed resume data in session.state['resume_JSON']")
    print()

    print(f"2. Job Posting Agent:")
    print(f"   - Name: {job_posting_agent.name}")
    print(f"   - output_key: 'job_posting_JSON'")
    print(
        f"   - Purpose: Stores analyzed job posting data in session.state['job_posting_JSON']"
    )
    print()

    print(f"3. Orchestrator Agent:")
    print(f"   - Name: {orchestrator_agent.name}")
    print(f"   - output_key: 'result'")
    print(f"   - Purpose: Stores orchestrator results in session.state['result']")
    print()

    print("=== How output_key Enables Data Flow ===")
    print()
    print("1. When resume_parser_agent completes:")
    print("   session.state['resume_JSON'] = parsed_resume_data")
    print()
    print("2. When job_posting_agent completes:")
    print("   session.state['job_posting_JSON'] = analyzed_job_data")
    print()
    print("3. Orchestrator can access this data using template variables:")
    print("   - {resume_JSON} - accesses session.state['resume_JSON']")
    print("   - {job_posting_JSON} - accesses session.state['job_posting_JSON']")
    print()

    print("=== Updated Orchestrator Instruction ===")
    print("The orchestrator instruction now includes:")
    print("- Resume data: {resume_JSON?}")
    print("- Job posting data: {job_posting_JSON?}")
    print()
    print("The '?' makes these template variables optional, so they won't cause")
    print("errors if the data hasn't been set yet. This allows the orchestrator")
    print("to gracefully handle cases where the specialized agents haven't run yet.")
    print()

    # Test session creation to show the mechanism
    print("=== Testing Session State Mechanism ===")
    session, _ = await get_or_create_session(
        "co_agent_recruitment", "test_user", session_service=_shared_session_service
    )

    # Simulate what happens when output_key is used
    session.state["resume_JSON"] = {
        "personal_details": {"full_name": "John Doe", "email": "john.doe@email.com"},
        "skills": {"technical": {"programming_languages": ["Python", "JavaScript"]}},
    }

    print(f"Session ID: {session.id}")
    print(f"Session state keys: {list(session.state.keys())}")
    print(f"resume_JSON data: {session.state.get('resume_JSON')}")
    print()

    print("=== Benefits of Using output_key ===")
    print(
        "1. Automatic Storage: Agent outputs are automatically saved to session state"
    )
    print(
        "2. Template Access: Other agents can access data using {key} syntax in instructions"
    )
    print(
        "3. Persistent State: Data persists throughout the session for multi-step workflows"
    )
    print("4. Clean Architecture: Separates data storage from business logic")


if __name__ == "__main__":
    asyncio.run(demonstrate_output_key_concept())
