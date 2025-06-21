"""
Pub/Sub tools that can be imported and attached to ADK agents.

These helpers wrap Google Cloud Pub/Sub so they can easily be used
inside an agent execution or from arbitrary application code.

Typical usage from an ADK agent:

    from co_agent_recruitment.tools import emit_event

    await emit_event("MyEvent", {"foo": "bar"})

You can also pull messages synchronously from the subscription by
calling ``receive_events`` – this is useful for unit-tests or when an
agent needs to consume events produced by other services.

Environment variables used
--------------------------
PROJECT_ID   – Google Cloud project id (defaults to "YOUR_PROJECT_ID")
TOPIC_ID     – Pub/Sub topic id  (defaults to "YOUR_TOPIC_ID")
SUB_ID       – Pub/Sub subscription id (defaults to "YOUR_SUBSCRIPTION_ID")
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Dict, List
import dotenv

from google.cloud import pubsub_v1

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
dotenv.load_dotenv()
# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
PROJECT_ID: str = os.getenv("PROJECT_ID", "YOUR_PROJECT_ID")
TOPIC_ID: str = os.getenv("TOPIC_ID", "YOUR_TOPIC_ID")
SUB_ID: str = os.getenv("SUB_ID", "YOUR_SUBSCRIPTION_ID")

_publisher = pubsub_v1.PublisherClient()

# Parse TOPIC_ID to ensure it's the short name
actual_topic_id = TOPIC_ID
if '/' in TOPIC_ID:  # Check if it might be a full path
    parts = TOPIC_ID.split('/')
    if len(parts) == 4 and parts[0] == "projects" and parts[2] == "topics":
        # Full path like projects/PROJECT_ID/topics/TOPIC_SHORT_ID
        if parts[1] != PROJECT_ID:
            logger.warning(
                f"Project ID in TOPIC_ID ('{parts[1]}') does not match "
                f"PROJECT_ID env var ('{PROJECT_ID}'). Using PROJECT_ID env var for path construction."
            )
        actual_topic_id = parts[3]
        logger.info(f"Extracted short topic ID '{actual_topic_id}' from full path '{TOPIC_ID}'.")
    else:
        # Not the expected full path format, assume last part is the ID as a fallback
        logger.warning(
            f"TOPIC_ID '{TOPIC_ID}' contains '/' but is not in 'projects/PROJECT/topics/TOPIC' format. "
            f"Using last part '{parts[-1]}' as topic ID. Please verify environment variable."
        )
        actual_topic_id = parts[-1]
_topic_path = _publisher.topic_path(PROJECT_ID, actual_topic_id)

_subscriber = pubsub_v1.SubscriberClient()

# Parse SUB_ID to ensure it's the short name
actual_sub_id = SUB_ID
if '/' in SUB_ID:  # Check if it might be a full path
    parts = SUB_ID.split('/')
    if len(parts) == 4 and parts[0] == "projects" and parts[2] == "subscriptions":
        # Full path like projects/PROJECT_ID/subscriptions/SUB_SHORT_ID
        if parts[1] != PROJECT_ID:
            logger.warning(
                f"Project ID in SUB_ID ('{parts[1]}') does not match "
                f"PROJECT_ID env var ('{PROJECT_ID}'). Using PROJECT_ID env var for path construction."
            )
        actual_sub_id = parts[3]
        logger.info(f"Extracted short subscription ID '{actual_sub_id}' from full path '{SUB_ID}'.")
    else:
        # Not the expected full path format, assume last part is the ID as a fallback
        logger.warning(
            f"SUB_ID '{SUB_ID}' contains '/' but is not in 'projects/PROJECT/subscriptions/SUBSCRIPTION' format. "
            f"Using last part '{parts[-1]}' as subscription ID. Please verify environment variable."
        )
        actual_sub_id = parts[-1]
_sub_path = _subscriber.subscription_path(PROJECT_ID, actual_sub_id)


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
async def emit_event(name: str, payload: Dict) -> str:
    """
    Publish an *event* message to the configured Pub/Sub topic.

    Args:
        name: Logical event name (will be written to the ``event`` attribute).
        payload: JSON-serialisable payload.

    Returns:
        The message id assigned by Pub/Sub.
    """
    logger.debug("Emit event %s – payload=%s", name, payload)
    data = json.dumps(payload).encode()  # Pub/Sub requires bytes

    future = _publisher.publish(
        _topic_path,
        data=data,
        event=name,
        content_type="application/json",
    )
    message_id: str = await asyncio.wrap_future(future)
    logger.info("Event %s published (message id=%s)", name, message_id)
    return message_id


async def receive_events(max_messages: int = 5, timeout: int = 5) -> List[Dict]:
    """
    Pull events from the configured Pub/Sub subscription.

    This is a convenience *tool* for agents/tests that need to consume events.

    Args:
        max_messages: How many messages to retrieve in one pull.
        timeout: Pull deadline in **seconds**.

    Returns:
        List of dictionaries with keys: ``message_id``, ``event``, ``data``.
    """
    logger.debug("Pulling up to %s messages from %s", max_messages, _sub_path)
    response = _subscriber.pull(
        request={
            "subscription": _sub_path,
            "max_messages": max_messages,
        },
        timeout=timeout,
    )

    results: List[Dict] = []
    ack_ids = []

    for received in response.received_messages:
        msg = received.message
        ack_ids.append(received.ack_id)

        try:
            decoded = json.loads(msg.data.decode())
        except json.JSONDecodeError:
            decoded = msg.data.decode()

        results.append(
            {
                "message_id": msg.message_id,
                "event": msg.attributes.get("event"),
                "data": decoded,
            }
        )

    # Always ack – tooling helper not streaming listener
    if ack_ids:
        _subscriber.acknowledge(
            request={"subscription": _sub_path, "ack_ids": ack_ids}
        )

    logger.info("Pulled %s messages", len(results))
    return results