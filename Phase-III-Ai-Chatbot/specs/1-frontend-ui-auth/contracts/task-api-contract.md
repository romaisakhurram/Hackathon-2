# Task API Contract

## Base URL
`/api/tasks`

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Endpoints

### GET /api/tasks
Retrieve all tasks for the authenticated user

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "priority": "low|medium|high",
      "status": "pending|in-progress|completed",
      "created_at": "datetime",
      "updated_at": "datetime",
      "user_id": "string"
    }
  ]
}
```

### POST /api/tasks
Create a new task for the authenticated user

**Request Body**:
```json
{
  "title": "string",
  "description": "string",
  "priority": "low|medium|high"
}
```

**Response (201 Created)**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "priority": "low|medium|high",
  "status": "pending",
  "created_at": "datetime",
  "updated_at": "datetime",
  "user_id": "string"
}
```

### PUT /api/tasks/{id}
Update an existing task

**Request Body**:
```json
{
  "title": "string",
  "description": "string",
  "priority": "low|medium|high",
  "status": "pending|in-progress|completed"
}
```

**Response (200 OK)**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "priority": "low|medium|high",
  "status": "pending|in-progress|completed",
  "created_at": "datetime",
  "updated_at": "datetime",
  "user_id": "string"
}
```

### DELETE /api/tasks/{id}
Delete a task

**Response (204 No Content)**

### PATCH /api/tasks/{id}/complete
Toggle task completion status

**Response (200 OK)**:
```json
{
  "id": "string",
  "status": "pending|in-progress|completed"
}
```

## Error Responses

**Generic Error Format (4xx/5xx)**:
```json
{
  "error": "string",
  "message": "string"
}
```

## Authentication Endpoints

### POST /api/auth/signin
Authenticate user

**Request Body**:
```json
{
  "email": "string",
  "password": "string"
}
```

**Response (200 OK)**:
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
  }
}
```

### POST /api/auth/signup
Register new user

**Request Body**:
```json
{
  "email": "string",
  "password": "string",
  "name": "string"
}
```

**Response (201 Created)**:
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
}
```