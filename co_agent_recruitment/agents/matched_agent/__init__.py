"""
Matched Agent module for candidate-job compatibility analysis.
"""

from .agent import matched_agent, create_matched_agent, analyze_match_compatibility, MatchAnalysis

__all__ = [
    "matched_agent",
    "create_matched_agent", 
    "analyze_match_compatibility",
    "MatchAnalysis",
]