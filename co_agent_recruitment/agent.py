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


async def parse_resume(resume_text: str) -> dict[str, Any]:
    """Parses unstructured resume text and returns a structured JSON object.

    Args:
        resume_text (str): The unstructured text content of a single resume.

    Returns:
        dict: A single, well-formed JSON object.

    Raises:
        ValueError: If input is invalid or too large.
        Exception: If AI parsing fails.
    """
    logging.info(f"Starting resume parsing for input text: {resume_text[:200]}...")  # Log input
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
        logging.info(f"Resume parsing successful. Output: {str(output_data)[:500]}...")  # Log output
        return output_data
    except Exception as e:
        # Log error but don't expose internal details
        logging.error(f"Resume parsing failed: {type(e).__name__} - {e}", exc_info=True)  # Log exception
        print(f"Resume parsing failed: {type(e).__name__}")
        raise Exception("Failed to parse resume")


# Session management callback functions
async def before_agent_callback(callback_context) -> None:
    """Callback executed before agent runs - handles session state initialization."""
    from google.adk.agents.callback_context import CallbackContext
    
    if not isinstance(callback_context, CallbackContext):
        return
    
    # Initialize session state for resume parsing
    callback_context.state['operation_start_time'] = datetime.datetime.now().isoformat()
    callback_context.state['operation_type'] = 'resume_parsing'
    
    logging.info(f"Session initialized for user: {callback_context._invocation_context.session.user_id}")

async def after_agent_callback(callback_context) -> None:
    """Callback executed after agent runs - handles session state cleanup and logging."""
    from google.adk.agents.callback_context import CallbackContext
    
    if not isinstance(callback_context, CallbackContext):
        return
    
    # Update session state with completion info
    callback_context.state['operation_end_time'] = datetime.datetime.now().isoformat()
    callback_context.state['operation_completed'] = True
    
    logging.info(f"Session completed for user: {callback_context._invocation_context.session.user_id}")

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
        after_agent_callback=after_agent_callback
    )


async def orchestrator_before_callback(callback_context) -> None:
    """Callback for orchestrator agent before execution."""
    from google.adk.agents.callback_context import CallbackContext
    
    if not isinstance(callback_context, CallbackContext):
        return
    
    # Track orchestrator session
    callback_context.state['orchestrator_start_time'] = datetime.datetime.now().isoformat()
    callback_context.state['interaction_count'] = callback_context.state.get('interaction_count', 0) + 1
    
    logging.info(f"Orchestrator session started for user: {callback_context._invocation_context.session.user_id}")

async def orchestrator_after_callback(callback_context) -> None:
    """Callback for orchestrator agent after execution."""
    from google.adk.agents.callback_context import CallbackContext
    
    if not isinstance(callback_context, CallbackContext):
        return
    
    # Update orchestrator session state
    callback_context.state['orchestrator_end_time'] = datetime.datetime.now().isoformat()
    callback_context.state['last_interaction_completed'] = True
    
    logging.info(f"Orchestrator session completed for user: {callback_context._invocation_context.session.user_id}")

def create_orchestrator_agent() -> Agent:
    """Create an orchestrator agent that manages the resume parsing and job posting agents with session management."""
    return Agent(
        name="orchestrator_agent",
        model=get_model_name(),
        description="Orchestrates the resume parsing and job posting agents. Dispatches work to the appropriate agents based on user input. Returns structured JSON data.",
        instruction=(
            "You are an orchestrator agent that manages resume parsing and job posting analysis. "
            "Your role is to call the appropriate specialized agent and return the structured JSON data.\\n\\n"
            "IMPORTANT: You must ALWAYS return the raw JSON data from the specialized agents, not formatted text.\\n\\n"
            "When the user provides a resume:\\n"
            "1. Call the parse_resume function with the resume text\\n"
            "2. Return the exact JSON result from parse_resume\\n\\n"
            "When the user provides a job posting:\\n"
            "1. Call the analyze_job_posting function with the job posting text\\n"
            "2. Return the exact JSON result from analyze_job_posting\\n\\n"
            "Do NOT format the output as text. Do NOT add explanations or markdown formatting. "
            "Simply return the structured JSON data as-is from the specialized agents.\\n\\n"
            "Available session data:\\n"
            "- Resume data: {resume_JSON?}\\n"
            "- Job posting data: {job_posting_JSON?}"
        ),
        tools=[parse_resume, analyze_job_posting],
        output_key="result",
        before_agent_callback=orchestrator_before_callback,
        after_agent_callback=orchestrator_after_callback
    )
# Session management functions
async def create_session(app_name: str, user_id: str, session_service: InMemorySessionService) -> Session:
    """Create a new session for the agent interaction."""
    return await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state={}
    )

async def get_or_create_session(app_name: str, user_id: str, session_id: Optional[str] = None,
                               session_service: Optional[InMemorySessionService] = None) -> tuple[Session, InMemorySessionService]:
    """Get an existing session or create a new one."""
    if session_service is None:
        session_service = InMemorySessionService()
    
    if session_id:
        # Try to get existing session
        session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        if session:
            return session, session_service
    
    # Create new session if not found or no session_id provided
    session = await create_session(app_name, user_id, session_service)
    return session, session_service

def update_session_state(session: Session, key: str, value: Any) -> None:
    """Update session state with a key-value pair."""
    session.state.update({key: value})

def get_session_state(session: Session, key: str, default: Any = None) -> Any:
    """Get a value from session state."""
    return session.state.get(key, default)

# Session-aware wrapper functions for external use
async def parse_resume_with_session(resume_text: str, user_id: str = "default_user",
                                   session_id: Optional[str] = None) -> tuple[dict[str, Any], str]:
    """Parse resume with session management and return result with session ID.
    
    Args:
        resume_text (str): The resume text to parse
        user_id (str): User identifier for session management
        session_id (Optional[str]): Existing session ID, if any
        
    Returns:
        tuple[dict[str, Any], str]: Parsed resume data and session ID
    """
    session, session_service = await get_or_create_session("co_agent_recruitment", user_id, session_id, _shared_session_service)
    result = await parse_resume(resume_text)
    return result, session.id

async def get_session_history(user_id: str, session_id: str) -> dict[str, Any]:
    """Get session history and state for a user.
    
    Args:
        user_id (str): User identifier
        session_id (str): Session identifier
        
    Returns:
        dict[str, Any]: Session state and history
    """
    session = await _shared_session_service.get_session(
        app_name="co_agent_recruitment",
        user_id=user_id,
        session_id=session_id
    )
    
    if not session:
        return {"error": "Session not found"}
    
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "app_name": session.app_name,
        "state": dict(session.state),
        "last_update_time": session.last_update_time,
        "events_count": len(session.events) if session.events else 0
    }

async def list_user_sessions(user_id: str) -> dict[str, Any]:
    """List all sessions for a user.
    
    Args:
        user_id (str): User identifier
        
    Returns:
        dict[str, Any]: List of user sessions
    """
    response = await _shared_session_service.list_sessions(
        app_name="co_agent_recruitment",
        user_id=user_id
    )
    
    return {
        "user_id": user_id,
        "sessions": [
            {
                "session_id": session.id,
                "last_update_time": session.last_update_time,
            }
            for session in response.sessions
        ]
    }

# Create shared session service
_shared_session_service = InMemorySessionService()

# Create agent instance with secure configuration and session management
root_agent = create_orchestrator_agent()

# Export session management utilities
__all__ = [
    "parse_resume",
    "parse_resume_with_session",
    "create_resume_parser_agent",
    "create_orchestrator_agent",
    "get_session_history",
    "list_user_sessions",
    "get_or_create_session",
    "update_session_state",
    "get_session_state",
    "root_agent",
    "Resume",
    "PersonalDetails",
    "WorkExperience",
    "Education",
    "Skills",
    "TechnicalSkills"
]
