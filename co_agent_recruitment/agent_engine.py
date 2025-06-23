from typing import cast
import asyncio
import logging
import json  # Added import
from typing import Optional
import dotenv

from google.adk.runners import Runner
from google.genai import types as genai_types
from co_agent_recruitment.agent import (
    APP_NAME,
    SESSION_ID,
    get_or_create_session_for_user,
    get_shared_session_service,
    root_agent,
)
from co_agent_recruitment.tools.pubsub import emit_event
from co_agent_recruitment.tools.pubsub import parse_dirty_json

# Configure logging with a clear format
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG to see detailed event logs
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
# load environment variables

dotenv.load_dotenv()


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
            content = genai_types.Content(
                role="user", parts=[genai_types.Part(text=query)]
            )

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
                        match event.author:
                            case "resume_parser_agent":

                                # value from state_delta may be Any; cast to str for typing
                                resume_JSON: str = cast(
                                    str,
                                    event.actions.state_delta.get(
                                        "resume_JSON", final_response_text
                                    ),
                                )
                                logger.info(
                                    f"Emitting ParseResumeEvent with final response. {resume_JSON}"
                                )
                                await emit_event(
                                    name="ParseResumeEvent",
                                    payload={
                                        "response": parse_dirty_json(
                                            resume_JSON
                                        ),
                                        "user_id": user_id,
                                        "session_id": active_session_id,
                                    },
                                )
                            case "job_posting_agent":
                                job_posting_JSON: str = cast(
                                    str,
                                    event.actions.state_delta.get(
                                        "job_posting_JSON", final_response_text
                                    ),
                                )
                                logger.info(
                                    f"Emitting JobPostingAnalysisEvent with final response. {job_posting_JSON}"
                                )
                                await emit_event(
                                    name="ParseJobPostingEvent",
                                    payload={
                                        "response": parse_dirty_json(
                                            job_posting_JSON
                                        ),
                                        "user_id": user_id,
                                        "session_id": active_session_id,
                                    },
                                )
                            case "matcher_agent":
                                await emit_event(
                                    name="CompatibilityScoreEvent",
                                    payload={
                                        "response": parse_dirty_json(
                                            final_response_text
                                        ),
                                        "user_id": user_id,
                                        "session_id": active_session_id,
                                    },
                                )
                            case _:
                                logger.warning(
                                    f"Unknown agent author: {event.author}. "
                                    "No specific event emitted."
                                )
                    logger.info(
                        f"Final response for user '{user_id}': {final_response_text}"
                    )
                    # break  # Stop processing events

            return final_response_text

        except Exception as e:
            logger.error(
                f"An error occurred while running the agent: {e}", exc_info=True
            )
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
    example_query = """ABHIJIT GUPTA, PhD
Data Scientist | Financial-Risk ML Specialist | PhD, Machine Learning | Bengaluru, India
abhijit038@gmail.com • +91 9561930406 • linkedin.com/in/abhijit-gupta-phd-639568166/
PROFESSIONAL SUMMARY
PhD‑trained ML scientist with 7+ years converting research into production. Generated £8 m+ in cost savings and 10 % alpha on £210 m commodity exposure. Deep expertise spans Bayesian inference, time‑series & causal modelling, graph neural networks, and large‑scale optimisation. Adept at partnering with business and engineering leaders to ship high‑impact solutions on Azure while mentoring cross‑functional teams. Multiple national AI wins and government‑funded research underscore a record of innovation and delivery.
CORE COMPETENCIES
ML / Statistics: Bayesian Inference • Deep / Graph NN • Causal TS • LLM/LLMOps • Agentic AI Econometrics
Cloud & MLOps: Azure ML • Databricks • Spark • Docker • Kubernetes • GitLab CI/CD
Domain & Leadership: Financial Risk Management • Commodity Hedging • Risk Analytics • Fraud Detection • Agile / OKRs • Mentoring • Algorithms Design • Generative AI/LLM for Finance
Programming: Python, C++, Java
PROFESSIONAL EXPERIENCE
TESCO, Bengaluru, India - Data Scientist | Nov 2023 – Present
Designed and deployed proprietary ML hedging models covering > £210 m in commodity futures; out‑performed market benchmarks by 10 % and realised £8 m savings.
Earned back-to-back “Exceptional” performance ratings for driving high-impact ML solutions in commodity risk management.
Built pricing & inventory‑optimization pipelines integrated with Azure ML + Databricks that recommends optimal implied cover levels across inflationary and deflationary cycles, enabling intelligent buying decisions that cut stock‑outs 9 % and lifted gross margin 3 pp.
Championed CI/CD-driven model governance with automated drift monitoring, reducing release cycle time by 40%.
Mentored data scientists, streamlining experiment workflows to cut model iteration time by 30 % and reduce post‑deployment defects by 20 %.
NICE ACTIMIZE - Tech Lead, Data Scientist | Feb 2021 – Nov 2023
Led 6‑member squad; probabilistic‑graph fraud models ↑ true positives 18 %, added $1 m+ YoY revenue.
Won company-wide CoDay 2022 for building scalable election-risk simulation using Java and Spark; recognized by CTO for innovation in risk modelling architecture.
Instituted Agile OKRs across the data science pipeline, increasing sprint on-time delivery from 68% to 92% by aligning delivery with strategic objectives.
INTEL CORPORATION - AI Ambassador (Part‑time) | Jul 2018 – Jan 2022
Created Computer Vision & NLP demos for Intel accelerators; tutorials viewed 8 k+ times.
Delivered 10+ workshops on ML applications in science and engineering to 300+ professionals; topics included deep learning and domain-specific use cases.
Contributed to open‑source OneAPI examples; code featured in Intel Developer Zone.
EDUCATION
PhD, Machine Learning | Indian Institute of Science Education and Research (IISER), Pune - 2022
MS, Computational Science | IISER Pune - 2017
B.Sc. | Hindu College, University of Delhi - 2015
PhD Thesis: Designing Scalable ML algorithms for molecular recognition; awarded Govt. of India DBT‑AI grant[BT/PR34215/AI/133/22/2019].
CERTIFICATIONS
Financial Engineering & Risk Management Specialization - Columbia University (2025)
NVIDIA – Rapid Application Development with Large Language Models (LLMs) – Jun 2025
Optimization methods in Asset Management – Coursera, Columbia University (2025)
AI and Machine Learning Algorithms and Techniques – Microsoft (2025)
Bayesian Statistics - Coursera (2023)
NVIDIA DLI: Accelerating Data Engineering Pipelines - Dec 2022
NVIDIA DLI: Natural Language Processing - Nov 2022
NVIDIA DLI: Fundamentals of Deep Learning - Sep 2022
HONOURS & AWARDS
All‑India Champion - Intel Python Hack Fury (4 000+ teams, organized by Intel, AWS)
Finalist - Microsoft Azure Hackathon (8 500+ teams)
Best Poster - IIT Delhi, BARC, Merck (multiple years)
DBT‑AI Grant - Government of India, ₹3.2 M research funding [BT/PR34215/AI/133/22/2019]
Certificate of Appreciation - Ministry of Electronics & IT, Govt of India (2020)
SELECTED PUBLICATIONS
Gupta, Abhijit. "Decoding Futures Price Dynamics: A Regularized Sparse Autoencoder for Interpretable Multi-Horizon Forecasting and Factor Discovery."  arXiv:2505.06795 (2025).
Gupta, A, Mukherjee, A. "Capturing surface complementarity in proteins using unsupervised learning and robust curvature measure." Proteins. 2022; 90(9): 1669-1683. doi:10.1002/prot.26345
Gupta, A., Kulkarni, M., Mukherjee, A. "Accurate prediction of B-form/A-form DNA conformation propensity from primary sequence: A machine learning and free energy handshake." Cell Patterns, 2(9), 2021, 100329. doi:10.1016/j.patter.2021.100329.
Gupta, A., Mukherjee, A. "Prediction of good reaction coordinates and future evolution of MD trajectories using Regularized Sparse Autoencoders: A novel deep learning approach."
Gupta, A., Mukherjee, A. "CardiGraphormer: Unveiling the Power of Self-Supervised Learning in Revolutionizing Drug Discovery", 2023, CardiGraphormer."""
    example_query = f"Parse this: '{example_query}'"
    # Get the runner and execute the query
    runner = get_agent_runner()
    response = await runner.run_async(
        user_id=example_user_id, query=example_query, session_id=SESSION_ID
    )
    logger.info(f"\\n--- Response ---\\n{response}")
    await emit_event(
        name="ParseResumeEvent", payload={"response": parse_dirty_json(response)}
    )
    logger.info(f"\\n--- Query ---\\n{example_query}")
    logger.info(f"\\n--- Agent Response ---\\n{response}")
    logger.info(
        f"\\n--- Emitted Test Event Payload (Structure) ---\\n{json.dumps({'response': parse_dirty_json(response)}, indent=2)}"
    )

    logger.info("\\n--- Agent Engine Example Finished ---")
    response_for_job_posting = await runner.run_async(
        user_id=example_user_id,
        query="Analyze this job posting - 'We are looking for a Machine Learning Engineer with expertise in Python, TensorFlow, and data analysis. The ideal candidate will have experience in deploying machine learning models in production environments.'",
        session_id=SESSION_ID,
    )
    # Emit the parsed job posting data
    await emit_event(
        name="JobPostingAnalysisEvent",
        payload={"response": parse_dirty_json(response_for_job_posting)},
    )

    logger.info(
        f"\\n--- Job Posting Analysis Response (Original String) ---\\n{response_for_job_posting}"
    )
    # Optionally log the structure that was actually sent to emit_event for verification
    logger.info(
        f"\\n--- Emitted Job Posting Payload (Structure) ---\\n{json.dumps({'response': parse_dirty_json(response_for_job_posting)}, indent=2)}"
    )
    logger.info("\\n--- Job Posting Analysis Finished ---")


if __name__ == "__main__":
    asyncio.run(main())
