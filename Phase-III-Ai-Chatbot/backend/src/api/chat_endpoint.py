"""
Chat endpoint that connects the AI agent to MCP tools for seamless natural language todo management.
"""
import logging
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..ai_agent.agent import AIAgent
from ..mcp_server.server import MCPServer
from ..dependencies.auth_dependencies import get_current_user_id
from ..config.ai_config import ai_config


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize global instances
ai_agent = AIAgent()
mcp_server = MCPServer()


class ChatMessageRequest(BaseModel):
    """
    Request model for chat messages.
    """
    message: str


class ChatMessageResponse(BaseModel):
    """
    Response model for chat messages.
    """
    message: str
    type: str
    action: str = None
    result: Dict[str, Any] = None


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    request: ChatMessageRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Process a natural language message from the user through the AI agent and MCP tools.

    Args:
        request: The user's message
        user_id: The authenticated user's ID (from JWT token)

    Returns:
        Natural language response to the user's message
    """
    try:
        # Process the message through the AI agent
        result = await ai_agent.process_message(request.message, user_id)

        # Log the interaction for debugging
        logger.info(f"Chat message processed for user {user_id}: {request.message} -> {result}")

        # Return the response
        return ChatMessageResponse(
            message=result.get("message", "I processed your request."),
            type=result.get("type", "success"),
            action=result.get("action"),
            result=result.get("result")
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error processing chat message for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


@router.get("/health")
async def chat_health():
    """
    Health check endpoint for the chat service.
    """
    return {
        "status": "healthy",
        "ai_agent": "initialized",
        "mcp_server": "initialized"
    }


# Register MCP tools with the server
# This would typically be done in the main application startup
def initialize_mcp_tools():
    """
    Initialize the MCP tools with the server.
    This function should be called during application startup.
    """
    from ..mcp_server.tools import (
        AddTaskTool, ListTasksTool, UpdateTaskTool,
        CompleteTaskTool, DeleteTaskTool
    )

    # Create instances of each tool
    add_task_tool = AddTaskTool()
    list_tasks_tool = ListTasksTool()
    update_task_tool = UpdateTaskTool()
    complete_task_tool = CompleteTaskTool()
    delete_task_tool = DeleteTaskTool()

    # Register tools with the MCP server
    mcp_server.register_tool("add_task", add_task_tool.execute)
    mcp_server.register_tool("list_tasks", list_tasks_tool.execute)
    mcp_server.register_tool("update_task", update_task_tool.execute)
    mcp_server.register_tool("complete_task", complete_task_tool.execute)
    mcp_server.register_tool("delete_task", delete_task_tool.execute)

    logger.info("MCP tools initialized and registered")


# Call the initialization function to register tools
initialize_mcp_tools()