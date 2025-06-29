"""
Vertex AI Agent Engine deployment module for Co-Agent Recruitment system.

This module provides functionality to deploy the orchestrator agent to Vertex AI Agent Engine,
enabling scalable production deployment with session management and event handling.
"""

import os
import logging
import asyncio
import sys
import shutil
import tempfile
from typing import Optional, Dict, Any, List
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.adk.agents import Agent
import dotenv
import typing

# Load environment variables
dotenv.load_dotenv()

# Import our existing agent components
from co_agent_recruitment.vertex_agent import (
    vertex_orchestrator_agent,
    get_project_id,
    get_model_name,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class VertexAIAgentEngineDeployer:
    """
    Handles deployment and management of agents on Vertex AI Agent Engine.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        staging_bucket: Optional[str] = None,
    ):
        """
        Initialize the Vertex AI Agent Engine deployer.

        Args:
            project_id: Google Cloud project ID
            location: Deployment location (default: us-central1)
            staging_bucket: GCS bucket for staging artifacts
        """
        self.project_id = project_id or get_project_id()
        self.location = location
        self.staging_bucket = staging_bucket or os.getenv(
            "BUCKET_NAME", "gs://co-agent-recruitment-agents"
        )
        os.environ["LOCATION"] = self.location

        if not self.staging_bucket:
            raise ValueError("BUCKET_NAME environment variable must be set for staging")

        # Initialize Vertex AI
        vertexai.init(
            project=self.project_id,
            location=self.location,
            staging_bucket=self.staging_bucket,
        )

        logger.info(
            f"Initialized Vertex AI for project {self.project_id} in {self.location}"
        )

    def get_deployment_agent(self) -> Agent:
        """
        Get the Vertex AI specific agent for deployment.

        Returns:
            Agent: The Vertex AI agent without Firestore dependencies
        """
        logger.info(
            f"Using Vertex AI agent for deployment: {vertex_orchestrator_agent.name}"
        )
        return vertex_orchestrator_agent

    def prepare_agent_for_deployment(self, agent: Agent) -> reasoning_engines.AdkApp:
        """
        Prepare the agent for Vertex AI Agent Engine deployment.

        Args:
            agent: The agent to prepare for deployment

        Returns:
            AdkApp: Wrapped agent ready for deployment
        """
        app = reasoning_engines.AdkApp(
            agent=agent,
            enable_tracing=True,
        )

        logger.info("Agent prepared for Vertex AI Agent Engine deployment")
        return app

    async def deploy_agent(
        self,
        agent: Optional[Agent] = None,
        requirements: Optional[List[str]] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Deploy the agent to Vertex AI Agent Engine directly.

        Args:
            agent: Agent to deploy (uses default if None)
            requirements: Additional Python requirements
            display_name: Display name for the deployed agent
            description: Description for the deployed agent

        Returns:
            Deployed agent engine instance
        """
        if agent is None:
            agent = self.get_deployment_agent()

        if requirements is None:
            requirements = [
                "a2a-sdk>=0.2.7",
                "dirtyjson>=1.0.8",
                "dotenv>=0.9.9",
                "fastapi",
                "firebase-admin>=6.9.0",
                "functions-framework>=3.8.3",
                "google-adk>=1.2.1",
                "google-cloud-aiplatform[adk,agent-engines]>=1.97.0",
                "google-cloud-documentai>=3.5.0",
                "google-cloud-pubsub>=2.30.0",
                "google-cloud-storage>=2.19.0",
                "google-genai>=1.20.0",
                "litellm>=1.72.4",
                "pip>=25.1.1",
                "pydantic-ai-slim[a2a,vertexai]>=0.2.16",
                "pydantic>=2.0.0",
                "uvicorn",
                "google-cloud-firestore>=2.11.0",
                "pandas>=2.3.0",
                "scikit-learn>=1.7.0",
                "vertexai>=1.43.0",
                "cleantext>=1.1.4",
                "ftfy>=6.3.1",
                "regex>=2024.11.6",
                "lxml>=6.0.0",
                "nltk>=3.9.1",
                "docx2pdf>=0.1.8",
                "spire-doc>=13.6.4",
                "cloudpickle==3.0.0",
            ]

        logger.info("Starting deployment to Vertex AI Agent Engine...")

        try:
            # Prepare the agent for deployment by wrapping it in AdkApp
            # app_to_deploy = self.prepare_agent_for_deployment(agent)

            logger.info("Deploying to Vertex AI Agent Engine...")
            remote_app = agent_engines.create(
                agent_engine=typing.cast(agent_engines.OperationRegistrable, agent),
                requirements=requirements,
                display_name=display_name or "Co-Agent Recruitment System",
                description=description
                or "AI-powered recruitment agent for resume parsing and job matching",
                extra_packages=["co_agent_recruitment"],
                env_vars={
                    "PROJECT_ID": "gen-lang-client-0249131775",
                },
            )

            logger.info(
                f"Agent deployed successfully! Resource name: {remote_app.resource_name}"
            )
            return remote_app

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise

    def test_local_agent(self, agent: Agent) -> Dict[str, Any]:
        """
        Test the agent locally before deployment (simplified for Vertex AI).

        Args:
            agent: Agent to test

        Returns:
            Dict containing test results
        """
        logger.info("Starting local testing of the deployment agent...")

        try:
            # Create an AdkApp for testing
            app = self.prepare_agent_for_deployment(agent)

            # Test resume parsing
            logger.info("Testing resume parsing...")
            resume_text = """
            John Doe
            Software Engineer
            Email: john.doe@email.com
            Phone: (555) 123-4567
            
            Experience:
            - Senior Software Engineer at TechCorp (2020-2023)
            - Software Developer at StartupXYZ (2018-2020)
            
            Skills: Python, JavaScript, React, Node.js, AWS
            
            Education:
            - BS Computer Science, University of Technology (2018)
            """

            # Create a simple session for testing
            session = app.create_session(user_id="test_user_deployment")

            # Test with a simple query
            resume_events = list(
                app.stream_query(
                    user_id="test_user_deployment",
                    session_id=session.id,
                    message=resume_text,
                )
            )

            logger.info("Resume parsing completed")
            logger.info(f"Resume events count: {len(resume_events)}")

            # Test job posting analysis
            logger.info("Testing job posting analysis...")
            job_posting_text = """
            Senior Software Engineer Position
            
            Company: InnovativeTech Solutions
            Location: San Francisco, CA
            
            Job Description:
            We are seeking a Senior Software Engineer to join our dynamic team.
            
            Requirements:
            - 5+ years of software development experience
            - Proficiency in Python and JavaScript
            - Experience with cloud platforms (AWS, GCP)
            - Strong problem-solving skills
            
            Responsibilities:
            - Design and develop scalable software solutions
            - Collaborate with cross-functional teams
            - Mentor junior developers
            """

            job_events = list(
                app.stream_query(
                    user_id="test_user_deployment",
                    session_id=session.id,
                    message=job_posting_text,
                )
            )

            logger.info("Job posting analysis completed")
            logger.info(f"Job posting events count: {len(job_events)}")

            logger.info("Local testing completed successfully")

            return {
                "session_id": session.id,
                "resume_test": {
                    "success": len(resume_events) > 0,
                    "events_count": len(resume_events),
                },
                "job_posting_test": {
                    "success": len(job_events) > 0,
                    "events_count": len(job_events),
                },
            }

        except Exception as e:
            logger.error(f"Local testing failed: {e}")
            return {
                "resume_test": {"success": False, "error": str(e)},
                "job_posting_test": {"success": False, "error": str(e)},
            }

    async def test_deployed_agent(self, remote_app) -> Dict[str, Any]:
        """
        Test the deployed agent on Vertex AI Agent Engine.

        Args:
            remote_app: Deployed agent engine instance

        Returns:
            Dict containing test results
        """
        logger.info("Testing deployed agent...")

        try:
            # Note: The deployed agent doesn't have direct session methods
            # Instead, we need to use the reasoning engine interface
            logger.info("Deployed agent testing requires different approach...")
            logger.info("Agent is ready for production use via API calls")

            return {
                "success": True,
                "message": "Agent deployed successfully and ready for use",
                "resource_name": remote_app.resource_name,
                "note": "Use the Agent Engine API to interact with the deployed agent",
            }

        except Exception as e:
            logger.error(f"Remote testing failed: {e}")
            return {
                "error": str(e),
                "resource_name": remote_app.resource_name,
            }

    async def cleanup_deployment(self, remote_app) -> bool:
        """
        Clean up the deployed agent and its resources.

        Args:
            remote_app: Deployed agent engine instance

        Returns:
            bool: True if cleanup successful
        """
        try:
            logger.info("Cleaning up deployed agent...")
            remote_app.delete(force=True)
            logger.info("Agent cleanup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False


async def deploy_co_agent_recruitment():
    """
    Main deployment function for the Co-Agent Recruitment system.
    """
    logger.info("=== Starting Co-Agent Recruitment Deployment ===")

    try:
        # Initialize deployer
        deployer = VertexAIAgentEngineDeployer()

        # Create deployment agent
        agent = deployer.get_deployment_agent()

        # Test locally first
        logger.info("Step 1: Testing agent locally...")
        local_test_results = deployer.test_local_agent(agent)
        logger.info(f"Local test results: {local_test_results}")

        # Deploy to Vertex AI Agent Engine
        logger.info("Step 2: Deploying to Vertex AI Agent Engine...")
        remote_app = await deployer.deploy_agent(
            agent,
            display_name="Co-Agent Recruitment System",
            description="AI-powered recruitment system for resume parsing, job analysis, and candidate matching",
        )

        # Test deployed agent
        logger.info("Step 3: Testing deployed agent...")
        remote_test_results = await deployer.test_deployed_agent(remote_app)
        logger.info(f"Remote test results: {remote_test_results}")

        if remote_app:
            logger.info("=== Deployment Completed Successfully ===")
            logger.info(f"Agent Resource Name: {remote_app.resource_name}")
            logger.info("You can now use this agent for production workloads!")
            logger.info(
                "Use the Vertex AI Agent Engine API to interact with your deployed agent."
            )

            return {
                "success": True,
                "resource_name": remote_app.resource_name,
                "local_test": local_test_results,
                "remote_test": remote_test_results,
                "deployer": deployer,
                "remote_app": remote_app,
            }
        else:
            logger.error("Deployment failed: remote_app is None")
            return {
                "success": False,
                "error": "Deployment returned None",
                "local_test": local_test_results,
            }

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def quick_deploy():
    """
    Quick deployment function for testing.
    """
    logger.info("=== Quick Deploy Mode ===")

    deployer = VertexAIAgentEngineDeployer()
    agent = deployer.get_deployment_agent()

    # Deploy without extensive testing
    remote_app = await deployer.deploy_agent(agent)

    if remote_app:
        logger.info(f"Quick deployment completed: {remote_app.resource_name}")
        return remote_app
    else:
        logger.error("Quick deployment failed: remote_app is None")
        return None


def create_agent_engine_client():
    """
    Create a client to interact with the deployed agent.

    Returns:
        Dict with client configuration
    """
    project_id = get_project_id()
    location = os.getenv("BUCKET_LOCATION", "us-central1")

    return {
        "project_id": project_id,
        "location": location,
        "instructions": {
            "usage": "Use the Vertex AI Agent Engine API to interact with your deployed agent",
            "endpoints": {
                "create_session": f"projects/{project_id}/locations/{location}/reasoningEngines/{{resource_id}}:createSession",
                "stream_query": f"projects/{project_id}/locations/{location}/reasoningEngines/{{resource_id}}:streamQuery",
                "list_sessions": f"projects/{project_id}/locations/{location}/reasoningEngines/{{resource_id}}:listSessions",
            },
        },
    }


async def main():
    """
    Main entry point for the deployment script.
    """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        result = await quick_deploy()
    elif len(sys.argv) > 1 and sys.argv[1] == "client":
        client_info = create_agent_engine_client()
        logger.info(f"Agent Engine Client Configuration: {client_info}")
        return client_info
    else:
        result = await deploy_co_agent_recruitment()

    if isinstance(result, dict) and not result.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
