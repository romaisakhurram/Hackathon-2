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

# CORS Configuration - This should be added FIRST
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers so frontend can read them
    expose_headers=["Access-Control-Allow-Origin", "Content-Type", "Authorization"]
)

# Custom authentication middleware - placed AFTER CORS middleware
@app.middleware("http")
async def handle_auth(request: Request, call_next):
    # Store original origin to preserve CORS headers
    origin = request.headers.get("origin", "")

    # Check if this is an API request that requires authentication
    if request.url.path.startswith('/api/') and request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
        # Check for authentication token in Authorization header first
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            # Extract token from Authorization header
            token = auth_header[7:]  # Remove "Bearer " prefix
            request.state.auth_token = token
            print(f"Using token from Authorization header")  # Debug log
        elif auth_header:  # If there's an Authorization header but it doesn't start with "Bearer "
            # Just use whatever is in the Authorization header
            request.state.auth_token = auth_header
            print(f"Using token from Authorization header (no Bearer prefix)")  # Debug log
        else:
            # If no Authorization header, check for common cookie names
            cookie_token = None
            cookie_name_found = None
            cookie_names = [
                # Common better-auth cookie patterns
                "better-auth.session_token",
                "better-auth.session",
                "better-auth-session",
                "__Secure-authjs.session-token",
                "authjs.session-token",
                "auth_token",
                "better_auth_token",
                "token",
                "session",
                # Try generic session cookies that might be used
                "session_token",
                "__session",
                # Additional authjs tokens
                "next-auth.session-token",
                "authjs.csrf-token",
                "authjs.callback-url",
            ]

            # Look for the cookie
            for cookie_name in cookie_names:
                if cookie_name in request.cookies:
                    cookie_token = request.cookies[cookie_name]
                    cookie_name_found = cookie_name
                    break

            # If we still don't have a token, check for any cookie that might be a JWT
            if not cookie_token:
                for cookie_name, cookie_value in request.cookies.items():
                    if cookie_value and cookie_value.startswith(('ey', 'eyJ')):  # JWTs start with 'ey' or 'eyJ'
                        cookie_token = cookie_value
                        cookie_name_found = cookie_name
                        break

            # If we found a token in cookies, add it to the request state
            if cookie_token:
                request.state.auth_token = cookie_token
                print(f"Found authentication token in cookie: {cookie_name_found}")  # Debug log
            else:
                print(f"No authentication token found. Headers: {list(request.headers.keys())}, Cookies: {list(request.cookies.keys())}")  # Debug log

    # Process the request and handle any exceptions
    try:
        response = await call_next(request)
    except Exception as exc:
        # Log the actual error for debugging
        logger.error(f"Unhandled exception: {exc}")
        import traceback
        logger.error(traceback.format_exc())

        # Create an error response
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "message": str(exc)}
        )

    # Ensure CORS headers are preserved even after processing
    # Only set if not already set by CORSMiddleware
    if origin and "Access-Control-Allow-Origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = origin
    if "Access-Control-Allow-Credentials" not in response.headers:
        response.headers["Access-Control-Allow-Credentials"] = "true"
    if "Access-Control-Allow-Headers" not in response.headers:
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    if "Access-Control-Allow-Methods" not in response.headers:
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"

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

# Include the new chat endpoint
try:
    from .api.chat_router import router as chat_router
    app.include_router(chat_router)
    logger.info("Chat router successfully loaded and included")
except ImportError as e:
    logger.error(f"Failed to import chat router: {e}")
    # Log the full traceback for better debugging
    import traceback
    logger.error(f"Full traceback: {traceback.format_exc()}")
    # If there's an import error, we should fail fast rather than silently skip
    raise

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

# Add an explicit OPTIONS handler for preflight requests
@app.options("/{full_path:path}")
async def cors_options(request: Request):
    response = JSONResponse(content={})
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    return response