# CLI Contract: Todo In-Memory Python Console App

## Command Interface

### Entry Point

```bash
python main.py [command] [options]
```

### Global Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message |
| `--version` | Show version (if implemented) |
| `--cli`, `-x` | Run in original CLI mode with commands |
| `--clean`, `-c` | Run in clean CLI mode with numbered menu (default) |
| `--interactive`, `-i` | Run in interactive mode with menu selection |

### Default Behavior

When running `python main.py` without any flags, the application defaults to clean CLI mode with numbered menu interface.

## Commands

### 1. Add Todo

**Command:** `add`

**Usage:**
```bash
python main.py add "Task title" [--description "Description"] [--priority low|medium|high]
```

**Arguments:**
| Position | Name | Type | Required | Default | Description |
|----------|------|------|----------|---------|-------------|
| 1 | title | string | Yes | N/A | Task title |

**Options:**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--description`, `-d` | string | `""` | Optional task description |
| `--priority`, `-p` | enum | `medium` | Priority level: low, medium, high |

**Output (Success):**
```
Added todo: [1] Buy groceries (High)
```

**Output (Error):**
```
Error: Title cannot be empty
```

---

### 2. List Todos

**Command:** `list`

**Usage:**
```bash
python main.py list [--status pending|in_progress|completed] [--priority low|medium|high]
```

**Options:**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--status`, `-s` | enum | All | Filter by status |
| `--priority`, `-p` | enum | All | Filter by priority |

**Output (Success):**
```
ID  | Status       | Priority | Title
----|--------------|----------|----------------
1   | pending      | high     | Buy groceries
2   | in_progress  | medium   | Walk the dog
3   | completed    | low      | Read book
```

**Output (Empty):**
```
No todos found. Add one with: python main.py add "Task title"
```

---

### 3. View Single Todo

**Command:** `show`

**Usage:**
```bash
python main.py show <id>
```

**Arguments:**
| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | id | int | Yes | Todo ID to display |

**Output (Success):**
```
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread
Status: pending
Priority: high
Created: 2026-01-01 10:00:00
```

**Output (Error):**
```
Error: Todo with ID 1 not found
```

---

### 4. Mark Complete

**Command:** `complete`

**Usage:**
```bash
python main.py complete <id>
```

**Arguments:**
| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | id | int | Yes | Todo ID to complete |

**Output (Success):**
```
Completed: [1] Buy groceries
```

**Output (Error - Not Found):**
```
Error: Todo with ID 1 not found
```

**Output (Error - Already Complete):**
```
Todo [1] is already completed
```

---/

### 5. Update Todo

**Command:** `update`

**Usage:**
```bash
python main.py update <id> [--title "New title"] [--description "New description"] [--priority low|medium|high]
```

**Arguments:**
| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | id | int | Yes | Todo ID to update |

**Options:**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--title`, `-t` | string | No change | New task title |
| `--description`, `-d` | string | No change | New description (use --description "" to clear) |
| `--priority`, `-p` | enum | No change | New priority level |

**Output (Success):**
```
Updated todo [1]:
  Title: Buy groceries -> Buy almond milk
  Priority: high -> medium
```

**Output (Error - Not Found):**
```
Error: Todo with ID 1 not found
```

**Output (Error - Validation):**
```
Error: Title cannot be empty
```

---

### 6. Delete Todo

**Command:** `delete`

**Usage:**
```bash
python main.py delete <id>
```

**Arguments:**
| Position | Name | Type | Required | Description |
|----------|------|------|----------|-------------|
| 1 | id | int | Yes | Todo ID to delete |

**Output (Success):**
```
Deleted todo [1] Buy groceries
```

**Output (Error - Not Found):**
```
Error: Todo with ID 1 not found
```

**Output (Error - Empty List):**
```
No todos to delete
```

---

### 7. Help

**Command:** `help` (or `--help`)

**Usage:**
```bash
python main.py help
```

**Output:**
```
TodoFlow CLI - In-Memory Todo Application

Usage:
  python main.py <command> [options]

Commands:
  add         Add a new todo item
  list        List all todos (with optional filters)
  show        Show details of a single todo
  complete    Mark a todo as completed
  update      Update a todo's title, description, or priority
  delete      Delete a todo item
  help        Show this help message

For more details on a specific command:
  python main.py help <command>
  python main.py <command> --help

Examples:
  python main.py add "Buy groceries" --priority high
  python main.py list --status pending
  python main.py complete 1
  python main.py update 1 --title "New title"
```

## Clean CLI Interface (Default Mode)

When running `python main.py` without flags, the application presents a clean, user-friendly interface with numbered menu options:

### Menu Options

| Number | Option | Description |
|--------|--------|-------------|
| 1 | Add new todo | Add a new todo item with title, description, priority |
| 2 | View all todos | Display all todos in clean table format |
| 3 | Show specific todo | Display details of a specific todo by ID |
| 4 | Update a todo | Update todo title, description, or priority |
| 5 | Complete a todo | Mark a todo as completed |
| 6 | Delete a todo | Remove a todo by ID |
| 7 | Exit | Exit the application |

### Interface Features

- **Welcome Message**: "TODOFLOW - Todo Manager" header
- **Visual Formatting**: Clear separators and proper spacing
- **Status Indicators**:
  - O = Pending
  - > = In Progress
  - X = Completed
- **Step-by-step Prompts**: Clear instructions for each operation
- **Input Validation**: User-friendly error messages
- **Clean Navigation**: Easy menu selection with numbers

### Example Output Format

```
==================================================
           TODOFLOW - Todo Manager
==================================================
Manage your tasks with a clean interface

SELECT AN OPTION:
------------------------------
1. Add new todo
2. View all todos
3. Show specific todo
4. Update a todo
5. Complete a todo
6. Delete a todo
7. Exit
------------------------------
Enter choice (1-7):
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (validation, unexpected) |
| 2 | Todo not found |
| 3 | Invalid arguments |
