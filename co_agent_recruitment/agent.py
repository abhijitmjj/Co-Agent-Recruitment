from typing import Any
import datetime
import os
import logging  # Add logging import
from typing import Optional
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.sessions.session import Session
from google.adk.agents.callback_context import CallbackContext
from .job_posting.agent import job_posting_agent
from .resume_parser.agent import (
    parse_resume,
    parse_resume_agent,
    sanitize_input,
)
from .matcher.agent import matcher_agent
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("MODEL_ID", "gemini-2.5-flash")


async def orchestrator_before_callback(callback_context: CallbackContext) -> None:
    """Callback for orchestrator agent before execution."""
    if not isinstance(callback_context, CallbackContext):
        return

    # Check if this is a new conversation or continuing one
    if "conversation_started" not in callback_context.state:
        callback_context.state["conversation_started"] = (
            datetime.datetime.now().isoformat()
        )
        callback_context.state["interaction_count"] = 0
        logger.info(
            f"New orchestrator conversation started for user: {callback_context._invocation_context.session.user_id}"
        )

    # Track orchestrator session interactions
    callback_context.state["interaction_count"] = (
        callback_context.state.get("interaction_count", 0) + 1
    )
    callback_context.state["last_interaction_start"] = (
        datetime.datetime.now().isoformat()
    )

    # Store session info for inclusion in response
    callback_context.state["current_session_info"] = {
        "session_id": callback_context._invocation_context.session.id,
        "user_id": callback_context._invocation_context.session.user_id,
        "interaction_number": callback_context.state["interaction_count"],
        "conversation_started": callback_context.state["conversation_started"],
        "interaction_start_time": callback_context.state["last_interaction_start"],
    }

    logger.info(
        f"Orchestrator interaction #{callback_context.state['interaction_count']} started for user: {callback_context._invocation_context.session.user_id}"
    )


async def orchestrator_after_callback(callback_context: CallbackContext) -> None:
    """Callback for orchestrator agent after execution."""
    if not isinstance(callback_context, CallbackContext):
        return

    # Update orchestrator session state
    callback_context.state["last_interaction_end"] = datetime.datetime.now().isoformat()
    callback_context.state["last_interaction_completed"] = True

    # Store completion status in session for future reference
    callback_context.state["last_operation_status"] = "completed"

    # Update session info with completion details
    if "current_session_info" in callback_context.state:
        callback_context.state["current_session_info"]["interaction_end_time"] = (
            callback_context.state["last_interaction_end"]
        )
        callback_context.state["current_session_info"]["status"] = "completed"
        callback_context.state["session_id"] = (
            callback_context._invocation_context.session.id
        )

    logger.info(
        f"Orchestrator interaction #{callback_context.state.get('interaction_count', 0)} completed for user: {callback_context._invocation_context.session.user_id} on session {callback_context._invocation_context.session.id}"
    )


def create_orchestrator_agent() -> Agent:
    """Create an orchestrator agent that manages the resume parsing and job posting agents with session management."""
    instruction_text = (
        "You are an orchestrator agent. Your primary role is to call specialized sub-agents "
        "(parse_resume_agent, job_posting_agent, matcher_agent) based on the user's query. "
        "The user's query will be a JSON string. This JSON string will contain an 'input_type' "
        "('resume', 'job_posting', or 'match_request'), 'text_input' (for resume or job_posting), "
        "and optionally 'candidate_id' and 'job_id' (for match_request).\n\n"
        "After receiving a structured result (typically a Python dictionary or JSON object) from a sub-agent, "
        "you MUST combine this result with session information. "
        "The session information is available to you in your state under the key 'current_session_info'.\n\n"
        "Your FINAL output MUST be a single, valid JSON string. This JSON string should have two top-level keys:\n"
        "1. A key representing the sub-agent's primary output (e.g., 'resume_parser_result', 'job_posting_result', or 'match_result'). "
        "   The value for this key will be the structured data returned by the sub-agent.\n"
        "2. A key named 'session_information'. The value for this key will be the object found in your state at 'current_session_info'.\n\n"
        "Example for a job posting input query like '{\"text_input\": \"Software Engineer...\", \"input_type\": \"job_posting\"}' :\n"
        "If job_posting_agent returns: {'title': 'Engineer', 'skills': ['Python']}\n"
        "And current_session_info from your state is: {'session_id': '123', 'user_id': 'abc'}\n"
        "Your final output (a JSON string) should be exactly like this (ensure proper JSON string escaping for the entire output string):\n"
        "'{ \"job_posting_result\": { \"title\": \"Engineer\", \"skills\": [\"Python\"] }, \"session_information\": { \"session_id\": \"123\", \"user_id\": \"abc\" } }'\n\n" # Note: Corrected example JSON string
        "Steps based on 'input_type' from the user's JSON query:\n"
        "IF 'input_type' is 'job_posting':\n"
        "1. Extract 'text_input' from the user's JSON query and call 'job_posting_agent' with it.\n"
        "2. Let its result be 'job_agent_output'.\n"
        "3. Retrieve 'current_session_info' from your state.\n"
        "4. Construct your final response as the JSON string: '{ \"job_posting_result\": job_agent_output, \"session_information\": current_session_info }'.\n\n"
        "IF 'input_type' is 'resume':\n"
        "1. Extract 'text_input' from the user's JSON query and call 'parse_resume_agent' with it.\n"
        "2. Let its result be 'resume_agent_output'.\n"
        "3. Retrieve 'current_session_info' from your state.\n"
        "4. Construct your final response as the JSON string: '{ \"resume_parser_result\": resume_agent_output, \"session_information\": current_session_info }'.\n\n"
        "IF 'input_type' is 'match_request':\n"
        "1. Extract 'candidate_id' and 'job_id' from the user's JSON query.\n"
        "2. Call 'matcher_agent' with these IDs.\n"
        "3. Let its result be 'match_output'.\n"
        "4. Retrieve 'current_session_info' from your state.\n"
        "5. Construct your final response as the JSON string: '{ \"match_result\": match_output, \"session_information\": current_session_info }'.\n\n"
        "Ensure the sub-agent results (which are dictionaries) are correctly embedded as JSON objects within your final JSON string output. Do not add any extra text outside this JSON string."
    )
    return Agent(
        name="orchestrator_agent",
        model=get_model_name(),
        description=(
            "Orchestrates resume parsing, job posting parsing, and candidate-job matching. "
            "Dispatches work to appropriate sub-agents. Retrieves session information from its state. "
            "Returns a final JSON string containing the sub-agent's result and session information."
        ),
        instruction=instruction_text,
        sub_agents=[parse_resume_agent, job_posting_agent, matcher_agent],
        output_key="result",
        before_agent_callback=orchestrator_before_callback,
        after_agent_callback=orchestrator_after_callback,
    )


# Session management functions for external API use
async def create_session_for_user(user_id: str, session_id: str) -> str:
    """Create a new session for a user and return the session ID.

    Args:
        user_id (str): User identifier

    Returns:
        str: New session ID
    """
    session = await _shared_session_service.create_session(
        app_name=APP_NAME, user_id=user_id, state={}, session_id=session_id
    )
    return session.id


async def get_or_create_session_for_user(
    user_id: str, session_id: Optional[str] = None
) -> str:
    """Get an existing session or create a new one for a user.

    Args:
        user_id (str): User identifier
        session_id (Optional[str]): Existing session ID, if any

    Returns:
        str: Session ID (existing or new)
    """
    if session_id:
        # Try to get existing session
        session = await _shared_session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        if session:
            return session.id

    # Create new session if not found or no session_id provided
    return await create_session_for_user(
        user_id, session_id or str(datetime.datetime.now().timestamp())
    )


def update_session_state(session: Session, key: str, value: Any) -> None:
    """Update session state with a key-value pair."""
    session.state.update({key: value})


def get_session_state(session: Session, key: str, default: Any = None) -> Any:
    """Get a value from session state."""
    return session.state.get(key, default)


async def get_session_history(user_id: str, session_id: str):
    """Get session history and state for a user.

    Args:
        user_id (str): User identifier
        session_id (str): Session identifier

    Returns:
        dict: Session state and history
    """
    session = await _shared_session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )

    if not session:
        return {"error": "Session not found"}

    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "app_name": session.app_name,
        "state": dict(session.state),
        "last_update_time": session.last_update_time,
        "events_count": len(session.events) if session.events else 0,
    }


async def list_user_sessions(user_id: str):
    """List all sessions for a user.

    Args:
        user_id (str): User identifier

    Returns:
        dict: List of user sessions
    """
    response = await _shared_session_service.list_sessions(
        app_name=APP_NAME, user_id=user_id
    )

    return {
        "user_id": user_id,
        "sessions": [
            {
                "session_id": session.id,
                "last_update_time": session.last_update_time,
            }
            for session in response.sessions
        ],
    }


# Create shared session service - this will persist across conversations
_shared_session_service = InMemorySessionService()


def get_shared_session_service() -> InMemorySessionService:
    """Get the shared InMemorySessionService instance."""
    return _shared_session_service


# Create agent instance with secure configuration and session management
root_agent = create_orchestrator_agent()
APP_NAME = "co_agent_recruitment"
SESSION_ID = "21-JUNE-2025"
# Export session management utilities
__all__ = [
    "parse_resume",
    "create_orchestrator_agent",
    "get_session_history",
    "get_shared_session_service",
    "list_user_sessions",
    "create_session_for_user",
    "get_or_create_session_for_user",
    "update_session_state",
    "get_session_state",
    "root_agent",
    "APP_NAME",
    "SESSION_ID",
    "sanitize_input",
]
