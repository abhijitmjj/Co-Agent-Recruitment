"""
Unit tests for the firestore_query tool.

These tests use mocking to test the tool functionality without requiring
a live Firestore connection. For integration tests with the Firestore emulator,
run the tests with FIRESTORE_EMULATOR_HOST environment variable set.
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the module under test
from co_agent_recruitment.tools.firestore_query import (
    query_firestore,
    get_document,
    retrieve_match_context,
    _get_firestore_client,
    TOOL_METADATA
)


@pytest.fixture
def mock_firestore_client():
    """Create a mock Firestore client for testing."""
    client = Mock()
    
    # Mock collection and document structure
    collection_mock = Mock()
    query_mock = Mock()
    doc_ref_mock = Mock()
    doc_mock = Mock()
    
    # Configure the mock chain
    client.collection.return_value = collection_mock
    collection_mock.where.return_value = query_mock
    collection_mock.order_by.return_value = query_mock
    collection_mock.limit.return_value = query_mock
    collection_mock.document.return_value = doc_ref_mock
    
    query_mock.where.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.limit.return_value = query_mock
    query_mock.stream.return_value = []
    
    doc_ref_mock.get.return_value = doc_mock
    doc_mock.exists = True
    doc_mock.id = "test_doc_id"
    doc_mock.to_dict.return_value = {"test": "data"}
    doc_mock.create_time = datetime.now()
    doc_mock.update_time = datetime.now()
    
    return client


@pytest.fixture
def sample_candidate_doc():
    """Sample candidate document for testing."""
    return {
        "id": "candidate_123",
        "data": {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["python", "javascript", "react"],
            "experience_years": 5,
            "location": "San Francisco",
            "salary_expectation": 120000,
            "status": "active"
        },
        "exists": True,
        "create_time": "2024-01-01T10:00:00",
        "update_time": "2024-01-15T15:30:00"
    }


@pytest.fixture
def sample_job_doc():
    """Sample job document for testing."""
    return {
        "id": "job_456",
        "data": {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco",
            "required_skills": ["python", "react", "sql"],
            "salary_range": {"min": 110000, "max": 140000},
            "experience_required": "3-7 years",
            "remote_work": True
        },
        "exists": True,
        "create_time": "2024-01-01T09:00:00",
        "update_time": "2024-01-10T12:00:00"
    }


class TestFirestoreQuery:
    """Test cases for the query_firestore function."""
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_query_firestore_basic(self, mock_get_client, mock_firestore_client):
        """Test basic query functionality."""
        mock_get_client.return_value = mock_firestore_client
        
        # Configure mock to return sample documents
        mock_doc = Mock()
        mock_doc.id = "test_id"
        mock_doc.to_dict.return_value = {"name": "test"}
        mock_doc.exists = True
        mock_doc.create_time = datetime.now()
        mock_doc.update_time = datetime.now()
        
        mock_firestore_client.collection.return_value.stream.return_value = [mock_doc]
        
        # Execute query
        results = query_firestore("candidates")
        
        # Verify results
        assert len(results) == 1
        assert results[0]["id"] == "test_id"
        assert results[0]["data"]["name"] == "test"
        assert results[0]["exists"] is True
        
        # Verify mock calls
        mock_firestore_client.collection.assert_called_with("candidates")
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_query_firestore_with_filters(self, mock_get_client, mock_firestore_client):
        """Test query with filters."""
        mock_get_client.return_value = mock_firestore_client
        
        # Set up query chain mock
        query_mock = Mock()
        mock_firestore_client.collection.return_value = query_mock
        query_mock.where.return_value = query_mock
        query_mock.stream.return_value = []
        
        # Execute query with filters
        filter_dict = {"status": "active", "experience_years": {">=": 3}}
        query_firestore("candidates", filter_dict)
        
        # Verify filter calls
        query_mock.where.assert_any_call("status", "==", "active")
        query_mock.where.assert_any_call("experience_years", ">=", 3)
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_query_firestore_with_array_contains(self, mock_get_client, mock_firestore_client):
        """Test query with array-contains filter."""
        mock_get_client.return_value = mock_firestore_client
        
        query_mock = Mock()
        mock_firestore_client.collection.return_value = query_mock
        query_mock.where.return_value = query_mock
        query_mock.stream.return_value = []
        
        # Execute query with array-contains filter
        filter_dict = {"skills": {"array-contains": "python"}}
        query_firestore("candidates", filter_dict)
        
        # Verify array-contains call
        query_mock.where.assert_called_with("skills", "array_contains", "python")
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_query_firestore_with_array_contains_any(self, mock_get_client, mock_firestore_client):
        """Test query with array-contains-any filter."""
        mock_get_client.return_value = mock_firestore_client
        
        query_mock = Mock()
        mock_firestore_client.collection.return_value = query_mock
        query_mock.where.return_value = query_mock
        query_mock.stream.return_value = []
        
        # Execute query with array-contains-any filter
        filter_dict = {"skills": {"array-contains-any": ["python", "javascript"]}}
        query_firestore("candidates", filter_dict)
        
        # Verify array-contains-any call
        query_mock.where.assert_called_with("skills", "array_contains_any", ["python", "javascript"])
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_query_firestore_with_projection(self, mock_get_client, mock_firestore_client):
        """Test query with field projection."""
        mock_get_client.return_value = mock_firestore_client
        
        # Configure mock document with multiple fields
        mock_doc = Mock()
        mock_doc.id = "test_id"
        mock_doc.to_dict.return_value = {
            "name": "John Doe",
            "email": "john@example.com", 
            "skills": ["python"],
            "private_field": "sensitive"
        }
        mock_doc.exists = True
        mock_doc.create_time = datetime.now()
        mock_doc.update_time = datetime.now()
        
        mock_firestore_client.collection.return_value.stream.return_value = [mock_doc]
        
        # Execute query with projection
        projection = ["name", "skills"]
        results = query_firestore("candidates", projection=projection)
        
        # Verify only projected fields are included
        assert "name" in results[0]["data"]
        assert "skills" in results[0]["data"]
        assert "email" not in results[0]["data"]
        assert "private_field" not in results[0]["data"]
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_query_firestore_with_ordering(self, mock_get_client, mock_firestore_client):
        """Test query with ordering."""
        mock_get_client.return_value = mock_firestore_client
        
        query_mock = Mock()
        mock_firestore_client.collection.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.stream.return_value = []
        
        # Test ascending order
        query_firestore("candidates", order_by="created_at", order_direction="ASCENDING")
        
        # Mock the firestore Query constants
        with patch('co_agent_recruitment.tools.firestore_query.firestore.Query') as mock_query:
            mock_query.ASCENDING = "ASCENDING"
            mock_query.DESCENDING = "DESCENDING" 
            
            query_firestore("candidates", order_by="created_at", order_direction="DESCENDING")
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_query_firestore_with_limit(self, mock_get_client, mock_firestore_client):
        """Test query with limit."""
        mock_get_client.return_value = mock_firestore_client
        
        query_mock = Mock()
        mock_firestore_client.collection.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.stream.return_value = []
        
        # Execute query with limit
        query_firestore("candidates", limit=10)
        
        # Verify limit call
        query_mock.limit.assert_called_with(10)
    
    def test_query_firestore_empty_collection(self):
        """Test query with empty collection name."""
        with pytest.raises(ValueError, match="Collection name cannot be empty"):
            query_firestore("")
    
    def test_query_firestore_invalid_filter_operator(self):
        """Test query with invalid filter operator."""
        with patch('co_agent_recruitment.tools.firestore_query._get_firestore_client'):
            with pytest.raises(ValueError, match="Unsupported filter operator"):
                query_firestore("candidates", {"field": {"invalid-op": "value"}})


class TestGetDocument:
    """Test cases for the get_document function."""
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_get_document_exists(self, mock_get_client, mock_firestore_client):
        """Test getting an existing document."""
        mock_get_client.return_value = mock_firestore_client
        
        # Configure mock document
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.id = "test_id"
        mock_doc.to_dict.return_value = {"name": "test"}
        mock_doc.create_time = datetime.now()
        mock_doc.update_time = datetime.now()
        
        mock_firestore_client.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Execute get_document
        result = get_document("candidates", "test_id")
        
        # Verify result
        assert result is not None
        assert result["id"] == "test_id"
        assert result["data"]["name"] == "test"
        assert result["exists"] is True
    
    @patch('co_agent_recruitment.tools.firestore_query._get_firestore_client')
    def test_get_document_not_exists(self, mock_get_client, mock_firestore_client):
        """Test getting a non-existent document."""
        mock_get_client.return_value = mock_firestore_client
        
        # Configure mock document that doesn't exist
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_firestore_client.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Execute get_document
        result = get_document("candidates", "nonexistent_id")
        
        # Verify result is None
        assert result is None


class TestRetrieveMatchContext:
    """Test cases for the retrieve_match_context function."""
    
    @patch('co_agent_recruitment.tools.firestore_query.get_document')
    @patch('co_agent_recruitment.tools.firestore_query.query_firestore')
    def test_retrieve_match_context_success(self, mock_query, mock_get_doc):
        """Test successful match context retrieval."""
        # Mock match document
        match_doc = {
            "id": "match_789",
            "data": {
                "candidate_id": "candidate_123",
                "job_id": "job_456",
                "status": "pending"
            }
        }
        
        # Mock candidate document
        candidate_doc = {
            "id": "candidate_123",
            "data": {"name": "John Doe", "skills": ["python"]}
        }
        
        # Mock job document  
        job_doc = {
            "id": "job_456",
            "data": {"title": "Software Engineer", "required_skills": ["python"]}
        }
        
        # Configure mock responses
        mock_get_doc.side_effect = [match_doc, candidate_doc, job_doc]
        mock_query.return_value = []  # Empty interview feedback
        
        # Execute retrieve_match_context
        result = retrieve_match_context("match_789")
        
        # Verify result
        assert result["success"] is True
        assert result["match_id"] == "match_789"
        assert result["candidate"]["id"] == "candidate_123"
        assert result["job"]["id"] == "job_456"
        assert "interview_feedback" in result
    
    @patch('co_agent_recruitment.tools.firestore_query.get_document')
    def test_retrieve_match_context_match_not_found(self, mock_get_doc):
        """Test match context retrieval when match doesn't exist."""
        mock_get_doc.return_value = None
        
        result = retrieve_match_context("nonexistent_match")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    @patch('co_agent_recruitment.tools.firestore_query.get_document')
    def test_retrieve_match_context_missing_ids(self, mock_get_doc):
        """Test match context retrieval with missing candidate/job IDs."""
        match_doc = {
            "id": "match_789",
            "data": {"status": "pending"}  # Missing candidate_id and job_id
        }
        
        mock_get_doc.return_value = match_doc
        
        result = retrieve_match_context("match_789")
        
        assert result["success"] is False
        assert "missing candidate_id or job_id" in result["error"]


class TestFirestoreClientInit:
    """Test cases for Firestore client initialization."""
    
    @patch('co_agent_recruitment.tools.firestore_query.firebase_admin')
    @patch('co_agent_recruitment.tools.firestore_query.firestore')
    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json"})
    def test_get_firestore_client_with_credentials(self, mock_firestore, mock_firebase_admin):
        """Test client initialization with service account credentials."""
        mock_firebase_admin._apps = []
        mock_firestore.client.return_value = Mock()
        
        client = _get_firestore_client()
        
        assert client is not None
        mock_firebase_admin.initialize_app.assert_called_once()
    
    @patch('co_agent_recruitment.tools.firestore_query.firebase_admin')
    @patch('co_agent_recruitment.tools.firestore_query.firestore')
    @patch.dict(os.environ, {"FIREBASE_SERVICE_ACCOUNT_KEY": '{"type": "service_account", "private_key": "test"}'})
    def test_get_firestore_client_with_service_key(self, mock_firestore, mock_firebase_admin):
        """Test client initialization with service account key."""
        mock_firebase_admin._apps = []
        mock_firestore.client.return_value = Mock()
        
        client = _get_firestore_client()
        
        assert client is not None
        mock_firebase_admin.initialize_app.assert_called_once()
    
    @patch('co_agent_recruitment.tools.firestore_query.firebase_admin')
    @patch('co_agent_recruitment.tools.firestore_query.firestore')
    def test_get_firestore_client_cached(self, mock_firestore, mock_firebase_admin):
        """Test that client is cached after first initialization."""
        # Reset the global client
        import co_agent_recruitment.tools.firestore_query
        co_agent_recruitment.tools.firestore_query._db = None
        
        mock_firebase_admin._apps = []
        mock_client = Mock()
        mock_firestore.client.return_value = mock_client
        
        # First call should initialize
        client1 = _get_firestore_client()
        # Second call should return cached client
        client2 = _get_firestore_client()
        
        assert client1 is client2
        assert mock_firestore.client.call_count == 1


class TestToolMetadata:
    """Test cases for tool metadata."""
    
    def test_tool_metadata_structure(self):
        """Test that tool metadata has the correct structure."""
        assert "name" in TOOL_METADATA
        assert "description" in TOOL_METADATA
        assert "parameters" in TOOL_METADATA
        
        assert TOOL_METADATA["name"] == "query_firestore"
        assert isinstance(TOOL_METADATA["description"], str)
        assert isinstance(TOOL_METADATA["parameters"], dict)
    
    def test_tool_metadata_parameters(self):
        """Test that tool metadata parameters are properly defined."""
        params = TOOL_METADATA["parameters"]
        
        assert params["type"] == "object"
        assert "properties" in params
        assert "required" in params
        assert "collection" in params["required"]
        
        properties = params["properties"]
        assert "collection" in properties
        assert "filter_dict" in properties
        assert "projection" in properties
        assert "limit" in properties
        assert "order_by" in properties
        assert "order_direction" in properties


# Integration tests (run only if emulator is available)
class TestFirestoreIntegration:
    """Integration tests using Firestore emulator."""
    
    @pytest.mark.skipif(
        not os.getenv("FIRESTORE_EMULATOR_HOST"),
        reason="Firestore emulator not available"
    )
    def test_integration_basic_query(self):
        """Test basic query against Firestore emulator."""
        # This test would run against the actual Firestore emulator
        # It requires FIRESTORE_EMULATOR_HOST to be set
        
        # Set up test data in emulator
        # Execute actual query
        # Verify results
        
        # For now, just verify the environment is configured
        assert os.getenv("FIRESTORE_EMULATOR_HOST") is not None
    
    @pytest.mark.skipif(
        not os.getenv("FIRESTORE_EMULATOR_HOST"),
        reason="Firestore emulator not available"
    )
    def test_integration_complex_query(self):
        """Test complex query with filters against Firestore emulator."""
        # This would test actual complex queries including:
        # - Multiple filters
        # - Array operations
        # - Ordering and limits
        # - Projection
        
        # For now, just verify the environment is configured
        assert os.getenv("FIRESTORE_EMULATOR_HOST") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])