# Quickstart: Backend API

**Feature**: 2-backend-api-auth
**Created**: 2026-01-09

## Prerequisites

- Python 3.11+
- pip or uv
- Access to Neon PostgreSQL database
- BETTER_AUTH_SECRET from frontend

## Environment Setup

```bash
# Clone and enter backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### .env Configuration

```env
# Neon PostgreSQL
DATABASE_URL="postgresql://neondb_owner:password@ep-xxx.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# JWT Authentication
BETTER_AUTH_SECRET="your-secret-from-frontend"
BETTER_AUTH_URL="https://localhost:3000"

# Server
API_HOST="0.0.0.0"
API_PORT=8000
DEBUG=true
```

## Database Setup

The first run will automatically create tables via SQLModel:

```bash
uvicorn src.main:app --reload
```

Tables created:
- `task` (with indexes on `user_id`, `status`, and composite)

## Running the Server

```bash
# Development
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tasks.py
```

## Project Structure

```
backend/
├── src/
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   ├── database.py       # SQLModel setup
│   ├── models/
│   │   └── task.py       # Task model
│   ├── schemas/
│   │   ├── task.py       # Pydantic schemas
│   │   └── auth.py       # JWT schemas
│   ├── routers/
│   │   ├── auth.py       # Auth utilities
│   │   └── tasks.py      # Task endpoints
│   └── dependencies.py   # Auth dependency
├── tests/
│   ├── conftest.py
│   ├── test_tasks.py
│   └── test_auth.py
├── requirements.txt
└── .env.example
```

## Verification Checklist

- [ ] Server starts without errors
- [ ] Health endpoint responds: `GET /health`
- [ ] JWT auth rejects unauthorized requests
- [ ] Tasks CRUD works with valid token
- [ ] User isolation: can't access other users' tasks
- [ ] Swagger docs accessible at `/docs`
