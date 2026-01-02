# Quickstart: Todo In-Memory Python Console App

## Prerequisites

- Python 3.13 or higher
- No external dependencies required

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Phase-I-In-Memory-Python-Console-App

# Navigate to project directory
cd todo_app

# Verify Python version
python --version  # Should show 3.13.x
```

## Running the Application

### From Source

```bash
# From the project root
python main.py --help

# Add a todo
python main.py add "Buy groceries" --priority high

# List all todos
python main.py list

# Complete a todo
python main.py complete 1

# Update a todo
python main.py update 1 --title "Buy almond milk"

# Delete a todo
python main.py delete 1
```

### Full Workflow Example

```bash
# 1. Add some todos
python main.py add "Buy groceries" --description "Milk, eggs, bread" --priority high
python main.py add "Walk the dog" --priority medium
python main.py add "Read book" --priority low

# 2. View all todos
python main.py list

# 3. Mark one as in progress
python main.py show 2  # View details first
python main.py complete 1

# 4. Update a todo
python main.py update 2 --priority high --description "Morning walk in park"

# 5. Clean up
python main.py delete 3
```

## Project Structure

```
todo_app/
├── main.py              # Entry point
├── todo_app/
│   ├── __init__.py      # Package initialization
│   ├── domain.py        # Todo, Status, Priority, exceptions
│   ├── application.py   # TodoList service class
│   └── cli.py           # Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_domain.py   # Todo entity tests
│   ├── test_application.py  # TodoList tests
│   └── test_cli.py      # CLI tests
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## Running Tests

```bash
# From project root
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_domain.py -v

# Run with coverage
python -m pytest tests/ --cov=todo_app
```

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Add docstrings to all public functions and classes
- Run linting: `python -m ruff check todo_app/`

### Adding New Features

1. Update `spec.md` with new user stories
2. Update `data-model.md` if entities change
3. Update `contracts/cli-contract.md` for CLI changes
4. Update `plan.md` with implementation approach
5. Generate new tasks with `/sp.tasks`
6. Implement following Red-Green-Refactor cycle

## Troubleshooting

**"Python 3.13 required"**
- Check Python version: `python --version`
- Install from python.org or use pyenv

**Import errors**
- Ensure you're running from project root
- Check that `__init__.py` files exist

**Tests failing**
- Run with verbose: `python -m pytest -v`
- Check for import path issues
