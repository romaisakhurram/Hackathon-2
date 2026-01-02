#!/usr/bin/env python3
"""Demo script for the clean CLI interface."""

from todo_app.application import TodoList
from todo_app.domain import Priority, Status


def demo_clean_cli_features():
    """Demonstrate the clean CLI interface features."""
    print("DEMO: Clean CLI Todo Application")
    print("=" * 40)
    print()
    
    # Create a todo list instance
    todo_list = TodoList()
    
    print("1. ADDING TODOS")
    print("-" * 20)
    
    # Add some todos
    todo1 = todo_list.add("Buy groceries", description="Milk, eggs, bread", priority=Priority.HIGH)
    print(f"+ Added: [{todo1.id}] {todo1.title}")

    todo2 = todo_list.add("Walk the dog", priority=Priority.MEDIUM)
    print(f"+ Added: [{todo2.id}] {todo2.title}")

    todo3 = todo_list.add("Read book", description="Finish chapter 3", priority=Priority.LOW)
    print(f"+ Added: [{todo3.id}] {todo3.title}")
    
    print(f"\n2. VIEWING ALL TODOS ({len(todo_list.get_all())} total)")
    print("-" * 30)
    
    # Display all todos in clean format
    todos = todo_list.get_all()
    print(f"{'ID':<3} | {'Status':<10} | {'Priority':<8} | {'Title':<25}")
    print("-" * 60)
    
    for todo in todos:
        status_symbol = "O" if todo.status == Status.PENDING else \
                      ">" if todo.status == Status.IN_PROGRESS else "X"

        print(f"{todo.id:<3} | {status_symbol} {todo.status.value:<8} | {todo.priority.value:<8} | {todo.title:<25}")
    
    print("\n3. COMPLETING A TODO")
    print("-" * 20)
    
    # Complete a todo
    completed_todo = todo_list.mark_complete(todo1.id)
    print(f"+ Completed: [{completed_todo.id}] {completed_todo.title}")

    print("\n4. VIEWING UPDATED LIST")
    print("-" * 25)

    # Display updated list
    todos = todo_list.get_all()
    print(f"{'ID':<3} | {'Status':<10} | {'Priority':<8} | {'Title':<25}")
    print("-" * 60)

    for todo in todos:
        status_symbol = "O" if todo.status == Status.PENDING else \
                      ">" if todo.status == Status.IN_PROGRESS else "X"

        print(f"{todo.id:<3} | {status_symbol} {todo.status.value:<8} | {todo.priority.value:<8} | {todo.title:<25}")

    print("\n5. UPDATING A TODO")
    print("-" * 20)

    # Update a todo
    updated_todo = todo_list.update(
        todo_id=todo2.id,
        title="Walk the dog in the morning",
        description="30 minute walk in the park",
        priority=Priority.HIGH
    )
    print(f"+ Updated: [{updated_todo.id}] {updated_todo.title}")

    print("\n6. DELETING A TODO")
    print("-" * 20)

    # Delete a todo
    print(f"Deleting: [{todo3.id}] {todo3.title}")
    todo_list.delete(todo3.id)
    print("+ Todo deleted")
    
    print("\n7. FINAL TODO LIST")
    print("-" * 20)
    
    # Display final todos
    final_todos = todo_list.get_all()
    if final_todos:
        print(f"{'ID':<3} | {'Status':<10} | {'Priority':<8} | {'Title':<25}")
        print("-" * 60)
        
        for todo in final_todos:
            status_symbol = "O" if todo.status == Status.PENDING else \
                          ">" if todo.status == Status.IN_PROGRESS else "X"

            print(f"{todo.id:<3} | {status_symbol} {todo.status.value:<8} | {todo.priority.value:<8} | {todo.title:<25}")
    else:
        print("No todos remaining.")
    
    print(f"\nFinal count: {len(final_todos)} todos")
    
    print("\nDemo completed! The clean CLI provides a user-friendly interface")
    print("with numbered menus and clear visual formatting.")


if __name__ == "__main__":
    demo_clean_cli_features()