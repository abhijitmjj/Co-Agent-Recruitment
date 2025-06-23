import functions_framework
import json
import base64
import os
import logging

# Import and initialize the Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore
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
    firebase_admin.initialize_app(cred, {
        'projectId': os.environ.get('GCP_PROJECT'),
    })

db = firestore.client()

# Decorator to register the function as a CloudEvent handler for Pub/Sub
@functions_framework.cloud_event
def save_resume_to_firestore_v2(cloud_event):
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
        parsed_resume: dict = json.loads(payload_str)
        logger.info(f"Received payload: {parsed_resume}")
        pure_resume = parsed_resume.get("response", {}).get("parse_resume_response", {}).get("resume_data", {})
        logger.info(f"Parsed resume data: {pure_resume}")
        uid = parsed_resume.get("user_id", "")
        session_id = parsed_resume.get("session_id", "")



    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Error decoding or parsing Pub/Sub message: {e}")
        # Exit gracefully if the message format is unexpected.
        return

    logger.info(f"Received parsed resume for: {parsed_resume.get('fullName', 'N/A')}")

    try:
        # The Firestore logic remains exactly the same.
        doc_ref = db.collection('candidates').add({
            "resume_data": pure_resume,
            "user_id": uid,
            "session_id": session_id,
        })
        logger.info(f"Successfully created document with ID: {doc_ref[1].id}")

    except Exception as e:
        logger.error(f"Error writing to Firestore: {e}")
        # Raising the exception signals a failure for potential retries.
        raise
# gcloud functions deploy save_resume_to_firestore_v2 \
# --gen2 \
# --runtime python313 \
# --region asia-south1 \
# --source . \
# --entry-point save_resume_to_firestore_v2 \
# --trigger-topic co-agent-recruitment-events