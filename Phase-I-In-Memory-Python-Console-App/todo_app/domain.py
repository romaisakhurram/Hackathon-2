"""Domain layer for TodoFlow application.

Contains the core business entities: Todo, Status, Priority, and domain exceptions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Status(Enum):
    """Represents the current state of a todo item."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Priority(Enum):
    """Represents the importance level of a todo item."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ValidationError(Exception):
    """Raised when validation fails for a todo operation."""

    def __init__(self, message: str) -> None:
        """Initialize validation error with message."""
        self.message = message
        super().__init__(message)


class TodoNotFoundError(Exception):
    """Raised when a todo operation targets a non-existent ID."""

    def __init__(self, todo_id: int) -> None:
        """Initialize not found error with the requested ID."""
        self.todo_id = todo_id
        message = f"Todo with ID {todo_id} not found"
        super().__init__(message)


@dataclass
class Todo:
    """Represents a single task item in the system.

    Attributes:
        id: Unique identifier, auto-assigned on creation.
        title: Task title, required and non-empty.
        description: Optional task description, defaults to empty string.
        status: Current task status, defaults to PENDING.
        priority: Task priority level, defaults to MEDIUM.
        created_at: UTC timestamp of creation, auto-generated.
    """

    title: str
    id: int = 0
    description: str = ""
    status: Status = Status.PENDING
    priority: Priority = Priority.MEDIUM
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate todo after initialization."""
        if not self.title or not self.title.strip():
            raise ValidationError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValidationError("Title must be 200 characters or less")
        if len(self.description) > 1000:
            raise ValidationError("Description must be 1000 characters or less")
