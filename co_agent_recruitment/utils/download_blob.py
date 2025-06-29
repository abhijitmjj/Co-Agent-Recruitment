import os
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, initialize_app, storage
from google.cloud.storage import Blob
from pathlib import Path


from google import genai
from google.genai import types
import pathlib
import httpx


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def download_firebase_blob(
    bucket_name: str,
    blob_path: str,
    destination_path: str,
    credentials_path: Optional[str] = None,
) -> Optional[str]:
    """
    Download a blob from Firebase Storage to a local file.

    Args:
        bucket_name (str): Name of the Firebase Storage bucket (without gs:// prefix)
        blob_path (str): Path to the blob in Firebase Storage
        destination_path (str): Local file path to save the downloaded blob
        credentials_path (Optional[str]): Path to Firebase credentials JSON file.
            If None, uses default credentials (default: None)

    Returns:
        Optional[str]: Path to the downloaded file or None if download fails
    """
    try:
        # Remove gs:// prefix if present
        clean_bucket_name = (
            bucket_name.replace("gs://", "")
            if bucket_name.startswith("gs://")
            else bucket_name
        )

        # Initialize Firebase app if not already initialized
        if not len(firebase_admin._apps):
            if credentials_path:
                cred = credentials.Certificate(credentials_path)
                initialize_app(cred, {"storageBucket": clean_bucket_name})
            else:
                initialize_app(options={"storageBucket": clean_bucket_name})

        # Get the storage bucket
        bucket = storage.bucket()

        # Create blob object
        blob = bucket.blob(blob_path)

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Download the blob to the destination path
        blob.download_to_filename(destination_path)

        # Verify file exists
        if not os.path.exists(destination_path):
            logger.error(f"Failed to verify downloaded file at {destination_path}")
            return None

        logger.info(f"Successfully downloaded blob to {destination_path}")
        return destination_path

    except Exception as e:
        logger.error(f"Error downloading blob: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage
    bucket_name_raw = os.getenv(
        "GCS_BUCKET_NAME", "gs://gen-lang-client-0249131775.firebasestorage.app"
    )
    # Remove gs:// prefix if present
    bucket_name = (
        bucket_name_raw.replace("gs://", "")
        if bucket_name_raw.startswith("gs://")
        else bucket_name_raw
    )
    blob_path = Path(
        "raw-resumes/117086493216486298257/1750730759879-Abhijit_Gupta_Resume.pdf"
    ).as_posix()
    destination_path = "./downloaded_resume.pdf"

    downloaded_file = download_firebase_blob(
        bucket_name,
        blob_path,
        destination_path,
    )

    if downloaded_file:
        logger.info(f"Downloaded file: {downloaded_file}")
    else:
        logger.error("Failed to download the file.")

    client = genai.Client()

    # Retrieve and encode the PDF byte
    filepath = pathlib.Path(destination_path)

    prompt = "Extract the text from the PDF"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type="application/pdf",
            ),
            prompt,
        ],
    )
    logger.info(response.text)
