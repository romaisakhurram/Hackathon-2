"""
User ownership validation for the MCP server.
Ensures that users can only perform operations on tasks they own.
"""
import logging
from typing import Dict, Any
from uuid import UUID


logger = logging.getLogger(__name__)


class OwnershipValidator:
    """
    Validates user ownership for task operations.
    """

    def __init__(self):
        """
        Initialize the ownership validator.
        """
        pass

    def validate_user_owns_task(self, user_id: UUID, task_data: Dict[str, Any]) -> bool:
        """
        Validate that the user owns the task.

        Args:
            user_id: The ID of the requesting user
            task_data: The task data to validate ownership for

        Returns:
            True if the user owns the task, False otherwise
        """
        try:
            task_owner_id = task_data.get("user_id") or task_data.get("owner_id")

            if not task_owner_id:
                logger.warning(f"Task data missing owner ID: {task_data}")
                return False

            # Convert to UUID if it's a string
            if isinstance(task_owner_id, str):
                task_owner_id = UUID(task_owner_id)

            return user_id == task_owner_id
        except Exception as e:
            logger.error(f"Error validating ownership for user {user_id}: {str(e)}")
            return False

    def validate_user_owns_tasks(self, user_id: UUID, tasks: list) -> bool:
        """
        Validate that the user owns all tasks in a list.

        Args:
            user_id: The ID of the requesting user
            tasks: List of task data to validate ownership for

        Returns:
            True if the user owns all tasks, False otherwise
        """
        for task in tasks:
            if not self.validate_user_owns_task(user_id, task):
                return False
        return True

    def validate_user_permission_for_operation(self, user_id: UUID, task_data: Dict[str, Any], operation: str) -> bool:
        """
        Validate that the user has permission to perform an operation on a task.

        Args:
            user_id: The ID of the requesting user
            task_data: The task data to validate permissions for
            operation: The operation being attempted (e.g., "read", "update", "delete")

        Returns:
            True if the user has permission, False otherwise
        """
        # For all operations, the user must own the task
        return self.validate_user_owns_task(user_id, task_data)

    async def validate_and_filter_tasks_for_user(self, user_id: UUID, tasks: list) -> list:
        """
        Filter a list of tasks to only include those owned by the user.

        Args:
            user_id: The ID of the requesting user
            tasks: List of tasks to filter

        Returns:
            List of tasks owned by the user
        """
        filtered_tasks = []

        for task in tasks:
            if self.validate_user_owns_task(user_id, task):
                filtered_tasks.append(task)
            else:
                logger.debug(f"Filtering out task not owned by user {user_id}")

        return filtered_tasks