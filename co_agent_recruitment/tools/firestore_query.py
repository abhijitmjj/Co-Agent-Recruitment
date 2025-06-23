"""
Firestore query tool for agentic access to Firestore collections.

This tool provides a clean interface for agents to query Firestore collections
with filtering, projection, and exponential backoff for reliability.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    try:
        # Try to use service account key if available
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': os.environ.get('GOOGLE_CLOUD_PROJECT', os.environ.get('PROJECT_ID', 'co-agent-recruitment')),
        })
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.warning(f"Firebase Admin SDK initialization failed (expected in test environments): {e}")
        # Set a flag to indicate we're in a test environment
        os.environ['FIREBASE_TEST_MODE'] = 'true'

# Get Firestore client
try:
    db = firestore.client()
    logger.info("Firestore client initialized successfully")
except Exception as e:
    logger.warning(f"Firestore client initialization failed (expected in test environments): {e}")
    db = None


def exponential_backoff_retry(max_retries: int = 3, initial_delay: float = 1.0):
    """Decorator for exponential backoff retry logic."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Final attempt failed for {func.__name__}: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
            return None
        return wrapper
    return decorator


@exponential_backoff_retry()
def query_firestore(
    collection: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    projection: Optional[List[str]] = None,
    limit: Optional[int] = None,
    order_by: Optional[str] = None,
    order_direction: str = "asc"
) -> List[Dict[str, Any]]:
    """
    Query Firestore collections with optional filtering and projection.
    
    Args:
        collection: The Firestore collection name (e.g., "candidates", "jobs")
        filter_dict: Dictionary of field filters. Supports:
            - Simple equality: {"status": "active"}
            - Array contains: {"skills": {"array-contains": "Python"}}
            - Array contains any: {"skills": {"array-contains-any": ["Python", "Java"]}}
            - Comparisons: {"age": {">=": 18}}
            - Range queries: {"salary": {">=": 50000, "<=": 100000}}
        projection: List of field names to include in results
        limit: Maximum number of documents to return
        order_by: Field to order results by
        order_direction: "asc" or "desc"
    
    Returns:
        List of documents as dictionaries, each including an "id" field
        with the document ID.
    
    Example:
        # Get all active candidates
        candidates = query_firestore("candidates", {"status": "active"})
        
        # Get candidates with Python skills
        python_devs = query_firestore(
            "candidates", 
            {"skills": {"array-contains": "Python"}},
            projection=["name", "skills", "experience"]
        )
        
        # Get jobs with salary range
        jobs = query_firestore(
            "jobs",
            {"salary": {">=": 50000, "<=": 100000}},
            limit=10,
            order_by="salary",
            order_direction="desc"
        )
    """
    if db is None:
        raise RuntimeError("Firestore client not initialized. Check Firebase credentials.")
        
    try:
        logger.info(f"Querying Firestore collection: {collection}")
        
        # Get collection reference
        collection_ref = db.collection(collection)
        query = collection_ref
        
        # Apply filters
        if filter_dict:
            for field, value in filter_dict.items():
                if isinstance(value, dict):
                    # Handle complex filter operations
                    for op, op_value in value.items():
                        if op == "array-contains":
                            query = query.where(field, "array_contains", op_value)
                        elif op == "array-contains-any":
                            query = query.where(field, "array_contains_any", op_value)
                        elif op in ["<", "<=", "==", "!=", ">=", ">"]:
                            query = query.where(field, op, op_value)
                        else:
                            logger.warning(f"Unsupported filter operation: {op}")
                else:
                    # Simple equality filter
                    query = query.where(field, "==", value)
        
        # Apply ordering
        if order_by:
            direction = firestore.Query.DESCENDING if order_direction.lower() == "desc" else firestore.Query.ASCENDING
            query = query.order_by(order_by, direction=direction)
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        # Apply projection (select specific fields)
        if projection:
            query = query.select(projection)
        
        # Execute query
        docs = query.stream()
        
        # Convert to list of dictionaries
        results = []
        for doc in docs:
            doc_dict = doc.to_dict()
            if doc_dict is None:
                doc_dict = {}
            doc_dict["id"] = doc.id  # Always include document ID
            results.append(doc_dict)
        
        logger.info(f"Successfully retrieved {len(results)} documents from {collection}")
        return results
        
    except Exception as e:
        logger.error(f"Error querying Firestore collection {collection}: {e}")
        raise


def get_document_by_id(collection: str, document_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single document by its ID.
    
    Args:
        collection: The Firestore collection name
        document_id: The document ID
    
    Returns:
        Document as dictionary with "id" field, or None if not found
    """
    if db is None:
        raise RuntimeError("Firestore client not initialized. Check Firebase credentials.")
        
    try:
        logger.info(f"Getting document {document_id} from collection {collection}")
        
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_dict = doc.to_dict()
            if doc_dict is None:
                doc_dict = {}
            doc_dict["id"] = doc.id
            logger.info(f"Successfully retrieved document {document_id}")
            return doc_dict
        else:
            logger.warning(f"Document {document_id} not found in collection {collection}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting document {document_id} from {collection}: {e}")
        raise


def create_document(collection: str, data: Dict[str, Any], document_id: Optional[str] = None) -> str:
    """
    Create a new document in Firestore.
    
    Args:
        collection: The Firestore collection name
        data: Document data as dictionary
        document_id: Optional document ID. If not provided, Firestore will generate one
    
    Returns:
        The document ID of the created document
    """
    if db is None:
        raise RuntimeError("Firestore client not initialized. Check Firebase credentials.")
        
    try:
        logger.info(f"Creating document in collection {collection}")
        
        if document_id:
            # Use specific document ID
            doc_ref = db.collection(collection).document(document_id)
            doc_ref.set(data)
            created_id = document_id
        else:
            # Let Firestore generate ID
            doc_ref = db.collection(collection).add(data)
            created_id = doc_ref[1].id
        
        logger.info(f"Successfully created document {created_id} in collection {collection}")
        return created_id
        
    except Exception as e:
        logger.error(f"Error creating document in collection {collection}: {e}")
        raise


# Tool registration for ADK agents
def register_firestore_tools():
    """
    Register Firestore tools for use with ADK agents.
    Returns a list of tool functions that can be used with Agent.tools.
    """
    return [
        {
            "name": "query_firestore",
            "description": "Query Firestore collections with filtering and projection support",
            "function": query_firestore,
        },
        {
            "name": "get_document_by_id", 
            "description": "Get a single Firestore document by its ID",
            "function": get_document_by_id,
        },
        {
            "name": "create_document",
            "description": "Create a new document in Firestore",
            "function": create_document,
        }
    ]


# Convenience function for matched agents
def retrieve_match_context(candidate_id: str, job_id: str) -> Dict[str, Any]:
    """
    Retrieve both candidate and job documents for matching context.
    
    Args:
        candidate_id: Candidate document ID
        job_id: Job document ID
    
    Returns:
        Dictionary with 'candidate' and 'job' keys containing the respective documents
    """
    try:
        logger.info(f"Retrieving match context for candidate {candidate_id} and job {job_id}")
        
        candidate = get_document_by_id("candidates", candidate_id)
        job = get_document_by_id("jobs", job_id)
        
        context = {
            "candidate": candidate,
            "job": job,
            "match_retrieved_at": time.time()
        }
        
        logger.info("Successfully retrieved match context")
        return context
        
    except Exception as e:
        logger.error(f"Error retrieving match context: {e}")
        raise


# Export public API
__all__ = [
    "query_firestore",
    "get_document_by_id", 
    "create_document",
    "retrieve_match_context",
    "register_firestore_tools"
]