"""
Test script for Vertex AI Agent Engine deployment.

This script tests the deployment functionality and provides examples
of how to use the deployed agent.
"""

import asyncio
import logging
import os
from co_agent_recruitment.vertexAI_engine import (
    VertexAIAgentEngineDeployer,
    deploy_co_agent_recruitment,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_local_deployment():
    """Test the agent locally before deploying to Vertex AI."""
    logger.info("=== Testing Local Deployment ===")

    try:
        deployer = VertexAIAgentEngineDeployer()
        agent = deployer.get_deployment_agent()

        # Test the agent locally
        test_results = await deployer.test_local_agent(agent)

        logger.info("Local deployment test completed successfully!")
        logger.info(f"Test results: {test_results}")

        return test_results

    except Exception as e:
        logger.error(f"Local deployment test failed: {e}")
        return {"error": str(e)}


async def test_full_deployment():
    """Test the full deployment pipeline."""
    logger.info("=== Testing Full Deployment Pipeline ===")

    try:
        result = await deploy_co_agent_recruitment()

        if result.get("success"):
            logger.info("Full deployment test completed successfully!")
            logger.info(f"Resource name: {result.get('resource_name')}")

            # Clean up the deployment
            if "remote_app" in result and result["remote_app"] and "deployer" in result:
                logger.info("Cleaning up test deployment...")
                deployer = result["deployer"]
                if isinstance(deployer, VertexAIAgentEngineDeployer):
                    cleanup_success = await deployer.cleanup_deployment(
                        result["remote_app"]
                    )
                    logger.info(f"Cleanup successful: {cleanup_success}")
                else:
                    logger.warning("Deployer object not available for cleanup")
        else:
            logger.error(f"Full deployment test failed: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f"Full deployment test failed: {e}")
        return {"error": str(e)}


async def test_agent_creation():
    """Test agent creation without deployment."""
    logger.info("=== Testing Agent Creation ===")

    try:
        deployer = VertexAIAgentEngineDeployer()
        agent = deployer.get_deployment_agent()

        logger.info(f"Agent created successfully: {agent.name}")
        logger.info(f"Agent description: {agent.description}")
        logger.info(f"Number of sub-agents: {len(agent.sub_agents)}")

        return {
            "success": True,
            "agent_name": agent.name,
            "sub_agents_count": len(agent.sub_agents),
        }

    except Exception as e:
        logger.error(f"Agent creation test failed: {e}")
        return {"error": str(e)}


async def run_all_tests():
    """Run all deployment tests."""
    logger.info("=== Running All Deployment Tests ===")

    results = {}

    # Test 1: Agent creation
    logger.info("\n--- Test 1: Agent Creation ---")
    results["agent_creation"] = await test_agent_creation()

    # Test 2: Local deployment
    logger.info("\n--- Test 2: Local Deployment ---")
    results["local_deployment"] = await test_local_deployment()

    # Test 3: Full deployment (commented out to avoid actual deployment costs)
    logger.info("\n--- Test 3: Full Deployment (Skipped) ---")
    logger.info("Full deployment test skipped to avoid costs. Uncomment to run.")
    # results["full_deployment"] = await test_full_deployment()

    logger.info("\n=== Test Results Summary ===")
    for test_name, result in results.items():
        success = result.get("success", False) if isinstance(result, dict) else False
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if not success and "error" in result:
            logger.info(f"  Error: {result['error']}")

    return results


def check_environment():
    """Check if the environment is properly configured."""
    logger.info("=== Checking Environment Configuration ===")

    required_vars = [
        "PROJECT_ID",
        "BUCKET_NAME",
        "BUCKET_LOCATION",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file")
        return False

    logger.info("Environment configuration looks good!")
    return True


async def main():
    """Main test function."""
    logger.info("=== Vertex AI Agent Engine Deployment Tests ===")

    # Check environment first
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        return

    # Run tests
    results = await run_all_tests()

    # Print final summary
    logger.info("\n=== Final Summary ===")
    total_tests = len(results)
    passed_tests = sum(
        1 for r in results.values() if isinstance(r, dict) and r.get("success", False)
    )

    logger.info(f"Tests run: {total_tests}")
    logger.info(f"Tests passed: {passed_tests}")
    logger.info(f"Tests failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Ready for deployment.")
    else:
        logger.info("⚠️  Some tests failed. Please review the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
