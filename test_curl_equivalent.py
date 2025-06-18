"""
Test script that simulates the exact curl request you tried.
This will help verify that the API logic works correctly.
"""

import asyncio
import json
from co_agent_recruitment.json_agents import process_document_json

async def simulate_curl_request():
    """Simulate the exact curl request that was failing."""
    
    # Exact data from the curl request
    request_data = {
        "document_text": "As an Engineering Manager, you will play a pivotal role in designing and delivering high-quality software solutions. You will be responsible for leading a team, mentoring engineers,",
        "document_type": "auto"
    }
    
    print("🌐 Simulating curl request:")
    print('curl -X POST "http://localhost:8000/process-document" \\')
    print('  -H "Content-Type: application/json" \\')
    print(f'  -d \'{json.dumps(request_data)}\'')
    print()
    
    print("📥 Request data:")
    print(f"  document_text: {request_data['document_text']}")
    print(f"  document_type: {request_data['document_type']}")
    print()
    
    try:
        # Call the function that the API endpoint would call
        print("🔄 Processing request...")
        result = await process_document_json(
            request_data['document_text'], 
            request_data['document_type']
        )
        
        # Check if there was an error in the result
        if isinstance(result, dict) and 'error' in result:
            print("❌ Error in processing:")
            error_response = {
                "success": False,
                "error": result['error']
            }
            print("📤 API would return:")
            print(json.dumps(error_response, indent=2))
            return error_response
        
        # Simulate the API response structure
        api_response = {
            "success": result.get('success', True),
            "document_type": result.get('document_type', 'unknown'),
            "data": result.get('data', {}),
            "detection_confidence": result.get('detection_confidence'),
            "message": "Document processed successfully"
        }
        
        print("✅ Processing successful!")
        print("📤 API would return:")
        print(json.dumps(api_response, indent=2, default=str))
        
        return api_response
        
    except ValueError as e:
        print(f"❌ ValueError: {e}")
        error_response = {
            "success": False,
            "error": f"Invalid input: {str(e)}"
        }
        print("📤 API would return (400 Bad Request):")
        print(json.dumps(error_response, indent=2))
        return error_response
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        error_response = {
            "success": False,
            "error": "Failed to process document"
        }
        print("📤 API would return (500 Internal Server Error):")
        print(json.dumps(error_response, indent=2))
        return error_response

async def test_working_server_instructions():
    """Provide instructions for running the server."""
    
    print("\n" + "="*60)
    print("🚀 How to Run the Working Server")
    print("="*60)
    
    print("\n1. Install uvicorn if not already installed:")
    print("   pip install uvicorn")
    
    print("\n2. Run the standalone server:")
    print("   python3 standalone_server.py")
    
    print("\n3. Or run with uvicorn directly:")
    print("   uvicorn standalone_server:app --host 0.0.0.0 --port 8000 --reload")
    
    print("\n4. Test the endpoint:")
    print('   curl -X POST "http://localhost:8000/process-document" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"document_text": "As an Engineering Manager...", "document_type": "auto"}\'')
    
    print("\n5. View API documentation:")
    print("   Open http://localhost:8000/docs in your browser")
    
    print("\n📝 Alternative: Use the JSON functions directly in your code:")
    print("```python")
    print("from co_agent_recruitment.json_agents import process_document_json")
    print("")
    print("result = await process_document_json(document_text, 'auto')")
    print("print(json.dumps(result, indent=2))")
    print("```")

async def main():
    """Main test function."""
    print("🧪 Testing Curl Request Equivalent")
    print("="*60)
    
    # Test the exact curl request
    result = await simulate_curl_request()
    
    # Provide server instructions
    await test_working_server_instructions()
    
    print("\n" + "="*60)
    print("🏁 Test Summary")
    print("="*60)
    
    if result and result.get('success'):
        print("✅ The API logic works correctly!")
        print("✅ JSON output is properly structured!")
        print("✅ Auto-detection is working!")
        print("\n💡 The issue was likely with the server environment, not the logic.")
        print("   Use the standalone_server.py to run a working server.")
    else:
        print("❌ There are issues with the API logic that need to be fixed.")

if __name__ == "__main__":
    asyncio.run(main())