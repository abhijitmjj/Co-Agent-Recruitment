"""
Unit tests for Firestore query tool.

These tests use mocking to avoid requiring a real Firestore instance,
following the pattern of existing tests in the codebase.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import the module under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from tools.firestore_query import (
        query_firestore,
        get_document_by_id,
        create_document,
        retrieve_match_context,
        register_firestore_tools,
    )
except ImportError as e:
    pytest.skip(f"Skipping tests due to missing dependencies: {e}")


class TestFirestoreQuery:
    """Test class for Firestore query functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_doc_data = {
            "name": "John Doe",
            "skills": ["Python", "JavaScript", "React"],
            "years_experience": 5,
            "salary_expectation": 75000,
            "status": "active"
        }
        
        self.mock_job_data = {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "required_skills": ["Python", "React", "PostgreSQL"],
            "required_experience": 3,
            "salary": 80000,
            "location": "Remote"
        }

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_query_firestore_simple_filter(self, mock_db):
        """Test basic query with simple equality filter."""
        # Mock Firestore response
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.mock_doc_data
        mock_doc.id = "doc_123"
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        # Execute query
        result = query_firestore(
            collection="candidates",
            filter_dict={"status": "active"}
        )
        
        # Verify results
        assert len(result) == 1
        assert result[0]["id"] == "doc_123"
        assert result[0]["name"] == "John Doe"
        assert result[0]["status"] == "active"
        
        # Verify Firestore calls
        mock_db.collection.assert_called_once_with("candidates")
        mock_collection.where.assert_called_with("status", "==", "active")

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_query_firestore_array_contains(self, mock_db):
        """Test query with array-contains filter."""
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.mock_doc_data
        mock_doc.id = "doc_123"
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        # Execute query
        result = query_firestore(
            collection="candidates",
            filter_dict={"skills": {"array-contains": "Python"}}
        )
        
        # Verify results
        assert len(result) == 1
        assert "Python" in result[0]["skills"]
        
        # Verify Firestore calls
        mock_collection.where.assert_called_with("skills", "array_contains", "Python")

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_query_firestore_with_projection(self, mock_db):
        """Test query with field projection."""
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {"name": "John Doe", "skills": ["Python"]}
        mock_doc.id = "doc_123"
        
        mock_query = Mock()
        mock_query.select.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_db.collection.return_value = mock_collection
        
        # Execute query
        result = query_firestore(
            collection="candidates",
            projection=["name", "skills"]
        )
        
        # Verify results
        assert len(result) == 1
        assert "name" in result[0]
        assert "skills" in result[0]
        assert result[0]["id"] == "doc_123"
        
        # Verify Firestore calls
        mock_collection.select.assert_called_with(["name", "skills"])

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_query_firestore_with_limit_and_order(self, mock_db):
        """Test query with limit and ordering."""
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.mock_doc_data
        mock_doc.id = "doc_123"
        
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_db.collection.return_value = mock_collection
        
        # Execute query
        result = query_firestore(
            collection="candidates",
            limit=10,
            order_by="years_experience",
            order_direction="desc"
        )
        
        # Verify results
        assert len(result) == 1
        
        # Verify Firestore calls
        mock_collection.order_by.assert_called_once()
        mock_query.limit.assert_called_with(10)

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_get_document_by_id_success(self, mock_db):
        """Test successful document retrieval by ID."""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = self.mock_doc_data
        mock_doc.id = "doc_123"
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        
        # Execute function
        result = get_document_by_id("candidates", "doc_123")
        
        # Verify results
        assert result is not None
        assert result["id"] == "doc_123"
        assert result["name"] == "John Doe"
        
        # Verify Firestore calls
        mock_db.collection.assert_called_once_with("candidates")
        mock_collection.document.assert_called_once_with("doc_123")

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_get_document_by_id_not_found(self, mock_db):
        """Test document retrieval when document doesn't exist."""
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_doc_ref = Mock()
        mock_doc_ref.get.return_value = mock_doc
        
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        
        # Execute function
        result = get_document_by_id("candidates", "nonexistent")
        
        # Verify results
        assert result is None

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_create_document_with_id(self, mock_db):
        """Test document creation with specified ID."""
        mock_doc_ref = Mock()
        
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        
        # Execute function
        result = create_document(
            collection="candidates",
            data=self.mock_doc_data,
            document_id="custom_id"
        )
        
        # Verify results
        assert result == "custom_id"
        
        # Verify Firestore calls
        mock_db.collection.assert_called_once_with("candidates")
        mock_collection.document.assert_called_once_with("custom_id")
        mock_doc_ref.set.assert_called_once_with(self.mock_doc_data)

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_create_document_auto_id(self, mock_db):
        """Test document creation with auto-generated ID."""
        mock_doc_ref = Mock()
        mock_doc_ref.id = "auto_generated_id"
        
        mock_collection = Mock()
        mock_collection.add.return_value = (None, mock_doc_ref)
        mock_db.collection.return_value = mock_collection
        
        # Execute function
        result = create_document(
            collection="candidates",
            data=self.mock_doc_data
        )
        
        # Verify results
        assert result == "auto_generated_id"
        
        # Verify Firestore calls
        mock_collection.add.assert_called_once_with(self.mock_doc_data)

    @patch('co_agent_recruitment.tools.firestore_query.get_document_by_id')
    def test_retrieve_match_context(self, mock_get_doc):
        """Test retrieving both candidate and job documents."""
        # Mock the get_document_by_id function
        def mock_get_doc_side_effect(collection, doc_id):
            if collection == "candidates" and doc_id == "candidate_123":
                return {**self.mock_doc_data, "id": "candidate_123"}
            elif collection == "jobs" and doc_id == "job_456":
                return {**self.mock_job_data, "id": "job_456"}
            return None
        
        mock_get_doc.side_effect = mock_get_doc_side_effect
        
        # Execute function
        result = retrieve_match_context("candidate_123", "job_456")
        
        # Verify results
        assert "candidate" in result
        assert "job" in result
        assert "match_retrieved_at" in result
        assert result["candidate"]["id"] == "candidate_123"
        assert result["job"]["id"] == "job_456"
        
        # Verify function calls
        assert mock_get_doc.call_count == 2

    def test_register_firestore_tools(self):
        """Test tool registration for ADK agents."""
        tools = register_firestore_tools()
        
        # Verify structure
        assert isinstance(tools, list)
        assert len(tools) == 3
        
        # Check tool names
        tool_names = [tool["name"] for tool in tools]
        expected_names = ["query_firestore", "get_document_by_id", "create_document"]
        assert all(name in tool_names for name in expected_names)
        
        # Check tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "function" in tool
            assert callable(tool["function"])

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_query_firestore_empty_result(self, mock_db):
        """Test query that returns no results."""
        mock_query = Mock()
        mock_query.stream.return_value = []
        
        mock_collection = Mock()
        mock_db.collection.return_value = mock_collection
        
        # Execute query
        result = query_firestore(collection="candidates")
        
        # Verify results
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_query_firestore_error_handling(self, mock_db):
        """Test error handling in query_firestore."""
        mock_db.collection.side_effect = Exception("Firestore connection error")
        
        # Execute query and expect exception
        with pytest.raises(Exception) as exc_info:
            query_firestore(collection="candidates")
        
        assert "Firestore connection error" in str(exc_info.value)

    @patch('co_agent_recruitment.tools.firestore_query.db')
    def test_query_firestore_comparison_operators(self, mock_db):
        """Test query with comparison operators."""
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.mock_doc_data
        mock_doc.id = "doc_123"
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        # Execute query with >= operator
        result = query_firestore(
            collection="candidates",
            filter_dict={"years_experience": {">=": 3}}
        )
        
        # Verify results
        assert len(result) == 1
        
        # Verify Firestore calls
        mock_collection.where.assert_called_with("years_experience", ">=", 3)


class TestFirestoreQueryIntegration:
    """Integration-style tests for Firestore query functionality."""

    def test_tool_registration_integration(self):
        """Test that tools can be properly registered and accessed."""
        tools = register_firestore_tools()
        
        # Test that we can access the functions
        query_tool = next(tool for tool in tools if tool["name"] == "query_firestore")
        assert query_tool["function"] == query_firestore
        
        get_doc_tool = next(tool for tool in tools if tool["name"] == "get_document_by_id")
        assert get_doc_tool["function"] == get_document_by_id
        
        create_doc_tool = next(tool for tool in tools if tool["name"] == "create_document")
        assert create_doc_tool["function"] == create_document

    def test_error_scenarios(self):
        """Test various error scenarios."""
        # Test with invalid collection name (should not raise exception during setup)
        try:
            with patch('co_agent_recruitment.tools.firestore_query.db') as mock_db:
                mock_db.collection.side_effect = Exception("Invalid collection")
                with pytest.raises(Exception):
                    query_firestore("invalid_collection")
        except ImportError:
            # Skip if module can't be imported (e.g., in CI without full Firebase setup)
            pytest.skip("Firebase dependencies not available")


if __name__ == "__main__":
    pytest.main([__file__])