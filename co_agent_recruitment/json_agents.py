"""
JSON-focused agents that return structured data without conversational formatting.
These agents are designed specifically for API usage where JSON output is required.
"""

import asyncio
import logging
from typing import Any, Dict
from co_agent_recruitment.agent import parse_resume, sanitize_input
from co_agent_recruitment.job_posting.agent import analyze_job_posting


async def parse_resume_json(resume_text: str) -> Dict[str, Any]:
    """
    Parse resume and return JSON data directly without conversational formatting.

    Args:
        resume_text (str): The resume text to parse

    Returns:
        Dict[str, Any]: Structured resume data as JSON

    Raises:
        ValueError: If input is invalid
        Exception: If parsing fails
    """
    logging.info("Starting JSON resume parsing")

    try:
        # Use the existing parse_resume function which already returns JSON
        result = await parse_resume(resume_text)

        # Ensure we return a dictionary
        if isinstance(result, dict):
            logging.info("Resume parsing successful - returning JSON")
            return result
        else:
            # This shouldn't happen with the current implementation, but handle it
            logging.error(f"Unexpected result type: {type(result)}")
            raise Exception(f"Expected dict, got {type(result)}")

    except Exception as e:
        logging.error(f"Resume parsing failed: {e}")
        # Return error in JSON format
        return {
            "error": "Resume parsing failed",
            "error_type": type(e).__name__,
            "message": str(e),
        }


async def analyze_job_posting_json(job_posting_text: str) -> Dict[str, Any]:
    """
    Analyze job posting and return JSON data directly without conversational formatting.

    Args:
        job_posting_text (str): The job posting text to analyze

    Returns:
        Dict[str, Any]: Structured job posting data as JSON

    Raises:
        ValueError: If input is invalid
        Exception: If analysis fails
    """
    logging.info("Starting JSON job posting analysis")

    try:
        # Use the existing analyze_job_posting function which already returns JSON
        result = await analyze_job_posting(job_posting_text)

        # Ensure we return a dictionary
        if isinstance(result, dict):
            # Check if it's an error response from the original function
            if "error" in result:
                logging.warning(
                    f"Job posting analysis returned error: {result['error']}"
                )
                return result
            else:
                logging.info("Job posting analysis successful - returning JSON")
                return result
        else:
            # This shouldn't happen with the current implementation, but handle it
            logging.error(f"Unexpected result type: {type(result)}")
            raise Exception(f"Expected dict, got {type(result)}")

    except Exception as e:
        logging.error(f"Job posting analysis failed: {e}")
        # Return error in JSON format
        return {
            "error": "Job posting analysis failed",
            "error_type": type(e).__name__,
            "message": str(e),
        }


async def process_document_json(
    document_text: str, document_type: str = "auto"
) -> Dict[str, Any]:
    """
    Process a document (resume or job posting) and return JSON data.

    Args:
        document_text (str): The document text to process
        document_type (str): Type of document ("resume", "job_posting", or "auto" for auto-detection)

    Returns:
        Dict[str, Any]: Structured document data as JSON with type information
    """
    logging.info(f"Processing document with type: {document_type}")

    try:
        # Sanitize input
        sanitized_text = sanitize_input(document_text)

        if document_type == "resume":
            result = await parse_resume_json(sanitized_text)
            return {
                "document_type": "resume",
                "data": result,
                "success": "error" not in result,
            }
        elif document_type == "job_posting":
            result = await analyze_job_posting_json(sanitized_text)
            return {
                "document_type": "job_posting",
                "data": result,
                "success": "error" not in result,
            }
        elif document_type == "auto":
            # Simple heuristic to detect document type
            text_lower = sanitized_text.lower()

            # Keywords that suggest it's a job posting
            job_keywords = [
                "responsibilities",
                "requirements",
                "qualifications",
                "we are seeking",
                "job description",
                "position",
                "role",
                "company",
                "salary",
                "benefits",
                "apply",
                "hiring",
                "candidate",
                "experience required",
            ]

            # Keywords that suggest it's a resume
            resume_keywords = [
                "education",
                "work experience",
                "skills",
                "projects",
                "certifications",
                "objective",
                "summary",
                "achievements",
                "accomplishments",
            ]

            job_score = sum(1 for keyword in job_keywords if keyword in text_lower)
            resume_score = sum(
                1 for keyword in resume_keywords if keyword in text_lower
            )

            if job_score > resume_score:
                detected_type = "job_posting"
                result = await analyze_job_posting_json(sanitized_text)
            else:
                detected_type = "resume"
                result = await parse_resume_json(sanitized_text)

            return {
                "document_type": detected_type,
                "detection_confidence": {
                    "job_posting_score": job_score,
                    "resume_score": resume_score,
                },
                "data": result,
                "success": "error" not in result,
            }
        else:
            return {
                "error": f"Invalid document_type: {document_type}",
                "valid_types": ["resume", "job_posting", "auto"],
            }

    except Exception as e:
        logging.error(f"Document processing failed: {e}")
        return {
            "error": "Document processing failed",
            "error_type": type(e).__name__,
            "message": str(e),
        }


# Export the JSON-focused functions
__all__ = ["parse_resume_json", "analyze_job_posting_json", "process_document_json"]
