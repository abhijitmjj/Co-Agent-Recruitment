"""Tool package providing Pub/Sub and Firestore helpers for agents.

Import convenience:
    from co_agent_recruitment.tools import emit_event, receive_events, query_firestore
"""

from __future__ import annotations

from .pubsub import emit_event, receive_events
from .firestore_query import query_firestore, get_document, retrieve_match_context

__all__ = [
    # Pub/Sub tools
    "emit_event", 
    "receive_events",
    
    # Firestore tools
    "query_firestore",
    "get_document", 
    "retrieve_match_context",
]
