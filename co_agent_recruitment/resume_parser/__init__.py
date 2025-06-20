"""Resume parsing agent for ADK."""
from co_agent_recruitment.resume_parser.agent import (
    parse_resume_agent,
    parse_resume,
)

# Export the agent for ADK discovery
agent = parse_resume_agent

__all__ = ["agent", "parse_resume_agent", "parse_resume"]