# Data Model: 2-backend-api-auth

**Feature**: Backend API with JWT Auth and Task CRUD
**Created**: 2026-01-09
**Based On**: [spec.md](spec.md)

## Entities

### Task

Represents a todo item owned by a specific user.

| Field | Type | Constraints | Index | Description |
|-------|------|-------------|-------|-------------|
| `id` | UUID | Primary Key | PK | Unique identifier |
| `title` | str(255) | NOT NULL | - | Task title |
| `description` | str | NULLABLE | - | Optional task details |
| `priority` | int | DEFAULT 0 | - | Priority level (0=low, 2=high) |
| `status` | str(20) | DEFAULT 'pending' | Yes | 'pending' or 'completed' |
| `user_id` | UUID | NOT NULL, FK | Yes | Owning user |
| `created_at` | datetime | NOT NULL | - | Creation timestamp |
| `updated_at` | datetime | NOT NULL | - | Last update timestamp |

### Indexes

- `idx_user_id`: `user_id` - For filtering user's tasks
- `idx_completed`: `status` - For filtering by completion status
- `idx_user_composite`: `user_id, status` - For common query pattern

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import uuid4

class Task(SQLModel, table=True):
    id: uuid4 = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = None
    priority: int = Field(default=0)
    status: str = Field(default="pending", max_length=20)
    user_id: uuid4 = Field(foreign_key="user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    # user: "User" = Relationship(back_populates="tasks")
```

### Validation Rules

- `title`: Required, max 255 characters
- `description`: Optional, no length limit
- `priority`: Integer 0-2 (low, medium, high)
- `status`: Must be 'pending' or 'completed'
- `user_id`: Set automatically from JWT token (not user-provided)

### State Transitions

```
pending <--> completed
     ^
     |
     +-- created
```

### Notes

- `user_id` is extracted from JWT token, never from request body
- All queries automatically filter by `current_user_id`
- Soft delete not required; hard delete via DELETE endpoint
