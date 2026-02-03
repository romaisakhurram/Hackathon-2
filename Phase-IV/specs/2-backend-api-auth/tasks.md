# Tasks: 2-backend-api-auth

**Feature**: Backend API with JWT Auth and Task CRUD
**Created**: 2026-01-09
**Based On**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md), [contracts/task-api-contract.md](contracts/task-api-contract.md), [research.md](research.md)

## Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (Compliance) → Phase 7 (Polish)
                                        ↑
                        Can run in parallel: Phase 3, 4, 5, 6 after foundational
```

## User Story Completion Order

| Story | Priority | Depends On | Independent Test |
|-------|----------|------------|------------------|
| US1: Auth Dashboard | P1 | Phase 2 | JWT verification + task list |
| US2: Task CRUD | P1 | US1 | Full task CRUD with isolation |
| US3: Performance | P2 | US1 | Concurrent access + response times |

---

## Phase 1: Setup

Project initialization and dependency configuration.

- [X] T001 Create `backend/` directory structure per plan.md
- [X] T002 Create `backend/src/__init__.py`
- [X] T003 Create `backend/src/models/__init__.py`
- [X] T004 Create `backend/src/schemas/__init__.py`
- [X] T005 Create `backend/src/routers/__init__.py`
- [X] T006 Create `backend/tests/__init__.py`
- [X] T007 Create `backend/requirements.txt` with all dependencies (FastAPI, SQLModel, python-jose, passlib, asyncpg)
- [X] T008 Create `backend/.env.example` with DATABASE_URL and BETTER_AUTH_SECRET

**Phase 1 Exit Criteria**: Project structure exists, requirements.txt complete

---

## Phase 2: Foundational

Blocking prerequisites that all user stories depend on.

- [X] T010 Create `backend/src/config.py` with Settings class and environment loading
- [X] T011 [P] Create `backend/src/database.py` with async SQLModel engine and session dependency
- [X] T012 [P] Create `backend/src/dependencies.py` with get_current_user_id dependency
- [X] T013 [P] Create `backend/src/middleware/auth.py` with Better Auth JWT verification middleware
- [X] T014 [P] Add token expiration validation in `backend/src/dependencies.py` (24-hour expiry per NFR-003)

**Phase 2 Exit Criteria**: Database connection works, auth dependency extracts user_id from JWT, token expiration handled

---

## Phase 3: User Story 1 - Authenticate and Access Secure Task Dashboard

**Goal**: JWT authentication working, user can list their tasks

**Independent Test**: Authenticate with JWT token and retrieve task list (empty initially)

**Acceptance**:
- Token verification rejects invalid/missing tokens
- Requests include user_id from token
- Task list endpoint returns only user's tasks
- Better Auth JWT tokens are properly verified

- [X] T020 [US1] Create `backend/src/schemas/auth.py` with JWTPayload Pydantic model
- [X] T021 [US1] Create `backend/src/schemas/task.py` with TaskCreate, TaskUpdate, TaskResponse schemas
- [X] T022 [US1] Create `backend/src/models/task.py` with Task SQLModel entity (with all required fields per spec)
- [X] T023 [US1] Create `backend/src/routers/auth.py` with register/login/logout endpoints per spec
- [X] T024 [US1] Create `backend/src/routers/tasks.py` with GET /api/tasks endpoint (list tasks)
- [X] T025 [US1] Create `backend/src/main.py` with FastAPI app, CORS, and health endpoint

**Phase 3 Exit Criteria**: GET /api/tasks returns 401 without token, returns user's tasks with valid token

---

## Phase 4: User Story 2 - Create and Manage Personal Tasks

**Goal**: Full task CRUD operations with user isolation

**Independent Test**: Create, read, update, delete tasks; verify only owner can access

**Acceptance**:
- Create task assigns current user's user_id
- Get/Update/Delete only works for owned tasks
- List shows only user's tasks

- [X] T030 [US2] Add POST /api/tasks endpoint in `backend/src/routers/tasks.py`
- [X] T031 [US2] Add GET /api/tasks/{id} endpoint in `backend/src/routers/tasks.py`
- [X] T032 [US2] Add PUT /api/tasks/{id} endpoint in `backend/src/routers/tasks.py`
- [X] T033 [US2] Add DELETE /api/tasks/{id} endpoint in `backend/src/routers/tasks.py`
- [X] T034 [US2] Add PATCH /api/tasks/{id}/toggle endpoint in `backend/src/routers/tasks.py`

**Phase 4 Exit Criteria**: All 6 task endpoints work with proper user isolation

---

## Phase 5: User Story 3 - Secure and Performant API

**Goal**: Performance requirements met, error handling, logging

**Independent Test**: Response times <3s p95, concurrent requests succeed

**Acceptance**:
- All responses under 3 seconds
- Concurrent requests handled efficiently
- Proper HTTP status codes for errors
- System handles graceful degradation during database issues

- [X] T040 [US3] Add request logging middleware in `backend/src/main.py`
- [X] T041 [US3] Add rate limiting dependency in `backend/src/dependencies.py`
- [X] T042 [US3] Add proper error handlers in `backend/src/main.py`
- [X] T043 [US3] Configure connection pooling in `backend/src/database.py` (pool_size=5, max_overflow=10)
- [X] T044 [US3] Add concurrent request handling tests in `backend/tests/test_performance.py`
- [X] T045 [US3] Add graceful degradation handling in `backend/src/database.py` for connection failures (NFR-007)

**Phase 5 Exit Criteria**: API meets NFR-001 (<3s p95), NFR-002 (100 concurrent users), and NFR-007 (graceful degradation)

---

## Phase 6: Compliance & Monitoring

Address compliance and operational requirements.

- [X] T050 Add GDPR/CCPA compliance measures in `backend/src/models/user.py` and privacy features
- [X] T051 Add monitoring and uptime validation in `backend/src/main.py` (NFR-005 99.9% uptime)
- [X] T052 Add Better Auth JWT integration validation in `backend/src/middleware/auth.py`
- [X] T053 Add concurrent request validation in `backend/tests/test_concurrent_requests.py`
- [X] T054 Verify Swagger UI at /docs works correctly per FR-010
- [X] T055 Run final verification against all Success Criteria in spec.md

**Phase 6 Exit Criteria**: All compliance measures implemented, monitoring in place, all success criteria validated

---

## Phase 7: Polish & Cross-Cutting Concerns

Final improvements and documentation.

- [X] T060 Add database index creation on startup in `backend/src/main.py`
- [X] T061 Create `backend/tests/conftest.py` with pytest fixtures
- [X] T062 Create `backend/tests/test_auth.py` for JWT verification tests
- [X] T063 Create `backend/tests/test_tasks.py` for task CRUD tests
- [X] T064 Add comprehensive API documentation in `backend/src/main.py` per FR-010
- [X] T065 Run final verification against Definition of Done in plan.md

**Phase 7 Exit Criteria**: All tests pass, documentation complete, Definition of Done met

---

## Implementation Strategy

### MVP Scope (Phase 3 only)
- Focus on US1 first: JWT auth + task list
- Validates the entire chain: token → user_id → query → response
- ~6 tasks, ~2-3 hours

### Incremental Delivery
1. **MVP**: Phase 3 (basic auth + list)
2. **Core Features**: Phase 4 (full CRUD)
3. **Performance**: Phase 5 (concurrency + error handling)
4. **Compliance**: Phase 6 (monitoring + compliance)
5. **Polish**: Phase 7 (final validation)

### Parallel Execution
- T010, T011, T012, T013, T014 can run in parallel (different files, no dependencies)
- T020-T025 (US1 tasks) can run in parallel once T012 is done
- T030-T034 (US2 tasks) can run in parallel once T022 is done

---

## Task Summary

| Phase | Task Count | Description |
|-------|------------|-------------|
| Phase 1 | 8 | Setup |
| Phase 2 | 5 | Foundational |
| Phase 3 (US1) | 6 | Auth + Task List |
| Phase 4 (US2) | 5 | Task CRUD |
| Phase 5 (US3) | 6 | Performance |
| Phase 6 | 6 | Compliance & Monitoring |
| Phase 7 | 6 | Polish |
| **Total** | **42** | |

**Suggested MVP**: Complete Phase 1 → Phase 2 → Phase 3 (US1) for initial validation
