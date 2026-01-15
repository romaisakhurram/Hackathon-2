from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from typing import AsyncGenerator
import logging
import time
from datetime import datetime
from .routers import tasks, auth

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from .database import get_engines
    async_engine, _ = get_engines()

    if async_engine is None:
        print("CRITICAL ERROR: async_engine is still None after initialization!")
        raise RuntimeError("Database engine initialization failed")

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(
    title="Todo Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# ✅ FIXED CORS: Added all possible local origins
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Allow all headers to ensure Authorization header passes through
)

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send


# Custom middleware to handle cookie-based authentication for better-auth compatibility
@app.middleware("http")
async def handle_auth_cookies(request: Request, call_next):
    # Check if this is an API request that requires authentication
    if request.url.path.startswith('/api/') and request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
        # Check for authentication token in cookies if not in header
        if not request.headers.get("Authorization"):
            # Look for common better-auth cookie names
            cookie_token = None
            cookie_names = [
                "better-auth.session",
                "better-auth-session",
                "authjs.session-token",
                "auth_token",
                "better_auth_token",
                "token",
                "session"
            ]

            for cookie_name in cookie_names:
                if cookie_name in request.cookies:
                    cookie_token = request.cookies[cookie_name]
                    break

            # If we found a token in cookies, add it to the request state to be accessed by dependencies
            if cookie_token:
                # Store the token in the request state for later use
                request.state.auth_token = f'Bearer {cookie_token}'

    response = await call_next(request)
    return response


# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response

# Routers (Ensure these exist in your project)
app.include_router(tasks.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Todo API", "status": "running"}


@app.get("/health")
async def health_check():
    from .database import check_database_connection
    db_healthy = await check_database_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "db": "healthy" if db_healthy else "unhealthy"
    }