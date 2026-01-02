"""Interactive CLI interface for TodoFlow application using simple input.

Provides a terminal-based UI with number selection for tasks.
"""

import sys
from typing import Optional, List

from .application import TodoList
from .domain import Priority, Status


class SimpleInteractiveTodoApp:
    """Simple interactive terminal UI for TodoFlow with number selection."""

    def __init__(self) -> None:
        """Initialize the interactive application."""
        self.todo_list = TodoList()
        
        # Main menu options
        self.main_menu_options = [
            "Add new todo",
            "View all todos",
            "Complete a todo",
            "Update a todo",
            "Delete a todo",
            "Exit"
        ]

    def display_main_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "="*50)
        print("TodoFlow - Interactive Todo Manager")
        print("="*50)
        print("Select an option using the number:")
        print()
        
        for i, option in enumerate(self.main_menu_options, 1):
            print(f"{i}. {option}")
        
        print()

    def display_todos(self) -> List:
        """Display all todos and return the list."""
        todos = self.todo_list.get_all()
        
        if not todos:
            print("\nNo todos found.")
            return todos
        
        print("\nYour Todos:")
        print("-" * 60)
        print(f"{'#':<3} | {'ID':<3} | {'Status':<12} | {'Priority':<8} | {'Title'}")
        print("-" * 60)
        
        for i, todo in enumerate(todos, 1):
            status_symbol = "○"  # pending
            if todo.status == Status.IN_PROGRESS:
                status_symbol = "▶"
            elif todo.status == Status.COMPLETED:
                status_symbol = "✓"
                
            print(f"{i:<3} | {todo.id:<3} | {status_symbol} {todo.status.value:<10} | {todo.priority.value:<8} | {todo.title}")
        
        print()
        return todos

    def get_user_choice(self, max_choice: int) -> Optional[int]:
        """Get user choice with validation."""
        try:
            choice = input(f"Enter your choice (1-{max_choice}, or 'q' to quit): ").strip().lower()

            if choice == 'q':
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= max_choice:
                return choice_num
            else:
                print(f"Please enter a number between 1 and {max_choice}")
                return self.get_user_choice(max_choice)
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
            return self.get_user_choice(max_choice)
        except EOFError:
            print("\nExiting...")
            return None

    def handle_add_todo(self) -> None:
        """Handle adding a new todo."""
        print("\n--- Add New Todo ---")
        try:
            title = input("Enter title: ").strip()
        except EOFError:
            print("\nReturning to main menu...")
            return

        if not title:
            print("Title cannot be empty!")
            return

        try:
            description = input("Enter description (optional, press Enter to skip): ").strip()
        except EOFError:
            print("\nReturning to main menu...")
            return

        print("Select priority:")
        priorities = ["low", "medium", "high"]
        for i, p in enumerate(priorities, 1):
            print(f"{i}. {p.title()}")

        try:
            priority_input = input(f"Enter priority (1-3, default 2): ")
            if priority_input.strip() == "":
                priority_choice = 2
            else:
                priority_choice = int(priority_input)
            if 1 <= priority_choice <= 3:
                priority_str = priorities[priority_choice - 1]
            else:
                priority_str = "medium"
        except ValueError:
            priority_str = "medium"

        priority = Priority[priority_str.upper()]

        try:
            todo = self.todo_list.add(title=title, description=description, priority=priority)
            print(f"✓ Added todo: [{todo.id}] {todo.title}")
        except Exception as e:
            print(f"Error adding todo: {e}")

    def handle_complete_todo(self) -> None:
        """Handle marking a todo as complete."""
        todos = self.display_todos()

        if not todos:
            try:
                input("\nPress Enter to continue...")
            except EOFError:
                print("\nReturning to main menu...")
            return

        try:
            choice_input = input(f"Enter the number of the todo to complete (1-{len(todos)}): ")
            choice = int(choice_input) - 1
            if 0 <= choice < len(todos):
                todo = todos[choice]
                completed = self.todo_list.mark_complete(todo.id)
                print(f"✓ Completed: [{completed.id}] {completed.title}")
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!")
        except EOFError:
            print("\nReturning to main menu...")

    def handle_update_todo(self) -> None:
        """Handle updating a todo."""
        todos = self.display_todos()

        if not todos:
            try:
                input("\nPress Enter to continue...")
            except EOFError:
                print("\nReturning to main menu...")
            return

        try:
            choice_input = input(f"Enter the number of the todo to update (1-{len(todos)}): ")
            choice = int(choice_input) - 1
            if 0 <= choice < len(todos):
                todo = todos[choice]
                print(f"\nUpdating todo: [{todo.id}] {todo.title}")

                try:
                    new_title_input = input(f"Enter new title (current: '{todo.title}', press Enter to keep): ")
                    new_title = new_title_input.strip()
                    if not new_title:
                        new_title = todo.title
                except EOFError:
                    print("\nReturning to main menu...")
                    return

                try:
                    new_description_input = input(f"Enter new description (current: '{todo.description}', press Enter to keep): ")
                    new_description = new_description_input.strip()
                    if not new_description:
                        new_description = todo.description
                except EOFError:
                    print("\nReturning to main menu...")
                    return

                print(f"Current priority: {todo.priority.value}")
                print("Select new priority:")
                priorities = ["low", "medium", "high"]
                for i, p in enumerate(priorities, 1):
                    print(f"{i}. {p.title()}")

                try:
                    priority_choice = input(f"Enter priority (1-3, press Enter to keep current): ").strip()
                    if priority_choice:
                        priority_choice = int(priority_choice)
                        if 1 <= priority_choice <= 3:
                            priority = Priority[priorities[priority_choice - 1].upper()]
                        else:
                            priority = todo.priority
                    else:
                        priority = todo.priority
                except ValueError:
                    priority = todo.priority

                updated = self.todo_list.update(
                    todo_id=todo.id,
                    title=new_title,
                    description=new_description,
                    priority=priority
                )

                print(f"✓ Updated todo: [{updated.id}] {updated.title}")
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!")
        except EOFError:
            print("\nReturning to main menu...")

    def handle_delete_todo(self) -> None:
        """Handle deleting a todo."""
        todos = self.display_todos()

        if not todos:
            try:
                input("\nPress Enter to continue...")
            except EOFError:
                print("\nReturning to main menu...")
            return

        try:
            choice_input = input(f"Enter the number of the todo to delete (1-{len(todos)}): ")
            choice = int(choice_input) - 1
            if 0 <= choice < len(todos):
                todo = todos[choice]
                try:
                    confirm = input(f"Are you sure you want to delete '{todo.title}'? (y/N): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        self.todo_list.delete(todo.id)
                        print(f"✓ Deleted todo: [{todo.id}] {todo.title}")
                    else:
                        print("Deletion cancelled.")
                except EOFError:
                    print("\nReturning to main menu...")
                    return
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!")
        except EOFError:
            print("\nReturning to main menu...")

    def run(self) -> None:
        """Run the interactive application."""
        print("Welcome to TodoFlow Interactive Mode!")
        print("Use numbers to select options, or 'q' to quit at any prompt.")
        
        while True:
            self.display_main_menu()
            choice = self.get_user_choice(len(self.main_menu_options))
            
            if choice is None:  # User chose to quit
                print("\nGoodbye!")
                break
            elif choice == 1:  # Add new todo
                self.handle_add_todo()
            elif choice == 2:  # View all todos
                self.display_todos()
                input("\nPress Enter to continue...")
            elif choice == 3:  # Complete a todo
                self.handle_complete_todo()
                input("\nPress Enter to continue...")
            elif choice == 4:  # Update a todo
                self.handle_update_todo()
                input("\nPress Enter to continue...")
            elif choice == 5:  # Delete a todo
                self.handle_delete_todo()
                input("\nPress Enter to continue...")
            elif choice == 6:  # Exit
                print("\nGoodbye!")
                break
            
            # Clear screen or just continue


def main() -> int:
    """Main entry point for the interactive CLI."""
    app = SimpleInteractiveTodoApp()
    app.run()
    return 0