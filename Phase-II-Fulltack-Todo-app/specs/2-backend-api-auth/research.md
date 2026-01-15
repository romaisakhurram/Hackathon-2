# Research: 2-backend-api-auth

**Feature**: Backend API with JWT Auth and Task CRUD
**Created**: 2026-01-09

## JWT Verification

### Decision: Use `python-jose` library

**Rationale**:
- Industry-standard library for JWT operations in Python
- Native support for HS256 (algorithm used by Better Auth)
- Straightforward secret key verification
- Active maintenance and good documentation
- Compatible with async FastAPI applications

**Alternatives Considered**:
- PyJWT: Less features, no async support
- firebase-admin: Overkill, designed for Firebase specifically

**Implementation**:
```python
from jose import jwt, JWTError

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

def verify_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

### Token Extraction Pattern

**Decision**: Extract from `Authorization: Bearer <token>` header

**Implementation**:
```python
from fastapi import HTTPException, status

def get_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    return parts[1]
```

---

## SQLModel + Neon PostgreSQL

### Decision: Async SQLModel with asyncpg driver

**Rationale**:
- Neon Serverless PostgreSQL natively supports async connections
- SQLModel v2+ provides async engine support via SQLAlchemy
- Connection pooling essential for serverless cold starts
- SSL required for Neon remote connections

**Alternatives Considered**:
- sync SQLModel: Blocks on each request, poor concurrency
- raw psycopg2: No ORM benefits, more boilerplate

**Connection Setup**:
```python
from sqlmodel import create_async_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Connection health checks
)

async def get_db():
    async with Session(engine) as session:
        yield session
```

### Index Strategy

**Decision**: Index `user_id`, `status`, and create composite index

**Rationale**:
- Most queries filter by user_id (user isolation)
- Common query: "get pending tasks for user"
- Composite index optimizes the most frequent pattern

**SQL**:
```sql
CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_status ON task(status);
CREATE INDEX idx_task_user_status ON task(user_id, status);
```

---

## User Isolation Pattern

### Decision: Query-level filtering via current_user_id dependency

**Rationale**:
- Constitution requirement: strict data partitioning
- Centralized in dependency for consistency
- Every query includes WHERE user_id = current_user_id

**Implementation**:
```python
async def get_current_user_id(token: str = Depends(get_token)) -> UUID:
    payload = verify_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return UUID(user_id)

# In each endpoint:
@router.get("/tasks")
async def list_tasks(user_id: UUID = Depends(get_current_user_id)):
    result = await session.execute(
        select(Task).where(Task.user_id == user_id)
    )
```

---

## FastAPI Best Practices

### CORS Configuration

**Decision**: Allow frontend origin with credentials

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error Handling

**Decision**: Use HTTPException with consistent error format

**Implementation**:
```python
from fastapi import HTTPException

class NotFoundError(HTTPException):
    def __init__(self, resource: str):
        super().__init__(status_code=404, detail=f"{resource} not found")

class UnauthorizedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Unauthorized")
```

---

## Performance Considerations

### Connection Pooling

- pool_size=5: Minimum connections to maintain
- max_overflow=10: Extra connections during bursts
- pool_pre_ping=True: Verify connections before use

### Async/Await

- All database operations use async/await
- Concurrent requests handled efficiently
- No blocking calls in request handlers

---

## Sources

- [python-jose documentation](https://python-jose.readthedocs.io/)
- [SQLModel documentation](https://sqlmodel.tiangolo.com/)
- [Neon Serverless documentation](https://neon.tech/docs/serverless)
- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
