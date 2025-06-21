from typing import Any
import datetime
import os
import re
import logging  # Add logging import
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent as PydanticAgent
from pydantic_ai.models.gemini import GeminiModel
from google.adk.agents import Agent
import dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

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
    return os.getenv("MODEL_ID", "gemini-2.5-flash")


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
    logger.info(
        f"Starting resume parsing for input text: {resume_text[:200]}..."
    )  # Log input
    try:
        # Sanitize input
        sanitized_text = sanitize_input(resume_text)

        # Get model name from environment
        model_name = get_model_name()

        agent = PydanticAgent(
            GeminiModel(model_name=model_name, provider="google-vertex"),
            instructions=(
                "You are an expert AI resume parser. Your task is to transform the unstructured resume text provided below "
                "into a single, structured, and comprehensive JSON object suitable for a modern Applicant Tracking System (ATS). "
                "Only extract information explicitly present in the text. For the awards section, ensure each award entry is a "
                "separate object in the awards array with its own title, awarder, date, and summary; do not merge multiple "
                "awards into one object or duplicate keys. For other list fields (certifications, education, work_experience, "
                "projects, languages), apply the same rule: each list item is separate. Output valid JSON with no duplicate keys."
            ),
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

        logger.info(
            f"Resume parsing successful. Output: {str(output_data)[:500]}..."
        )  # Log output
        return final_output
    except Exception as e:
        # Log error but don't expose internal details
        logger.error(
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
        logger.info(
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

    logger.info(
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

    logger.info(
        f"Operation #{callback_context.state.get('operation_count', 0)} completed for user: {callback_context._invocation_context.session.user_id} on session {callback_context.state['session_id']}"
    )


def create_resume_parser_agent() -> Agent:
    """Create a secure resume parser agent with environment configuration and session management."""
    model_name = get_model_name()

    return Agent(
        name="resume_parser_agent",
        model=model_name,
        description="Agent to parse unstructured resume text and transform it into a structured, comprehensive JSON object.",
        instruction=(
            "You are an expert AI resume parser. Your task is to transform the unstructured resume text provided below "
            "into a single, structured, and comprehensive JSON object suitable for a modern Applicant Tracking System (ATS). "
            "Only extract information explicitly present in the text. For the awards section, ensure each award entry is a "
            "separate object in the awards array with its own title, awarder, date, and summary; do not merge multiple "
            "awards into one object or duplicate keys. For other list fields (certifications, education, work_experience, "
            "projects, languages), apply the same rule: each list item is separate. Output valid JSON with no duplicate keys."
        ),
        tools=[parse_resume],
        output_key="resume_JSON",
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
    )


parse_resume_agent = create_resume_parser_agent()
