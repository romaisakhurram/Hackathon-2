#!/usr/bin/env python3
"""Test script to demonstrate the interactive features of TodoFlow."""

from todo_app.application import TodoList
from todo_app.domain import Priority, Status


def demo_interactive_features():
    """Demonstrate the interactive features of TodoFlow."""
    print("TodoFlow Interactive Features Demo")
    print("=" * 40)
    
    # Create a todo list instance
    todo_list = TodoList()
    
    print("\n1. ADDING TODOS")
    print("-" * 20)
    
    # Add some todos
    todo1 = todo_list.add("Buy groceries", description="Milk, eggs, bread", priority=Priority.HIGH)
    print(f"[+] Added: [{todo1.id}] {todo1.title} (Priority: {todo1.priority.value})")
    
    todo2 = todo_list.add("Walk the dog", priority=Priority.MEDIUM)
    print(f"[+] Added: [{todo2.id}] {todo2.title} (Priority: {todo2.priority.value})")
    
    todo3 = todo_list.add("Read book", description="Finish chapter 3", priority=Priority.LOW)
    print(f"[+] Added: [{todo3.id}] {todo3.title} (Priority: {todo3.priority.value})")
    
    print("\n2. VIEWING ALL TODOS")
    print("-" * 20)
    
    # Display all todos
    todos = todo_list.get_all()
    print(f"{'#':<3} | {'ID':<3} | {'Status':<12} | {'Priority':<8} | {'Title'}")
    print("-" * 60)
    
    for i, todo in enumerate(todos, 1):
        if todo.status == Status.PENDING:
            status_symbol = "O"
        elif todo.status == Status.IN_PROGRESS:
            status_symbol = ">"
        elif todo.status == Status.COMPLETED:
            status_symbol = "X"
            
        print(f"{i:<3} | {todo.id:<3} | {status_symbol} {todo.status.value:<10} | {todo.priority.value:<8} | {todo.title}")
    
    print(f"\nTotal todos: {len(todos)}")
    
    print("\n3. COMPLETING A TODO")
    print("-" * 20)
    
    # Complete a todo
    completed_todo = todo_list.mark_complete(todo1.id)
    print(f"[+] Completed: [{completed_todo.id}] {completed_todo.title}")
    print(f"  New status: {completed_todo.status.value}")
    
    print("\n4. UPDATING A TODO")
    print("-" * 20)
    
    # Update a todo
    updated_todo = todo_list.update(
        todo_id=todo2.id,
        title="Walk the dog in the morning",
        description="30 minute walk in the park",
        priority=Priority.HIGH
    )
    print(f"[+] Updated: [{updated_todo.id}] {updated_todo.title}")
    print(f"  New priority: {updated_todo.priority.value}")
    print(f"  New description: {updated_todo.description}")
    
    print("\n5. VIEWING TODOS AFTER CHANGES")
    print("-" * 35)
    
    # Display all todos after changes
    todos = todo_list.get_all()
    print(f"{'#':<3} | {'ID':<3} | {'Status':<12} | {'Priority':<8} | {'Title'}")
    print("-" * 60)
    
    for i, todo in enumerate(todos, 1):
        if todo.status == Status.PENDING:
            status_symbol = "O"
        elif todo.status == Status.IN_PROGRESS:
            status_symbol = ">"
        elif todo.status == Status.COMPLETED:
            status_symbol = "X"
            
        print(f"{i:<3} | {todo.id:<3} | {status_symbol} {todo.status.value:<10} | {todo.priority.value:<8} | {todo.title}")
    
    print("\n6. DELETING A TODO")
    print("-" * 20)
    
    # Delete a todo
    print(f"Deleting: [{todo3.id}] {todo3.title}")
    todo_list.delete(todo3.id)
    print("[+] Todo deleted")
    
    print("\n7. FINAL TODO LIST")
    print("-" * 20)
    
    # Display final todos
    final_todos = todo_list.get_all()
    if final_todos:
        print(f"{'#':<3} | {'ID':<3} | {'Status':<12} | {'Priority':<8} | {'Title'}")
        print("-" * 60)
        
        for i, todo in enumerate(final_todos, 1):
            if todo.status == Status.PENDING:
                status_symbol = "O"
            elif todo.status == Status.IN_PROGRESS:
                status_symbol = ">"
            elif todo.status == Status.COMPLETED:
                status_symbol = "X"
                
            print(f"{i:<3} | {todo.id:<3} | {status_symbol} {todo.status.value:<10} | {todo.priority.value:<8} | {todo.title}")
    else:
        print("No todos remaining.")
    
    print(f"\nFinal count: {len(final_todos)} todos")
    
    print("\nDemo completed! The interactive mode provides a menu-driven interface")
    print("where users can select options by number instead of typing commands.")


if __name__ == "__main__":
    demo_interactive_features()