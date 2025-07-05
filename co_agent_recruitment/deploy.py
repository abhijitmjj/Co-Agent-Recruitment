#!/usr/bin/env python3
"""
Simple deployment script for Co-Agent Recruitment system to Vertex AI Agent Engine.

Usage:
    python deploy.py                    # Full deployment with testing
    python deploy.py --quick           # Quick deployment without extensive testing
    python deploy.py --test-only       # Test locally without deploying
    python deploy.py --help            # Show help
"""

import asyncio
import argparse
import logging
import sys
from co_agent_recruitment.vertexAI_engine import (
    VertexAIAgentEngineDeployer,
    deploy_co_agent_recruitment,
    quick_deploy,
    create_agent_engine_client,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_only():
    """Test the agent locally without deploying."""
    logger.info("=== Local Testing Only ===")

    try:
        deployer = VertexAIAgentEngineDeployer()
        agent = deployer.get_deployment_agent()

        # Test the agent locally
        test_results = deployer.test_local_agent(agent)

        logger.info("✅ Local testing completed successfully!")
        logger.info(f"Test results: {test_results}")

        return True

    except Exception as e:
        logger.error(f"❌ Local testing failed: {e}")
        return False


async def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(
        description="Deploy Co-Agent Recruitment system to Vertex AI Agent Engine"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick deployment without extensive testing",
    )
    parser.add_argument(
        "--test-only", action="store_true", help="Test locally without deploying"
    )
    parser.add_argument(
        "--client-info",
        action="store_true",
        help="Show client configuration information",
    )

    args = parser.parse_args()

    if args.client_info:
        client_info = create_agent_engine_client()
        logger.info("=== Agent Engine Client Configuration ===")
        logger.info(f"Configuration: {client_info}")
        return

    if args.test_only:
        success = await test_only()
        sys.exit(0 if success else 1)

    if args.quick:
        logger.info("=== Quick Deployment Mode ===")
        try:
            remote_app = await quick_deploy()
            if remote_app:
                logger.info("🎉 Quick deployment successful!")
                logger.info(f"Resource name: {remote_app.resource_name}")
                logger.info("Your agent is now deployed and ready for use!")
            else:
                logger.error("❌ Quick deployment failed")
                sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Quick deployment failed: {e}")
            sys.exit(1)
    else:
        logger.info("=== Full Deployment with Testing ===")
        try:
            result = await deploy_co_agent_recruitment()
            if result.get("success"):
                logger.info("🎉 Full deployment successful!")
                logger.info(f"Resource name: {result.get('resource_name')}")
                logger.info("Your agent is now deployed and ready for production use!")

                # Show usage information
                logger.info("\n=== Usage Information ===")
                logger.info(
                    "Your agent can now be accessed via the Vertex AI Agent Engine API."
                )
                logger.info("Use the following resource name in your API calls:")
                logger.info(f"  {result.get('resource_name')}")
                logger.info("\nFor client configuration, run:")
                logger.info("  python deploy.py --client-info")
            else:
                logger.error(f"❌ Full deployment failed: {result.get('error')}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Full deployment failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
