"""
Test script to simulate the FastAPI endpoint and verify it works correctly.
"""

import asyncio
import json
from co_agent_recruitment.json_agents import process_document_json

async def simulate_process_document_endpoint():
    """Simulate the /process-document endpoint."""
    
    # Test data from the user's curl request
    document_text = "As an Engineering Manager, you will play a pivotal role in designing and delivering high-quality software solutions. You will be responsible for leading a team, mentoring engineers,"
    document_type = "auto"
    
    print("🧪 Simulating /process-document endpoint")
    print(f"Input document_text: {document_text[:100]}...")
    print(f"Input document_type: {document_type}")
    print()
    
    try:
        # Call the underlying function that the API endpoint uses
        result = await process_document_json(document_text, document_type)
        
        print("✅ Function call successful!")
        print(f"Result type: {type(result)}")
        print()
        
        # Check if there was an error in the result
        if isinstance(result, dict) and 'error' in result:
            print("❌ Error in result:")
            print(f"Error: {result['error']}")
            return {
                "success": False,
                "error": result['error']
            }
        
        # Simulate the API response structure
        api_response = {
            "success": result.get('success', True),
            "document_type": result.get('document_type', 'unknown'),
            "data": result.get('data', {}),
            "detection_confidence": result.get('detection_confidence'),
            "message": "Document processed successfully"
        }
        
        print("📋 API Response Structure:")
        print(json.dumps(api_response, indent=2, default=str))
        
        return api_response
        
    except ValueError as e:
        error_response = {
            "success": False,
            "error": f"Invalid input: {str(e)}"
        }
        print(f"❌ ValueError: {e}")
        return error_response
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": "Failed to process document"
        }
        print(f"❌ Exception: {e}")
        return error_response

async def test_different_inputs():
    """Test with different types of inputs."""
    
    test_cases = [
        {
            "name": "Job Posting (explicit)",
            "text": "Engineering Manager position. Responsibilities: Lead team, mentor engineers. Requirements: 5+ years experience.",
            "type": "job_posting"
        },
        {
            "name": "Resume (explicit)", 
            "text": "John Doe. Software Engineer. Experience: 5 years at TechCorp. Education: BS Computer Science.",
            "type": "resume"
        },
        {
            "name": "Job Posting (auto-detect)",
            "text": "We are hiring a Senior Developer. Responsibilities include coding and mentoring.",
            "type": "auto"
        },
        {
            "name": "Resume (auto-detect)",
            "text": "Jane Smith. Work Experience: Software Developer at ABC Corp. Skills: Python, JavaScript.",
            "type": "auto"
        }
    ]
    
    print("\n" + "="*60)
    print("🧪 Testing Different Input Types")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        try:
            result = await process_document_json(test_case['text'], test_case['type'])
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success: {result.get('document_type', 'unknown')} detected")
                if 'detection_confidence' in result:
                    print(f"   Confidence: {result['detection_confidence']}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")

async def main():
    """Main test function."""
    print("🚀 Testing API Endpoint Functionality")
    print("="*60)
    
    # Test the specific case from the user's curl request
    await simulate_process_document_endpoint()
    
    # Test additional cases
    await test_different_inputs()
    
    print("\n" + "="*60)
    print("🏁 Testing completed!")
    print("\n💡 If this test passes, the API endpoint logic is working correctly.")
    print("   The issue might be with the FastAPI server setup or environment.")

if __name__ == "__main__":
    asyncio.run(main())