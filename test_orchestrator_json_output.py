"""
Test script to verify that the orchestrator agent returns proper JSON output
instead of plain text formatting.
"""

import asyncio
import json
from google.adk.sessions import InMemorySessionService
from co_agent_recruitment.agent import (
    create_orchestrator_agent,
    get_or_create_session,
    _shared_session_service
)

# Sample job posting that was causing plain text output
SAMPLE_JOB_POSTING = """
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

SAMPLE_RESUME = """
Jane Smith
Senior Data Engineer
Email: jane.smith@email.com
Phone: (555) 987-6543

PROFESSIONAL SUMMARY
Experienced data engineer with 6+ years in big data and MLOps.

WORK EXPERIENCE
Senior Data Engineer | DataCorp | 2021 - Present
- Built MLOps pipelines using Kubernetes and Docker
- Managed big data infrastructure on AWS
- Led data engineering team of 4 people

Data Engineer | TechStart | 2019 - 2021
- Developed data pipelines using Apache Spark
- Implemented machine learning models in production

EDUCATION
Master of Science in Data Science
Stanford University | 2017 - 2019

SKILLS
Programming: Python, Scala, SQL
Big Data: Apache Spark, Hadoop, Kafka
MLOps: Kubernetes, Docker, MLflow
Cloud: AWS, GCP
"""

async def test_orchestrator_with_job_posting():
    """Test orchestrator agent with job posting to ensure JSON output."""
    print("=== Testing Orchestrator with Job Posting ===")
    
    # Create session
    session, session_service = await get_or_create_session(
        "co_agent_recruitment", 
        "test_user_job", 
        session_service=_shared_session_service
    )
    
    # Create orchestrator agent
    orchestrator = create_orchestrator_agent()
    
    try:
        # Test with job posting
        print("📋 Analyzing job posting...")
        result = await orchestrator.run(
            session=session,
            user_input=f"Please analyze this job posting:\n\n{SAMPLE_JOB_POSTING}"
        )
        
        print(f"✅ Orchestrator completed successfully!")
        print(f"Result type: {type(result)}")
        
        # Check if result is a string (plain text) or structured data
        if isinstance(result, str):
            print("❌ Result is plain text (this is the problem):")
            print(f"Text output: {result[:500]}...")
            
            # Try to parse as JSON
            try:
                parsed_json = json.loads(result)
                print("✅ But it can be parsed as JSON")
                return parsed_json
            except json.JSONDecodeError:
                print("❌ Cannot parse as JSON - this is plain text formatting")
                return None
        else:
            print("✅ Result is structured data:")
            print(json.dumps(result, indent=2, default=str))
            return result
            
    except Exception as e:
        print(f"❌ Orchestrator failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

async def test_orchestrator_with_resume():
    """Test orchestrator agent with resume to ensure JSON output."""
    print("\n=== Testing Orchestrator with Resume ===")
    
    # Create session
    session, session_service = await get_or_create_session(
        "co_agent_recruitment", 
        "test_user_resume", 
        session_service=_shared_session_service
    )
    
    # Create orchestrator agent
    orchestrator = create_orchestrator_agent()
    
    try:
        # Test with resume
        print("📄 Parsing resume...")
        result = await orchestrator.run(
            session=session,
            user_input=f"Please parse this resume:\n\n{SAMPLE_RESUME}"
        )
        
        print(f"✅ Orchestrator completed successfully!")
        print(f"Result type: {type(result)}")
        
        # Check if result is a string (plain text) or structured data
        if isinstance(result, str):
            print("❌ Result is plain text (this is the problem):")
            print(f"Text output: {result[:500]}...")
            
            # Try to parse as JSON
            try:
                parsed_json = json.loads(result)
                print("✅ But it can be parsed as JSON")
                return parsed_json
            except json.JSONDecodeError:
                print("❌ Cannot parse as JSON - this is plain text formatting")
                return None
        else:
            print("✅ Result is structured data:")
            print(json.dumps(result, indent=2, default=str))
            return result
            
    except Exception as e:
        print(f"❌ Orchestrator failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

async def check_session_state(session, data_type):
    """Check what's stored in session state."""
    print(f"\n=== Checking Session State for {data_type} ===")
    print(f"Session state keys: {list(session.state.keys())}")
    
    if data_type == "job_posting" and "job_posting_JSON" in session.state:
        print("✅ job_posting_JSON found in session state:")
        print(json.dumps(session.state["job_posting_JSON"], indent=2, default=str))
    elif data_type == "resume" and "resume_JSON" in session.state:
        print("✅ resume_JSON found in session state:")
        print(json.dumps(session.state["resume_JSON"], indent=2, default=str))
    else:
        print(f"❌ No {data_type} data found in session state")

async def main():
    """Main test function."""
    print("🧪 Testing Orchestrator Agent JSON Output")
    print("=" * 60)
    
    # Test job posting
    job_result = await test_orchestrator_with_job_posting()
    
    # Test resume
    resume_result = await test_orchestrator_with_resume()
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!")
    
    # Summary
    print("\n📊 Summary:")
    job_success = job_result is not None and isinstance(job_result, dict)
    resume_success = resume_result is not None and isinstance(resume_result, dict)
    
    print(f"Job posting analysis: {'✅ Returns JSON' if job_success else '❌ Returns plain text'}")
    print(f"Resume parsing: {'✅ Returns JSON' if resume_success else '❌ Returns plain text'}")
    
    if not job_success or not resume_success:
        print("\n🔧 Issue identified: Orchestrator is returning plain text instead of JSON")
        print("This needs to be fixed in the agent configuration.")

if __name__ == "__main__":
    asyncio.run(main())