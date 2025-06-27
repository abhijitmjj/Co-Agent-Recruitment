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
        instructions=(
            "You are an expert recruitment assistant. Your task is to generate a detailed compatibility score between the provided resume and job posting data.\n\n"
            "ANALYSIS FRAMEWORK:\n"
            "1. Skills Analysis (40% weight):\n"
            "   - Technical skills alignment\n"
            "   - Programming languages match\n"
            "   - Tools and technologies overlap\n"
            "   - Domain expertise relevance\n\n"
            "2. Experience Analysis (30% weight):\n"
            "   - Years of experience vs requirements\n"
            "   - Industry experience relevance\n"
            "   - Role progression and seniority\n"
            "   - Achievement quantification\n\n"
            "3. Education & Qualifications (20% weight):\n"
            "   - Degree level and field alignment\n"
            "   - Certifications relevance\n"
            "   - Continuous learning evidence\n\n"
            "4. Cultural & Soft Skills Fit (10% weight):\n"
            "   - Leadership experience\n"
            "   - Team collaboration\n"
            "   - Communication skills\n"
            "   - Adaptability indicators\n\n"
            "SCORING CRITERIA:\n"
            "- 90-100: Exceptional match - candidate exceeds requirements\n"
            "- 80-89: Strong match - meets all key requirements with some extras\n"
            "- 70-79: Good match - meets most requirements with minor gaps\n"
            "- 60-69: Fair match - meets basic requirements with notable gaps\n"
            "- 50-59: Weak match - significant gaps in key areas\n"
            "- Below 50: Poor match - major misalignment\n\n"
            "OUTPUT REQUIREMENTS:\n"
            "- Provide specific examples from both documents\n"
            "- List exact matching skills and missing skills\n"
            "- Give detailed reasoning for the score\n"
            "- Include actionable insights for improvement\n"
        ),
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
        instruction=(
            "You are an expert recruitment assistant that generates detailed compatibility analysis between resumes and job postings.\n\n"
            "CRITICAL WORKFLOW:\n"
            "1. When given resume and job posting data, IMMEDIATELY call the generate_compatibility_score tool\n"
            "2. ALWAYS return ONLY the JSON output from the generate_compatibility_score tool\n"
            "3. DO NOT add any additional text, explanations, or formatting\n"
            "4. DO NOT return conversational responses\n\n"
            "EXPECTED INPUT FORMAT:\n"
            "- Resume data as a dictionary/JSON object\n"
            "- Job posting data as a dictionary/JSON object\n\n"
            "EXPECTED OUTPUT FORMAT:\n"
            "- Return ONLY the structured JSON from generate_compatibility_score\n"
            "- Must include: compatibility_score, summary, matching_skills, missing_skills\n\n"
            "EXAMPLE WORKFLOW:\n"
            "User: 'Generate compatibility score for resume X and job posting Y'\n"
            "You: [Call generate_compatibility_score tool and return its JSON output directly]\n\n"
            "IMPORTANT: Your response must be valid JSON that can be parsed programmatically."
        ),
        tools=[generate_compatibility_score],
        output_key="matcher_output",
        before_agent_callback=matcher_before_callback,
        after_agent_callback=matcher_after_callback,
    )


matcher_agent = create_matcher_agent()
