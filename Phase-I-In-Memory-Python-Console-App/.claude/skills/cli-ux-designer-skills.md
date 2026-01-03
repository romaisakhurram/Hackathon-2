# CLI UX Designer Subagent Skills

**Description:** Specialized skills for designing intuitive, visually appealing, and user-friendly CLI interfaces with interactive menus, rich formatting, and excellent user experience.

**Invocation:** These skills are automatically applied when the cli-ux-designer agent is active.

---

## Core Design Capabilities

### 1. Menu Design & Navigation
**Purpose:** Create intuitive, hierarchical menu systems for CLI applications.

#### Menu Structure Design:
- **Main Menu:**
  - Clear numbered or lettered options
  - Logical grouping of related actions
  - Exit/quit option always available
  - Help option easily accessible

- **Sub-Menus:**
  - Hierarchical navigation structure
  - Breadcrumb trail showing current location
  - Back/return to parent menu option
  - Consistent navigation patterns

- **Menu Flow:**
  - Logical task-based organization
  - Minimal clicks to common actions
  - Quick access to frequent operations
  - Context-aware option visibility

- **Navigation Patterns:**
  - Number-based selection (1, 2, 3...)
  - Letter-based shortcuts (A, D, U, V, Q...)
  - Arrow key navigation (when using rich/prompt_toolkit)
  - Search/filter within menus

#### Implementation Guidelines:
```python
# Example menu structure
Main Menu:
  [1] Add Task        → Add task workflow
  [2] View Tasks      → Task listing submenu
  [3] Update Task     → Update task workflow
  [4] Delete Task     → Delete task workflow
  [5] Mark Complete   → Toggle completion
  [H] Help            → Show help/guide
  [Q] Quit            → Exit application

View Tasks Submenu:
  [A] All Tasks
  [P] Pending Only
  [C] Completed Only
  [F] Filter/Sort
  [B] Back to Main Menu
```

---

### 2. Interactive Prompts & Confirmations
**Purpose:** Design clear, user-friendly prompts that guide users through workflows.

#### Prompt Design Principles:
- **Clear Questions:**
  - Use simple, direct language
  - One question at a time
  - Provide context when needed
  - Show expected format/examples

- **Input Types:**
  - Text input with validation
  - Single choice (Y/N, 1-5)
  - Multiple choice (checkboxes)
  - Autocomplete for common values
  - Date/time pickers when appropriate

- **Confirmation Dialogs:**
  - For destructive actions (delete)
  - Show what will be affected
  - Default to safe option (No/Cancel)
  - Allow easy cancellation (ESC, Ctrl+C)

- **Progressive Disclosure:**
  - Show advanced options only when needed
  - Collapse detailed information by default
  - Expand on user request
  - Keep common workflows simple

#### Best Practices:
```python
# Good prompt examples:
"Enter task title: "
"Priority (1=Low, 2=Medium, 3=High) [2]: "
"Are you sure you want to delete 'Fix bug #123'? (y/N): "
"Select tasks to mark complete (comma-separated IDs): "

# With rich library:
from rich.prompt import Prompt, Confirm, IntPrompt
title = Prompt.ask("Enter task title")
priority = IntPrompt.ask("Priority", choices=["1", "2", "3"], default=2)
confirmed = Confirm.ask("Delete this task?", default=False)
```

---

### 3. Console Output & Formatting
**Purpose:** Create readable, well-structured output that presents information clearly.

#### Output Formatting:
- **Tables:**
  - Use rich.table for structured data
  - Column alignment (left for text, right for numbers)
  - Header row with clear labels
  - Alternating row colors for readability
  - Responsive width handling

- **Lists:**
  - Bullet points for unordered items
  - Numbered lists for sequences
  - Nested lists for hierarchies
  - Proper indentation

- **Panels & Boxes:**
  - Group related information
  - Highlight important messages
  - Create visual hierarchy
  - Use borders effectively

- **Text Styling:**
  - Bold for emphasis
  - Italic for secondary info
  - Underline for links/actions
  - Color coding for meaning

#### Layout Principles:
- **Whitespace:** Use spacing to separate sections
- **Alignment:** Keep related items aligned
- **Consistency:** Same format for same data types
- **Hierarchy:** Size/color to show importance
- **Readability:** Avoid clutter, keep it clean

#### Example Implementation:
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# Task list table
table = Table(title="📋 Task List", box=box.ROUNDED)
table.add_column("ID", style="cyan", justify="right")
table.add_column("Title", style="white")
table.add_column("Status", style="yellow")
table.add_column("Priority", justify="center")

table.add_row("1", "Fix login bug", "✓ Done", "🔴 High")
table.add_row("2", "Update docs", "⧗ In Progress", "🟡 Medium")
table.add_row("3", "Add tests", "○ Pending", "🟢 Low")

console.print(table)

# Success message panel
console.print(Panel(
    "✓ Task created successfully!",
    style="green",
    border_style="green"
))
```

---

### 4. Error Messaging & User Guidance
**Purpose:** Provide helpful, actionable error messages that guide users to resolution.

#### Error Message Design:
- **Clear Problem Statement:**
  - What went wrong
  - Why it happened (when relevant)
  - What the user can do to fix it
  - Never show technical stack traces

- **Error Severity Levels:**
  - 🔴 Error: Critical, operation failed
  - 🟡 Warning: Potential issue, proceed with caution
  - 🔵 Info: Informational message
  - 🟢 Success: Operation completed

- **Actionable Guidance:**
  - Suggest next steps
  - Offer alternatives
  - Link to help/documentation
  - Provide examples of correct input

- **Context-Aware Help:**
  - Show relevant commands
  - Display available options
  - Suggest common fixes
  - Link to related documentation

#### Example Messages:
```python
# Good error messages
❌ Error: Task ID '99' not found
   Available IDs: 1, 2, 3, 5, 8
   Try: view-tasks to see all tasks

⚠️  Warning: Task title is very long (150 chars)
   Consider shortening to improve readability
   Continue anyway? (y/N)

ℹ️  No tasks found matching filters
   • Status: completed
   • Priority: high
   Try removing filters or create new tasks

✓ Success: Task #5 marked as complete
   3 of 10 tasks completed (30%)
```

---

### 5. Task Visibility (Status & Priority)
**Purpose:** Make task status and priority immediately visible and understandable.

#### Visual Status Indicators:
- **Status Symbols:**
  - ○ Pending (empty circle)
  - ⧗ In Progress (hourglass/spinner)
  - ✓ Completed (checkmark)
  - ✗ Cancelled (X mark)
  - ⚠ Blocked (warning)

- **Priority Indicators:**
  - 🔴 High (red circle)
  - 🟡 Medium (yellow circle)
  - 🟢 Low (green circle)
  - Or: !!! High, !! Medium, ! Low

- **Color Coding:**
  - Red: High priority, errors, critical
  - Yellow/Orange: Medium priority, warnings
  - Green: Low priority, success
  - Blue: Information
  - Gray: Completed/archived

- **Progress Visualization:**
  - Progress bars for completion
  - Percentage indicators
  - Task counters (3/10 completed)
  - Time tracking (if applicable)

#### Implementation:
```python
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console

console = Console()

# Status with icons and colors
def format_status(status: str) -> str:
    status_map = {
        "pending": "[grey]○[/grey] Pending",
        "in_progress": "[yellow]⧗[/yellow] In Progress",
        "completed": "[green]✓[/green] Completed"
    }
    return status_map.get(status, status)

def format_priority(priority: str) -> str:
    priority_map = {
        "high": "[red]🔴[/red] High",
        "medium": "[yellow]🟡[/yellow] Medium",
        "low": "[green]🟢[/green] Low"
    }
    return priority_map.get(priority, priority)

# Progress bar
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
) as progress:
    progress.add_task("Loading tasks...", total=None)
```

---

### 6. Consistent CLI Commands & Feedback
**Purpose:** Provide predictable command patterns and clear feedback across all operations.

#### Command Consistency:
- **Naming Conventions:**
  - Verb-noun pattern: `add-task`, `delete-task`, `view-tasks`
  - Or noun-verb: `task-add`, `task-delete`, `task-list`
  - Keep consistent throughout app
  - Use aliases for common commands

- **Argument Patterns:**
  - Required arguments first
  - Optional flags with -- prefix
  - Short flags with - prefix
  - Consistent flag naming across commands

- **Response Format:**
  - Always acknowledge user action
  - Show what changed
  - Indicate success/failure clearly
  - Provide next step suggestions

- **Feedback Timing:**
  - Immediate response for quick operations
  - Progress indicators for slow operations
  - Estimated time for long operations
  - Cancellation option during processing

#### Example Commands:
```bash
# Consistent command structure
todo add "Task title" --priority high --description "Details"
todo list --status pending --sort priority
todo update 5 --title "New title" --priority medium
todo delete 3 --confirm
todo complete 7

# With feedback
$ todo add "Fix bug"
✓ Task created successfully!
  ID: 8
  Title: Fix bug
  Status: Pending
  Priority: Medium

Next: Run 'todo list' to view all tasks
```

---

### 7. Session State Awareness
**Purpose:** Maintain context across user interactions within a session.

#### State Management:
- **Remember User Preferences:**
  - Last used filters
  - Default priority/status
  - Preferred view mode
  - Color theme preference

- **Context Preservation:**
  - Current working set of tasks
  - Last selected task
  - Recent actions history
  - Undo/redo capability (if applicable)

- **Session History:**
  - Command history (up/down arrows)
  - Recent tasks viewed
  - Last search/filter criteria
  - Quick access to frequent tasks

- **Smart Defaults:**
  - Pre-fill based on last input
  - Suggest based on context
  - Learn from user patterns
  - Adapt to user workflow

#### Implementation Ideas:
```python
# Session state management
class SessionState:
    def __init__(self):
        self.last_filter = None
        self.last_sort = None
        self.recent_tasks = []
        self.command_history = []
        self.preferences = {}

    def remember_filter(self, filter_criteria):
        self.last_filter = filter_criteria

    def get_default_filter(self):
        return self.last_filter or "all"

    def add_to_history(self, command):
        self.command_history.append(command)

# Use in prompts
default_priority = session.preferences.get('default_priority', 'medium')
priority = Prompt.ask("Priority", default=default_priority)
```

---

### 8. Colorful Output using Rich/Prompt Toolkit
**Purpose:** Leverage modern CLI libraries for beautiful, interactive interfaces.

#### Rich Library Features:
- **Styling:**
  - Text colors and styles
  - Markup syntax for inline styling
  - Theme support
  - Emoji support

- **Components:**
  - Tables with flexible columns
  - Panels and boxes
  - Progress bars and spinners
  - Syntax highlighting
  - Tree views

- **Layout:**
  - Columns and grids
  - Responsive layouts
  - Padding and alignment
  - Live updates

#### Prompt Toolkit Features:
- **Interactive Input:**
  - Autocomplete
  - History navigation
  - Syntax validation
  - Key bindings

- **Menus:**
  - Arrow key navigation
  - Search functionality
  - Multi-select
  - Custom styling

#### Example Implementation:
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.tree import Tree
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

console = Console()

# Rich table with styling
table = Table(
    title="📋 Task Dashboard",
    box=box.DOUBLE_EDGE,
    title_style="bold magenta",
    header_style="bold cyan"
)
table.add_column("ID", style="dim", width=4)
table.add_column("Title", style="white", no_wrap=False)
table.add_column("Status", justify="center")
table.add_column("Priority", justify="center")

# Panel for messages
success_panel = Panel(
    "[green]✓[/green] Task created successfully!",
    title="Success",
    border_style="green",
    expand=False
)

# Tree for hierarchical data
tree = Tree("📁 Task Categories")
urgent = tree.add("🔴 High Priority")
urgent.add("Fix critical bug")
urgent.add("Deploy hotfix")

# Prompt toolkit with autocomplete
task_completer = WordCompleter(['add', 'delete', 'update', 'view', 'complete'])
command = prompt('Enter command: ', completer=task_completer)

# Live updating display
with Live(table, refresh_per_second=4) as live:
    # Update table dynamically
    table.add_row("1", "Processing...", "⧗", "🟡")
```

---

### 9. Modular Design for Reuse
**Purpose:** Create reusable UI components that can be shared across different workflows.

#### Component Library:
- **Input Components:**
  - `prompt_text()` - Simple text input
  - `prompt_choice()` - Single selection
  - `prompt_multiselect()` - Multiple selections
  - `prompt_confirm()` - Yes/No confirmation
  - `prompt_number()` - Numeric input with validation

- **Output Components:**
  - `display_table()` - Formatted table
  - `display_list()` - Bullet/numbered list
  - `display_panel()` - Boxed message
  - `display_tree()` - Hierarchical data
  - `display_progress()` - Progress indicator

- **Status Components:**
  - `show_success()` - Success message
  - `show_error()` - Error message
  - `show_warning()` - Warning message
  - `show_info()` - Information message

- **Navigation Components:**
  - `show_menu()` - Menu with options
  - `show_breadcrumb()` - Navigation trail
  - `show_help()` - Help text
  - `show_header()` - App header/title

#### Design Patterns:
```python
# Reusable UI components module
# ui_components.py

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

def show_success(message: str):
    """Display success message in green panel."""
    console.print(Panel(
        f"✓ {message}",
        style="green",
        border_style="green"
    ))

def show_error(message: str, suggestion: str = None):
    """Display error message with optional suggestion."""
    content = f"❌ {message}"
    if suggestion:
        content += f"\n\n💡 {suggestion}"
    console.print(Panel(
        content,
        style="red",
        border_style="red",
        title="Error"
    ))

def prompt_with_validation(
    prompt_text: str,
    validator,
    error_message: str
):
    """Prompt with custom validation and retry."""
    while True:
        value = Prompt.ask(prompt_text)
        if validator(value):
            return value
        show_error(error_message)

def display_task_table(tasks: list):
    """Display tasks in formatted table."""
    from rich.table import Table
    table = Table(title="📋 Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status")
    table.add_column("Priority")

    for task in tasks:
        table.add_row(
            str(task.id),
            task.title,
            format_status(task.status),
            format_priority(task.priority)
        )

    console.print(table)
    return table

# Use components across workflows
def add_task_workflow():
    title = prompt_with_validation(
        "Task title",
        lambda x: len(x) > 0,
        "Title cannot be empty"
    )
    # ... rest of workflow
    show_success(f"Task '{title}' created!")
```

---

## UX Design Principles

### Clarity:
- ✓ Use simple, clear language
- ✓ One action per screen/prompt
- ✓ Obvious next steps
- ✗ Avoid jargon and technical terms

### Consistency:
- ✓ Same patterns throughout app
- ✓ Predictable command structure
- ✓ Uniform styling and colors
- ✗ Don't surprise users with inconsistency

### Feedback:
- ✓ Always acknowledge actions
- ✓ Show progress for long operations
- ✓ Clear success/error states
- ✗ Never leave users wondering

### Efficiency:
- ✓ Minimize steps to complete tasks
- ✓ Provide shortcuts for power users
- ✓ Remember user preferences
- ✗ Don't make users repeat information

### Accessibility:
- ✓ Keyboard-only navigation
- ✓ Screen reader friendly text
- ✓ Colorblind-friendly indicators
- ✓ Optional color themes

---

## Testing UX Design

### Usability Testing:
- Test with real users
- Observe workflows
- Gather feedback
- Iterate on design

### Validation Checklist:
- [ ] All menus have clear exit options
- [ ] Destructive actions require confirmation
- [ ] Error messages are helpful
- [ ] Status indicators are clear
- [ ] Navigation is intuitive
- [ ] Output is readable
- [ ] Commands are consistent
- [ ] Feedback is immediate
- [ ] Colors enhance (not required for) understanding
- [ ] Works without mouse

---

## Performance Guidelines

- Instant response for UI interactions (< 50ms)
- Lazy load heavy components
- Cache formatted output
- Stream large datasets
- Progressive rendering

---

## Best Practices Summary

1. **Keep it simple** - Don't overcomplicate
2. **Be consistent** - Same patterns everywhere
3. **Provide feedback** - Always acknowledge
4. **Guide users** - Help them succeed
5. **Use color wisely** - Enhance, don't distract
6. **Make it modular** - Reusable components
7. **Test with users** - Real feedback matters
8. **Iterate often** - Continuous improvement

---

**Last Updated:** 2026-01-04
**Related Agent:** cli-ux-designer
**Libraries:** rich, prompt_toolkit
**Version:** 1.0
