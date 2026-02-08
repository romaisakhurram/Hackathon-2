# API Contracts: Advanced Todo Features

## Overview
This document defines the API contracts for the advanced todo features including recurring tasks, due dates, reminders, priorities, tags, search, filter, and sort functionality.

## Base URL
`https://api.todo-chatbot.com/v1`

## Authentication
All endpoints require authentication via Bearer token in the Authorization header:
`Authorization: Bearer {jwt_token}`

## Common Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Optional message",
  "errors": []
}
```

## Task Management Endpoints

### GET /tasks
Retrieve a list of tasks with optional filtering, sorting, and pagination.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): Filter by status (pending, in-progress, completed, cancelled)
- `priority` (string, optional): Filter by priority name (high, medium, low)
- `due_date_from` (string, optional): Filter tasks with due date after this date (ISO 8601)
- `due_date_to` (string, optional): Filter tasks with due date before this date (ISO 8601)
- `tags` (string, optional): Filter by tags (comma-separated)
- `search` (string, optional): Search term for title/description
- `sort_by` (string, optional): Field to sort by (created_at, due_date, priority, title)
- `sort_order` (string, optional): Sort direction (asc, desc, default: desc)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "uuid",
        "title": "Task title",
        "description": "Task description",
        "status": "pending",
        "dueDate": "2023-12-31T23:59:59.000Z",
        "completedAt": null,
        "priority": {
          "id": "uuid",
          "name": "High",
          "value": 1,
          "color": "#FF0000"
        },
        "tags": [
          {
            "id": "uuid",
            "name": "Work",
            "color": "#0000FF"
          }
        ],
        "recurrenceRule": {
          "id": "uuid",
          "interval": "weekly",
          "frequency": 1,
          "daysOfWeek": [1, 3, 5],
          "endDate": null,
          "occurrenceCount": null
        },
        "reminders": [
          {
            "id": "uuid",
            "scheduledTime": "2023-12-31T09:00:00.000Z",
            "method": "in-app",
            "sent": false
          }
        ],
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### POST /tasks
Create a new task.

**Request Body:**
```json
{
  "title": "Task title",
  "description": "Task description",
  "status": "pending",
  "dueDate": "2023-12-31T23:59:59.000Z",
  "priorityId": "uuid",
  "tagIds": ["uuid1", "uuid2"],
  "recurrenceRule": {
    "interval": "weekly",
    "frequency": 1,
    "daysOfWeek": [1, 3, 5],
    "endDate": "2024-12-31T23:59:59.000Z",
    "occurrenceCount": null
  },
  "reminders": [
    {
      "scheduledTime": "2023-12-31T09:00:00.000Z",
      "method": "in-app"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "status": "pending",
      "dueDate": "2023-12-31T23:59:59.000Z",
      "completedAt": null,
      "priority": {
        "id": "uuid",
        "name": "High",
        "value": 1,
        "color": "#FF0000"
      },
      "tags": [
        {
          "id": "uuid",
          "name": "Work",
          "color": "#0000FF"
        }
      ],
      "recurrenceRule": {
        "id": "uuid",
        "interval": "weekly",
        "frequency": 1,
        "daysOfWeek": [1, 3, 5],
        "endDate": "2024-12-31T23:59:59.000Z",
        "occurrenceCount": null
      },
      "reminders": [
        {
          "id": "uuid",
          "scheduledTime": "2023-12-31T09:00:00.000Z",
          "method": "in-app",
          "sent": false
        }
      ],
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
}
```

### GET /tasks/{id}
Retrieve a specific task by ID.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "status": "pending",
      "dueDate": "2023-12-31T23:59:59.000Z",
      "completedAt": null,
      "priority": {
        "id": "uuid",
        "name": "High",
        "value": 1,
        "color": "#FF0000"
      },
      "tags": [
        {
          "id": "uuid",
          "name": "Work",
          "color": "#0000FF"
        }
      ],
      "recurrenceRule": {
        "id": "uuid",
        "interval": "weekly",
        "frequency": 1,
        "daysOfWeek": [1, 3, 5],
        "endDate": "2024-12-31T23:59:59.000Z",
        "occurrenceCount": null
      },
      "reminders": [
        {
          "id": "uuid",
          "scheduledTime": "2023-12-31T09:00:00.000Z",
          "method": "in-app",
          "sent": false
        }
      ],
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
}
```

### PUT /tasks/{id}
Update an existing task.

**Request Body:**
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "status": "in-progress",
  "dueDate": "2023-12-31T23:59:59.000Z",
  "priorityId": "uuid",
  "tagIds": ["uuid1", "uuid2"],
  "recurrenceRule": {
    "id": "uuid",
    "interval": "weekly",
    "frequency": 1,
    "daysOfWeek": [1, 3, 5],
    "endDate": "2024-12-31T23:59:59.000Z",
    "occurrenceCount": null
  },
  "reminders": [
    {
      "id": "uuid",
      "scheduledTime": "2023-12-31T09:00:00.000Z",
      "method": "in-app"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "uuid",
      "title": "Updated task title",
      "description": "Updated task description",
      "status": "in-progress",
      "dueDate": "2023-12-31T23:59:59.000Z",
      "completedAt": null,
      "priority": {
        "id": "uuid",
        "name": "High",
        "value": 1,
        "color": "#FF0000"
      },
      "tags": [
        {
          "id": "uuid",
          "name": "Work",
          "color": "#0000FF"
        }
      ],
      "recurrenceRule": {
        "id": "uuid",
        "interval": "weekly",
        "frequency": 1,
        "daysOfWeek": [1, 3, 5],
        "endDate": "2024-12-31T23:59:59.000Z",
        "occurrenceCount": null
      },
      "reminders": [
        {
          "id": "uuid",
          "scheduledTime": "2023-12-31T09:00:00.000Z",
          "method": "in-app",
          "sent": false
        }
      ],
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-02T00:00:00.000Z"
    }
  }
}
```

### DELETE /tasks/{id}
Delete a task.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Task deleted successfully"
  }
}
```

## Tag Management Endpoints

### GET /tags
Retrieve a list of tags for the authenticated user.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "id": "uuid",
        "name": "Work",
        "color": "#0000FF",
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z"
      }
    ]
  }
}
```

### POST /tags
Create a new tag.

**Request Body:**
```json
{
  "name": "Personal",
  "color": "#FF0000"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "tag": {
      "id": "uuid",
      "name": "Personal",
      "color": "#FF0000",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
}
```

### PUT /tags/{id}
Update an existing tag.

**Request Body:**
```json
{
  "name": "Updated Personal",
  "color": "#00FF00"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tag": {
      "id": "uuid",
      "name": "Updated Personal",
      "color": "#00FF00",
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-02T00:00:00.000Z"
    }
  }
}
```

### DELETE /tags/{id}
Soft delete a tag (remove association from tasks but keep tag record).

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Tag deleted successfully"
  }
}
```

## Priority Management Endpoints

### GET /priorities
Retrieve a list of available priorities.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "priorities": [
      {
        "id": "uuid",
        "name": "High",
        "value": 1,
        "color": "#FF0000"
      },
      {
        "id": "uuid",
        "name": "Medium",
        "value": 2,
        "color": "#FFA500"
      },
      {
        "id": "uuid",
        "name": "Low",
        "value": 3,
        "color": "#008000"
      }
    ]
  }
}
```

## Search Endpoint

### POST /search/tasks
Search tasks with advanced filtering options.

**Request Body:**
```json
{
  "query": "meeting",
  "filters": {
    "status": ["pending", "in-progress"],
    "priorities": ["high", "medium"],
    "dueDateRange": {
      "from": "2023-01-01T00:00:00.000Z",
      "to": "2023-12-31T23:59:59.000Z"
    },
    "tags": ["work", "important"]
  },
  "sortBy": "due_date",
  "sortOrder": "asc",
  "page": 1,
  "limit": 20
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tasks": [
      // Same structure as GET /tasks response
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "pages": 1
    },
    "searchMeta": {
      "query": "meeting",
      "tookMs": 15
    }
  }
}
```