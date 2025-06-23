import logging
from typing import Any, Dict
from .agent import generate_compatibility_score
import dotenv

dotenv.load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def generate_compatibility_score_json(
    resume_data: Dict[str, Any], job_posting_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a compatibility score and return JSON data directly.

    Args:
        resume_data (Dict[str, Any]): Structured resume data
        job_posting_data (Dict[str, Any]): Structured job posting data

    Returns:
        Dict[str, Any]: Compatibility score data as JSON
    """
    logger.info("Starting JSON compatibility score generation")

    try:
        result = await generate_compatibility_score(resume_data, job_posting_data)

        logger.info("Compatibility score generation successful - returning JSON")
        return result

    except Exception as e:
        logger.exception("Compatibility score generation failed")
        return {
            "error": "Compatibility score generation failed",
            "error_type": type(e).__name__,
            "message": str(e),
        }


__all__ = ["generate_compatibility_score_json"]
