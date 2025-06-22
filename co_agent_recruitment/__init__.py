"""Co-Agent Recruitment package with ADK agent exports."""

from co_agent_recruitment.agent import (
    root_agent,
    parse_resume_agent,
    job_posting_agent,
    get_or_create_session_for_user,
)

# Export the main agent for ADK discovery
agent = root_agent

__all__ = [
    "agent",
    "root_agent",
    "parse_resume_agent",
    "job_posting_agent",
    "get_or_create_session_for_user",
]
