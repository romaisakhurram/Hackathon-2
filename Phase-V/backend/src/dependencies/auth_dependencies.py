"""
Authentication dependencies for the chat persistence feature.
Handles JWT validation and user_id extraction from request headers.
"""
from fastapi import HTTPException, status, Request
from typing import Optional
import os
from datetime import datetime, timezone
from jose import JWTError, jwt


# Initialize JWT settings from environment
from ..config import settings
SECRET_KEY = settings.better_auth_secret
ALGORITHM = "HS256"


async def get_current_user_id(request: Request) -> str:
    """
    Extract and validate user_id from JWT token.
    First checks for token in request.state.auth_token (set by middleware),
    then falls back to Authorization header.

    Args:
        request: The incoming request containing the Authorization header

    Returns:
        str: The user_id extracted from the JWT token

    Raises:
        HTTPException: If the token is invalid, expired, or missing
    """
    # First check for token that may have been set by middleware in request.state
    token = getattr(request.state, 'auth_token', None)

    # If no token in request.state, fall back to checking Authorization header directly
    if not token:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )

        # Extract token from header (expects "Bearer <token>")
        token_prefix = "Bearer "
        if not auth_header.startswith(token_prefix):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer <token>'"
            )

        token = auth_header[len(token_prefix):]

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user_id from the token
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - no user_id in token"
            )

        # Additional validation could include checking token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


def validate_user_owns_conversation(user_id: str, conversation_user_id: str) -> bool:
    """
    Validate that the authenticated user owns the conversation.

    Args:
        user_id: The ID of the authenticated user from JWT token
        conversation_user_id: The ID of the user who owns the conversation

    Returns:
        bool: True if the user owns the conversation, False otherwise
    """
    return user_id == conversation_user_id


def validate_user_owns_message(user_id: str, message_user_id: str) -> bool:
    """
    Validate that the authenticated user owns the message.

    Args:
        user_id: The ID of the authenticated user from JWT token
        message_user_id: The ID of the user who sent the message

    Returns:
        bool: True if the user owns the message, False otherwise
    """
    return user_id == message_user_id