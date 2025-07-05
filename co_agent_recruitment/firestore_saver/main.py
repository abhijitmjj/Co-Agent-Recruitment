import functions_framework
import json
import base64
import os
import logging

# Import and initialize the Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import ValidationError
from co_agent_recruitment.events import (
    ParseResumeEvent,
    ParseJobPostingEvent,
    CompatibilityScoreEvent,
)
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure logging with a clear format
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG to see detailed event logs
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# This global initialization is still the correct pattern.
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(
        cred,
        {
            "projectId": os.environ.get("GCP_PROJECT"),
        },
    )

db = firestore.client()


def save_resume(event: ParseResumeEvent):
    """Saves resume data to Firestore."""
    try:
        doc_ref = db.collection("candidates").add(event.model_dump())
        logger.info(
            f"Successfully created document with ID: {doc_ref[1].id} in candidates collection"
        )
    except Exception as e:
        logger.error(f"Error writing resume to Firestore: {e}")
        raise


def save_job_posting(event: ParseJobPostingEvent):
    """Saves job posting data to Firestore."""
    try:
        doc_ref = db.collection("jobPostings").add(event.model_dump())
        logger.info(
            f"Successfully created document with ID: {doc_ref[1].id} in jobPostings collection"
        )
    except Exception as e:
        logger.error(f"Error writing job posting to Firestore: {e}")
        raise


def save_compatibility_score(event: CompatibilityScoreEvent):
    """Saves compatibility score data to Firestore."""
    try:
        doc_ref = db.collection("compatibility_scores").add(event.model_dump())
        logger.info(
            f"Successfully created document with ID: {doc_ref[1].id} in compatibility_scores collection"
        )
    except Exception as e:
        logger.error(f"Error writing compatibility score to Firestore: {e}")
        raise


# Decorator to register the function as a CloudEvent handler for Pub/Sub
@functions_framework.cloud_event
def save_to_firestore(cloud_event):
    """
    Triggered by a message on a Pub/Sub topic and saves data to Firestore.
    This version uses the modern functions_framework.

    Args:
         cloud_event (cloudevents.http.CloudEvent): The event payload.
    """
    logger.info(f"Processing function trigger for messageId: {cloud_event['id']}")

    try:
        raw_data = cloud_event.data.get("message", {}).get("data", "")
        # Decode the Pub/Sub message data from base64
        payload_bytes = base64.b64decode(raw_data)
        payload_str = payload_bytes.decode("utf-8")
        data: dict = json.loads(payload_str)
        logger.info(f"Received payload: {data}")

        event_name = data.get("name", "")

        if event_name == "ParseResumeEvent":
            event = ParseResumeEvent(**data["payload"])
            save_resume(event)
        elif event_name == "ParseJobPostingEvent":
            event = ParseJobPostingEvent(**data["payload"])
            save_job_posting(event)
        elif event_name == "CompatibilityScoreEvent":
            event = CompatibilityScoreEvent(**data["payload"])
            save_compatibility_score(event)
        else:
            logger.warning(f"Unknown event type: {event_name}")

    except (
        ValidationError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as e:
        logger.error(f"Error decoding or parsing Pub/Sub message: {e}")
        # Exit gracefully if the message format is unexpected.
        return
