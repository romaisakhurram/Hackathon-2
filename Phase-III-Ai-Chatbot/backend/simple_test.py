import requests
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

print("Testing authentication fix...")

# Create a test token
token, user_id = create_test_token()
print(f"Created test token for user: {user_id[:8]}...")

# Test unauthorized request
print("\n1. Testing UNAUTHORIZED request (should return 401):")
try:
    response = requests.get("http://localhost:8000/api/tasks/", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json() if response.content else 'No content'}")
except requests.exceptions.RequestException as e:
    print(f"   Error: {e}")

# Test authorized request
print(f"\n2. Testing AUTHORIZED request (should return 200):")
headers = {"Authorization": f"Bearer {token}"}
try:
    response = requests.get("http://localhost:8000/api/tasks/", headers=headers, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json() if response.content else 'No content'}")
    if response.status_code == 200:
        print("   ✅ SUCCESS: Authentication is working correctly!")
    else:
        print("   ❌ FAILED: Authentication may still have issues")
except requests.exceptions.RequestException as e:
    print(f"   Error: {e}")

print(f"\n3. Testing health endpoint (should return 200 without auth):")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json() if response.content else 'No content'}")
except requests.exceptions.RequestException as e:
    print(f"   Error: {e}")

print("\nAuthentication test completed!")