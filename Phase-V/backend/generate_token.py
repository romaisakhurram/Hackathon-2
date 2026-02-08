#!/usr/bin/env python3
"""
Generate a test JWT token for authentication testing.
"""
import uuid
from datetime import datetime, timedelta
from jose import jwt
import os

# Use the same secret as the backend
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_for_development")
ALGORITHM = "HS256"

def create_test_token():
    """Create a valid test JWT token."""
    user_id = str(uuid.uuid4())

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow().timestamp(),
        "sub": "test@example.com"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, user_id

if __name__ == "__main__":
    token, user_id = create_test_token()
    print(f"Generated test token for user: {user_id}")
    print(f"Token: {token}")
    print(f"\nTo test with curl:")
    print(f"curl -X GET \"http://127.0.0.1:8000/api/tasks/\" -H \"Authorization: Bearer {token}\" -H \"Content-Type: application/json\"")