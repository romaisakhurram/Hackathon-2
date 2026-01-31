#!/usr/bin/env python3
"""
Test script to verify the authentication fix.
"""
import requests
import json
import uuid
from datetime import datetime, timedelta
from jose import jwt

# Test server URL
BASE_URL = "http://localhost:8000"

def create_test_token():
    """Create a valid test JWT token."""
    secret = "fallback_secret_for_development"  # Same as in the backend
    user_id = str(uuid.uuid4())

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow().timestamp(),
        "sub": "test@example.com"
    }

    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, user_id

def test_unauthorized_request():
    """Test request without authentication."""
    print("Testing unauthorized request to /api/tasks/...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_authorized_request():
    """Test request with proper authentication."""
    print("\nTesting authorized request to /api/tasks/...")

    # Create a valid token
    token, user_id = create_test_token()
    print(f"Created test token for user: {user_id}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("✅ Authentication working correctly!")
        else:
            print(f"Response: {response.json()}")
            print("❌ Authentication may still have issues")
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_health_endpoint():
    """Test the health endpoint which should not require authentication."""
    print("\nTesting health endpoint (should not require auth)...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Backend Authentication Fix\n")
    print("=" * 40)

    # Test health endpoint first
    test_health_endpoint()

    # Test unauthorized request
    test_unauthorized_request()

    # Test authorized request
    test_authorized_request()

    print("\n" + "=" * 40)
    print("Test completed!")