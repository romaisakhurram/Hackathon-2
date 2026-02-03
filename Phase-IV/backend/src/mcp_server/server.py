"""
Base MCP server framework for the Todo AI Chatbot.
Implements the core MCP server functionality that exposes tools for AI agent consumption.
"""
import asyncio
import logging
from typing import Any, Dict, Callable, Optional
from uuid import UUID
from datetime import datetime
import time

from .tools import (
    AddTaskTool, ListTasksTool, UpdateTaskTool,
    CompleteTaskTool, DeleteTaskTool
)
from ..config.ai_config import ai_config


logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server that exposes standardized tools for task operations with proper authentication
    and user ownership validation.
    """

    def __init__(self):
        """
        Initialize the MCP server with tools and validators.
        """
        self.tools: Dict[str, Any] = {}
        self.timeout = ai_config.mcp_tool_timeout
        self.initialized = False

        # Initialize with default tools
        self._register_default_tools()

    def _register_default_tools(self):
        """
        Register the default tools that come with the system.
        """
        # Create instances of each tool
        add_task_tool = AddTaskTool()
        list_tasks_tool = ListTasksTool()
        update_task_tool = UpdateTaskTool()
        complete_task_tool = CompleteTaskTool()
        delete_task_tool = DeleteTaskTool()

        # Register tools with the server
        self.register_tool("add_task", add_task_tool)
        self.register_tool("list_tasks", list_tasks_tool)
        self.register_tool("update_task", update_task_tool)
        self.register_tool("complete_task", complete_task_tool)
        self.register_tool("delete_task", delete_task_tool)

    def register_tool(self, name: str, tool_instance: Any):
        """
        Register an MCP tool with the server.

        Args:
            name: Name of the tool
            tool_instance: Instance of the tool class
        """
        self.tools[name] = tool_instance
        logger.info(f"Registered MCP tool: {name}")

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute an MCP tool with proper authentication and ownership validation.

        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool call
            user_id: ID of the authenticated user

        Returns:
            Result of the tool execution
        """
        if not self.initialized:
            await self.initialize()

        if tool_name not in self.tools:
            logger.error(f"Unknown tool requested: {tool_name}")
            return {
                "error": f"Unknown tool: {tool_name}",
                "code": "UNKNOWN_TOOL_ERROR"
            }

        try:
            # Execute the tool with timeout
            start_time = time.time()

            # Get the tool instance and call its execute method
            tool_instance = self.tools[tool_name]
            result = await asyncio.wait_for(
                tool_instance.execute(parameters, user_id),
                timeout=self.timeout
            )

            execution_time = time.time() - start_time
            logger.info(f"MCP tool {tool_name} executed successfully in {execution_time:.2f}s for user {user_id}")

            return result
        except asyncio.TimeoutError:
            logger.error(f"MCP tool {tool_name} timed out after {self.timeout} seconds for user {user_id}")
            return {
                "error": "Tool execution timed out",
                "code": "TIMEOUT_ERROR"
            }
        except Exception as e:
            logger.error(f"Error executing MCP tool {tool_name} for user {user_id}: {str(e)}")
            return {
                "error": str(e),
                "code": "EXECUTION_ERROR"
            }

    async def initialize(self):
        """
        Initialize the MCP server and all registered tools.
        """
        logger.info("Initializing MCP server...")

        # Initialize all tools if they have an initialize method
        for tool_name, tool_instance in self.tools.items():
            if hasattr(tool_instance, 'initialize'):
                try:
                    await tool_instance.initialize()
                    logger.info(f"Initialized tool: {tool_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize tool {tool_name}: {str(e)}")

        self.initialized = True
        logger.info("MCP server initialized successfully")

    async def shutdown(self):
        """
        Perform cleanup operations when shutting down the server.
        """
        logger.info("Shutting down MCP server...")

        # Clean up all tools if they have a cleanup method
        for tool_name, tool_instance in self.tools.items():
            if hasattr(tool_instance, 'cleanup'):
                try:
                    await tool_instance.cleanup()
                    logger.info(f"Cleaned up tool: {tool_name}")
                except Exception as e:
                    logger.error(f"Failed to clean up tool {tool_name}: {str(e)}")

        self.initialized = False
        logger.info("MCP server shut down complete")


# Global MCP server instance
mcp_server = MCPServer()


async def get_mcp_server() -> MCPServer:
    """
    Get the global MCP server instance, initializing it if needed.

    Returns:
        MCPServer instance
    """
    if not mcp_server.initialized:
        await mcp_server.initialize()
    return mcp_server