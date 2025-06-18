from typing import Any
import datetime
import asyncio
import os
import re
import logging  # Add logging import
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent as PydanticAgent
from pydantic_ai.models.gemini import GeminiModel
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.sessions.session import Session
from google.adk.sessions.state import State
from co_agent_recruitment.job_posting import analyze_job_posting, job_posting_agent


class Location(BaseModel):
    address: Optional[str] = Field(
        None,
        description="To add multiple address lines, use \\n. For example, 1234 Street Name\\nBuilding 5. Floor 2.",
    )
    postalCode: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    countryCode: Optional[str] = Field(
        None, description="code as per ISO-3166-1 ALPHA-2, e.g. US, AU, IN"
    )
    region: Optional[str] = Field(
        None,
        description="The general region where you live. Can be a US state, or a province, for instance.",
    )

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 500:
            raise ValueError("Address too long")
        return v

    @field_validator("countryCode")
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[A-Z]{2}$", v):
            raise ValueError("Invalid country code format")
        return v


class Link(BaseModel):
    type: Literal["LinkedIn", "GitHub", "Portfolio", "Other"] = Field(
        ..., description="The type of the link."
    )
    url: str = Field(..., description="The URL of the link.")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        # Basic URL validation to prevent malicious URLs
        if not re.match(r"^https?://", v):
            raise ValueError("URL must start with http:// or https://")
        if len(v) > 2000:
            raise ValueError("URL too long")
        return v


class PersonalDetails(BaseModel):
    full_name: str = Field(..., description="The full name of the person.")
    email: Optional[str] = Field(None, description="The email address of the person.")
    phone_number: Optional[str] = Field(
        None, description="The phone number of the person."
    )
    location: Optional[Location] = Field(
        None, description="The location of the person."
    )
    links: Optional[List[Link]] = Field(
        None, description="A list of links to professional profiles."
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("Full name too long")
        # Remove potential script tags or suspicious content
        if re.search(r"<[^>]*>", v):
            raise ValueError("Invalid characters in full name")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v


class WorkExperience(BaseModel):
    job_title: str = Field(..., description="The job title.")
    company: str = Field(..., description="The company name.")
    location: Optional[str] = Field(None, description="The location of the job.")
    start_date: str = Field(..., description="The start date of the job.")
    end_date: Optional[str] = Field(None, description="The end date of the job.")
    is_current: bool = Field(..., description="Whether this is a current job.")
    responsibilities: Optional[List[str]] = Field(
        None, description="A list of responsibilities."
    )

    @field_validator("responsibilities")
    @classmethod
    def validate_responsibilities(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            for resp in v:
                if len(resp) > 1000:
                    raise ValueError("Responsibility description too long")
        return v


class Education(BaseModel):
    institution: str = Field(..., description="The name of the institution.")
    degree: Optional[str] = Field(None, description="The degree obtained.")
    field_of_study: Optional[str] = Field(None, description="The field of study.")
    start_date: Optional[str] = Field(
        None, description="The start date of the education."
    )
    graduation_date: Optional[str] = Field(None, description="The graduation date.")


class TechnicalSkills(BaseModel):
    programming_languages: Optional[List[str]] = Field(
        None, description="A list of programming languages."
    )
    frameworks_libraries: Optional[List[str]] = Field(
        None, description="A list of frameworks and libraries."
    )
    databases: Optional[List[str]] = Field(None, description="A list of databases.")
    cloud_platforms: Optional[List[str]] = Field(
        None, description="A list of cloud platforms."
    )
    tools_technologies: Optional[List[str]] = Field(
        None, description="A list of other tools and technologies."
    )


class Skills(BaseModel):
    technical: Optional[TechnicalSkills] = Field(
        None, description="The technical skills."
    )
    soft_skills: Optional[List[str]] = Field(None, description="A list of soft skills.")


class Certification(BaseModel):
    name: str = Field(..., description="The name of the certification.")
    issuing_organization: str = Field(..., description="The issuing organization.")
    date_issued: Optional[str] = Field(
        None, description="The date the certification was issued."
    )


class Project(BaseModel):
    name: str = Field(..., description="The name of the project.")
    description: Optional[str] = Field(
        None, description="A description of the project."
    )
    technologies_used: Optional[List[str]] = Field(
        None, description="A list of technologies used in the project."
    )
    link: Optional[str] = Field(None, description="A link to the project.")

    @field_validator("link")
    @classmethod
    def validate_link(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^https?://", v):
            raise ValueError("Project link must start with http:// or https://")
        return v


class Language(BaseModel):
    language: str = Field(..., description="The language.")
    proficiency: Literal[
        "Native", "Fluent", "Professional", "Conversational", "Basic"
    ] = Field(..., description="The proficiency level in the language.")


class Award(BaseModel):
    title: Optional[str] = Field(
        None, description="e.g. One of the 100 greatest minds of the century"
    )
    date: Optional[str] = Field(None)
    awarder: Optional[str] = Field(None, description="e.g. Time Magazine")
    summary: Optional[str] = Field(
        None, description="e.g. Received for my work with Quantum Physics"
    )


class Volunteer(BaseModel):
    organization: Optional[str] = Field(None, description="e.g. Facebook")
    position: Optional[str] = Field(None, description="e.g. Software Engineer")
    url: Optional[str] = Field(None, description="e.g. http://facebook.example.com")
    startDate: Optional[str] = Field(None)
    endDate: Optional[str] = Field(None)
    summary: Optional[str] = Field(
        None, description="Give an overview of your responsibilities at the company"
    )
    highlights: Optional[List[str]] = Field(
        None, description="Specify accomplishments and achievements"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^https?://", v):
            raise ValueError("Volunteer URL must start with http:// or https://")
        return v


class Resume(BaseModel):
    personal_details: PersonalDetails = Field(
        ..., description="The personal details of the person."
    )
    professional_summary: Optional[str] = Field(
        None, description="The professional summary."
    )
    inferred_experience_level: Optional[
        Literal[
            "Entry-Level",
            "Junior",
            "Mid-Level",
            "Senior",
            "Lead",
            "Principal",
            "Executive",
        ]
    ] = Field(None, description="The inferred experience level.")
    total_years_experience: Optional[float] = Field(
        None, description="The total years of experience."
    )
    work_experience: Optional[List[WorkExperience]] = Field(
        None, description="A list of work experiences."
    )
    education: Optional[List[Education]] = Field(
        None, description="A list of educational qualifications."
    )
    skills: Optional[Skills] = Field(None, description="The skills of the person.")
    certifications: Optional[List[Certification]] = Field(
        None, description="A list of certifications."
    )
    projects: Optional[List[Project]] = Field(None, description="A list of projects.")
    languages: Optional[List[Language]] = Field(
        None, description="A list of languages."
    )
    awards: Optional[List[Award]] = Field(
        None, description="A list of awards and recognitions."
    )
    volunteers: Optional[List[Volunteer]] = Field(
        None, description="A list of volunteer experiences."
    )


def sanitize_input(text: Any) -> str:
    """Sanitize input text to prevent injection attacks."""
    if not text or not isinstance(text, str):
        raise ValueError("Invalid input: must be a non-empty string")

    # Limit input size to prevent DoS
    if len(text) > 50000:  # 50KB limit
        raise ValueError("Input text too large")

    # Remove potential script tags and suspicious content
    sanitized = re.sub(
        r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL
    )
    sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r"on\w+\s*=", "", sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-05-20")


async def parse_resume(resume_text: str):
    """Parses unstructured resume text and returns a structured JSON object with session info.

    Args:
        resume_text (str): The unstructured text content of a single resume.

    Returns:
        dict: A single, well-formed JSON object with session information.

    Raises:
        ValueError: If input is invalid or too large.
        Exception: If AI parsing fails.
    """
    logging.info(
        f"Starting resume parsing for input text: {resume_text[:200]}..."
    )  # Log input
    try:
        # Sanitize input
        sanitized_text = sanitize_input(resume_text)

        # Get model name from environment
        model_name = get_model_name()

        agent = PydanticAgent(
            GeminiModel(model_name=model_name, provider="google-vertex"),
            instructions="You are an expert AI resume parser. Your task is to transform the unstructured resume text provided below into a single, structured, and comprehensive JSON object suitable for a modern Applicant Tracking System (ATS). Only extract information explicitly present in the text.",
        )
        result = await agent.run(sanitized_text, output_type=Resume)
        output_data = result.output.model_dump()

        # Add session information to the output
        session_info = {
            "operation_type": "resume_parsing",
            "timestamp": datetime.datetime.now().isoformat(),
            "processing_time": "completed",
            "model_used": model_name,
        }

        # Wrap the result with session information
        final_output = {
            "resume_data": output_data,
            "session_info": session_info,
            "operation_status": "success",
        }

        logging.info(
            f"Resume parsing successful. Output: {str(output_data)[:500]}..."
        )  # Log output
        return final_output
    except Exception as e:
        # Log error but don't expose internal details
        logging.error(
            f"Resume parsing failed: {type(e).__name__} - {e}", exc_info=True
        )  # Log exception
        print(f"Resume parsing failed: {type(e).__name__}")

        # Return error with session info
        error_session_info = {
            "operation_type": "resume_parsing",
            "timestamp": datetime.datetime.now().isoformat(),
            "processing_time": "failed",
            "error": f"Failed to parse resume: {type(e).__name__}",
        }

        return {
            "resume_data": None,
            "session_info": error_session_info,
            "operation_status": "error",
        }


# Session management callback functions
async def before_agent_callback(callback_context) -> None:
    """Callback executed before agent runs - handles session state initialization."""
    from google.adk.agents.callback_context import CallbackContext

    if not isinstance(callback_context, CallbackContext):
        return

    # Check if this is a new conversation or continuing one
    if "conversation_started" not in callback_context.state:
        callback_context.state["conversation_started"] = (
            datetime.datetime.now().isoformat()
        )
        callback_context.state["operation_count"] = 0
        logging.info(
            f"New conversation started for user: {callback_context._invocation_context.session.user_id}"
        )

    # Increment operation count for this session
    callback_context.state["operation_count"] = (
        callback_context.state.get("operation_count", 0) + 1
    )
    callback_context.state["last_operation_start"] = datetime.datetime.now().isoformat()
    callback_context.state["operation_type"] = "resume_parsing"
    callback_context.state["session_id"] = (
        callback_context._invocation_context.session.id
    )

    logging.info(
        f"Operation #{callback_context.state['operation_count']} started for user: {callback_context._invocation_context.session.user_id} on session {callback_context.state['session_id']}"
    )


async def after_agent_callback(callback_context) -> None:
    """Callback executed after agent runs - handles session state cleanup and logging."""
    from google.adk.agents.callback_context import CallbackContext

    if not isinstance(callback_context, CallbackContext):
        return

    # Update session state with completion info
    callback_context.state["last_operation_end"] = datetime.datetime.now().isoformat()
    callback_context.state["last_operation_completed"] = True
    callback_context.state["session_id"] = (
        callback_context._invocation_context.session.id
    )

    logging.info(
        f"Operation #{callback_context.state.get('operation_count', 0)} completed for user: {callback_context._invocation_context.session.user_id} on session {callback_context.state['session_id']}"
    )


def create_resume_parser_agent() -> Agent:
    """Create a secure resume parser agent with environment configuration and session management."""
    model_name = get_model_name()

    return Agent(
        name="resume_parser_agent",
        model=model_name,
        description="Agent to parse unstructured resume text and transform it into a structured, comprehensive JSON object.",
        instruction="You are an expert AI resume parser. Your task is to transform the unstructured resume text provided below into a single, structured, and comprehensive JSON object suitable for a modern Applicant Tracking System (ATS). Only extract information explicitly present in the text.",
        tools=[parse_resume],
        output_key="resume_JSON",
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
    )


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
        logging.info(
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

    logging.info(
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

    logging.info(
        f"Orchestrator interaction #{callback_context.state.get('interaction_count', 0)} completed for user: {callback_context._invocation_context.session.user_id}"
    )


parse_resume_agent = create_resume_parser_agent()


def create_orchestrator_agent() -> Agent:
    """Create an orchestrator agent that manages the resume parsing and job posting agents with session management."""
    return Agent(
        name="orchestrator_agent",
        model=get_model_name(),
        description="Orchestrates the resume parsing and job posting agents. Dispatches work to the appropriate agents based on user input. Returns structured JSON data with session information.",
        instruction=(
            "You are an orchestrator agent that manages resume parsing and job posting analysis with session management. "
            "Your role is to call the appropriate specialized agent and return the structured JSON data WITH session information.\\n\\n"
            "IMPORTANT: You must ALWAYS include session information in your response.\\n\\n"
            "When the user provides a resume:\\n"
            # "1. Call the parse_resume function with the resume text\\n"
            "1. Call the parse_resume_agent with the resume text\\n"
            # "2. Get the result from parse_resume (which already includes session_info)\\n"
            "2. Get the result from parse_resume_agent (which already includes session_info)\\n"
            "3. Add orchestrator session information to the response\\n"
            "4. Return the complete JSON with both parse results and session data\\n\\n"
            "When the user provides a job posting:\\n"
            "1. Call the analyze_job_posting function with the job posting text\\n"
            "2. Get the result from analyze_job_posting\\n"
            "3. Add orchestrator session information to the response\\n"
            "4. Return the complete JSON with both analysis results and session data\\n\\n"
            "ALWAYS include in your response:\\n"
            "- The original function result (resume_data or job_posting_data)\\n"
            "- session_info with: session_id, user_id, interaction_number, timestamps\\n"
            "- orchestrator_info with: agent_name, processing_status, completion_time\\n\\n"
            "Example response format:\\n"
            "{\\n"
            '  \\"resume_data\\": {...},\\n'
            '  \\"session_info\\": {\\n'
            '    \\"session_id\\": \\"abc-123\\",\\n'
            '    \\"user_id\\": \\"user_123\\",\\n'
            '    \\"interaction_number\\": 1,\\n'
            '    \\"conversation_started\\": \\"2025-06-18T20:00:00\\",\\n'
            '    \\"interaction_start_time\\": \\"2025-06-18T20:00:00\\"\\n'
            "  },\\n"
            '  \\"orchestrator_info\\": {\\n'
            '    \\"agent_name\\": \\"orchestrator_agent\\",\\n'
            '    \\"processing_status\\": \\"completed\\",\\n'
            '    \\"completion_time\\": \\"2025-06-18T20:00:01\\"\\n'
            "  }\\n"
            "}"
        ),
        tools=[analyze_job_posting],
        sub_agents=[parse_resume_agent],
        output_key="result",
        before_agent_callback=orchestrator_before_callback,
        after_agent_callback=orchestrator_after_callback,
    )


# Session management functions for external API use
async def create_session_for_user(user_id: str) -> str:
    """Create a new session for a user and return the session ID.

    Args:
        user_id (str): User identifier

    Returns:
        str: New session ID
    """
    session = await _shared_session_service.create_session(
        app_name="co_agent_recruitment", user_id=user_id, state={}
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
            app_name="co_agent_recruitment", user_id=user_id, session_id=session_id
        )
        if session:
            return session.id

    # Create new session if not found or no session_id provided
    return await create_session_for_user(user_id)


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
        app_name="co_agent_recruitment", user_id=user_id, session_id=session_id
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
        app_name="co_agent_recruitment", user_id=user_id
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

# Create agent instance with secure configuration and session management
root_agent = create_orchestrator_agent()

# Export session management utilities
__all__ = [
    "parse_resume",
    "create_resume_parser_agent",
    "create_orchestrator_agent",
    "get_session_history",
    "list_user_sessions",
    "create_session_for_user",
    "get_or_create_session_for_user",
    "update_session_state",
    "get_session_state",
    "root_agent",
    "Resume",
    "PersonalDetails",
    "WorkExperience",
    "Education",
    "Skills",
    "TechnicalSkills",
]
