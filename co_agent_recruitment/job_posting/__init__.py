"""Job posting analysis agent for ADK."""

from co_agent_recruitment.job_posting.agent import (
    job_posting_agent,
    analyze_job_posting,
)

# Export the agent for ADK discovery
agent = job_posting_agent

__all__ = ["agent", "job_posting_agent", "analyze_job_posting"]
