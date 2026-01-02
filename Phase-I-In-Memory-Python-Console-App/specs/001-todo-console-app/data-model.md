# Data Model: Todo In-Memory Python Console App

## Entities

### Todo

Represents a single task item in the system.

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | int | Yes | Auto-generated | Unique identifier, starts at 1 and increments |
| `title` | str | Yes | N/A | Task title, non-empty, max 200 chars |
| `description` | str | No | `""` | Optional task description, max 1000 chars |
| `status` | Status | No | `Status.PENDING` | Current task status |
| `priority` | Priority | No | `Priority.MEDIUM` | Task priority level |
| `created_at` | datetime | Yes | Auto-generated | UTC timestamp of creation |

**Validation Rules:**
- Title must be non-empty (after stripping whitespace)
- Title max length: 200 characters
- Description max length: 1000 characters
- ID must be unique across all todos

### Status (Enum)

Represents the current state of a todo item.

```python
class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

**State Transitions:**
- `PENDING` → `IN_PROGRESS` (when user starts working)
- `PENDING` → `COMPLETED` (when user marks complete)
- `IN_PROGRESS` → `COMPLETED` (when user marks complete)
- No transitions from `COMPLETED` (final state)

### Priority (Enum)

Represents the importance level of a todo item.

```python
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

**Ordering:** LOW < MEDIUM < HIGH (for sorting purposes)

### TodoList

Manages the collection of Todo items in memory.

**Internal State:**

| Field | Type | Description |
|-------|------|-------------|
| `_todos` | dict[int, Todo] | Map of ID → Todo for O(1) lookups |
| `_next_id` | int | Counter for generating unique IDs |

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add()` | title: str, description: str, priority: Priority | Todo | Creates and returns new Todo |
| `get()` | todo_id: int | Todo \| None | Retrieves todo by ID |
| `get_all()` | None | list[Todo] | Returns all todos sorted by ID |
| `update()` | todo_id: int, title?: str, description?: str, priority?: Priority | Todo | Updates specified fields |
| `delete()` | todo_id: int | None | Removes todo from collection |
| `mark_complete()` | todo_id: int | Todo | Sets status to COMPLETED |

## Error Types

| Error | Raised When |
|-------|-------------|
| `TodoNotFoundError` | Operation targets non-existent ID |
| `ValidationError` | Invalid input (empty title, invalid priority) |
| `DuplicateTodoError` | Attempt to add duplicate ID (should not occur) |
