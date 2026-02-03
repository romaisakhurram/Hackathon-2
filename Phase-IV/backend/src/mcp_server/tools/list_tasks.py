"""
MCP tool for listing tasks.
Implements the list_tasks functionality for the Todo AI Chatbot.
"""
import logging
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


class ListTasksTool(BaseMCPTaskTool):
    """
    MCP tool for retrieving all tasks for the authenticated user.
    """

    def __init__(self):
        """
        Initialize the list_tasks tool.
        """
        super().__init__()
        self.owner_validator = OwnershipValidator()

    async def execute(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the list_tasks operation.

        Args:
            parameters: Parameters for the task listing (currently none needed)
            user_id: ID of the authenticated user (as string)

        Returns:
            Array of task objects owned by the user
        """
        try:
            # Convert user_id string to UUID
            try:
                user_uuid = UUID(str(user_id))
            except (ValueError, TypeError):
                return self.format_error("Invalid user ID format", "INVALID_USER_ID")

            # Query tasks filtered by user_id to ensure data isolation
            async with get_async_session_context() as session:
                statement = select(Task).where(Task.user_id == user_uuid)
                results = await session.execute(statement)
                tasks = results.scalars().all()

            # Convert tasks to the expected format
            priority_reverse_map = {1: "low", 2: "medium", 3: "high"}
            tasks_list = []

            for task in tasks:
                task_dict = {
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
                tasks_list.append(task_dict)

            return {"tasks": tasks_list}

        except Exception as e:
            logger.error(f"Error in list_tasks tool: {str(e)}")
            return self.format_error(f"Failed to retrieve tasks: {str(e)}", "EXECUTION_ERROR")