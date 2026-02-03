import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing authentication flow...")

# Step 1: Register a user to get a token
print("\n1. Registering a user to get an auth token...")
register_data = {
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
}

try:
    register_resp = requests.post(f"{BASE_URL}/api/auth/register",
                                 headers={"Content-Type": "application/json"},
                                 json=register_data)
    print(f"Register status: {register_resp.status_code}")

    if register_resp.status_code == 200:
        token_data = register_resp.json()
        access_token = token_data.get('access_token')
        print(f"Got token: {access_token[:20]}..." if access_token else "No token received")

        # Step 2: Use the token to access protected endpoint
        print("\n2. Accessing protected /api/tasks/ endpoint with token...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        tasks_resp = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        print(f"Tasks endpoint status: {tasks_resp.status_code}")
        print(f"Tasks response: {tasks_resp.json()}")

    else:
        print(f"Registration failed: {register_resp.text}")

except Exception as e:
    print(f"Error during testing: {e}")