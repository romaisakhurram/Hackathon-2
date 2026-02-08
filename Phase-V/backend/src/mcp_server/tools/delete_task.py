"""
MCP tool for deleting tasks.
Implements the delete_task functionality for the Todo AI Chatbot.
"""
import logging
from typing import Any, Dict
from uuid import UUID

from sqlmodel import select, delete
from sqlalchemy import and_

from ...models.task import Task
from ...database import get_async_session, get_async_session_context
from ...config.ai_config import ai_config
from ..validators.ownership_validator import OwnershipValidator
from .base import BaseMCPTaskTool


logger = logging.getLogger(__name__)


class DeleteTaskTool(BaseMCPTaskTool):
    """
    MCP tool for removing a task for the authenticated user.
    """

    def __init__(self):
        """
        Initialize the delete_task tool.
        """
        super().__init__()
        self.owner_validator = OwnershipValidator()

    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the delete_task operation.

        Args:
            parameters: Parameters for the task deletion
                - task_id (str): ID of the task to delete (required)
            user_id: ID of the authenticated user (as string)

        Returns:
            Boolean indicating successful deletion
        """
        try:
            # Convert user_id string to UUID
            try:
                user_uuid = UUID(str(user_id))
            except (ValueError, TypeError):
                return self.format_error("Invalid user ID format", "INVALID_USER_ID")

            # Validate required parameters
            if not parameters.get("task_id"):
                return self.format_error("Task ID is required", "MISSING_PARAMETER")

            # Get task ID
            task_id = UUID(parameters["task_id"])

            # Query the task to delete
            async with get_async_session_context() as session:
                statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_uuid))
                results = await session.execute(statement)
                task = results.scalar_one_or_none()

                if not task:
                    return self.format_error("Task not found or not owned by user", "FORBIDDEN_ACCESS")

                # Delete the task
                delete_statement = delete(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
                await session.execute(delete_statement)

                # Commit the transaction
                await session.commit()

            # Return success result
            return {"success": True}

        except ValueError as e:
            # This handles UUID parsing errors
            logger.error(f"Invalid task ID format in delete_task tool: {str(e)}")
            return self.format_error("Invalid task ID format", "INVALID_PARAMETER")
        except Exception as e:
            logger.error(f"Error in delete_task tool: {str(e)}")
            return self.format_error(f"Failed to delete task: {str(e)}", "EXECUTION_ERROR")