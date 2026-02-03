"""
MCP tool for adding tasks.
Implements the add_task functionality for the Todo AI Chatbot.
"""
import logging
from typing import Any, Dict
from uuid import UUID

from ...models.task import Task
from ...schemas.task import TaskCreate
from ...database import get_async_session, get_async_session_context
from ...dependencies import get_current_user_id
from ...config.ai_config import ai_config
from ..validators.ownership_validator import OwnershipValidator
from .base import BaseMCPTaskTool


logger = logging.getLogger(__name__)


class AddTaskTool(BaseMCPTaskTool):
    """
    MCP tool for adding new tasks for the authenticated user.
    """

    def __init__(self):
        """
        Initialize the add_task tool.
        """
        super().__init__()
        self.owner_validator = OwnershipValidator()

    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the add_task operation.

        Args:
            parameters: Parameters for the task creation
                - title (str): The task title/description (required)
                - description (str, optional): Task description
                - priority (str, optional): Priority level (low, medium, high)

            user_id: ID of the authenticated user (as string)

        Returns:
            Created task object
        """
        try:
            # Convert user_id string to UUID
            try:
                user_uuid = UUID(str(user_id))
            except (ValueError, TypeError):
                return self.format_error("Invalid user ID format", "INVALID_USER_ID")

            # Validate parameters
            if not parameters.get("title"):
                return self.format_error("Task title is required", "MISSING_PARAMETER")

            # Convert priority from string to integer (as expected by backend)
            priority_map = {
                "low": 1,
                "medium": 2,
                "high": 3
            }

            priority_param = parameters.get("priority", "medium").lower()
            priority_int = priority_map.get(priority_param, 2)  # Default to medium

            # Prepare task data
            task_data = {
                "title": parameters["title"],
                "description": parameters.get("description", ""),
                "priority": priority_int,
                "status": "pending"  # Default to pending
            }

            # Create task using the existing backend functionality
            # We'll call the existing backend functions directly
            async with get_async_session_context() as session:
                # Create the task object
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    priority=task_data["priority"],
                    status=task_data["status"],
                    user_id=user_uuid  # Assign to the authenticated user
                )

                # Add to session and commit
                session.add(task)
                await session.commit()
                await session.refresh(task)

            # Convert the created task to the expected format
            # Map priority integer back to string for response
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

        except Exception as e:
            logger.error(f"Error in add_task tool: {str(e)}")
            return self.format_error(f"Failed to create task: {str(e)}", "EXECUTION_ERROR")