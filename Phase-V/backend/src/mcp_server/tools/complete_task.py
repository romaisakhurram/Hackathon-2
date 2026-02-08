"""
MCP tool for completing tasks.
Implements the complete_task functionality for the Todo AI Chatbot.
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


class CompleteTaskTool(BaseMCPTaskTool):
    """
    MCP tool for marking a task as completed for the authenticated user.
    """

    def __init__(self):
        """
        Initialize the complete_task tool.
        """
        super().__init__()
        self.owner_validator = OwnershipValidator()

    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the complete_task operation.

        Args:
            parameters: Parameters for the task completion
                - task_id (str): ID of the task to mark as completed (required)
                - task_index (int): Alternative way to specify task by index (1-based)
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
            if not parameters.get("task_id") and not parameters.get("task_index"):
                return self.format_error("Task ID or task index is required", "MISSING_PARAMETER")

            task = None

            async with get_async_session_context() as session:
                # If task_id is provided and looks like a UUID, use it directly
                if parameters.get("task_id"):
                    try:
                        task_id = UUID(str(parameters["task_id"]))
                        statement = select(Task).where(and_(Task.id == task_id, Task.user_id == user_uuid))
                        results = await session.execute(statement)
                        task = results.scalar_one_or_none()
                    except ValueError:
                        # If task_id is not a valid UUID, it might be a numeric index
                        pass

                # If task_id didn't work or wasn't provided, try using task_index
                if not task and parameters.get("task_index"):
                    try:
                        task_index = int(parameters["task_index"]) - 1  # Convert to 0-based index
                        if task_index < 0:
                            return self.format_error("Task index must be positive", "INVALID_PARAMETER")

                        # Get all tasks for the user ordered by creation date
                        statement = select(Task).where(Task.user_id == user_uuid).order_by(Task.created_at)
                        results = await session.execute(statement)
                        user_tasks = results.scalars().all()

                        if 0 <= task_index < len(user_tasks):
                            task = user_tasks[task_index]
                        else:
                            return self.format_error(f"Task index out of range. You have {len(user_tasks)} tasks.", "INVALID_PARAMETER")
                    except ValueError:
                        return self.format_error("Invalid task index format", "INVALID_PARAMETER")

                # If still no task found and we have a task_id that wasn't a UUID, try to match by partial ID
                if not task and parameters.get("task_id"):
                    task_id_str = str(parameters["task_id"])

                    # If it's a numeric string, treat it as an index
                    if task_id_str.isdigit():
                        task_index = int(task_id_str) - 1  # Convert to 0-based index
                        if task_index < 0:
                            return self.format_error("Task index must be positive", "INVALID_PARAMETER")

                        # Get all tasks for the user ordered by creation date
                        statement = select(Task).where(Task.user_id == user_uuid).order_by(Task.created_at)
                        results = await session.execute(statement)
                        user_tasks = results.scalars().all()

                        if 0 <= task_index < len(user_tasks):
                            task = user_tasks[task_index]
                        else:
                            return self.format_error(f"Task index out of range. You have {len(user_tasks)} tasks.", "INVALID_PARAMETER")
                    else:
                        # Try to find a task whose ID starts with the given string
                        statement = select(Task).where(
                            and_(
                                Task.user_id == user_uuid,
                                Task.id.cast(str).startswith(task_id_str)
                            )
                        )
                        results = await session.execute(statement)
                        task = results.scalar_one_or_none()

                if not task:
                    return self.format_error("Task not found or not owned by user", "FORBIDDEN_ACCESS")

                # Update the task status to completed
                task.status = "completed"

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

        except Exception as e:
            logger.error(f"Error in complete_task tool: {str(e)}")
            return self.format_error(f"Failed to complete task: {str(e)}", "EXECUTION_ERROR")