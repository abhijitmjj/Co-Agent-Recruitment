"""
Simple test runner for Firestore query functionality.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add module path
sys.path.insert(0, 'co_agent_recruitment/tools')
import firestore_query

def test_with_mock():
    """Test query_firestore with mocked database."""
    print("Testing query_firestore with mock...")
    
    # Mock the database
    with patch.object(firestore_query, 'db') as mock_db:
        # Setup mock response
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {"name": "Test Candidate", "skills": ["Python"]}
        mock_doc.id = "test_123"
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        # Test the function
        result = firestore_query.query_firestore(
            collection="candidates",
            filter_dict={"status": "active"}
        )
        
        # Verify results
        assert len(result) == 1, f"Expected 1 result, got {len(result)}"
        assert result[0]["id"] == "test_123", f"Expected ID test_123, got {result[0]['id']}"
        assert result[0]["name"] == "Test Candidate", f"Expected name 'Test Candidate', got {result[0]['name']}"
        
        print("✓ Basic query test passed")
        
        # Verify the mock was called correctly
        mock_db.collection.assert_called_once_with("candidates")
        mock_collection.where.assert_called_with("status", "==", "active")
        
        print("✓ Mock interaction test passed")

def test_register_tools():
    """Test tool registration function."""
    print("Testing tool registration...")
    
    tools = firestore_query.register_firestore_tools()
    
    assert isinstance(tools, list), "Tools should be a list"
    assert len(tools) == 3, f"Expected 3 tools, got {len(tools)}"
    
    tool_names = [tool["name"] for tool in tools]
    expected_names = ["query_firestore", "get_document_by_id", "create_document"]
    
    for expected_name in expected_names:
        assert expected_name in tool_names, f"Missing tool: {expected_name}"
    
    # Check tool structure
    for tool in tools:
        assert "name" in tool, "Tool missing 'name' field"
        assert "description" in tool, "Tool missing 'description' field"
        assert "function" in tool, "Tool missing 'function' field"
        assert callable(tool["function"]), "Tool function should be callable"
    
    print("✓ Tool registration test passed")

def test_error_handling():
    """Test error handling when database is None."""
    print("Testing error handling...")
    
    # Temporarily set db to None
    original_db = firestore_query.db
    firestore_query.db = None
    
    try:
        # This should raise a RuntimeError
        try:
            firestore_query.query_firestore("test")
            assert False, "Expected RuntimeError but function succeeded"
        except RuntimeError as e:
            assert "Firestore client not initialized" in str(e)
            print("✓ Error handling test passed")
    finally:
        # Restore original db
        firestore_query.db = original_db

if __name__ == "__main__":
    print("Running Firestore query tests...")
    print("=" * 50)
    
    try:
        test_with_mock()
        test_register_tools()
        test_error_handling()
        
        print("=" * 50)
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)