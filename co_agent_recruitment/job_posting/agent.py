from pydantic_ai.models.gemini import GeminiModel
from typing import List, Optional  # Added Union
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent as PydanticAgent
from google.adk.agents import Agent
from datetime import datetime
import os
import logging  # Add logging import

import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# --------------------------------------------------------------------------- #


class KeySkills(BaseModel):
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


class Education(BaseModel):
    institution: str = Field(..., description="The name of the institution.")
    degree: Optional[str] = Field(None, description="The degree obtained.")
    field_of_study: Optional[str] = Field(None, description="The field of study.")


class Location(BaseModel):
    city: Optional[str] = Field(
        None, description="The city or cities where the job is located."
    )
    state: Optional[str] = Field(
        None, description="The state or region where the job is located."
    )
    countryCode: Optional[str] = Field(
        None, description="code as per ISO-3166-1 ALPHA-2, e.g. US, AU, IN"
    )
    remote: Optional[bool] = Field(None, description="Whether the job is remote or not")


class HiringOrg(BaseModel):
    description: Optional[str] = Field(
        None, description="A brief description of the company."
    )
    name: Optional[str] = Field(None, description="The name of the company.")
    website_url: Optional[str] = Field(
        None, description="The URL of the company's website."
    )
    application_email: Optional[str] = Field(
        None, description="The email address for job applications."
    )


class BaseSalary(BaseModel):
    amount: Optional[float] = Field(None, description="The base salary amount.")
    currency: Optional[str] = Field(
        None, description="The currency of the salary amount, e.g., USD, EUR."
    )
    unit: Optional[str] = Field(
        None, description="The unit of the salary, e.g., per year, per month, per hour."
    )
    description: Optional[str] = Field(
        None, description="A brief description of the salary structure."
    )


class JobPosting(BaseModel):
    job_title: str = Field(..., description="The job title or role.")
    company: Optional[HiringOrg] = Field(
        None, description="The company details, including name and description."
    )
    location: Location = Field(..., description="The location of the job.")
    years_of_experience: Optional[str] = Field(
        None,
        description="The number of years of experience required. Mention + or - if applicable, e.g., 3+ years, 5-7 years.",
    )
    key_responsibilities: List[str] = Field(
        ...,
        description="A list of key responsibilities for the role. List main 10 responsibilities in bullet points briefly.",
    )
    required_skills: KeySkills = Field(
        ..., description="A list of key skills required for the role."
    )
    required_qualifications: Optional[List[Education]] = Field(
        None, description="A list of qualifications required for the role."
    )
    industry_type: Optional[str] = Field(
        ...,
        description="The industry type or sector for the job. eg Manufacturing, IT, Finance, Mortgage, Insurance etc.",
    )
    salary_range: Optional[str] = Field(
        None, description="The salary range for the job, if available."
    )
    base_salary: Optional[BaseSalary] = Field(
        None, description="The base salary for the job, if available."
    )
    type_of_employment: Optional[str] = Field(
        None,
        description="The type of employment, e.g., Full-time, Part-time, Contract, Internship.",
    )
    date_posted: Optional[str] = Field(
        None, description="The date when the job was posted."
    )
    validThrough: Optional[datetime] = Field(
        None,
        description="The date and time until which the job posting is valid. Format: ISO 8601.",
    )


def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("MODEL_ID", "gemini-2.5-flash")


async def analyze_job_posting(job_posting: str):
    """Analyzes unstructured job posting text and returns a structured JSON object with session info.

    Args:
        job_posting(str): The unstructured text content of a job posting.

    Returns:
        dict: A structured JSON object containing key information about the job posting with session information.
    """
    logger.info(
        f"Starting job posting analysis for input text: {job_posting[:200]}..."
    )  # Log input
    model_name = get_model_name()
    agent = PydanticAgent(
        GeminiModel(model_name=model_name, provider="google-vertex"),
        instructions="You are an expert job posting parser. Your task is to transform the unstructured job posting text provided below into a single, structured, and comprehensive JSON object. Extract only the information that is explicitly present in the text. Do not make assumptions or add information that is not clearly stated.",
    )
    try:
        result = await agent.run(job_posting, output_type=JobPosting)
        output_data = result.output.model_dump(exclude_none=True)

        # Add session information to the output
        session_info = {
            "operation_type": "job_posting_analysis",
            "timestamp": datetime.now().isoformat(),
            "processing_time": "completed",
            "model_used": model_name,
        }

        # Wrap the result with session information
        final_output = {
            "job_posting_data": output_data,
            "session_info": session_info,
            "operation_status": "success",
        }

        logger.info(
            f"Job posting analysis successful. Output: {str(output_data)[:500]}..."
        )  # Log output
        return final_output
    except ValidationError as e:
        # Log the error or handle it as needed
        error_messages = []
        for error in e.errors():
            error_messages.append(
                f"Field: {error.get('loc', 'N/A')}, Type: {error.get('type', 'N/A')}, Message: {error.get('msg', 'N/A')}"
            )
        logger.error(
            f"Pydantic validation failed during job posting analysis: {error_messages}",
            exc_info=True,
        )  # Log exception

        # Return error with session info
        error_session_info = {
            "operation_type": "job_posting_analysis",
            "timestamp": datetime.now().isoformat(),
            "processing_time": "failed",
            "error": "Pydantic validation failed",
        }

        return {
            "job_posting_data": None,
            "session_info": error_session_info,
            "operation_status": "validation_error",
            "error_details": error_messages,
        }
    except Exception as e:
        # Catch any other unexpected errors from the agent.run call
        logger.error(
            f"An unexpected error occurred during job posting analysis: {type(e).__name__} - {e}",
            exc_info=True,
        )  # Log exception

        # Return error with session info
        error_session_info = {
            "operation_type": "job_posting_analysis",
            "timestamp": datetime.now().isoformat(),
            "processing_time": "failed",
            "error": f"Unexpected error: {type(e).__name__}",
        }

        return {
            "job_posting_data": None,
            "session_info": error_session_info,
            "operation_status": "error",
            "error_details": str(e),
        }


# Session management callback functions for job posting agent
async def job_posting_before_callback(callback_context) -> None:
    """Callback executed before job posting agent runs."""
    from google.adk.agents.callback_context import CallbackContext

    if not isinstance(callback_context, CallbackContext):
        return

    # Initialize session state for job posting analysis
    callback_context.state["job_posting_start_time"] = datetime.now().isoformat()
    callback_context.state["operation_type"] = "job_posting_analysis"

    logger.info(
        f"Job posting analysis session initialized for user: {callback_context._invocation_context.session.user_id}"
    )


async def job_posting_after_callback(callback_context) -> None:
    """Callback executed after job posting agent runs."""
    from google.adk.agents.callback_context import CallbackContext

    if not isinstance(callback_context, CallbackContext):
        return

    # Update session state with completion info
    callback_context.state["job_posting_end_time"] = datetime.now().isoformat()
    callback_context.state["job_posting_completed"] = True

    logger.info(
        f"Job posting analysis session completed for user: {callback_context._invocation_context.session.user_id}"
    )
    logger.info(
        f"Session state: {callback_context.state}"
    )  # Log final state for debugging


def create_job_posting_agent() -> Agent:
    """Creates and returns the job posting agent with session management."""
    return Agent(
        name="job_posting_agent",
        model=get_model_name(),
        description="Agent to parse job posting text and transform it into a structured JSON object.",
        instruction=(
            "You are an expert job posting parser. Your task is to transform the unstructured job posting text provided below "
            "into a single, structured, and comprehensive JSON object.\n\n"
            
            "IMPORTANT REQUIREMENTS:\n"
            "1. ALWAYS call the analyze_job_posting tool with the provided job posting text\n"
            "2. ALWAYS return the complete structured JSON response from analyze_job_posting\n"
            "3. NEVER return just a brief description of what you are\n"
            "4. Extract ALL information explicitly present in the text\n\n"
            
            "PARSING RULES:\n"
            "- Extract only information that is explicitly present in the text\n"
            "- Do not make assumptions or add information that is not clearly stated\n"
            "- Include session information in the response\n"
            "- Return structured JSON data, not plain text\n\n"
            
            "WORKFLOW:\n"
            "1. When user provides job posting text, immediately call analyze_job_posting tool\n"
            "2. Return the complete structured JSON output from the tool\n"
            "3. Do not provide explanatory text unless there's an error\n"
        ),
        tools=[analyze_job_posting],
        output_key="job_posting_JSON",
        before_agent_callback=job_posting_before_callback,
        after_agent_callback=job_posting_after_callback,
    )


job_posting_agent = create_job_posting_agent()

# root_agent = job_posting_agent
