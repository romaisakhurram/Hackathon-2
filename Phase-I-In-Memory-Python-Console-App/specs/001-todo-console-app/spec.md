# Feature Specification: Todo In-Memory Python Console App

**Feature Branch**: `001-todo-console-app`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User description: "Phase I: Todo In-Memory Python Console App"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Todo Item (Priority: P1)

As a user, I want to add new todo items with a title, optional description, and optional priority so that I can track tasks I need to accomplish.

**Why this priority**: Adding items is the foundational feature - without it, nothing else matters.

**Independent Test**: Can be tested by running the CLI with add command and verifying the new item appears in the list.

**Acceptance Scenarios**:

1. **Given** no todos exist, **When** I add a todo with title "Buy groceries", **Then** the todo list shows exactly one item with title "Buy groceries"
2. **Given** a todo exists, **When** I add another todo with title "Walk the dog" and priority "High", **Then** the list shows both items with correct priority
3. **Given** I add a todo without priority, **Then** the default priority is "Medium"

---

### User Story 2 - View Todo Items (Priority: P1)

As a user, I want to view all my todo items so that I can see what tasks I have pending.

**Why this priority**: Users need visibility into their task list to prioritize and plan work.

**Independent Test**: Can be tested by adding items and verifying the view command displays all items correctly.

**Acceptance Scenarios**:

1. **Given** no todos exist, **When** I view the list, **Then** I see a message indicating no todos exist
2. **Given** three todos exist, **When** I view the list, **Then** I see all three items displayed
3. **Given** todos exist with different priorities, **When** I view the list, **Then** priorities are visible for each item

---

### User Story 3 - Mark Todo Complete (Priority: P1)

As a user, I want to mark a todo item as complete so that I can track my progress on tasks.

**Why this priority**: Completing tasks is the core value proposition of a todo app.

**Independent Test**: Can be tested by adding items, marking one complete, and verifying its status changes.

**Acceptance Scenarios**:

1. **Given** a todo exists with status "Pending", **When** I mark it complete, **Then** its status becomes "Completed"
2. **Given** multiple todos exist, **When** I mark one complete, **Then** only that todo's status changes
3. **Given** a todo is already completed, **When** I try to mark it complete again, **Then** the system indicates it is already complete

---

### User Story 4 - Delete Todo Item (Priority: P2)

As a user, I want to delete todo items so that I can remove tasks that are no longer relevant.

**Why this priority**: Deletion cleans up the list and maintains relevance of displayed items.

**Independent Test**: Can be tested by adding items, deleting one, and verifying it no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** three todos exist, **When** I delete one by ID, **Then** the list shows exactly two items
2. **Given** a todo with ID "1" exists, **When** I delete it, **Then** trying to view or modify it returns an error
3. **Given** no todos exist, **When** I try to delete, **Then** the system indicates nothing to delete

---

### User Story 5 - Update Todo Item (Priority: P2)

As a user, I want to update existing todo items so that I can correct mistakes or refine task details.

**Why this priority**: Updates allow users to improve task information over time without recreating items.

**Independent Test**: Can be tested by adding an item, updating its fields, and verifying the changes.

**Acceptance Scenarios**:

1. **Given** a todo with title "Buy milk" exists, **When** I update its title to "Buy almond milk", **Then** the todo shows the new title
2. **Given** a todo with priority "Low" exists, **When** I update its priority to "High", **Then** the todo shows priority "High"
3. **Given** a todo exists, **When** I update its description, **Then** the new description is displayed

---

### User Story 6 - Clean CLI Interface (Priority: P1)

As a user, I want a clean, user-friendly CLI interface with numbered menu options so that I can easily navigate and manage my todos without remembering complex commands.

**Why this priority**: Provides an intuitive interface that improves user experience and accessibility.

**Independent Test**: Can be tested by running the application and verifying the clean numbered menu interface appears by default.

**Acceptance Scenarios**:

1. **Given** I run the application, **When** I execute `python main.py`, **Then** I see a clean numbered menu interface (options 1-7) with visual separators
2. **Given** the clean CLI is running, **When** I select option 1-7, **Then** the corresponding action is performed with clear prompts
3. **Given** I'm using the clean CLI, **When** I view todos, **Then** they are displayed with status indicators (O pending, > in progress, X completed)

---

### Edge Cases

- Empty title provided when adding a todo
- Invalid priority value (not Low, Medium, or High)
- Non-existent todo ID referenced for update/delete/mark-complete
- Duplicate todo IDs (system must ensure unique IDs)
- Very long title or description (should handle gracefully)
- Special characters in title or description (should be preserved)
- Invalid menu selection in clean CLI (should show error and prompt again)
- EOF input during prompts (should handle gracefully)

## Clarifications

### Session 2026-01-01

- Q: Error handling strategy (detailed vs user-friendly) → A: User-friendly messages only for CLI output

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to add a todo item with a title, optional description, and optional priority
- **FR-002**: System MUST assign a unique identifier to each todo item
- **FR-003**: System MUST default priority to "Medium" when not specified
- **FR-004**: System MUST allow users to view all todo items
- **FR-005**: System MUST allow users to view a single todo item by ID
- **FR-006**: System MUST allow users to mark a todo item as complete
- **FR-007**: System MUST allow users to delete a todo item by ID
- **FR-008**: System MUST allow users to update a todo item's title, description, and/or priority
- **FR-009**: System MUST display an error when an operation targets a non-existent todo ID
- **FR-010**: System MUST display a message when list is empty
- **FR-011**: System MUST reject todo items with empty or whitespace-only titles
- **FR-012**: System MUST provide a help command showing available operations
- **FR-013**: System MUST provide a clean CLI interface with numbered menu options (1-7) by default
- **FR-014**: System MUST display a welcome message and clear visual separators in clean CLI mode
- **FR-015**: System MUST provide step-by-step prompts with clear instructions in clean CLI mode
- **FR-016**: System MUST display status indicators (O pending, > in progress, X completed) in clean CLI mode
- **FR-017**: System MUST validate user input and provide user-friendly error messages in clean CLI mode
- **FR-018**: System MUST provide an exit option in clean CLI mode
- **FR-019**: System MUST maintain backward compatibility with original CLI commands via --cli flag

### Key Entities *(include if feature involves data)*

- **Todo**: Represents a single task item with the following attributes:
  - `id`: Integer, unique identifier auto-assigned on creation
  - `title`: String, required, non-empty
  - `description`: String, optional, defaults to empty string
  - `status`: Enum (Pending, In Progress, Completed), defaults to Pending
  - `priority`: Enum (Low, Medium, High), defaults to Medium
  - `created_at`: Timestamp, set automatically on creation

- **TodoList**: Manages collection of Todo items in memory:
  - `todos`: List/collection of Todo objects
  - `next_id`: Integer counter for generating unique IDs
  - Methods: add(), delete(), update(), get(), get_all(), mark_complete()

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 core features (Add, Delete, Update, View, Mark Complete) are functional and can be executed from the CLI
- **SC-002**: Code follows Python 3.13+ conventions with type hints and docstrings for all public functions
- **SC-003**: Domain logic (Todo, TodoList) is separate from CLI interface code
- **SC-004**: Application runs deterministically with consistent behavior across sessions
- **SC-005**: Each user story can be tested independently without requiring other features
- **SC-006**: Architecture allows extension to future phases without breaking changes
- **SC-007**: Clean CLI interface provides numbered menu options (1-7) by default when running `python main.py`
- **SC-008**: Clean CLI interface displays visual separators and clear formatting for improved user experience
- **SC-009**: Clean CLI interface provides step-by-step prompts with clear instructions for all operations
- **SC-010**: Clean CLI interface displays status indicators (O pending, > in progress, X completed) for todos
- **SC-011**: Clean CLI interface validates user input and provides user-friendly error messages
- **SC-012**: Original CLI functionality is preserved and accessible via --cli flag
- **SC-013**: All existing tests continue to pass (39/39) after adding new clean CLI features
