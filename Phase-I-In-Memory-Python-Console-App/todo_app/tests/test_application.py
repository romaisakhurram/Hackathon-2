"""Tests for the application layer (TodoList service)."""

import pytest

from todo_app.application import TodoList
from todo_app.domain import Priority, Status, ValidationError


class TestTodoListAdd:
    """Tests for TodoList.add() method."""

    def test_add_valid_todo(self) -> None:
        """Should create and return a new todo."""
        todo_list = TodoList()
        todo = todo_list.add("Buy groceries")
        assert todo.title == "Buy groceries"
        assert todo.id == 1
        assert todo.status == Status.PENDING
        assert todo.priority == Priority.MEDIUM
        assert len(todo_list.get_all()) == 1

    def test_add_with_description(self) -> None:
        """Should create todo with description."""
        todo_list = TodoList()
        todo = todo_list.add("Buy groceries", description="Milk, eggs, bread")
        assert todo.description == "Milk, eggs, bread"

    def test_add_with_priority(self) -> None:
        """Should create todo with specified priority."""
        todo_list = TodoList()
        todo = todo_list.add("Buy groceries", priority=Priority.HIGH)
        assert todo.priority == Priority.HIGH

    def test_add_multiple_todos(self) -> None:
        """Should assign unique IDs to each todo."""
        todo_list = TodoList()
        todo1 = todo_list.add("First task")
        todo2 = todo_list.add("Second task")
        todo3 = todo_list.add("Third task")
        assert todo1.id == 1
        assert todo2.id == 2
        assert todo3.id == 3
        assert len(todo_list.get_all()) == 3

    def test_add_validation_empty_title(self) -> None:
        """Should raise ValidationError for empty title."""
        todo_list = TodoList()
        with pytest.raises(ValidationError) as exc_info:
            todo_list.add("")
        assert "Title cannot be empty" in str(exc_info.value)

    def test_add_validation_whitespace_title(self) -> None:
        """Should raise ValidationError for whitespace-only title."""
        todo_list = TodoList()
        with pytest.raises(ValidationError) as exc_info:
            todo_list.add("   ")
        assert "Title cannot be empty" in str(exc_info.value)


class TestTodoListGet:
    """Tests for TodoList.get() method."""

    def test_get_existing_todo(self) -> None:
        """Should return the todo when it exists."""
        todo_list = TodoList()
        added = todo_list.add("Test task")
        retrieved = todo_list.get(added.id)
        assert retrieved is not None
        assert retrieved.title == "Test task"

    def test_get_nonexistent_todo(self) -> None:
        """Should return None when todo doesn't exist."""
        todo_list = TodoList()
        result = todo_list.get(999)
        assert result is None


class TestTodoListGetAll:
    """Tests for TodoList.get_all() method."""

    def test_get_all_empty(self) -> None:
        """Should return empty list when no todos exist."""
        todo_list = TodoList()
        assert todo_list.get_all() == []

    def test_get_all_with_todos(self) -> None:
        """Should return all todos sorted by ID."""
        todo_list = TodoList()
        todo_list.add("Third")
        todo_list.add("First")
        todo_list.add("Second")
        all_todos = todo_list.get_all()
        assert len(all_todos) == 3
        assert all_todos[0].id == 1
        assert all_todos[1].id == 2
        assert all_todos[2].id == 3


class TestTodoListMarkComplete:
    """Tests for TodoList.mark_complete() method."""

    def test_mark_complete_success(self) -> None:
        """Should mark todo as completed."""
        todo_list = TodoList()
        todo = todo_list.add("Test task")
        completed = todo_list.mark_complete(todo.id)
        assert completed.status == Status.COMPLETED

    def test_mark_complete_not_found(self) -> None:
        """Should raise error when todo doesn't exist."""
        todo_list = TodoList()
        with pytest.raises(Exception):
            todo_list.mark_complete(999)


class TestTodoListUpdate:
    """Tests for TodoList.update() method."""

    def test_update_single_field(self) -> None:
        """Should update a single field."""
        todo_list = TodoList()
        todo = todo_list.add("Original title")
        updated = todo_list.update(todo.id, title="New title")
        assert updated.title == "New title"

    def test_update_multiple_fields(self) -> None:
        """Should update multiple fields."""
        todo_list = TodoList()
        todo = todo_list.add("Original")
        updated = todo_list.update(
            todo.id,
            title="New title",
            priority=Priority.HIGH,
        )
        assert updated.title == "New title"
        assert updated.priority == Priority.HIGH

    def test_update_not_found(self) -> None:
        """Should raise error when todo doesn't exist."""
        todo_list = TodoList()
        with pytest.raises(Exception):
            todo_list.update(999, title="New title")


class TestTodoListDelete:
    """Tests for TodoList.delete() method."""

    def test_delete_success(self) -> None:
        """Should remove todo from collection."""
        todo_list = TodoList()
        todo = todo_list.add("Test task")
        todo_list.delete(todo.id)
        assert len(todo_list.get_all()) == 0
        assert todo_list.get(todo.id) is None

    def test_delete_not_found(self) -> None:
        """Should raise error when todo doesn't exist."""
        todo_list = TodoList()
        with pytest.raises(Exception):
            todo_list.delete(999)
