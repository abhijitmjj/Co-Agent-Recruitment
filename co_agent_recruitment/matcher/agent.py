from pydantic_ai.models.gemini import GeminiModel
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent as PydanticAgent
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from datetime import datetime
import os
import logging
import dotenv

dotenv.load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompatibilityScore(BaseModel):
    """
    Data model for the compatibility score between a resume and a job posting.
    """

    compatibility_score: int = Field(
        ...,
        description="A score from 0 to 100 representing how well the resume matches the job posting.",
    )
    summary: str = Field(
        ...,
        description="A brief summary of why the score was given, highlighting key strengths and weaknesses.",
    )
    matching_skills: Optional[List[str]] = Field(
        None, description="A list of skills from the resume that match the job posting."
    )
    missing_skills: Optional[List[str]] = Field(
        None,
        description="A list of skills required by the job posting that are missing from the resume.",
    )


def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("MODEL_ID", "gemini-2.5-flash")


async def generate_compatibility_score(
    resume_data: Dict[str, Any], job_posting_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates a compatibility score between a parsed resume and job posting.
    """
    logger.info("Generating compatibility score...")
    model_name = get_model_name()
    agent = PydanticAgent(
        GeminiModel(model_name=model_name, provider="google-vertex"),
        instructions="You are an expert recruitment assistant. Your task is to generate a compatibility score between the provided resume and job posting data. Analyze the skills, experience, and qualifications in both documents and provide a score from 0 to 100, along with a summary of the match.",
    )

    try:
        result = await agent.run(
            f"Resume: {resume_data}\n\nJob Posting: {job_posting_data}",
            output_type=CompatibilityScore,
        )
        output_data = result.output.model_dump(exclude_none=True)
        final_output: Dict[str, Any] = {
            "compatibility_data": output_data,
            "session_info": {
                "operation_type": "compatibility_score",
                "timestamp": datetime.now().isoformat(),
                "model_used": model_name,
            },
            "operation_status": "success",
        }
        logger.info("Compatibility score generated successfully.")
        return final_output
    except Exception as e:
        logger.error(f"Failed to generate compatibility score: {e}", exc_info=True)
        return {
            "compatibility_data": None,
            "session_info": {
                "operation_type": "compatibility_score",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            },
            "operation_status": "error",
        }


async def matcher_before_callback(callback_context: CallbackContext) -> None:
    """Callback executed before matcher agent runs."""
    callback_context.state["matcher_start_time"] = datetime.now().isoformat()
    logger.info(
        f"Matcher session initialized for user: {getattr(callback_context, '_invocation_context').session.user_id}"
    )


async def matcher_after_callback(callback_context: CallbackContext) -> None:
    """Callback executed after matcher agent runs."""
    callback_context.state["matcher_end_time"] = datetime.now().isoformat()
    logger.info(
        f"Matcher session completed for user: {getattr(callback_context, '_invocation_context').session.user_id}"
    )


def create_matcher_agent() -> Agent:
    """Creates and returns the matcher agent."""
    return Agent(
        name="matcher_agent",
        model=get_model_name(),
        description="Agent to generate a compatibility score between a resume and a job posting.",
        instruction="You are a helpful assistant that generates a compatibility score between a resume and a job posting.",
        tools=[generate_compatibility_score],
        output_key="matcher_output",
        before_agent_callback=matcher_before_callback,
        after_agent_callback=matcher_after_callback,
    )


matcher_agent = create_matcher_agent()