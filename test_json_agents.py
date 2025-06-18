"""
Test the new JSON-focused agents to ensure they return proper JSON output.
"""

import asyncio
import json
from co_agent_recruitment.json_agents import (
    parse_resume_json,
    analyze_job_posting_json,
    process_document_json,
)

# Test data
SAMPLE_RESUME = """
John Doe
Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years of experience in full-stack development.

WORK EXPERIENCE
Senior Software Engineer | Tech Corp | 2020 - Present
- Developed web applications using React and Node.js
- Led a team of 3 developers

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2014 - 2018

SKILLS
Programming Languages: Python, JavaScript, Java
"""

SAMPLE_JOB_POSTING = """
Engineering Manager - Big Data & MLOps

Industry: Technology

We are seeking an experienced Engineering Manager to lead our Big Data and MLOps team.

Key Responsibilities:
- Lead and mentor an engineering team
- Contribute to system architecture
- Ensure adherence to engineering best practices
- Drive operational efficiency and deliver high-value solutions

Required Skills:
- MLOps
- Big Data
- AI/ML
- Software Development

Experience: 5+ years in engineering management
Location: Remote
"""


async def test_parse_resume_json():
    """Test the JSON resume parsing function."""
    print("=== Testing parse_resume_json ===")

    try:
        result = await parse_resume_json(SAMPLE_RESUME)

        print(f"✅ Function completed successfully")
        print(f"Result type: {type(result)}")
        print(f"Is dict: {isinstance(result, dict)}")

        if isinstance(result, dict):
            if "error" in result:
                print(f"❌ Error in result: {result['error']}")
                return False
            else:
                print(f"✅ Valid JSON structure")
                print(f"Keys: {list(result.keys())}")
                print("\n📄 Resume JSON:")
                print(json.dumps(result, indent=2, default=str))
                return True
        else:
            print(f"❌ Expected dict, got {type(result)}")
            return False

    except Exception as e:
        print(f"❌ Function failed: {e}")
        return False


async def test_analyze_job_posting_json():
    """Test the JSON job posting analysis function."""
    print("\n=== Testing analyze_job_posting_json ===")

    try:
        result = await analyze_job_posting_json(SAMPLE_JOB_POSTING)

        print(f"✅ Function completed successfully")
        print(f"Result type: {type(result)}")
        print(f"Is dict: {isinstance(result, dict)}")

        if isinstance(result, dict):
            if "error" in result:
                print(f"❌ Error in result: {result['error']}")
                return False
            else:
                print(f"✅ Valid JSON structure")
                print(f"Keys: {list(result.keys())}")
                print("\n📋 Job Posting JSON:")
                print(json.dumps(result, indent=2, default=str))
                return True
        else:
            print(f"❌ Expected dict, got {type(result)}")
            return False

    except Exception as e:
        print(f"❌ Function failed: {e}")
        return False


async def test_process_document_json():
    """Test the unified document processing function."""
    print("\n=== Testing process_document_json ===")

    # Test with explicit resume type
    print("\n📄 Testing with explicit resume type...")
    try:
        result = await process_document_json(SAMPLE_RESUME, "resume")
        print(f"✅ Resume processing successful")
        print(f"Document type: {result.get('document_type')}")
        print(f"Success: {result.get('success')}")

        if result.get("success"):
            print("✅ Resume data extracted successfully")
        else:
            print("❌ Resume processing had errors")

    except Exception as e:
        print(f"❌ Resume processing failed: {e}")

    # Test with explicit job posting type
    print("\n📋 Testing with explicit job posting type...")
    try:
        result = await process_document_json(SAMPLE_JOB_POSTING, "job_posting")
        print(f"✅ Job posting processing successful")
        print(f"Document type: {result.get('document_type')}")
        print(f"Success: {result.get('success')}")

        if result.get("success"):
            print("✅ Job posting data extracted successfully")
        else:
            print("❌ Job posting processing had errors")

    except Exception as e:
        print(f"❌ Job posting processing failed: {e}")

    # Test with auto-detection
    print("\n🔍 Testing with auto-detection...")
    try:
        result = await process_document_json(SAMPLE_JOB_POSTING, "auto")
        print(f"✅ Auto-detection successful")
        print(f"Detected type: {result.get('document_type')}")
        print(f"Detection confidence: {result.get('detection_confidence')}")
        print(f"Success: {result.get('success')}")

        if result.get("document_type") == "job_posting":
            print("✅ Correctly detected as job posting")
        else:
            print("❌ Incorrect detection")

    except Exception as e:
        print(f"❌ Auto-detection failed: {e}")


async def main():
    """Main test function."""
    print("🧪 Testing JSON-Focused Agents")
    print("=" * 60)

    # Test individual functions
    resume_success = await test_parse_resume_json()
    job_success = await test_analyze_job_posting_json()

    # Test unified function
    await test_process_document_json()

    print("\n" + "=" * 60)
    print("🏁 Testing completed!")

    # Summary
    print("\n📊 Summary:")
    print(f"Resume JSON parsing: {'✅ Success' if resume_success else '❌ Failed'}")
    print(f"Job posting JSON analysis: {'✅ Success' if job_success else '❌ Failed'}")

    if resume_success and job_success:
        print("\n🎉 All JSON functions work correctly!")
        print(
            "💡 Use these functions instead of the orchestrator agent for API responses."
        )
        print("\n📝 Usage examples:")
        print("```python")
        print(
            "from co_agent_recruitment.json_agents import parse_resume_json, analyze_job_posting_json"
        )
        print("")
        print("# For resume parsing")
        print("resume_data = await parse_resume_json(resume_text)")
        print("")
        print("# For job posting analysis")
        print("job_data = await analyze_job_posting_json(job_posting_text)")
        print("")
        print("# For auto-detection")
        print("result = await process_document_json(document_text, 'auto')")
        print("```")
    else:
        print("\n❌ Some functions failed - check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
