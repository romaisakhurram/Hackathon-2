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
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Standard HTTPBearer security scheme
security = HTTPBearer()


def get_token_with_fallback(request: Request) -> str:
    """
    Extract and return the token from the authorization header or from request state (for cookie fallback).
    """
    # First, try to get token from the Authorization header using HTTPBearer
    try:
        # Try to get the credentials from the header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
    except:
        pass

    # If not in header, check if the middleware stored a token in the request state
    if hasattr(request, 'state') and hasattr(request.state, 'auth_token'):
        token = getattr(request.state, 'auth_token', None)
        if token and isinstance(token, str):
            # Remove "Bearer " prefix if it exists
            if token.startswith("Bearer "):
                return token[7:]
            return token

    # If no token found, use the original HTTPBearer approach to raise appropriate error
    auth_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
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
    Get the current user ID from the JWT token, checking both header and cookie (via request state).
    This updated version works with both the original header-based auth and cookie fallback.
    """
    # Get the token using our fallback method
    token = get_token_with_fallback(request)

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
            if (current_time - issued_time) > timedelta(hours=24):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token issued more than 24 hours ago (NFR-003)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    return payload


# Additionally, create alternative functions that work with the request object to check cookies
def get_token_with_fallback():
    """
    Create a dependency function that can check both Authorization header and cookies.
    This function will work with the request object to access cookies.
    """
    async def token_dependency(request: Request) -> str:
        # First, try to get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix

        # Then, try to get token from cookies (common with better-auth)
        # Check for common better-auth cookie names
        cookie_names = [
            "better-auth.session",  # Most common better-auth cookie name
            "better-auth-session",
            "authjs.session-token",  # Alternative authjs token
            "auth_token",
            "better_auth_token",
            "token",
            "session"
        ]

        for cookie_name in cookie_names:
            token_cookie = request.cookies.get(cookie_name)
            if token_cookie:
                return token_cookie

        # If no token found anywhere, raise 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_dependency


# Get the dependency function
get_token_from_request = get_token_with_fallback()


def get_current_user_id_from_request(request: Request) -> uuid.UUID:
    """
    Get the current user ID from the JWT token, checking both header and cookies.
    This function works with the request object to access both headers and cookies.
    """
    # Get the token (from header or cookie)
    token = get_token_from_request(request)

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


async def validate_token_expiration_from_request(request: Request):
    """
    Validate token expiration to ensure 24-hour expiry as per NFR-003.
    This function works with the request object to access both headers and cookies.
    """
    # Get the token (from header or cookie)
    token = get_token_from_request(request)

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
            if (current_time - issued_time) > timedelta(hours=24):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token issued more than 24 hours ago (NFR-003)",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    return payload