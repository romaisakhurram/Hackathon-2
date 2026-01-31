# Implementation Plan: 2-backend-api-auth

**Branch**: `2-backend-api-auth` | **Date**: 2026-01-09 | **Spec**: [spec.md](spec.md)

## Summary

Implement a secure FastAPI backend with JWT authentication, user-isolated Task CRUD, and Neon PostgreSQL integration. The backend will verify JWT tokens from Better Auth frontend, enforce user data isolation via user_id filtering, and expose RESTful API endpoints for task management.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, python-jose (JWT), passlib (bcrypt), asyncpg (async PostgreSQL)
**Storage**: Neon Serverless PostgreSQL via DATABASE_URL
**Testing**: pytest with httpx for async API testing
**Target Platform**: Linux server (uvicorn)
**Project Type**: Web backend (FastAPI standalone)
**Performance Goals**: <3s p95 latency, 100+ concurrent users
**Constraints**: JWT verification via BETTER_AUTH_SECRET, user_id isolation on all queries
**Scale/Scope**: Single-user to 100 concurrent users, Neon serverless handles scaling

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| Spec-Driven Accuracy | PASS | Based on `specs/2-backend-api-auth/spec.md` |
| Agentic Autonomy | PASS | All code via agent prompts |
| User Isolation | PASS | user_id filtering enforced |
| Security Rigor | PASS | JWT Bearer token verification |

## Project Structure

### Documentation (this feature)

```text
specs/2-backend-api-auth/
├── plan.md              # This file
├── research.md          # Phase 0 output (JWT/SQLModel patterns)
├── data-model.md        # Phase 1 output (SQLModel entities)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output
│   └── task-api-contract.md
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings from environment
│   ├── database.py          # SQLModel engine/session
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py          # Pydantic schemas
│   │   └── auth.py          # JWT payload schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Token verification utilities
│   │   └── tasks.py         # Task CRUD endpoints
│   └── dependencies.py      # Auth dependency
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytest fixtures
│   ├── test_tasks.py        # Task API tests
│   └── test_auth.py         # Auth tests
├── requirements.txt
└── .env.example
```

**Structure Decision**: Flat structure under `backend/src/` for simplicity. Models, schemas, and routers separated by responsibility. Database layer centralized.

## Complexity Tracking

No constitution violations requiring justification.

---

## Phase 0: Research Findings

### JWT Verification Approach

**Decision**: Use `python-jose` library for JWT verification

**Rationale**:
- `python-jose` is the standard choice for FastAPI/JWT integration
- Supports HS256 algorithm (used by Better Auth)
- Provides straightforward secret key verification
- Compatible with async environments

**Implementation Pattern**:
```python
from jose import JWTError, jwt
from fastapi import HTTPException, status

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")
```

### SQLModel + Neon PostgreSQL Approach

**Decision**: Use async SQLModel with asyncpg driver

**Rationale**:
- Neon Serverless supports async connections
- `sqlmodel` with `AsyncEngine` from `sqlalchemy` (v2.0+)
- Connection pooling configured for serverless: pool_size=5, max_overflow=10
- SSL required for Neon: `sslmode=require`

**Implementation Pattern**:
```python
from sqlmodel import SQLModel, create_async_engine, Session, select
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)

async def get_db():
    async with Session(engine) as session:
        yield session
```

### User Isolation Strategy

**Decision**: Filter all queries by `user_id` from JWT token

**Rationale**:
- Constitution requirement: strict data partitioning
- Every endpoint uses `current_user_id` dependency
- Database queries include `where(Task.user_id == current_user_id)`

---

## Phase 1: Design & Contracts

### Data Model (see `data-model.md`)

**Task Entity**:
- `id`: UUID primary key
- `title`: str (max 255), required
- `description`: str (optional)
- `priority`: int (default 0)
- `status`: str (pending/completed, default pending)
- `created_at`: datetime
- `updated_at`: datetime
- `user_id`: UUID foreign key (indexed)
- Indexes: `idx_user_id`, `idx_completed`, `idx_user_composite`

### API Contracts (see `contracts/task-api-contract.md`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/tasks | List user's tasks | JWT Required |
| POST | /api/tasks | Create new task | JWT Required |
| GET | /api/tasks/{id} | Get specific task | JWT Required |
| PUT | /api/tasks/{id} | Update task | JWT Required |
| DELETE | /api/tasks/{id} | Delete task | JWT Required |
| PATCH | /api/tasks/{id}/toggle | Toggle completion | JWT Required |
| GET | /health | Health check | None |

### Quickstart (see `quickstart.md`)

Setup instructions for running the backend locally and in production.

---

## Next Steps

Execute `/sp.tasks` to generate task breakdown from this plan.
