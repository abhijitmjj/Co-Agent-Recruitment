"""
Tests for the matcher agent.
"""

import pytest
from unittest.mock import patch, AsyncMock
from co_agent_recruitment.matcher.agent import (
    generate_compatibility_score,
    CompatibilityScore,
)


@pytest.mark.asyncio
async def test_generate_compatibility_score_success():
    """Test that the matcher agent can generate a compatibility score successfully."""
    resume_data = {"skills": ["Python", "FastAPI"]}
    job_posting_data = {"required_skills": ["Python", "FastAPI", "React"]}

    with patch("co_agent_recruitment.matcher.agent.PydanticAgent") as mock_agent_class:
        mock_agent_instance = AsyncMock()
        mock_agent_class.return_value = mock_agent_instance

        mock_run_result = AsyncMock()
        mock_run_result.output = CompatibilityScore(
            compatibility_score=80,
            summary="Good match",
            matching_skills=["Python", "FastAPI"],
            missing_skills=["React"],
        )
        mock_agent_instance.run.return_value = mock_run_result

        result = await generate_compatibility_score(resume_data, job_posting_data)

        assert result["operation_status"] == "success"
        assert result["compatibility_data"]["compatibility_score"] == 80


@pytest.mark.asyncio
async def test_generate_compatibility_score_error():
    """Test that the matcher agent handles errors gracefully."""
    resume_data = {"skills": ["Python", "FastAPI"]}
    job_posting_data = {"required_skills": ["Python", "FastAPI", "React"]}

    with patch("co_agent_recruitment.matcher.agent.PydanticAgent") as mock_agent_class:
        mock_agent_instance = AsyncMock()
        mock_agent_class.return_value = mock_agent_instance
        mock_agent_instance.run.side_effect = Exception("AI service error")

        result = await generate_compatibility_score(resume_data, job_posting_data)

        assert result["operation_status"] == "error"
        assert "AI service error" in result["session_info"]["error"]
