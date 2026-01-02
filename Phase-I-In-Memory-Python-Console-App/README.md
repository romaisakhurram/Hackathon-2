# TodoFlow

A simple in-memory todo console application built with Python 3.13+.

## Features

- Add todo items with title, optional description, and priority
- View all todos or a single todo
- Mark todos as complete
- Update todo details
- Delete todos
- Help command for all operations
- **NEW**: Interactive mode with menu selection

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Phase-I-In-Memory-Python-Console-App

# Install dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should show 3.13 or higher
```

## Usage

### Default Clean CLI Mode (New!)
When you run `python main.py`, it now defaults to the clean, user-friendly interface:

```bash
# Run in clean CLI mode (default)
python main.py

# Features:
# - Clean numbered menu interface
# - Step-by-step prompts
# - Clear visual separators
# - Easy navigation with numbers
# - Select options 1-7 to manage todos
```

### Standard CLI Mode
To use the original command-line interface:

```bash
# Run in original CLI mode
python main.py --cli

# Add a todo
python main.py --cli add "Buy groceries" --priority high --description "Milk, eggs, bread"

# List all todos
python main.py --cli list

# View a single todo
python main.py --cli show 1

# Mark a todo as complete
python main.py --cli complete 1

# Update a todo
python main.py --cli update 1 --title "Buy almond milk"

# Delete a todo
python main.py --cli delete 1

# Get help
python main.py --cli --help
```

### Interactive Mode (Alternative)
To use the interactive menu system where you can select options by number:

```bash
# Run in interactive mode with menu selection
python main.py --interactive

# In interactive mode, you can:
# - Select options by number instead of typing commands
# - View all todos with status indicators
# - Complete, update, or delete todos using menu navigation
# - Add new todos with guided prompts
```

## Development

- Run tests: `python -m pytest tests/ -v`
- Run with coverage: `python -m pytest tests/ --cov=todo_app`
- Linting: `python -m ruff check todo_app/`

## Architecture

- `todo_app/domain.py` - Domain layer (Todo, Status, Priority, exceptions)
- `todo_app/application.py` - Application layer (TodoList service)
- `todo_app/cli.py` - CLI interface
- `todo_app/interactive_cli.py` - Interactive CLI interface
- `main.py` - Entry point

## License

MIT