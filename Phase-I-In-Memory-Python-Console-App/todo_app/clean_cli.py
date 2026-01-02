#!/usr/bin/env python3
"""Clean and user-friendly CLI Todo application with numbered menu interface."""

import sys
from typing import Optional, List

from .application import TodoList
from .domain import Priority, Status


class CleanTodoApp:
    """Clean and user-friendly CLI Todo application with numbered menu interface."""

    def __init__(self) -> None:
        """Initialize the clean todo application."""
        self.todo_list = TodoList()
        self.menu_options = [
            "Add new todo",
            "View all todos",
            "Show specific todo",
            "Update a todo",
            "Complete a todo",
            "Delete a todo",
            "Exit"
        ]

    def display_welcome(self) -> None:
        """Display welcome message."""
        print("=" * 50)
        print("           TODOFLOW - Todo Manager")
        print("=" * 50)
        print("Manage your tasks with a clean interface")
        print()

    def display_menu(self) -> None:
        """Display the main menu with numbered options."""
        print("SELECT AN OPTION:")
        print("-" * 30)
        
        for i, option in enumerate(self.menu_options, 1):
            print(f"{i}. {option}")
        
        print("-" * 30)

    def get_choice(self, max_choice: int) -> Optional[int]:
        """Get and validate user choice."""
        try:
            choice = input(f"Enter choice (1-{max_choice}): ").strip()
            
            if choice.lower() in ['q', 'quit', 'exit']:
                return max_choice  # Return exit option
            
            choice_num = int(choice)
            if 1 <= choice_num <= max_choice:
                return choice_num
            else:
                print(f"! Invalid choice. Please enter 1-{max_choice}")
                return self.get_choice(max_choice)
        except ValueError:
            print("! Please enter a valid number")
            return self.get_choice(max_choice)
        except EOFError:
            print("\n! Exiting...")
            return max_choice

    def display_todos(self) -> List:
        """Display all todos in a clean format."""
        todos = self.todo_list.get_all()
        
        if not todos:
            print("\nNo todos found.")
            return todos
        
        print(f"\nYOUR TODOS ({len(todos)} total):")
        print("-" * 60)
        print(f"{'ID':<3} | {'Status':<10} | {'Priority':<8} | {'Title':<25}")
        print("-" * 60)
        
        for todo in todos:
            status_symbol = "O" if todo.status == Status.PENDING else \
                          ">" if todo.status == Status.IN_PROGRESS else "X"

            print(f"{todo.id:<3} | {status_symbol} {todo.status.value:<8} | {todo.priority.value:<8} | {todo.title:<25}")
        
        print("-" * 60)
        return todos

    def add_todo(self) -> None:
        """Add a new todo with clean prompts."""
        print("\n[ADDING NEW TODO]")
        print("-" * 20)
        
        try:
            title = input("Enter title: ").strip()
            if not title:
                print("! Title cannot be empty")
                return
            
            description = input("Enter description (optional): ").strip()
            
            print("\nSelect priority:")
            priorities = ["Low", "Medium", "High"]
            for i, p in enumerate(priorities, 1):
                print(f"  {i}. {p}")
            
            priority_choice = input(f"Priority (1-3, default 2): ").strip()
            if priority_choice == "":
                priority_choice = "2"
            
            priority_choice = int(priority_choice)
            if 1 <= priority_choice <= 3:
                priority = Priority[priorities[priority_choice-1].upper()]
            else:
                priority = Priority.MEDIUM
            
            todo = self.todo_list.add(title=title, description=description, priority=priority)
            print(f"\n✓ Added: [{todo.id}] {todo.title}")
            
        except ValueError:
            print("! Invalid priority choice")
        except Exception as e:
            print(f"! Error adding todo: {e}")

    def show_todo(self) -> None:
        """Show details of a specific todo."""
        todos = self.todo_list.get_all()
        if not todos:
            print("\n! No todos to show")
            return
        
        print(f"\n[SHOW TODO - {len(todos)} available]")
        print("-" * 20)
        
        for todo in todos:
            print(f"  {todo.id}. {todo.title}")
        
        try:
            todo_id = int(input(f"\nEnter todo ID (1-{todos[-1].id}): "))
            todo = self.todo_list.get(todo_id)
            
            if todo:
                print(f"\nTODO DETAILS:")
                print("-" * 20)
                print(f"ID:         {todo.id}")
                print(f"Title:      {todo.title}")
                print(f"Description: {todo.description}")
                print(f"Status:     {todo.status.value}")
                print(f"Priority:   {todo.priority.value}")
                print(f"Created:    {todo.created_at.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"! Todo with ID {todo_id} not found")
        except ValueError:
            print("! Please enter a valid ID")

    def update_todo(self) -> None:
        """Update a todo with clean prompts."""
        todos = self.todo_list.get_all()
        if not todos:
            print("\n! No todos to update")
            return
        
        print(f"\n[UPDATE TODO - {len(todos)} available]")
        print("-" * 20)
        
        for todo in todos:
            print(f"  {todo.id}. {todo.title}")
        
        try:
            todo_id = int(input(f"\nEnter todo ID to update (1-{todos[-1].id}): "))
            todo = self.todo_list.get(todo_id)
            
            if not todo:
                print(f"! Todo with ID {todo_id} not found")
                return
            
            print(f"\nCurrent: {todo.title}")
            new_title = input(f"New title (current: '{todo.title}'): ").strip()
            if not new_title:
                new_title = todo.title
            
            new_description = input(f"New description (current: '{todo.description}'): ").strip()
            if new_description == "":
                new_description = todo.description
            
            print(f"\nCurrent priority: {todo.priority.value}")
            print("Select new priority:")
            priorities = ["Low", "Medium", "High"]
            for i, p in enumerate(priorities, 1):
                print(f"  {i}. {p}")
            
            priority_choice = input(f"New priority (1-3, Enter to keep current): ").strip()
            if priority_choice:
                priority_choice = int(priority_choice)
                if 1 <= priority_choice <= 3:
                    priority = Priority[priorities[priority_choice-1].upper()]
                else:
                    priority = todo.priority
            else:
                priority = todo.priority
            
            updated = self.todo_list.update(
                todo_id=todo_id,
                title=new_title,
                description=new_description,
                priority=priority
            )
            
            print(f"\n✓ Updated: [{updated.id}] {updated.title}")
            
        except ValueError:
            print("! Please enter valid inputs")

    def complete_todo(self) -> None:
        """Mark a todo as complete."""
        todos = self.todo_list.get_all()
        if not todos:
            print("\n! No todos to complete")
            return
        
        print(f"\n[COMPLETE TODO - {len(todos)} available]")
        print("-" * 20)
        
        for todo in todos:
            status_symbol = "○" if todo.status == Status.PENDING else \
                          "▶" if todo.status == Status.IN_PROGRESS else "✓"
            print(f"  {todo.id}. {status_symbol} {todo.title}")
        
        try:
            todo_id = int(input(f"\nEnter todo ID to complete (1-{todos[-1].id}): "))
            todo = self.todo_list.get(todo_id)
            
            if not todo:
                print(f"! Todo with ID {todo_id} not found")
                return
            
            if todo.status == Status.COMPLETED:
                print(f"! Todo [{todo.id}] is already completed")
                return
            
            completed = self.todo_list.mark_complete(todo_id)
            print(f"\n✓ Completed: [{completed.id}] {completed.title}")
            
        except ValueError:
            print("! Please enter a valid ID")

    def delete_todo(self) -> None:
        """Delete a todo."""
        todos = self.todo_list.get_all()
        if not todos:
            print("\n! No todos to delete")
            return
        
        print(f"\n[DELETE TODO - {len(todos)} available]")
        print("-" * 20)
        
        for todo in todos:
            print(f"  {todo.id}. {todo.title}")
        
        try:
            todo_id = int(input(f"\nEnter todo ID to delete (1-{todos[-1].id}): "))
            todo = self.todo_list.get(todo_id)
            
            if not todo:
                print(f"! Todo with ID {todo_id} not found")
                return
            
            confirm = input(f"Confirm delete '{todo.title}'? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                self.todo_list.delete(todo_id)
                print(f"\n✓ Deleted: [{todo.id}] {todo.title}")
            else:
                print("! Delete cancelled")
                
        except ValueError:
            print("! Please enter a valid ID")

    def run(self) -> None:
        """Run the clean todo application."""
        self.display_welcome()
        
        while True:
            self.display_menu()
            choice = self.get_choice(len(self.menu_options))
            
            if choice == 1:  # Add
                self.add_todo()
            elif choice == 2:  # View all
                self.display_todos()
            elif choice == 3:  # Show specific
                self.show_todo()
            elif choice == 4:  # Update
                self.update_todo()
            elif choice == 5:  # Complete
                self.complete_todo()
            elif choice == 6:  # Delete
                self.delete_todo()
            elif choice == 7:  # Exit
                print("\nThank you for using TodoFlow!")
                break
            
            print()  # Add spacing
            input("Press Enter to continue...")


def main() -> int:
    """Main entry point for the clean CLI."""
    app = CleanTodoApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())