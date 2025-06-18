"""
Test script to verify JSON output from agents and identify the plain text issue.
"""

import asyncio
import json
from co_agent_recruitment.agent import parse_resume
from co_agent_recruitment.job_posting.agent import analyze_job_posting

# The job posting that was causing plain text output
PROBLEMATIC_JOB_POSTING = """
Engineering Manager - Big Data & MLOps

Industry: Technology

We are seeking an experienced Engineering Manager to lead our Big Data and MLOps team.

Key Responsibilities:
- Lead and mentor an engineering team
- Contribute to system architecture
- Ensure adherence to engineering best practices
- Drive operational efficiency and deliver high-value solutions
- Mentor and develop a high-performing team of Big Data and MLOps engineers
- Drive best practices in software development, data management, and model deployment
- Ensure solutions are secure, scalable, and efficient
- Perform hands-on development to tackle complex challenges
- Collaborate across teams to define requirements and deliver innovative solutions
- Keep stakeholders and senior management informed on progress, risks, and opportunities
- Stay ahead of advancements in AI/ML technologies and drive their application

Required Skills:
- MLOps
- Big Data
- AI/ML
- Software Development
- Data Management
- Model Deployment

Experience: 5+ years in engineering management
Location: Remote
"""

async def test_direct_function_calls():
    """Test the direct function calls to ensure they return JSON."""
    print("=== Testing Direct Function Calls ===")
    
    # Test job posting analysis
    print("📋 Testing analyze_job_posting function...")
    try:
        job_result = await analyze_job_posting(PROBLEMATIC_JOB_POSTING)
        print(f"✅ Job posting analysis successful!")
        print(f"Result type: {type(job_result)}")
        
        if isinstance(job_result, dict):
            print("✅ Returns dictionary (JSON-like structure)")
            if 'error' in job_result:
                print(f"❌ Contains error: {job_result['error']}")
            else:
                print("✅ No errors in result")
                print(f"Keys: {list(job_result.keys())}")
        else:
            print(f"❌ Returns {type(job_result)} instead of dict")
            
        print("\n📋 Job Posting JSON Output:")
        print(json.dumps(job_result, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Job posting analysis failed: {e}")
        job_result = None
    
    return job_result

def create_json_output_wrapper():
    """Create a wrapper function that ensures JSON output."""
    
    async def json_analyze_job_posting(job_posting_text: str) -> dict:
        """Wrapper that ensures JSON output for job posting analysis."""
        try:
            result = await analyze_job_posting(job_posting_text)
            
            # Ensure we return a dictionary
            if isinstance(result, dict):
                return result
            elif isinstance(result, str):
                # Try to parse as JSON if it's a string
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    # If it's not valid JSON, wrap it in an error response
                    return {
                        "error": "Function returned plain text instead of JSON",
                        "raw_output": result
                    }
            else:
                return {
                    "error": f"Function returned unexpected type: {type(result)}",
                    "raw_output": str(result)
                }
        except Exception as e:
            return {
                "error": f"Function execution failed: {str(e)}",
                "error_type": type(e).__name__
            }
    
    async def json_parse_resume(resume_text: str) -> dict:
        """Wrapper that ensures JSON output for resume parsing."""
        try:
            result = await parse_resume(resume_text)
            
            # Ensure we return a dictionary
            if isinstance(result, dict):
                return result
            elif isinstance(result, str):
                # Try to parse as JSON if it's a string
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    # If it's not valid JSON, wrap it in an error response
                    return {
                        "error": "Function returned plain text instead of JSON",
                        "raw_output": result
                    }
            else:
                return {
                    "error": f"Function returned unexpected type: {type(result)}",
                    "raw_output": str(result)
                }
        except Exception as e:
            return {
                "error": f"Function execution failed: {str(e)}",
                "error_type": type(e).__name__
            }
    
    return json_analyze_job_posting, json_parse_resume

async def test_json_wrappers():
    """Test the JSON wrapper functions."""
    print("\n=== Testing JSON Wrapper Functions ===")
    
    json_analyze_job_posting, json_parse_resume = create_json_output_wrapper()
    
    # Test job posting wrapper
    print("📋 Testing JSON wrapper for job posting...")
    job_result = await json_analyze_job_posting(PROBLEMATIC_JOB_POSTING)
    
    print(f"Result type: {type(job_result)}")
    print(f"Is dict: {isinstance(job_result, dict)}")
    
    if 'error' in job_result:
        print(f"❌ Error detected: {job_result['error']}")
        if 'raw_output' in job_result:
            print(f"Raw output: {job_result['raw_output'][:200]}...")
    else:
        print("✅ JSON wrapper successful!")
        print(f"Keys: {list(job_result.keys())}")
    
    return job_result

async def main():
    """Main test function."""
    print("🧪 Testing JSON Output Fix")
    print("=" * 60)
    
    # Test direct function calls
    direct_result = await test_direct_function_calls()
    
    # Test JSON wrappers
    wrapper_result = await test_json_wrappers()
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!")
    
    # Analysis
    print("\n📊 Analysis:")
    if direct_result and isinstance(direct_result, dict) and 'error' not in direct_result:
        print("✅ Direct function calls work correctly and return JSON")
        print("🔍 The issue is likely in how the orchestrator agent processes the output")
        print("💡 Solution: The orchestrator agent needs to be configured to return the raw JSON")
        print("   instead of formatting it as human-readable text.")
    else:
        print("❌ Direct function calls have issues")
        if direct_result and 'error' in direct_result:
            print(f"   Error: {direct_result['error']}")

if __name__ == "__main__":
    asyncio.run(main())