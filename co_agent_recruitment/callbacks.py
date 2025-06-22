import datetime
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Optional, Dict, Any
import logging

# Configure logging with a clear format
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG to see detailed event logs
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmResponse
) -> None:
    """Modify the LLM request to include session and user IDs in system instructions."""
    if not isinstance(callback_context, CallbackContext):
        return

    session = callback_context._invocation_context.session
    prefix = f"Session ID: {session.id}\nUser ID: {session.user_id}\n"
    llm_request.config.system_instruction = prefix + (
        llm_request.config.system_instruction or ""
    )


async def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> None:
    """Modify the LLM response to include session and user IDs as additional kwargs."""
    if not isinstance(callback_context, CallbackContext):
        return

    session = callback_context._invocation_context.session
    if hasattr(llm_response, "additional_kwargs"):
        llm_response.additional_kwargs["session_id"] = session.id
        llm_response.additional_kwargs["user_id"] = session.user_id
        logger.info(
            f"LLM response updated with session ID {session.id} and user ID {session.user_id}"
        )


async def before_tool_callback(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> None:
    """Modify tool arguments to include session and user IDs."""
    # Skip injecting into transfer or parser/posting functions to avoid unexpected args
    name = getattr(tool, "name", None)
    if name in ("transfer_to_agent", "analyze_job_posting", "parse_resume"):
        return None
    session = tool_context._invocation_context.session
    args["session_id"] = session.id
    args["user_id"] = session.user_id


async def after_tool_callback(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Modify tool response to include session and user IDs."""
    # Do not modify transfer or parser/posting function responses
    name = getattr(tool, "name", None)
    session = tool_context._invocation_context.session
    logger.info(
        f"Tool response updated with session ID {session.id} and user ID {session.user_id}"
    )
    if name in ("transfer_to_agent", "analyze_job_posting", "parse_resume"):
        return tool_response
    # session = tool_context._invocation_context.session
    tool_response["session_id"] = session.id
    tool_response["user_id"] = session.user_id
    tool_context.actions.skip_summarization = True
    # logger.info(
    #     f"Tool response updated with session ID {session.id} and user ID {session.user_id}"
    # )
    return tool_response
