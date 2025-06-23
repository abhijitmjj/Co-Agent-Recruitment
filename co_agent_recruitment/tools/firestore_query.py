"""
Firestore query tool for ADK agents.

This module provides an agentic tool for querying Firestore collections,
allowing agents to fetch documents with filtering and projection capabilities.
It reuses the existing Firebase Admin initialization patterns and includes
exponential backoff for robust error handling.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

import dotenv
import firebase_admin
from firebase_admin import credentials, firestore

from co_agent_recruitment.utils.retry import firestore_retry

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global Firestore client - initialized once
_db: Optional[firestore.Client] = None


def _get_firestore_client() -> firestore.Client:
    """
    Get or initialize the Firestore client.
    
    Reuses the existing Firebase Admin initialization pattern from
    co_agent_recruitment.firestore_saver.main
    
    Returns:
        Firestore client instance
    """
    global _db
    
    if _db is None:
        # Initialize Firebase Admin if not already initialized
        if not firebase_admin._apps:
            # Try to get credentials from environment
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                # Use service account credentials
                cred = credentials.ApplicationDefault()
            elif os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY'):
                # Use service account key from environment variable
                import json
                service_key = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY'))
                if service_key.get('private_key') and isinstance(service_key['private_key'], str):
                    service_key['private_key'] = service_key['private_key'].replace('\\n', '\n')
                cred = credentials.Certificate(service_key)
            else:
                # Fall back to Application Default Credentials
                cred = credentials.ApplicationDefault()
            
            # Initialize with project ID
            project_id = os.getenv('PROJECT_ID') or os.getenv('GCP_PROJECT')
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
            logger.info(f"Initialized Firebase Admin with project ID: {project_id}")
        
        _db = firestore.client()
        logger.info("Firestore client initialized")
    
    return _db


@firestore_retry
def query_firestore(
    collection: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    projection: Optional[List[str]] = None,
    limit: Optional[int] = None,
    order_by: Optional[str] = None,
    order_direction: str = "ASCENDING"
) -> List[Dict[str, Any]]:
    """
    Query Firestore collection with optional filtering and projection.
    
    This function provides an agentic interface for Firestore queries,
    supporting common query patterns like filtering, projection, and ordering.
    
    Args:
        collection: Name of the Firestore collection to query
        filter_dict: Optional dictionary of field filters. Supports:
            - Simple equality: {"field": "value"}
            - Array contains: {"field": {"array-contains": "value"}}
            - Array contains any: {"field": {"array-contains-any": ["val1", "val2"]}}
            - Comparison operators: {"field": {">=": 10}}
        projection: Optional list of field names to include in results
        limit: Optional maximum number of documents to return
        order_by: Optional field name to order results by
        order_direction: Sort direction, either "ASCENDING" or "DESCENDING"
    
    Returns:
        List of document dictionaries, each containing document data and metadata
    
    Raises:
        ValueError: If collection name is invalid or filter format is incorrect
        Exception: If Firestore query fails
    
    Examples:
        # Get all candidates
        candidates = query_firestore("candidates")
        
        # Get specific candidate by ID
        candidate = query_firestore("candidates", {"__name__": "candidate_123"})
        
        # Get candidates with specific skills
        skilled_candidates = query_firestore(
            "candidates", 
            {"skills": {"array-contains-any": ["python", "javascript"]}}
        )
        
        # Get recent job postings with projection
        recent_jobs = query_firestore(
            "jobs",
            {"created_at": {">=": "2024-01-01"}},
            projection=["title", "company", "salary_range"],
            limit=10,
            order_by="created_at",
            order_direction="DESCENDING"
        )
    """
    if not collection:
        raise ValueError("Collection name cannot be empty")
    
    logger.info(f"Querying Firestore collection: {collection}")
    
    try:
        db = _get_firestore_client()
        query = db.collection(collection)
        
        # Apply filters if provided
        if filter_dict:
            for field, value in filter_dict.items():
                if field == "__name__":
                    # Special case for document ID
                    query = query.where(firestore.FieldPath.document_id(), "==", value)
                elif isinstance(value, dict):
                    # Handle complex filter operators
                    for operator, operand in value.items():
                        if operator == "array-contains":
                            query = query.where(field, "array_contains", operand)
                        elif operator == "array-contains-any":
                            query = query.where(field, "array_contains_any", operand)
                        elif operator in ["<", "<=", "==", "!=", ">=", ">"]:
                            query = query.where(field, operator, operand)
                        else:
                            raise ValueError(f"Unsupported filter operator: {operator}")
                else:
                    # Simple equality filter
                    query = query.where(field, "==", value)
        
        # Apply ordering if specified
        if order_by:
            direction = firestore.Query.DESCENDING if order_direction.upper() == "DESCENDING" else firestore.Query.ASCENDING
            query = query.order_by(order_by, direction=direction)
        
        # Apply limit if specified
        if limit:
            query = query.limit(limit)
        
        # Execute query
        docs = query.stream()
        
        results = []
        for doc in docs:
            doc_data = doc.to_dict()
            
            # Apply projection if specified
            if projection:
                doc_data = {field: doc_data.get(field) for field in projection if field in doc_data}
            
            # Add document metadata
            result = {
                "id": doc.id,
                "data": doc_data,
                "exists": doc.exists,
                "create_time": doc.create_time.isoformat() if doc.create_time else None,
                "update_time": doc.update_time.isoformat() if doc.update_time else None,
            }
            results.append(result)
        
        logger.info(f"Successfully queried {len(results)} documents from {collection}")
        return results
        
    except Exception as e:
        logger.error(f"Error querying Firestore collection {collection}: {e}")
        raise


def get_document(collection: str, document_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific document by ID from a Firestore collection.
    
    This is a convenience function for fetching single documents,
    commonly used for retrieving candidate or job documents by ID.
    
    Args:
        collection: Name of the Firestore collection
        document_id: ID of the document to retrieve
    
    Returns:
        Document dictionary with data and metadata, or None if not found
    
    Examples:
        # Get a specific candidate
        candidate = get_document("candidates", "candidate_123")
        
        # Get a specific job posting
        job = get_document("jobs", "job_456")
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return {
                "id": doc.id,
                "data": doc.to_dict(),
                "exists": doc.exists,
                "create_time": doc.create_time.isoformat() if doc.create_time else None,
                "update_time": doc.update_time.isoformat() if doc.update_time else None,
            }
        else:
            logger.warning(f"Document {document_id} not found in collection {collection}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting document {document_id} from {collection}: {e}")
        raise


def retrieve_match_context(match_id: str) -> Dict[str, Any]:
    """
    Higher-level helper to retrieve candidate and job context for a match.
    
    This function demonstrates how to use query_firestore to fetch related
    documents for a matching operation, providing richer context for agents.
    
    Args:
        match_id: ID of the match to retrieve context for
    
    Returns:
        Dictionary containing candidate and job data, or error information
    
    Example:
        context = retrieve_match_context("match_789")
        if context.get("success"):
            candidate = context["candidate"]
            job = context["job"]
            # Process matching logic...
    """
    try:
        # First, get the match document to find candidate and job IDs
        match_doc = get_document("matches", match_id)
        if not match_doc:
            return {
                "success": False,
                "error": f"Match {match_id} not found"
            }
        
        match_data = match_doc["data"]
        candidate_id = match_data.get("candidate_id")
        job_id = match_data.get("job_id")
        
        if not candidate_id or not job_id:
            return {
                "success": False,
                "error": "Match document missing candidate_id or job_id"
            }
        
        # Fetch candidate and job documents
        candidate = get_document("candidates", candidate_id)
        job = get_document("jobs", job_id)
        
        if not candidate:
            return {
                "success": False,
                "error": f"Candidate {candidate_id} not found"
            }
        
        if not job:
            return {
                "success": False,
                "error": f"Job {job_id} not found"
            }
        
        # Optionally fetch related documents like interview feedback
        feedback_docs = query_firestore(
            "interview_feedback",
            {"candidate_id": candidate_id},
            limit=10,
            order_by="created_at",
            order_direction="DESCENDING"
        )
        
        return {
            "success": True,
            "match_id": match_id,
            "match_data": match_data,
            "candidate": candidate,
            "job": job,
            "interview_feedback": feedback_docs
        }
        
    except Exception as e:
        logger.error(f"Error retrieving match context for {match_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Tool metadata for ADK integration
TOOL_METADATA = {
    "name": "query_firestore",
    "description": "Query Firestore collections to retrieve candidate profiles, job descriptions, and related documents",
    "parameters": {
        "type": "object",
        "properties": {
            "collection": {
                "type": "string",
                "description": "Name of the Firestore collection to query (e.g., 'candidates', 'jobs', 'matches')"
            },
            "filter_dict": {
                "type": "object",
                "description": "Optional dictionary of field filters for querying specific documents",
                "properties": {},
                "additionalProperties": True
            },
            "projection": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of field names to include in results"
            },
            "limit": {
                "type": "integer",
                "description": "Optional maximum number of documents to return"
            },
            "order_by": {
                "type": "string",
                "description": "Optional field name to order results by"
            },
            "order_direction": {
                "type": "string",
                "enum": ["ASCENDING", "DESCENDING"],
                "description": "Sort direction for ordered results"
            }
        },
        "required": ["collection"]
    }
}