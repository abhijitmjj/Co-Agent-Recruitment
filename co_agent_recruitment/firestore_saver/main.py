import functions_framework
import json
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
        payload_str = cloud_event.data["message"]["data"]
        parsed_resume = json.loads(payload_str)
        
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        logger.error(f"Error decoding or parsing Pub/Sub message: {e}")
        # Exit gracefully if the message format is unexpected.
        return

    logger.info(f"Received parsed resume for: {parsed_resume.get('fullName', 'N/A')}")

    try:
        # The Firestore logic remains exactly the same.
        doc_ref = db.collection('candidates').add(parsed_resume)
        logger.info(f"Successfully created document with ID: {doc_ref[1].id}")

    except Exception as e:
        logger.error(f"Error writing to Firestore: {e}")
        # Raising the exception signals a failure for potential retries.
        raise