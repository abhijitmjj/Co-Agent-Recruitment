import dotenv
import os
import re
import logging
import json, asyncio
from google.cloud import pubsub_v1
dotenv.load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


PROJECT_ID = os.getenv("PROJECT_ID", "YOUR_PROJECT_ID")
TOPIC_ID = os.getenv("TOPIC_ID", "YOUR_TOPIC_ID")
SUB_ID = os.getenv("SUB_ID")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

async def emit_event(name: str, payload: dict):
    """Generic helper you can call from anywhere in your app."""
    logger.info(f"Emitting event '{name}' with payload: {payload}")
    data = json.dumps(payload).encode()          # Pub/Sub wants bytes
    # Add small headers as message attributes
    future = publisher.publish(
        topic_path,
        data=data,
        event=name,                              # custom attribute
        content_type="application/json"
    )
    # Optionally await the server ack:
    message_id = await asyncio.wrap_future(future)
    logger.info(f"Event '{name}' published with message ID: {message_id}")
