"""
Base class for MCP tools.
Provides common functionality for all MCP tool implementations.
"""
import logging
from typing import Any, Dict
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class BaseMCPTaskTool(ABC):
    """
    Base class for MCP task tools.
    Provides common functionality and error handling for all task tools.
    """

    def __init__(self):
        """
        Initialize the base MCP task tool.
        """
        pass

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters and user ID.

        Args:
            parameters: Dictionary of parameters for the tool
            user_id: ID of the authenticated user

        Returns:
            Dictionary containing the result of the tool execution
        """
        pass

    def format_error(self, message: str, error_code: str = "EXECUTION_ERROR") -> Dict[str, Any]:
        """
        Format an error response in a standardized way.

        Args:
            message: The error message
            error_code: The error code

        Returns:
            Formatted error dictionary
        """
        logger.error(f"Tool error [{error_code}]: {message}")
        return {
            "status": "error",
            "error": message,
            "code": error_code
        }

    def format_success(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format a success response in a standardized way.

        Args:
            data: The success data

        Returns:
            Formatted success dictionary
        """
        if data is None:
            data = {}
        
        return {
            "status": "success",
            **data
        }
