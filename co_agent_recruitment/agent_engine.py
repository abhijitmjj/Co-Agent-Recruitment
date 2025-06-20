import asyncio
import logging
from typing import Optional

from google.adk.runners import Runner
from google.genai import types as genai_types

from co_agent_recruitment.agent import (
    APP_NAME,
    SESSION_ID,
    get_or_create_session_for_user,
    get_shared_session_service,
    root_agent,
)

# Configure logging with a clear format
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG to see detailed event logs
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class OrchestratorAgentRunner:
    """A runner to interact with the orchestrator agent and manage sessions."""

    def __init__(self):
        """Initializes the OrchestratorAgentRunner."""
        self.runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=get_shared_session_service(),
        )
        logger.info(
            f"Runner created for agent '{self.runner.agent.name}' in app '{APP_NAME}'."
        )

    async def run_async(
        self, user_id: str, query: str, session_id: Optional[str] = None
    ) -> str:
        """
        Runs a query against the orchestrator agent for a given user.

        Args:
            user_id: The identifier for the user.
            query: The user's query for the agent.
            session_id: The existing session ID, if any.

        Returns:
            The agent's final text response.
        """
        logger.info(f"Received query from user '{user_id}' in session '{session_id}'.")
        try:
            # Get an existing session or create a new one
            active_session_id = await get_or_create_session_for_user(
                user_id=user_id, session_id=session_id
            )
            logger.info(f"Using session '{active_session_id}' for user '{user_id}'.")

            # Prepare the user's message in ADK format
            content = genai_types.Content(role="user", parts=[genai_types.Part(text=query)])

            final_response_text = "Agent did not produce a final response."  # Default

            # run_async executes the agent logic and yields Events
            async for event in self.runner.run_async(
                user_id=user_id, session_id=active_session_id, new_message=content
            ):
                # Detailed logging for every event to debug the flow
                logger.debug(
                    f"Event received: Author='{event.author}', "
                    f"Type='{type(event).__name__}', "
                    f"Final='{event.is_final_response()}', "
                    f"Content='{str(event.content)[:200]}...'"
                    f" User ID='{user_id}', "
                    f"Session ID='{active_session_id}'"
                )
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = (
                            event.content.parts[0].text
                            or "Agent returned empty content."
                        )
                    logger.info(
                        f"Final response for user '{user_id}': {final_response_text}"
                    )
                    # break  # Stop processing events

            return final_response_text

        except Exception as e:
            logger.error(f"An error occurred while running the agent: {e}", exc_info=True)
            return f"An error occurred: {e}"


# Singleton instance of the runner
agent_runner = OrchestratorAgentRunner()


def get_agent_runner() -> OrchestratorAgentRunner:
    """Get the singleton agent runner instance."""
    return agent_runner


async def main():
    """Example usage of the agent runner."""
    logger.info("--- Starting Agent Engine Example ---")

    # Example user and query
    example_user_id = "test_user_001"
    example_query = "parse this - 'Highly analytical and innovative Machine Learning Scientist with 5+ years of experience in developing, deploying, and optimizing scalable ML models across diverse industries including finance and healthcare. Proficient in Python, TensorFlow, PyTorch, and scikit-learn, with a proven track record in deep learning, natural language processing (NLP), and predictive modeling. Successfully led projects from conception to production, resulting in 20% improved fraud detection accuracy for a leading fintech firm and 15% increased diagnostic efficiency in clinical settings. Adept at feature engineering, model evaluation, and MLOps practices to ensure robust and interpretable solutions. Seeking to leverage advanced algorithmic expertise and problem-solving skills to drive data-driven innovation in a challenging research and development environment. Passionate about transforming complex data into actionable insights and contributing to cutting-edge AI advancements.'"

    # Get the runner and execute the query
    runner = get_agent_runner()
    response = await runner.run_async(user_id=example_user_id, query=example_query, session_id=SESSION_ID)

    logger.info(f"\n--- Query ---\n{example_query}")
    logger.info(f"\n--- Agent Response ---\n{response}")

    logger.info("\n--- Agent Engine Example Finished ---")
    response_for_job_posting = await runner.run_async(
        user_id=example_user_id,
        query="Analyze this job posting - 'We are looking for a Machine Learning Engineer with expertise in Python, TensorFlow, and data analysis. The ideal candidate will have experience in deploying machine learning models in production environments.'",
        session_id=SESSION_ID,
    )
    logger.info(f"\n--- Job Posting Analysis Response ---\n{response_for_job_posting}")
    logger.info("\n--- Job Posting Analysis Finished ---")


if __name__ == "__main__":
    asyncio.run(main())
