"""
Simple test for Firestore query tool without ADK dependencies.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_basic_imports():
    """Test that we can import the basic functions."""
    try:
        from tools.firestore_query import query_firestore, get_document_by_id
        assert callable(query_firestore)
        assert callable(get_document_by_id)
        print("✓ Basic imports successful")
    except ImportError as e:
        pytest.skip(f"Imports failed: {e}")

@patch('tools.firestore_query.db')
def test_query_firestore_mock(mock_db):
    """Test query_firestore with mocked Firestore."""
    try:
        from tools.firestore_query import query_firestore
        
        # Mock Firestore response
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {"name": "Test", "skills": ["Python"]}
        mock_doc.id = "test_123"
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_db.collection.return_value = mock_collection
        
        # Execute query
        result = query_firestore(collection="test")
        
        # Verify
        assert len(result) == 1
        assert result[0]["id"] == "test_123"
        assert result[0]["name"] == "Test"
        print("✓ Basic query test passed")
        
    except ImportError as e:
        pytest.skip(f"Test skipped due to imports: {e}")

if __name__ == "__main__":
    test_basic_imports()
    print("Basic tests completed!")