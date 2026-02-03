"""
MCP tool for updating tasks.
Implements the update_task functionality for the Todo AI Chatbot.
"""
import logging
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from sqlmodel import select
from sqlalchemy import and_

from ...models.task import Task
from ...database import get_async_session, get_async_session_context
from ...config.ai_config import ai_config
from ..validators.ownership_validator import OwnershipValidator
from .base import BaseMCPTaskTool


logger = logging.getLogger(__name__)


class UpdateTaskTool(BaseMCPTaskTool):
    """
    MCP tool for updating an existing task for the authenticated user.
    """

    def __init__(self):
        """
        Initialize the update_task tool.
        """
        super().__init__()
        self.owner_validator = OwnershipValidator()

    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the update_task operation.

        Args:
            parameters: Parameters for the task update
                - task_id (str): ID of the task to update (required)
                - title (str, optional): New task title/description
                - description (str, optional): New task description
                - priority (str, optional): New priority level (low, medium, high)
                - completed (bool, optional): Completion status
            user_id: ID of the authenticated user (as string)

        Returns:
            Updated task object
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

            # Convert priority from string to integer (as expected by backend)
            priority_map = {
                "low": 1,
                "medium": 2,
                "high": 3
            }

            # Query the task to update
            async with get_async_session_context() as session:
                statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_uuid))
                results = await session.execute(statement)
                task = results.scalar_one_or_none()

                if not task:
                    return self.format_error("Task not found or not owned by user", "FORBIDDEN_ACCESS")

                # Update only the fields that are provided
                if "title" in parameters and parameters["title"] is not None:
                    task.title = parameters["title"]

                if "description" in parameters and parameters["description"] is not None:
                    task.description = parameters["description"]

                if "priority" in parameters and parameters["priority"] is not None:
                    priority_param = parameters["priority"].lower()
                    task.priority = priority_map.get(priority_param, task.priority)

                if "completed" in parameters and parameters["completed"] is not None:
                    task.status = "completed" if parameters["completed"] else "pending"

                # Update the timestamp
                task.updated_at = datetime.utcnow()

                # Commit changes
                await session.commit()
                await session.refresh(task)

            # Convert the updated task to the expected format
            priority_reverse_map = {1: "low", 2: "medium", 3: "high"}

            result_task = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description or "",
                "completed": task.status == "completed",
                "priority": priority_reverse_map.get(task.priority, "medium"),
                "status": task.status,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "user_id": str(task.user_id)
            }

            return result_task

        except ValueError as e:
            # This handles UUID parsing errors
            logger.error(f"Invalid task ID format in update_task tool: {str(e)}")
            return self.format_error("Invalid task ID format", "INVALID_PARAMETER")
        except Exception as e:
            logger.error(f"Error in update_task tool: {str(e)}")
            return self.format_error(f"Failed to update task: {str(e)}", "EXECUTION_ERROR")