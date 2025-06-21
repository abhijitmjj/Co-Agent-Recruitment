import asyncio
import logging
import os
import re
import json
import dotenv
from google.cloud import pubsub_v1

dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict | None:
    """
    Strip Markdown code-block fences (``` / ```json) and return a dict.

    Returns None if the payload is not valid JSON.
    """
    if not text:
        return None

    cleaned = text.strip()

    # Remove ``` or ```json fences if present
    fenced = re.match(r"```(?:json)?\n(.*)```", cleaned, flags=re.DOTALL)
    if fenced:
        cleaned = fenced.group(1)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Failed to decode JSON from agent response.")
        return None


# Environment variables
PROJECT_ID = os.getenv("PROJECT_ID", "your-project")
SUB_ID = os.getenv("SUB_ID", "my-events-sub")


def on_msg(message):
    """Callback function to process incoming Pub/Sub messages."""
    event_type = message.attributes.get("event", "N/A")
    logger.info(f"Received event '{event_type}': {(message.data.decode('utf-8'))}")
    message.ack()


def main():
    """Starts the Pub/Sub subscriber and listens for messages."""
    subscriber = pubsub_v1.SubscriberClient()
    sub_path = subscriber.subscription_path(PROJECT_ID, SUB_ID)

    streaming_future = subscriber.subscribe(sub_path, callback=on_msg)
    logger.info(f"Listening for messages on {sub_path}...")

    try:
        # Block indefinitely, waiting for messages, and allowing for graceful shutdown.
        streaming_future.result()
        logger.info("Subscriber started successfully.")
    except KeyboardInterrupt:
        streaming_future.cancel()
        logger.info("Subscriber stopped.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        streaming_future.cancel()


if __name__ == "__main__":
    main()
