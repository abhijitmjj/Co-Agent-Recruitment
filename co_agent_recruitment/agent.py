from typing import Any
import datetime
import os
import logging  # Add logging import
from typing import Optional
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.sessions.session import Session
from co_agent_recruitment.job_posting import job_posting_agent
from co_agent_recruitment.resume_parser import (
    parse_resume,
    parse_resume_agent,
    sanitize_input,
)
import dotenv
# Load environment variables from .env file
dotenv.load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("MODEL_ID", "gemini-2.5-flash")


async def orchestrator_before_callback(callback_context) -> None:
    """Callback for orchestrator agent before execution."""
    from google.adk.agents.callback_context import CallbackContext

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


async def orchestrator_after_callback(callback_context) -> None:
    """Callback for orchestrator agent after execution."""
    from google.adk.agents.callback_context import CallbackContext

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
    return Agent(
        name="orchestrator_agent",
        model=get_model_name(),
        description="Orchestrates the resume parsing and job posting agents. Dispatches work to the appropriate agents based on user input. Returns structured JSON data with session information.",
        instruction=(
            "You are an orchestrator agent that manages resume parsing and job posting parsing with session management. "
            "Your role is to call the appropriate specialized agent and return the structured JSON data WITH session information.\\n\\n"
            "IMPORTANT: You must ALWAYS include session information in your response.\\n\\n"
            "When the user provides a resume:\\n"
            "1. Call the parse_resume_agent with the resume text\\n"
            "2. Get the result from parse_resume_agent\\n"
            "3. Add orchestrator session information to the response\\n"
            "4. Return the complete JSON with both parse results and session data\\n\\n"
            "When the user provides a job posting:\\n"
            "1. Call the job_posting_agent with the job posting text\\n"
            "2. Get the result from job_posting_agent\\n"
            "3. Add orchestrator session information to the response\\n"
            "4. Return the complete JSON with both job posting results and session data\\n\\n"
        ),
        sub_agents=[parse_resume_agent, job_posting_agent],
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
