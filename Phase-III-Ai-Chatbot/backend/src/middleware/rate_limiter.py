"""
Rate limiting middleware for the Todo AI Chatbot.
Implements per-user rate limiting to prevent abuse.
"""
import time
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta


class RateLimiter:
    """
    Simple in-memory rate limiter that tracks requests per user.
    NOTE: This is a basic implementation. In production, use redis-backed rate limiting
    for distributed systems.
    """

    def __init__(self, requests: int = 10, window: int = 60):
        """
        Initialize the rate limiter.

        Args:
            requests: Number of requests allowed per window
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        # Dictionary to store request timestamps for each user_id
        self.requests_log: Dict[str, list] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request from the given user is allowed based on rate limits.

        Args:
            user_id: The ID of the user making the request

        Returns:
            True if the request is allowed, False otherwise
        """
        now = time.time()
        # Clean up old requests outside the current window
        self.requests_log[user_id] = [
            timestamp for timestamp in self.requests_log[user_id]
            if now - timestamp < self.window
        ]

        # Check if the user has exceeded the rate limit
        if len(self.requests_log[user_id]) >= self.requests:
            return False

        # Add current request timestamp
        self.requests_log[user_id].append(now)
        return True


# Global rate limiter instance with default settings (10 requests per minute per user)
rate_limiter = RateLimiter(requests=10, window=60)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware that checks if requests exceed the limit per user.
    """
    # Extract user_id from the request state (set by auth middleware)
    # If the auth middleware has already validated the JWT and extracted user_id,
    # it should be available in request.state
    user_id = getattr(request.state, 'auth_token', None)

    # If user_id is not in request.state, try to extract from path parameters
    if not user_id and 'user_id' in request.path_params:
        user_id = request.path_params['user_id']

    # If we still don't have a user_id, we can't apply rate limiting effectively
    # In a real implementation, we'd ensure the authentication middleware runs first
    # and sets the user_id in request.state

    # For this implementation, we'll skip rate limiting if we can't identify the user
    # In a production system, we might rate limit by IP as a fallback
    response = await call_next(request)

    # Return the response as-is if we can't identify the user
    if not user_id:
        return response

    # Apply rate limiting
    if not rate_limiter.is_allowed(str(user_id)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {rate_limiter.requests} requests per {rate_limiter.window} seconds."
        )

    return response