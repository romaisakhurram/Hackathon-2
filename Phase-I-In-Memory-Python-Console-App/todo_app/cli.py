"""CLI interface for TodoFlow application.

Provides command-line interface for managing todo items.
"""

import argparse
import sys
from typing import Optional
from todo_app.application import TodoList
from todo_app.domain import Priority, TodoNotFoundError, ValidationError


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="todoflow",
        description="A simple in-memory todo console application",
        epilog="Use 'todoflow help <command>' for more info on a specific command.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new todo item")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument(
        "-d", "--description", help="Task description", default=""
    )
    add_parser.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="Task priority (default: medium)",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all todo items")
    list_parser.add_argument(
        "-s",
        "--status",
        choices=["pending", "in_progress", "completed"],
        help="Filter by status",
    )
    list_parser.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
        help="Filter by priority",
    )

    # Show command
    show_parser = subparsers.add_parser("show", help="Show a single todo item")
    show_parser.add_argument("id", type=int, help="Todo ID to display")

    # Complete command
    complete_parser = subparsers.add_parser(
        "complete", help="Mark a todo as completed"
    )
    complete_parser.add_argument("id", type=int, help="Todo ID to complete")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a todo item")
    update_parser.add_argument("id", type=int, help="Todo ID to update")
    update_parser.add_argument("-t", "--title", help="New task title")
    update_parser.add_argument("-d", "--description", help="New description")
    update_parser.add_argument(
        "-p",
        "--priority",
        choices=["low", "medium", "high"],
        help="New priority level",
    )

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a todo item")
    delete_parser.add_argument("id", type=int, help="Todo ID to delete")

    return parser


def priority_from_string(value: str) -> Priority:
    """Convert priority string to Priority enum.

    Args:
        value: Priority string ('low', 'medium', 'high').

    Returns:
        Corresponding Priority enum value.
    """
    mapping = {
        "low": Priority.LOW,
        "medium": Priority.MEDIUM,
        "high": Priority.HIGH,
    }
    return mapping[value]


def handle_add(args: argparse.Namespace, todo_list: TodoList) -> int:
    """Handle the add command.

    Args:
        args: Parsed command arguments.
        todo_list: The todo list instance.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        priority = priority_from_string(args.priority)
        todo = todo_list.add(
            title=args.title,
            description=args.description,
            priority=priority,
        )
        print(f"Added todo: [{todo.id}] {todo.title} ({todo.priority.value})")
        return 0
    except ValidationError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return 1


def handle_list(args: argparse.Namespace, todo_list: TodoList) -> int:
    """Handle the list command.

    Args:
        args: Parsed command arguments.
        todo_list: The todo list instance.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    todos = todo_list.get_all()

    if not todos:
        print("No todos found. Add one with: todoflow add 'Task title'")
        return 0

    # Filter by status if specified
    if args.status:
        status_map = {
            "pending": "pending",
            "in_progress": "in_progress",
            "completed": "completed",
        }
        todos = [t for t in todos if t.status.value == status_map[args.status]]

    # Filter by priority if specified
    if args.priority:
        todos = [t for t in todos if t.priority.value == args.priority]

    if not todos:
        print("No todos match the specified filters.")
        return 0

    # Print header
    print(f"{'ID':<4} | {'Status':<12} | {'Priority':<8} | {'Title'}")
    print("-" * 60)

    for todo in todos:
        print(
            f"{todo.id:<4} | {todo.status.value:<12} | {todo.priority.value:<8} | {todo.title}"
        )

    return 0


def handle_show(args: argparse.Namespace, todo_list: TodoList) -> int:
    """Handle the show command.

    Args:
        args: Parsed command arguments.
        todo_list: The todo list instance.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    todo = todo_list.get(args.id)
    if todo is None:
        print(f"Error: Todo with ID {args.id} not found", file=sys.stderr)
        return 2

    print(f"ID: {todo.id}")
    print(f"Title: {todo.title}")
    print(f"Description: {todo.description}")
    print(f"Status: {todo.status.value}")
    print(f"Priority: {todo.priority.value}")
    print(f"Created: {todo.created_at.isoformat()}")

    return 0


def handle_complete(args: argparse.Namespace, todo_list: TodoList) -> int:
    """Handle the complete command.

    Args:
        args: Parsed command arguments.
        todo_list: The todo list instance.

    Returns:
        Exit code (0 for success, 1 for error, 2 for not found).
    """
    try:
        todo = todo_list.mark_complete(args.id)
        print(f"Completed: [{todo.id}] {todo.title}")
        return 0
    except TodoNotFoundError:
        print(f"Error: Todo with ID {args.id} not found", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_update(args: argparse.Namespace, todo_list: TodoList) -> int:
    """Handle the update command.

    Args:
        args: Parsed command arguments.
        todo_list: The todo list instance.

    Returns:
        Exit code (0 for success, 1 for error, 2 for not found).
    """
    try:
        priority: Optional[Priority] = None
        if args.priority:
            priority = priority_from_string(args.priority)

        todo = todo_list.update(
            todo_id=args.id,
            title=args.title,
            description=args.description,
            priority=priority,
        )

        # Show what was updated
        print(f"Updated todo [{todo.id}]:")
        if args.title:
            print(f"  Title: {args.title}")
        if args.description is not None:
            print(f"  Description: {args.description}")
        if args.priority:
            print(f"  Priority: {args.priority}")

        return 0
    except TodoNotFoundError:
        print(f"Error: Todo with ID {args.id} not found", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_delete(args: argparse.Namespace, todo_list: TodoList) -> int:
    """Handle the delete command.

    Args:
        args: Parsed command arguments.
        todo_list: The todo list instance.

    Returns:
        Exit code (0 for success, 1 for error, 2 for not found).
    """
    try:
        todo = todo_list.get(args.id)
        if todo is None:
            print(f"Error: Todo with ID {args.id} not found", file=sys.stderr)
            return 2
        todo_list.delete(args.id)
        print(f"Deleted todo [{args.id}] {todo.title}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_help() -> int:
    """Handle the help command.

    Returns:
        Exit code (0 for success).
    """
    print("""TodoFlow CLI - In-Memory Todo Application

Usage:
  todoflow <command> [options]

Commands:
  add         Add a new todo item
  list        List all todos (with optional filters)
  show        Show details of a single todo
  complete    Mark a todo as completed
  update      Update a todo's title, description, or priority
  delete      Delete a todo item
  help        Show this help message

For more details on a specific command:
  todoflow <command> --help

Examples:
  todoflow add "Buy groceries" --priority high
  todoflow list --status pending
  todoflow complete 1
  todoflow update 1 --title "New title"
""")
    return 0


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code from the executed command.
    """
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:] if sys.argv[1:] else ["--help"])

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "help":
        return handle_help()

    todo_list = TodoList()

    handlers = {
        "add": handle_add,
        "list": handle_list,
        "show": handle_show,
        "complete": handle_complete,
        "update": handle_update,
        "delete": handle_delete,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args, todo_list)

    return 0
