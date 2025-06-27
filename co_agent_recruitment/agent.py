from typing import Any
import datetime
import os
import logging  # Add logging import
from typing import Optional
from google.adk.agents import Agent
from .firestore_session_service import FirestoreSessionService
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


def get_project_id() -> str:
    """Get Google Cloud project ID from environment variable."""
    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        raise ValueError("PROJECT_ID environment variable not set.")
    return project_id


def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("MODEL_ID", "gemini-2.5-flash")


async def orchestrator_before_callback(callback_context: CallbackContext) -> None:
    """Callback for orchestrator agent before execution."""
    if not isinstance(callback_context, CallbackContext):
        return

    session_id = callback_context._invocation_context.session.id
    user_id = callback_context._invocation_context.session.user_id

    # Load existing session state from Firestore if it exists
    try:
        existing_session = await _shared_session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        if existing_session and existing_session.state:
            # Load the existing state into the callback context
            callback_context.state.update(existing_session.state)
            logger.info(
                f"Loaded existing session state for user: {user_id} in session: {session_id} with {existing_session.state.get('interaction_count', 0)} previous interactions"
            )
        else:
            logger.info(
                f"No existing session state found for user: {user_id} in session: {session_id}"
            )
    except Exception as e:
        logger.warning(f"Error loading session state for {session_id}: {e}")

    # Check if this is a new conversation or continuing one
    if "conversation_started" not in callback_context.state:
        callback_context.state["conversation_started"] = (
            datetime.datetime.now().isoformat()
        )
        callback_context.state["interaction_count"] = 0
        logger.info(
            f"New orchestrator conversation started for user: {user_id} in session: {session_id}"
        )
    else:
        logger.info(
            f"Continuing orchestrator conversation for user: {user_id} in session: {session_id}"
        )

    # Track orchestrator session interactions - increment the count
    current_count = callback_context.state.get("interaction_count", 0)
    callback_context.state["interaction_count"] = current_count + 1
    callback_context.state["last_interaction_start"] = (
        datetime.datetime.now().isoformat()
    )

    # Store session info for inclusion in response
    callback_context.state["current_session_info"] = {
        "session_id": session_id,
        "user_id": user_id,
        "interaction_number": callback_context.state["interaction_count"],
        "conversation_started": callback_context.state["conversation_started"],
        "interaction_start_time": callback_context.state["last_interaction_start"],
    }

    logger.info(
        f"Orchestrator interaction #{callback_context.state['interaction_count']} started for user: {user_id} in session: {session_id}"
    )


async def orchestrator_after_callback(callback_context: CallbackContext) -> None:
    """Callback for orchestrator agent after execution."""
    if not isinstance(callback_context, CallbackContext):
        return

    session_id = callback_context._invocation_context.session.id
    user_id = callback_context._invocation_context.session.user_id

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
        callback_context.state["session_id"] = session_id

    # Save the updated state back to Firestore
    try:
        # Get the current session and update its state
        session = callback_context._invocation_context.session

        # Create a clean state dictionary with only basic serializable data
        state_dict = {}

        # Extract only the essential state information we need
        if hasattr(callback_context.state, "get"):
            # If state acts like a dict, extract key values safely
            essential_keys = [
                "interaction_count",
                "conversation_started",
                "last_interaction_start",
                "last_interaction_end",
                "last_interaction_completed",
                "last_operation_status",
                "current_session_info",
                "session_id",
            ]

            for key in essential_keys:
                try:
                    value = callback_context.state.get(key)
                    if value is not None and isinstance(
                        value, (str, int, float, bool, dict, list)
                    ):
                        state_dict[key] = value
                except Exception:
                    continue

        # Ensure we have at least the interaction count
        if "interaction_count" not in state_dict:
            state_dict["interaction_count"] = 1

        # Update session state safely
        session.state.clear()
        session.state.update(state_dict)
        session.last_update_time = datetime.datetime.now().timestamp()

        await _shared_session_service.update_session(session)
        logger.info(
            f"Session state saved to Firestore for session {session_id} with interaction count {state_dict.get('interaction_count', 0)}"
        )
    except Exception as e:
        logger.error(
            f"Error saving session state to Firestore for session {session_id}: {e}"
        )

    logger.info(
        f"Orchestrator interaction #{callback_context.state.get('interaction_count', 0)} completed for user: {user_id} on session {session_id}"
    )


def create_orchestrator_agent() -> Agent:
    """Create an orchestrator agent that manages the resume parsing and job posting agents with session management."""
    return Agent(
        name="orchestrator_agent",
        model=get_model_name(),
        description="Orchestrates the resume parsing and job posting agents. Dispatches work to the appropriate agents based on user input. Returns structured JSON data with session information.",
        instruction=(
            "You are an orchestrator agent that manages resume parsing, job posting parsing, and matching with session management. "
            "Your purpose is to dispatch work to the appropriate agents (resume parser, job posting parser, or matcher) based on your input and return structured JSON data, always including session information.\\n\\n"
            "IMPORTANT RULES:\\n"
            "1. You must ALWAYS include session information in your response\\n"
            "2. You must ALWAYS return structured JSON data, never plain text responses\\n"
            "3. You must properly identify the type of content the user is providing\\n\\n"
            "CONTENT IDENTIFICATION:\\n"
            "- If the user asks 'who are you?', respond with your identity and purpose\\n"
            "- If the user says 'parse this:', 'analyze this:', or provides content that looks like a resume or job posting, identify the content type\\n"
            "- Resume indicators: personal details, work experience, education, skills, contact information\\n"
            "- Job posting indicators: job title, company description, requirements, responsibilities, qualifications\\n\\n"
            "PROCESSING WORKFLOW:\\n"
            "When the user provides a RESUME:\\n"
            "1. Transfer to resume_parser_agent\\n"
            "2. Call parse_resume with the resume text\\n"
            "3. Return the complete structured JSON with session information\\n\\n"
            "When the user provides a JOB POSTING:\\n"
            "1. Transfer to job_posting_agent\\n"
            "2. Call analyze_job_posting with the job posting text\\n"
            "3. Return the complete structured JSON with session information\\n\\n"
            "When the user requests MATCHING:\\n"
            "1. Transfer to matcher_agent\\n"
            "2. Call generate_compatibility_score with both resume and job posting data\\n"
            "3. Return the compatibility analysis with session information\\n\\n"
            "RESPONSE FORMAT:\\n"
            "Always return structured JSON responses. Never return plain text explanations unless specifically asked about your identity.\\n"
        ),
        sub_agents=[parse_resume_agent, job_posting_agent, matcher_agent],
        output_key="result",
        before_agent_callback=orchestrator_before_callback,
        after_agent_callback=orchestrator_after_callback,
    )


# Session management functions for external API use
async def create_session_for_user(
    user_id: str, session_id: Optional[str] = None
) -> str:
    """Create a new session for a user and return the session ID.

    Args:
        user_id (str): User identifier
        session_id (Optional[str]): Specific session ID to use, or None for auto-generated

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
        try:
            session = await _shared_session_service.get_session(
                app_name=APP_NAME, user_id=user_id, session_id=session_id
            )
            if session:
                logger.info(
                    f"Reusing existing session {session_id} for user {user_id} with {session.state.get('interaction_count', 0)} previous interactions"
                )
                return session.id
            else:
                logger.info(
                    f"Session {session_id} not found for user {user_id}, creating new session with same ID"
                )
                # Session ID was provided but doesn't exist, create it with the same ID
                return await create_session_for_user(user_id, session_id)
        except Exception as e:
            logger.warning(
                f"Error getting session {session_id} for user {user_id}: {e}, creating new session"
            )
            # If there's an error getting the session, create a new one with the same ID
            return await create_session_for_user(user_id, session_id)

    # Create new session with auto-generated ID if no session_id provided
    logger.info(f"No session ID provided for user {user_id}, creating new session")
    return await create_session_for_user(user_id, None)


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
_shared_session_service = FirestoreSessionService(project_id=get_project_id())


def get_shared_session_service() -> FirestoreSessionService:
    """Get the shared FirestoreSessionService instance."""
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
