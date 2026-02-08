# Quickstart Guide: Advanced Todo Features

## Overview
This guide provides instructions for setting up and running the advanced todo features locally.

## Prerequisites
- Node.js 18.x or higher
- PostgreSQL 12.x or higher
- Redis 6.x or higher
- Git

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/todo-chatbot-system.git
cd todo-chatbot-system
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Update .env with your local configuration
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=todo_dev
# DB_USER=your_username
# DB_PASS=your_password
# REDIS_URL=redis://localhost:6379
```

### 3. Database Setup
```bash
# Create database
createdb todo_dev

# Run migrations
npm run migrate

# Seed initial data (optional)
npm run seed
```

### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Update .env with your local configuration
# REACT_APP_API_URL=http://localhost:3000/api
```

### 5. Running the Applications

#### Backend
```bash
# From the backend directory
npm run dev
# Server will start on http://localhost:3000
```

#### Frontend
```bash
# From the frontend directory
npm start
# App will be available at http://localhost:3000
```

## Key Features Implementation

### Recurring Tasks
To implement recurring tasks:
1. Create a `RecurrenceRule` entity with interval, frequency, and end conditions
2. Link it to a `Task` entity via `recurrenceRuleId`
3. Implement the recurrence service to generate future task instances

### Due Dates & Reminders
For due dates and reminders:
1. Use the `dueDate` field in the `Task` entity
2. Create `Reminder` entities linked to tasks
3. Implement a scheduler service to process reminders

### Priorities & Tags
For priorities and tags:
1. Use the `Priority` entity to define priority levels
2. Use the `Tag` entity for task categorization
3. Implement many-to-many relationships between tasks and tags

### Search, Filter & Sort
For search, filter, and sort functionality:
1. Implement full-text search using PostgreSQL's tsvector
2. Add query parameters to filter tasks by status, priority, tags, etc.
3. Allow sorting by various fields (due date, priority, creation date)

## Running Tests
```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test

# End-to-end tests
cd frontend
npm run test:e2e
```

## Useful Scripts
- `npm run migrate`: Run database migrations
- `npm run seed`: Populate database with sample data
- `npm run lint`: Lint code
- `npm run format`: Format code
- `npm run coverage`: Generate test coverage report

## Troubleshooting
- If database migrations fail, ensure PostgreSQL is running and credentials are correct
- If Redis connection fails, ensure Redis server is running
- For frontend build issues, try clearing node_modules and reinstalling dependencies