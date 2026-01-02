"""Tests for the domain layer."""

import pytest

from todo_app.domain import Priority, Status, Todo, ValidationError


class TestStatusEnum:
    """Tests for Status enum values."""

    def test_status_has_pending(self) -> None:
        """Status enum should have PENDING value."""
        assert Status.PENDING.value == "pending"

    def test_status_has_in_progress(self) -> None:
        """Status enum should have IN_PROGRESS value."""
        assert Status.IN_PROGRESS.value == "in_progress"

    def test_status_has_completed(self) -> None:
        """Status enum should have COMPLETED value."""
        assert Status.COMPLETED.value == "completed"


class TestPriorityEnum:
    """Tests for Priority enum values."""

    def test_priority_has_low(self) -> None:
        """Priority enum should have LOW value."""
        assert Priority.LOW.value == "low"

    def test_priority_has_medium(self) -> None:
        """Priority enum should have MEDIUM value."""
        assert Priority.MEDIUM.value == "medium"

    def test_priority_has_high(self) -> None:
        """Priority enum should have HIGH value."""
        assert Priority.HIGH.value == "high"


class TestTodoDataclass:
    """Tests for Todo dataclass creation with defaults."""

    def test_todo_with_minimal_fields(self) -> None:
        """Todo should be creatable with only a title."""
        todo = Todo(title="Test task")
        assert todo.title == "Test task"
        assert todo.id == 0
        assert todo.description == ""
        assert todo.status == Status.PENDING
        assert todo.priority == Priority.MEDIUM
        assert todo.created_at is not None

    def test_todo_with_all_fields(self) -> None:
        """Todo should accept all fields."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        todo = Todo(
            id=1,
            title="Buy milk",
            description="Get 2% milk",
            status=Status.IN_PROGRESS,
            priority=Priority.HIGH,
            created_at=now,
        )
        assert todo.id == 1
        assert todo.title == "Buy milk"
        assert todo.description == "Get 2% milk"
        assert todo.status == Status.IN_PROGRESS
        assert todo.priority == Priority.HIGH
        assert todo.created_at == now

    def test_todo_validation_empty_title(self) -> None:
        """Todo should raise ValidationError for empty title."""
        with pytest.raises(ValidationError) as exc_info:
            Todo(title="")
        assert "Title cannot be empty" in str(exc_info.value)

    def test_todo_validation_whitespace_title(self) -> None:
        """Todo should raise ValidationError for whitespace-only title."""
        with pytest.raises(ValidationError) as exc_info:
            Todo(title="   ")
        assert "Title cannot be empty" in str(exc_info.value)

    def test_todo_repr_contains_title(self) -> None:
        """Todo repr should contain the title."""
        todo = Todo(title="Test task")
        assert "Test task" in repr(todo)
