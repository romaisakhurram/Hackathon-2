"""Application layer for TodoFlow.

Contains the TodoList service class that manages the in-memory collection of todos.
"""

from typing import Optional

from todo_app.domain import Priority, Status, Todo, TodoNotFoundError, ValidationError


class TodoList:
    """Manages a collection of Todo items in memory.

    Provides CRUD operations for todo management with O(1) lookups
    using a dictionary for efficient ID-based access.

    Attributes:
        _todos: Dictionary mapping todo IDs to Todo instances.
        _next_id: Counter for generating unique todo IDs.
    """

    def __init__(self) -> None:
        """Initialize an empty todo list."""
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM) -> Todo:
        """Create and add a new todo item.

        Args:
            title: The todo title, must be non-empty.
            description: Optional description for the todo.
            priority: Priority level, defaults to MEDIUM.

        Returns:
            The newly created Todo instance.

        Raises:
            ValidationError: If title is empty or invalid.
        """
        # Validate before creating
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")

        todo = Todo(
            id=self._next_id,
            title=title.strip(),
            description=description.strip() if description else "",
            priority=priority,
        )
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    def get(self, todo_id: int) -> Optional[Todo]:
        """Retrieve a todo by its ID.

        Args:
            todo_id: The ID of the todo to retrieve.

        Returns:
            The Todo instance if found, None otherwise.
        """
        return self._todos.get(todo_id)

    def get_all(self) -> list[Todo]:
        """Retrieve all todos sorted by ID.

        Returns:
            List of all todos in ID order.
        """
        return [self._todos[tid] for tid in sorted(self._todos.keys())]

    def mark_complete(self, todo_id: int) -> Todo:
        """Mark a todo as completed.

        Args:
            todo_id: The ID of the todo to mark complete.

        Returns:
            The updated Todo instance.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
        """
        todo = self._todos.get(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        if todo.status == Status.COMPLETED:
            raise ValidationError(f"Todo [{todo_id}] is already completed")
        todo.status = Status.COMPLETED
        return todo

    def update(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
    ) -> Todo:
        """Update a todo's fields.

        Args:
            todo_id: The ID of the todo to update.
            title: New title (optional).
            description: New description (optional).
            priority: New priority (optional).

        Returns:
            The updated Todo instance.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
            ValidationError: If title is empty when provided.
        """
        todo = self._todos.get(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)

        if title is not None:
            if not title or not title.strip():
                raise ValidationError("Title cannot be empty")
            todo.title = title.strip()

        if description is not None:
            todo.description = description.strip() if description else ""

        if priority is not None:
            todo.priority = priority

        return todo

    def delete(self, todo_id: int) -> None:
        """Delete a todo by its ID.

        Args:
            todo_id: The ID of the todo to delete.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(todo_id)
        del self._todos[todo_id]
