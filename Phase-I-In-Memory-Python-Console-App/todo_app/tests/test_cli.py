"""Tests for the CLI interface."""

import pytest
from io import StringIO
from unittest.mock import patch

from todo_app.cli import (
    handle_add,
    handle_delete,
    handle_help,
    handle_list,
    handle_show,
    handle_complete,
    handle_update,
)
from todo_app.application import TodoList
from todo_app.domain import Priority, Status


class TestHandleList:
    """Tests for list CLI command."""

    def test_list_empty(self) -> None:
        """Should show message when list is empty."""
        todo_list = TodoList()
        with patch("sys.stdout", new=StringIO()) as f:
            result = handle_list(todo_list=todo_list, args=None)
        assert "No todos found" in f.getvalue()
        assert result == 0

    def test_list_with_todos(self) -> None:
        """Should list all todos."""
        todo_list = TodoList()
        todo_list.add("First")
        todo_list.add("Second")
        with patch("sys.stdout", new=StringIO()) as f:
            class Args:
                status = None
                priority = None
            result = handle_list(args=Args(), todo_list=todo_list)
        output = f.getvalue()
        assert "First" in output
        assert "Second" in output
        assert result == 0


class TestHandleShow:
    """Tests for show CLI command."""

    def test_show_existing_todo(self) -> None:
        """Should show todo details."""
        todo_list = TodoList()
        todo = todo_list.add("Test task")
        with patch("sys.stdout", new=StringIO()) as f:
            class Args:
                id = 1
            result = handle_show(args=Args(), todo_list=todo_list)
        output = f.getvalue()
        assert "Test task" in output
        assert result == 0

    def test_show_not_found(self) -> None:
        """Should return error when todo not found."""
        todo_list = TodoList()
        with patch("sys.stderr", new=StringIO()) as f:
            class Args:
                id = 999
            result = handle_show(args=Args(), todo_list=todo_list)
        assert "not found" in f.getvalue()
        assert result == 2


class TestHandleComplete:
    """Tests for complete CLI command."""

    def test_complete_success(self) -> None:
        """Should mark todo as complete."""
        todo_list = TodoList()
        todo_list.add("Test task")
        with patch("sys.stdout", new=StringIO()) as f:
            class Args:
                id = 1
            result = handle_complete(args=Args(), todo_list=todo_list)
        output = f.getvalue()
        assert "Completed" in output
        assert result == 0

    def test_complete_not_found(self) -> None:
        """Should return error when todo not found."""
        todo_list = TodoList()
        with patch("sys.stderr", new=StringIO()) as f:
            class Args:
                id = 999
            result = handle_complete(args=Args(), todo_list=todo_list)
        assert "not found" in f.getvalue()
        assert result == 2


class TestHandleUpdate:
    """Tests for update CLI command."""

    def test_update_title(self) -> None:
        """Should update todo title."""
        todo_list = TodoList()
        todo_list.add("Original")
        with patch("sys.stdout", new=StringIO()) as f:
            class Args:
                id = 1
                title = "New title"
                description = None
                priority = None
            result = handle_update(args=Args(), todo_list=todo_list)
        output = f.getvalue()
        assert "New title" in output
        assert result == 0

    def test_update_not_found(self) -> None:
        """Should return error when todo not found."""
        todo_list = TodoList()
        with patch("sys.stderr", new=StringIO()) as f:
            class Args:
                id = 999
                title = "New title"
                description = None
                priority = None
            result = handle_update(args=Args(), todo_list=todo_list)
        assert "not found" in f.getvalue()
        assert result == 2


class TestHandleDelete:
    """Tests for delete CLI command."""

    def test_delete_success(self) -> None:
        """Should delete todo."""
        todo_list = TodoList()
        todo_list.add("Test task")
        with patch("sys.stdout", new=StringIO()) as f:
            class Args:
                id = 1
            result = handle_delete(args=Args(), todo_list=todo_list)
        output = f.getvalue()
        assert "Deleted" in output
        assert len(todo_list.get_all()) == 0
        assert result == 0

    def test_delete_not_found(self) -> None:
        """Should return error when todo not found."""
        todo_list = TodoList()
        with patch("sys.stderr", new=StringIO()) as f:
            class Args:
                id = 999
            result = handle_delete(args=Args(), todo_list=todo_list)
        assert "not found" in f.getvalue()
        assert result == 2


class TestHandleHelp:
    """Tests for help CLI command."""

    def test_help_shows_usage(self) -> None:
        """Should show help message."""
        with patch("sys.stdout", new=StringIO()) as f:
            result = handle_help()
        output = f.getvalue()
        assert "Usage" in output
        assert "add" in output
        assert "list" in output
        assert result == 0
