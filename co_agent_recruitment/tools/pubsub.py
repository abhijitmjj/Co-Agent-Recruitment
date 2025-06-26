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
from typing import Dict, List, Any, Union
import dotenv
import dirtyjson

from google.cloud import pubsub_v1

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
dotenv.load_dotenv()
# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
PROJECT_ID: str = os.getenv("PROJECT_ID", "YOUR_PROJECT_ID")
TOPIC_ID: str = os.getenv("TOPIC_ID", "co-agent-recruitment-events")
SUB_ID: str = os.getenv("SUB_ID", "co-agent-recruitment-events-sub")

_publisher = pubsub_v1.PublisherClient()
_topic_path = _publisher.topic_path(PROJECT_ID, TOPIC_ID)

_subscriber = pubsub_v1.SubscriberClient()
_sub_path = _subscriber.subscription_path(PROJECT_ID, SUB_ID)


def parse_dirty_json(text_blob: str) -> Union[Dict[str, Any], List[Any], None]:
    """
    Robustly finds and parses a JSON-like object from a string.

    This function is designed to handle strings that may contain a JSON object
    wrapped in other text (like markdown code blocks) or JSON that doesn't
    strictly adhere to the standard (e.g., uses single quotes).

    Args:
        text_blob: A string that is expected to contain a JSON object.

    Returns:
        A Python dictionary or list if a valid JSON object is found and parsed.
        Returns None if no valid JSON object can be found or if parsing fails.
    """
    if not isinstance(text_blob, str):
        logger.error("Input was not a string, cannot parse.")
        return None

    # --- 1. Find the start of a potential JSON object ---
    # A JSON object can start with '{' or a JSON array with '['
    try:
        first_brace = text_blob.index("{")
    except ValueError:
        first_brace = -1

    try:
        first_bracket = text_blob.index("[")
    except ValueError:
        first_bracket = -1

    # Determine the actual starting position of the JSON content
    if first_brace == -1 and first_bracket == -1:
        logger.warning("No JSON start character ('{' or '[') found in the text blob.")
        return None

    start_index = -1
    if first_brace != -1 and first_bracket != -1:
        start_index = min(first_brace, first_bracket)
    elif first_brace != -1:
        start_index = first_brace
    else:  # first_bracket != -1
        start_index = first_bracket

    # --- 2. Find the end of the potential JSON object ---
    # We look for the last '}' or ']'
    try:
        last_brace = text_blob.rindex("}")
    except ValueError:
        last_brace = -1

    try:
        last_bracket = text_blob.rindex("]")
    except ValueError:
        last_bracket = -1

    end_index = max(last_brace, last_bracket)

    if end_index == -1 or end_index < start_index:
        logger.warning(
            "Found a JSON start, but no corresponding end character ('}' or ']') found."
        )
        return None

    # --- 3. Extract and parse the potential JSON string ---
    potential_json = text_blob[start_index : end_index + 1]

    try:
        logger.info("Attempting to parse extracted text with dirtyjson...")
        # Use dirtyjson to parse the leniently formatted JSON
        parsed_data = dirtyjson.loads(potential_json)
        logger.info("Successfully parsed JSON data.")
        return json.loads(json.dumps(parsed_data))
    except dirtyjson.Error as e:
        logger.error(f"dirtyjson failed to parse the string. Error: {e}")
        logger.debug(f"Problematic string segment:\n{potential_json}")
        return None
    except Exception as e:
        # Catch any other unexpected errors during parsing
        logger.error(f"An unexpected error occurred during parsing. Error: {e}")
        return None


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
    
    Example payload:{
        "subscription": "projects/my-project/subscriptions/my-subscription",
        "message": {
            "@type": "type.googleapis.com/google.pubsub.v1.PubsubMessage",
            "attributes": {
            "attr1":"attr1-value"
            },
            "data": "dGVzdCBtZXNzYWdlIDM=",
            "messageId": "message-id",
            "publishTime":"2021-02-05T04:06:14.109Z"
        }
    }
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
        _subscriber.acknowledge(request={"subscription": _sub_path, "ack_ids": ack_ids})

    logger.info("Pulled %s messages", len(results))
    return results
