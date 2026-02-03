---
id: 001
title: Backend API Auth Plan
stage: plan
date_iso: 2026-01-09
surface: agent
model: sonnet-4-5-20250929
feature: backend-api-auth
branch: 2-backend-api-auth
user: Claude Code User
command: /sp.plan create plan spec 2-backend-api-auth
labels: ["backend", "fastapi", "jwt", "neon-postgresql"]
links:
  spec: "specs/2-backend-api-auth/spec.md"
  plan: "specs/2-backend-api-auth/plan.md"
files_created:
  - specs/2-backend-api-auth/plan.md
  - specs/2-backend-api-auth/data-model.md
  - specs/2-backend-api-auth/research.md
  - specs/2-backend-api-auth/quickstart.md
  - specs/2-backend-api-auth/contracts/task-api-contract.md
files_modified: []
tests_run: []
tests_added: []
---

## Prompt Text

```text
/p.plan create plan spec 2-backend-api-auth # sp.plan — Backend Implementation Plan (Phase II)

## Objective
Implement a secure FastAPI backend with JWT auth, user-isolated Task CRUD, and Neon PostgreSQL integration. Fully compatible with the Next.js frontend.

## High-Level Steps

1. Initialize Backend
   - FastAPI app, routing structure, CORS setup
   - Health check endpoint

2. Database Setup
   - Neon PostgreSQL connection via DATABASE_URL
   - SQLModel engine and session

3. Data Models
   - SQLModel Task with indexes for user_id and completed

4. Schemas
   - Pydantic models for create/update/response
   - Enforce field validation

5. JWT Auth
   - Verify token from Authorization header
   - Decode user context
   - Shared secret: BETTER_AUTH_SECRET

6. User Isolation
   - Match JWT user_id with route user_id
   - Filter all queries by authenticated user
   - Reject unauthorized access

7. Task CRUD Endpoints
   - List, create, get, update, delete, toggle complete
   - Auth required on all endpoints
   - Proper HTTP status codes

8. Error Handling
   - 400: invalid input
   - 401/403: auth failure
   - 404: missing resource

9. Frontend Integration
   - Enable CORS
   - JSON response shapes verified

10. Final Verification
    - All endpoints require JWT
    - Tasks fully user-scoped
    - Backend runs without warnings

## Definition of Done
- JWT auth enforced everywhere
- User data isolated
- Task CRUD fully functional
- Frontend integration successful
- Matches specifications exactly
```

## Response Text

Created implementation plan for 2-backend-api-auth feature with:
- Technical Context: Python 3.11, FastAPI, SQLModel, python-jose, Neon PostgreSQL
- Project structure: backend/src/ with models/schemas/routers organization
- Research findings on JWT verification and SQLModel async patterns
- Data model: Task entity with user_id isolation and proper indexes
- API contracts: 7 endpoints for Task CRUD with auth requirements
- Quickstart guide: setup, running, testing instructions

## Outcome

Plan completed. Ready for /sp.tasks to generate implementation tasks.
