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
def save_data_to_firestore(cloud_event):
    """
    Triggered by a message on a Pub/Sub topic and saves resume or job posting data to Firestore.
    
    Args:
         cloud_event (cloudevents.http.CloudEvent): The event payload.
    """
    logger.info(f"Processing function trigger for messageId: {cloud_event['id']}")

    try:
        raw_data = cloud_event.data.get("message", {}).get("data", "")
        payload_bytes = base64.b64decode(raw_data)
        payload_str = payload_bytes.decode("utf-8")
        message_data: dict = json.loads(payload_str) # This is the {event_name, payload} object
        logger.info(f"Received message data: {message_data}")

        event_name = message_data.get("event_name")
        actual_payload = message_data.get("payload", {})

        if not event_name or not actual_payload:
            logger.error("Missing event_name or payload in message data.")
            return

        user_id = actual_payload.get("user_id", "") # Common field
        session_id = actual_payload.get("session_id", "") # Common field
        data_to_save = {}
        collection_name = ""
        log_identifier = "N/A"

        if event_name == "candidate_submitted":
            logger.info(f"Processing 'candidate_submitted' event for user: {user_id}")
            collection_name = 'candidates'
            data_to_save = {
                "fullName": actual_payload.get("fullName"),
                "skills": actual_payload.get("skills"),
                "experienceSummary": actual_payload.get("experienceSummary"),
                "locationPreference": actual_payload.get("locationPreference"),
                "aiSummary": actual_payload.get("aiSummary"),
                "user_id": user_id,
                "session_id": session_id,
                "candidate_id": actual_payload.get("id"), # from newCandidate.id
                "event_name": event_name,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            log_identifier = data_to_save.get('fullName', user_id)

        elif event_name == "job_description_submitted":
            logger.info(f"Processing 'job_description_submitted' event for user: {user_id}")
            collection_name = 'job_postings'
            
            orchestrator_data = actual_payload.get("processedDataFromOrchestrator", {})
            job_posting_result = orchestrator_data.get("job_posting_result", {})
            # session_info_from_orchestrator = orchestrator_data.get("session_information", {})

            data_to_save = {
                "jobTitle": actual_payload.get("jobTitle"),
                "responsibilities": actual_payload.get("responsibilities"),
                "requiredSkills": actual_payload.get("requiredSkills"),
                "companyName": actual_payload.get("companyName"),
                "user_id": user_id,
                "session_id": session_id,
                "job_id": actual_payload.get("id"), # from newJob.id
                "orchestrator_processed_data": job_posting_result, # Save the parsed data from orchestrator
                # "orchestrator_session_info": session_info_from_orchestrator,
                "event_name": event_name,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            log_identifier = data_to_save.get('jobTitle', user_id)
        
        else:
            logger.warning(f"Received unhandled event_name: {event_name}. Payload: {actual_payload}")
            return # Exit if event type is not handled

        if not collection_name or not data_to_save:
            logger.error(f"Failed to prepare data for saving for event: {event_name}")
            return

        logger.info(f"Attempting to save data for '{log_identifier}' to collection '{collection_name}'.")

    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Error decoding or parsing Pub/Sub message: {e}")
        # Exit gracefully if the message format is unexpected.
        return

    # logger.info(f"Received parsed resume for: {parsed_resume.get('fullName', 'N/A')}") # Old log

    try:
        # Firestore logic adapted
        doc_ref = db.collection(collection_name).add(data_to_save)
        logger.info(f"Successfully created document in '{collection_name}' with ID: {doc_ref[1].id} for {log_identifier}")

    except Exception as e:
        logger.error(f"Error writing to Firestore: {e}")
        # Raising the exception signals a failure for potential retries.
        raise
# gcloud functions deploy save_data_to_firestore \
# --gen2 \
# --runtime python313 \
# --region asia-south1 \
# --source . \
# --entry-point save_data_to_firestore \
# --trigger-topic co-agent-recruitment-events