"""
Matched Agent implementation for candidate-job compatibility analysis.

This agent uses Firestore query tools to retrieve and analyze candidate-job matches,
providing detailed compatibility scoring and recommendations.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from pydantic import BaseModel, Field

from ..tools.firestore_query import (
    query_firestore,
    get_document_by_id,
    create_document,
    retrieve_match_context,
)
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MatchAnalysis(BaseModel):
    """Data model for match analysis results."""
    
    match_id: str = Field(description="Unique identifier for this match")
    candidate_id: str = Field(description="Candidate document ID")
    job_id: str = Field(description="Job document ID")
    overall_score: int = Field(description="Overall compatibility score (0-100)")
    component_scores: Dict[str, int] = Field(description="Breakdown of scores by category")
    analysis: Dict[str, List[str]] = Field(description="Detailed analysis with strengths, concerns, recommendations")
    next_steps: str = Field(description="Recommended next steps")
    confidence_level: str = Field(description="Confidence level: Low, Medium, High")
    analyzed_at: str = Field(description="ISO timestamp of analysis")
    analyzed_by: str = Field(default="matched_agent", description="Agent that performed the analysis")


def get_model_name() -> str:
    """Get AI model name from environment variable with fallback."""
    return os.getenv("MODEL_ID", "gemini-2.5-flash")


async def analyze_match_compatibility(
    candidate_id: str, 
    job_id: str
) -> Dict[str, Any]:
    """
    Analyze compatibility between a candidate and job using Firestore data.
    
    Args:
        candidate_id: Candidate document ID
        job_id: Job document ID
    
    Returns:
        Match analysis results as dictionary
    """
    try:
        logger.info(f"Starting match analysis for candidate {candidate_id} and job {job_id}")
        
        # Retrieve both documents
        match_context = retrieve_match_context(candidate_id, job_id)
        candidate = match_context.get("candidate")
        job = match_context.get("job")
        
        if not candidate or not job:
            return {
                "error": "Could not retrieve candidate or job data",
                "candidate_found": candidate is not None,
                "job_found": job is not None
            }
        
        # Create match analysis
        analysis = MatchAnalysis(
            match_id=f"match_{candidate_id}_{job_id}",
            candidate_id=candidate_id,
            job_id=job_id,
            overall_score=0,  # Will be calculated
            component_scores={},
            analysis={"strengths": [], "concerns": [], "recommendations": []},
            next_steps="Analysis pending",
            confidence_level="Medium",
            analyzed_at=datetime.now().isoformat()
        )
        
        # Analyze skills compatibility
        candidate_skills = candidate.get("skills", [])
        required_skills = job.get("required_skills", [])
        preferred_skills = job.get("preferred_skills", [])
        
        skill_matches = len(set(candidate_skills) & set(required_skills))
        skill_score = min(100, int((skill_matches / max(len(required_skills), 1)) * 100))
        
        # Analyze experience
        candidate_experience = candidate.get("years_experience", 0)
        required_experience = job.get("required_experience", 0)
        experience_score = min(100, int((candidate_experience / max(required_experience, 1)) * 100))
        
        # Analyze salary compatibility
        candidate_salary = candidate.get("salary_expectation", 0)
        job_salary = job.get("salary", 0)
        salary_compatible = abs(candidate_salary - job_salary) / max(job_salary, 1) <= 0.2
        salary_score = 90 if salary_compatible else 60
        
        # Calculate component scores
        analysis.component_scores = {
            "skills": skill_score,
            "experience": experience_score,
            "compensation": salary_score,
            "location": 85,  # Default for now
            "culture_fit": 75  # Default for now
        }
        
        # Calculate overall score (weighted average)
        weights = {"skills": 0.25, "experience": 0.20, "compensation": 0.20, "location": 0.15, "culture_fit": 0.20}
        analysis.overall_score = int(sum(analysis.component_scores[k] * weights[k] for k in analysis.component_scores))
        
        # Generate analysis insights
        if skill_score >= 80:
            analysis.analysis["strengths"].append(f"Strong skills match: {skill_matches}/{len(required_skills)} required skills")
        else:
            analysis.analysis["concerns"].append(f"Limited skills match: {skill_matches}/{len(required_skills)} required skills")
        
        if experience_score >= 80:
            analysis.analysis["strengths"].append(f"Experience aligns well: {candidate_experience} years vs {required_experience} required")
        else:
            analysis.analysis["concerns"].append(f"Experience gap: {candidate_experience} years vs {required_experience} required")
        
        if salary_compatible:
            analysis.analysis["strengths"].append("Salary expectations align with job offer")
        else:
            analysis.analysis["concerns"].append("Salary expectations may need negotiation")
        
        # Generate recommendations
        if analysis.overall_score >= 80:
            analysis.analysis["recommendations"].append("Recommend proceeding with interview process")
            analysis.next_steps = "Strong match - schedule interview"
            analysis.confidence_level = "High"
        elif analysis.overall_score >= 60:
            analysis.analysis["recommendations"].append("Consider as potential candidate with reservations")
            analysis.next_steps = "Moderate match - evaluate further"
            analysis.confidence_level = "Medium"
        else:
            analysis.analysis["recommendations"].append("Not recommended for this position")
            analysis.next_steps = "Weak match - consider other opportunities"
            analysis.confidence_level = "Low"
        
        logger.info(f"Match analysis completed with overall score: {analysis.overall_score}")
        return analysis.dict()
        
    except Exception as e:
        logger.error(f"Error in match analysis: {e}")
        return {"error": str(e)}


async def matched_agent_before_callback(callback_context: CallbackContext) -> None:
    """Callback executed before matched agent runs."""
    callback_context.state["matched_agent_start_time"] = datetime.now().isoformat()
    logger.info(
        f"Matched agent session initialized for user: {getattr(callback_context, '_invocation_context').session.user_id}"
    )


async def matched_agent_after_callback(callback_context: CallbackContext) -> None:
    """Callback executed after matched agent runs."""
    callback_context.state["matched_agent_end_time"] = datetime.now().isoformat()
    logger.info(
        f"Matched agent session completed for user: {getattr(callback_context, '_invocation_context').session.user_id}"
    )


def create_matched_agent() -> Agent:
    """Creates and returns the matched agent."""
    return Agent(
        name="matched_agent",
        model=get_model_name(),
        description="Agent that analyzes candidate-job compatibility using Firestore data",
        instruction=(
            "You are the Matched Agent responsible for analyzing candidate-job compatibility. "
            "Use the Firestore query tools to retrieve candidate profiles and job descriptions, "
            "then provide detailed compatibility analysis with scoring and recommendations. "
            "Always base your analysis on actual data retrieved from Firestore. "
            "Provide structured, actionable insights for hiring decisions."
        ),
        tools=[
            query_firestore,
            get_document_by_id,
            create_document,
            retrieve_match_context,
            analyze_match_compatibility,
        ],
        output_key="match_analysis",
        before_agent_callback=matched_agent_before_callback,
        after_agent_callback=matched_agent_after_callback,
    )


# Create agent instance
matched_agent = create_matched_agent()

# Export for use in other modules
__all__ = [
    "matched_agent",
    "create_matched_agent",
    "analyze_match_compatibility",
    "MatchAnalysis",
]