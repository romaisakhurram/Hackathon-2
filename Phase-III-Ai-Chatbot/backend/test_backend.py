import requests
import json

# Test the backend API endpoints
BASE_URL = "http://127.0.0.1:8000"

print("Testing backend connectivity...")

# Test health endpoint
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")

# Test auth endpoint
try:
    response = requests.get(f"{BASE_URL}/api/auth/get-session", 
                           headers={"Content-Type": "application/json"})
    print(f"Auth check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Auth check failed: {e}")

# Test tasks endpoint without auth (should fail)
try:
    response = requests.get(f"{BASE_URL}/api/tasks/", 
                           headers={"Content-Type": "application/json"})
    print(f"Tasks check (no auth): {response.status_code} - {response.text}")
except Exception as e:
    print(f"Tasks check (no auth) failed: {e}")

# Test tasks endpoint with dummy auth (should fail differently)
try:
    response = requests.get(f"{BASE_URL}/api/tasks/", 
                           headers={
                               "Content-Type": "application/json",
                               "Authorization": "Bearer dummy_token"
                           })
    print(f"Tasks check (dummy auth): {response.status_code} - {response.text}")
except Exception as e:
    print(f"Tasks check (dummy auth) failed: {e}")