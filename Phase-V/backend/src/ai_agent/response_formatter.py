"""
Response formatting for the AI agent.
Formats responses in natural language for users.
"""
import logging
from typing import Any, Dict


logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Formats responses from the AI agent in natural language for users.
    """

    def __init__(self):
        """
        Initialize the response formatter.
        """
        pass

    def format_response(self, intent_type: str, result: Dict[str, Any], original_input: str = "") -> str:
        """
        Format the result of an operation into a natural language response.

        Args:
            intent_type: The type of intent that was processed
            result: The result of the operation
            original_input: The original user input for context

        Returns:
            Formatted natural language response
        """
        try:
            if result.get("status") == "error":
                return self._format_error_response(result)

            # Format responses based on intent type
            if intent_type == "add_task":
                return self._format_add_task_response(result)
            elif intent_type == "list_tasks":
                return self._format_list_tasks_response(result)
            elif intent_type == "update_task":
                return self._format_update_task_response(result)
            elif intent_type == "complete_task":
                return self._format_complete_task_response(result)
            elif intent_type == "delete_task":
                return self._format_delete_task_response(result)
            else:
                # For unknown intents, provide a generic response
                return f"OK, I've processed your request: {original_input}"

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return "I've processed your request, but there was an issue formatting the response."

    def _format_add_task_response(self, result: Dict[str, Any]) -> str:
        """
        Format response for add_task operations.
        """
        task_title = result.get("parameters", {}).get("title", "the task")
        return f"I've added the task '{task_title}' to your list."

    def _format_list_tasks_response(self, result: Dict[str, Any]) -> str:
        """
        Format response for list_tasks operations.
        """
        tasks = result.get("tasks", [])

        if not tasks:
            return "You don't have any tasks currently."

        task_count = len(tasks)
        if task_count == 1:
            return f"You have 1 task: {tasks[0].get('title', 'Untitled task')}"
        else:
            task_titles = [task.get('title', 'Untitled task') for task in tasks[:5]]  # Show first 5 tasks
            if len(tasks) > 5:
                return f"You have {task_count} tasks. Here are the first 5: {', '.join(task_titles)} and {len(tasks) - 5} more."
            else:
                return f"You have {task_count} tasks: {', '.join(task_titles)}"

    def _format_update_task_response(self, result: Dict[str, Any]) -> str:
        """
        Format response for update_task operations.
        """
        task_id = result.get("task_id", "the task")
        return f"I've updated task #{task_id} for you."

    def _format_complete_task_response(self, result: Dict[str, Any]) -> str:
        """
        Format response for complete_task operations.
        """
        task_id = result.get("task_id", "the task")
        return f"I've marked task #{task_id} as completed."

    def _format_delete_task_response(self, result: Dict[str, Any]) -> str:
        """
        Format response for delete_task operations.
        """
        task_id = result.get("task_id", "the task")
        return f"I've deleted task #{task_id} from your list."

    def _format_error_response(self, result: Dict[str, Any]) -> str:
        """
        Format response for error cases.
        """
        error_msg = result.get("error", "An error occurred")
        return f"I'm sorry, but I encountered an issue: {error_msg}"

    def format_error(self, error_message: str) -> str:
        """
        Format a general error message for the user in abstract terms.

        Args:
            error_message: The technical error message

        Returns:
            User-friendly error message
        """
        # Log the technical details for debugging
        logger.error(f"AI Agent error: {error_message}")

        # Return a user-friendly message without exposing technical details
        return "I'm sorry, but I encountered an issue while processing your request. Please try again or rephrase your request."