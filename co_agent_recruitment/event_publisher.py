"""
Deprecated shim for backward compatibility.

`co_agent_recruitment.event_publisher.emit_event` has moved to
`co_agent_recruitment.tools.pubsub.emit_event`.

Importing from this module will continue to work but will raise a
`DeprecationWarning`.  New code should import from the tools package:

    from co_agent_recruitment.tools.pubsub import emit_event
"""

from __future__ import annotations

import warnings
from typing import Dict, Any

from co_agent_recruitment.tools.pubsub import emit_event as _emit_event


__all__ = ["emit_event"]


def emit_event(name: str, payload: Dict[str, Any]):
    """Forwarder that calls the new implementation in tools.pubsub."""
    warnings.warn(
        "co_agent_recruitment.event_publisher is deprecated; "
        "use co_agent_recruitment.tools.pubsub instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _emit_event(name, payload)
