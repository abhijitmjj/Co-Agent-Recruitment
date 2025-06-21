"""Tool package providing Pub/Sub helpers for agents.

Import convenience:
    from co_agent_recruitment.tools import emit_event, receive_events
"""

from __future__ import annotations

from .pubsub import emit_event, receive_events

__all__ = ["emit_event", "receive_events"]