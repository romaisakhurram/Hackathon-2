# API Contracts: Task Management

**Feature**: 2-backend-api-auth
**Created**: 2026-01-09

## Authentication

All endpoints (except `/health`) require JWT authentication.

**Header**: `Authorization: Bearer <token>`

**Token Payload** (from Better Auth):
```json
{
  "user_id": "uuid-string",
  "exp": 1234567890,
  "iat": 1234567800
}
```

## Error Response Format

```json
{
  "detail": "Error message description"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Invalid input / validation error |
| 401 | Missing or invalid JWT token |
| 403 | Forbidden (not your resource) |
| 404 | Resource not found |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

---

## Endpoints

### GET /health

Health check endpoint (no auth required).

**Response** (200 OK):
```json
{
  "status": "healthy"
}
```

---

### GET /api/tasks

List all tasks for the authenticated user.

**Auth**: JWT Required

**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | str | optional | Filter by 'pending' or 'completed' |
| `limit` | int | 100 | Max results |
| `offset` | int | 0 | Pagination offset |

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "uuid-string",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "priority": 1,
      "status": "pending",
      "created_at": "2026-01-09T10:00:00Z",
      "updated_at": "2026-01-09T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### POST /api/tasks

Create a new task for the authenticated user.

**Auth**: JWT Required

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Optional description",
  "priority": 1
}
```

**Validation**:
- `title`: required, max 255 chars
- `description`: optional, string
- `priority`: optional, 0-2, default 0

**Response** (201 Created):
```json
{
  "id": "uuid-string",
  "title": "Buy groceries",
  "description": "Optional description",
  "priority": 1,
  "status": "pending",
  "user_id": "uuid-string",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z"
}
```

---

### GET /api/tasks/{id}

Get a specific task by ID.

**Auth**: JWT Required

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Buy groceries",
  "description": "Optional description",
  "priority": 1,
  "status": "pending",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z"
}
```

**Errors**:
- 404: Task not found or doesn't belong to user

---

### PUT /api/tasks/{id}

Update a task. All fields are optional.

**Auth**: JWT Required

**Request Body**:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "priority": 2
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Updated title",
  "description": "Updated description",
  "priority": 2,
  "status": "pending",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T11:00:00Z"
}
```

**Errors**:
- 404: Task not found or doesn't belong to user

---

### DELETE /api/tasks/{id}

Delete a task.

**Auth**: JWT Required

**Response** (204 No Content): Empty body

**Errors**:
- 404: Task not found or doesn't belong to user

---

### PATCH /api/tasks/{id}/toggle

Toggle task completion status.

**Auth**: JWT Required

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Buy groceries",
  "status": "completed",
  "updated_at": "2026-01-09T11:00:00Z"
}
```

**Errors**:
- 404: Task not found or doesn't belong to user
