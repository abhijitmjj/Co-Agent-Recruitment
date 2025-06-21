"""
Test script to identify JSON output issues with resume and job posting agents.
"""

import asyncio
import json
from co_agent_recruitment.agent import parse_resume
from co_agent_recruitment.job_posting.agent import analyze_job_posting

# Sample resume text for testing
SAMPLE_RESUME = """
John Doe
Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years of experience in full-stack development.

WORK EXPERIENCE
Senior Software Engineer | Tech Corp | 2020 - Present
- Developed web applications using React and Node.js
- Led a team of 3 developers
- Implemented CI/CD pipelines

Software Engineer | StartupXYZ | 2018 - 2020
- Built REST APIs using Python and Django
- Worked with PostgreSQL databases

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2014 - 2018

SKILLS
Programming Languages: Python, JavaScript, Java
Frameworks: React, Django, Node.js
Databases: PostgreSQL, MongoDB
Cloud: AWS, Docker
"""

# Sample job posting text for testing
SAMPLE_JOB_POSTING = """
Senior Full Stack Developer
TechCorp Inc.

Location: San Francisco, CA (Remote options available)
Experience: 5+ years
Salary: $120,000 - $150,000

About the Company:
TechCorp Inc. is a leading technology company specializing in cloud solutions.

Job Description:
We are seeking a Senior Full Stack Developer to join our engineering team.

Key Responsibilities:
- Design and develop scalable web applications
- Work with React, Node.js, and Python
- Collaborate with cross-functional teams
- Mentor junior developers
- Implement best practices for code quality

Required Skills:
- 5+ years of experience in full-stack development
- Proficiency in JavaScript, Python, React, Node.js
- Experience with cloud platforms (AWS, Azure)
- Strong problem-solving skills
- Bachelor's degree in Computer Science or related field

Benefits:
- Competitive salary
- Health insurance
- 401k matching
- Flexible work arrangements

Apply by sending your resume to jobs@techcorp.com
"""


async def test_resume_parsing():
    """Test resume parsing and check JSON output."""
    print("=== Testing Resume Parsing ===")
    try:
        result = await parse_resume(SAMPLE_RESUME)
        print("✅ Resume parsing successful!")
        print(f"Result type: {type(result)}")
        print(
            f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
        )

        # Pretty print the JSON
        print("\n📄 Parsed Resume JSON:")
        print(json.dumps(result, indent=2, default=str))

        return result
    except Exception as e:
        print(f"❌ Resume parsing failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return None


async def test_job_posting_analysis():
    """Test job posting analysis and check JSON output."""
    print("\n=== Testing Job Posting Analysis ===")
    try:
        result = await analyze_job_posting(SAMPLE_JOB_POSTING)
        print("✅ Job posting analysis successful!")
        print(f"Result type: {type(result)}")
        print(
            f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
        )

        # Pretty print the JSON
        print("\n📋 Analyzed Job Posting JSON:")
        print(json.dumps(result, indent=2, default=str))

        return result
    except Exception as e:
        print(f"❌ Job posting analysis failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return None


async def validate_json_structure(data, data_type):
    """Validate the JSON structure and identify potential issues."""
    print(f"\n=== Validating {data_type} JSON Structure ===")

    if not isinstance(data, dict):
        print(f"❌ Expected dict, got {type(data)}")
        return False

    if not data:
        print("❌ Empty result")
        return False

    # Check for error fields
    if "error" in data:
        print(f"❌ Error in result: {data.get('error')}")
        if "details" in data:
            print(f"   Details: {data.get('details')}")
        return False

    # Check for required fields based on data type
    if data_type == "Resume":
        required_fields = ["personal_details"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return False

    elif data_type == "Job Posting":
        required_fields = ["job_title", "location"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return False

    print(f"✅ {data_type} JSON structure is valid")
    return True


async def main():
    """Main test function."""
    print("🧪 Testing Resume and Job Posting Agents JSON Output")
    print("=" * 60)

    # Test resume parsing
    resume_result = await test_resume_parsing()
    if resume_result:
        await validate_json_structure(resume_result, "Resume")

    # Test job posting analysis
    job_posting_result = await test_job_posting_analysis()
    if job_posting_result:
        await validate_json_structure(job_posting_result, "Job Posting")

    print("\n" + "=" * 60)
    print("🏁 Testing completed!")

    # Summary
    print("\n📊 Summary:")
    print(
        f"Resume parsing: {'✅ Success' if resume_result and 'error' not in resume_result else '❌ Failed'}"
    )
    print(
        f"Job posting analysis: {'✅ Success' if job_posting_result and 'error' not in job_posting_result else '❌ Failed'}"
    )


if __name__ == "__main__":
    asyncio.run(main())
