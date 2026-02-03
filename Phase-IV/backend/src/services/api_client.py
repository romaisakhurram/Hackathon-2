"""
Base API client for accessing existing backend models and services directly.
Provides a unified interface for interacting with the existing backend functionality.
"""
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class BackendAPIClient:
    """
    API client for accessing existing backend functionality.
    Provides methods to interact with task management endpoints and other backend services.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the API client with the backend base URL.

        Args:
            base_url: Base URL for the backend API. If None, uses environment variable.
        """
        import os
        self.base_url = base_url or os.getenv("BACKEND_API_URL", "http://localhost:8000")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """
        Async context manager entry.
        """
        self.session = aiohttp.ClientSession(
            headers={'Content-Type': 'application/json'}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit.
        """
        if self.session:
            await self.session.close()
        self.session = None

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the backend API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint to call
            data: Request data to send (for POST, PUT, PATCH)
            headers: Additional headers to include
            user_id: User ID for authentication (will be added as JWT token)

        Returns:
            Response data from the API
        """
        if not self.session:
            raise RuntimeError("API client not initialized. Use within async context manager.")

        # Construct the full URL
        url = f"{self.base_url}{endpoint}"

        # Prepare headers
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)

        # Add authentication header if user_id is provided
        if user_id:
            # In a real implementation, we would create a proper JWT token
            # For this example, we'll simulate adding an auth header
            # In practice, you'd use the same JWT creation approach as in jwt_handler.py
            import jwt
            import os
            secret = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_for_development")

            # Create a temporary token for this request (in real implementation,
            # you'd likely receive an existing token from the request context)
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(minutes=30)  # 30-minute expiration
            }
            temp_token = jwt.encode(payload, secret, algorithm="HS256")
            request_headers["Authorization"] = f"Bearer {temp_token}"

        # Prepare request parameters
        params = {
            "headers": request_headers,
            "ssl": False  # Disable SSL for localhost development
        }

        if data:
            params["json"] = data

        try:
            async with self.session.request(method, url, **params) as response:
                # Get response status
                status = response.status

                # Try to parse JSON response
                try:
                    response_data = await response.json()
                except Exception:
                    # If response is not JSON, get text
                    response_data = await response.text()

                if status >= 400:
                    # Raise an exception for error status codes
                    raise Exception(f"API request failed with status {status}: {response_data}")

                return response_data

        except aiohttp.ClientError as e:
            raise Exception(f"Network error during API request: {str(e)}")
        except Exception as e:
            raise e

    async def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks for a specific user.

        Args:
            user_id: ID of the user whose tasks to retrieve

        Returns:
            List of tasks for the user
        """
        return await self._make_request("GET", "/api/tasks/", headers={}, user_id=user_id)

    async def create_task(self, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task for a user.

        Args:
            user_id: ID of the user creating the task
            task_data: Task data including title, description, priority, etc.

        Returns:
            Created task data
        """
        return await self._make_request("POST", "/api/tasks/", data=task_data, user_id=user_id)

    async def get_task(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific task by ID for a user.

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the user requesting the task

        Returns:
            Task data if found and accessible, None otherwise
        """
        try:
            return await self._make_request("GET", f"/api/tasks/{task_id}", headers={}, user_id=user_id)
        except Exception:
            return None

    async def update_task(self, task_id: str, user_id: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a specific task for a user.

        Args:
            task_id: ID of the task to update
            user_id: ID of the user updating the task
            task_data: Updated task data

        Returns:
            Updated task data if successful, None otherwise
        """
        try:
            return await self._make_request("PUT", f"/api/tasks/{task_id}", data=task_data, user_id=user_id)
        except Exception:
            return None

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Delete a specific task for a user.

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user deleting the task

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            await self._make_request("DELETE", f"/api/tasks/{task_id}", headers={}, user_id=user_id)
            return True
        except Exception:
            return False

    async def toggle_task_completion(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Toggle the completion status of a task for a user.

        Args:
            task_id: ID of the task to toggle
            user_id: ID of the user toggling the task

        Returns:
            Updated task data if successful, None otherwise
        """
        try:
            return await self._make_request("PATCH", f"/api/tasks/{task_id}/toggle", headers={}, user_id=user_id)
        except Exception:
            return None

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information.

        Args:
            user_id: ID of the user whose profile to retrieve

        Returns:
            User profile data if found, None otherwise
        """
        try:
            return await self._make_request("GET", f"/api/users/{user_id}", headers={}, user_id=user_id)
        except Exception:
            return None


class TaskServiceAdapter:
    """
    Adapter service that provides a direct interface to the existing backend task functionality.
    """

    def __init__(self, api_client: Optional[BackendAPIClient] = None):
        """
        Initialize the task service adapter.

        Args:
            api_client: Backend API client instance. If None, creates a new one.
        """
        self.api_client = api_client or BackendAPIClient()

    async def get_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks for the specified user.

        Args:
            user_id: ID of the user whose tasks to retrieve

        Returns:
            List of tasks belonging to the user
        """
        async with self.api_client as client:
            return await client.get_user_tasks(user_id)

    async def create_task(self, user_id: str, title: str, description: Optional[str] = None,
                         priority: Optional[str] = "medium") -> Optional[Dict[str, Any]]:
        """
        Create a new task for the specified user.

        Args:
            user_id: ID of the user creating the task
            title: Title of the task
            description: Optional description of the task
            priority: Priority level ('low', 'medium', 'high')

        Returns:
            Created task if successful, None otherwise
        """
        # Convert priority from string to integer as expected by backend
        from .utils.priority_converter import priority_string_to_int
        priority_int = priority_string_to_int(priority) if priority else 2  # default to medium

        task_data = {
            "title": title,
            "description": description or "",
            "priority": priority_int
        }

        async with self.api_client as client:
            return await client.create_task(user_id, task_data)

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific task by ID for the specified user.

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the user requesting the task

        Returns:
            Task data if found and accessible, None otherwise
        """
        async with self.api_client as client:
            return await client.get_task(task_id, user_id)

    async def update_task_by_id(self, task_id: str, user_id: str,
                               title: Optional[str] = None, description: Optional[str] = None,
                               priority: Optional[str] = None, status: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a specific task for the specified user.

        Args:
            task_id: ID of the task to update
            user_id: ID of the user updating the task
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status (optional)

        Returns:
            Updated task data if successful, None otherwise
        """
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if priority is not None:
            from .utils.priority_converter import priority_string_to_int
            update_data["priority"] = priority_string_to_int(priority)
        if status is not None:
            update_data["status"] = status

        async with self.api_client as client:
            return await client.update_task(task_id, user_id, update_data)

    async def delete_task_by_id(self, task_id: str, user_id: str) -> bool:
        """
        Delete a specific task for the specified user.

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user deleting the task

        Returns:
            True if deletion was successful, False otherwise
        """
        async with self.api_client as client:
            return await client.delete_task(task_id, user_id)

    async def toggle_task_completion_by_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Toggle the completion status of a specific task for the specified user.

        Args:
            task_id: ID of the task to toggle
            user_id: ID of the user toggling the task

        Returns:
            Updated task data if successful, None otherwise
        """
        async with self.api_client as client:
            return await client.toggle_task_completion(task_id, user_id)


# Global API client instance
api_client = BackendAPIClient()