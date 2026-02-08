from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .config import settings
import uuid
from collections import defaultdict
import time


# Rate limiting implementation (T041)
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_size: int = 60):
        self.max_requests = max_requests  # 100 requests per minute
        self.window_size = window_size  # 60 seconds window
        self.requests = defaultdict(list)

    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if the identifier has exceeded the rate limit.
        """
        current_time = time.time()

        # Clean old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_size
        ]

        # Check if rate limit exceeded
        if len(self.requests[identifier]) >= self.max_requests:
            return False

        # Add current request
        self.requests[identifier].append(current_time)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_size=60)  # NFR-002: 100 concurrent users


def check_rate_limit(request: Request = None) -> None:
    """
    Dependency to check rate limit based on client IP.
    """
    if request:
        # Get client IP from request
        client_ip = request.client.host if request.client else "unknown"

        if not rate_limiter.check_rate_limit(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload.
    """
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Standard HTTPBearer security scheme (for potential use in other contexts)
security = HTTPBearer()


def get_token_with_fallback(request: Request) -> str:
    """
    Extract and return the token from the authorization header or from request state (for cookie fallback).
    The middleware in main.py processes the Authorization header and stores the cleaned token
    in request.state.auth_token. We prioritize getting it from there to ensure consistency
    with how the middleware processed the token.
    """
    # First, check if the middleware stored a token in the request state (primary source)
    # The middleware processes the Authorization header and stores the cleaned token (without "Bearer " prefix)
    if hasattr(request, 'state') and hasattr(request.state, 'auth_token'):
        token = getattr(request.state, 'auth_token', None)
        if token and isinstance(token, str):
            return token

    # If not in request state, get from the Authorization header as fallback
    auth_header = request.headers.get("Authorization")
    if auth_header:
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        else:
            # If it doesn't have "Bearer " prefix, return the whole header value
            return auth_header

    # If no token found, raise appropriate error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No authentication token provided",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract and return the token from the authorization header.
    This maintains compatibility with existing dependencies.
    """
    return credentials.credentials


def get_current_user_id(request: Request) -> uuid.UUID:
    """
    Get the current user ID from the JWT token.
    This version works with both the middleware (when request.state.auth_token is available)
    and direct API calls/Swagger (when Authorization header is present).
    """
    # First, try to get the token from the middleware (if available)
    if hasattr(request, 'state') and hasattr(request.state, 'auth_token'):
        token = getattr(request.state, 'auth_token', None)
        if token and isinstance(token, str):
            # Use the token from middleware
            pass
        else:
            # Fallback to Authorization header if no token in request state
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No authentication token provided",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    else:
        # Fallback to Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authentication token provided",
                headers={"WWW-Authenticate": "Bearer"},
            )

    payload = verify_token(token)
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def validate_token_expiration(request: Request):
    """
    Validate token expiration to ensure 24-hour expiry as per NFR-003.
    This updated version works with both header and cookie (via request state) authentication.
    """
    # Get the token using our fallback method
    token = get_token_with_fallback(request)

    payload = verify_token(token)
    exp: int = payload.get("exp")

    if exp:
        expiration_time = datetime.fromtimestamp(exp)
        current_time = datetime.utcnow()

        # Check if token has expired
        if current_time > expiration_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token was issued more than 24 hours ago (NFR-003)
        iat: int = payload.get("iat")
        if iat:
            issued_time = datetime.fromtimestamp(iat)
            if (datetime.utcnow() - issued_time) > timedelta(hours=24):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token issued more than 24 hours ago (NFR-003)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    return payload


# The duplicate validate_token_expiration function has been removed to prevent conflicts.
# The original validate_token_expiration function (defined at line 144) should be sufficient.