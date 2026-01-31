#!/usr/bin/env python3
"""
Test script to authenticate and call GET /api/tasks/ endpoint
This solves the 401 error by obtaining a valid JWT token first.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_tasks_with_auth():
    """
    1. Register/Login to get a JWT token
    2. Use that token to call GET /api/tasks/
    """
    
    print("=" * 60)
    print("STEP 1: Get JWT Token via Login/Register")
    print("=" * 60)
    
    # Register a new user
    register_payload = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Register Status: {register_response.status_code}")
    print(f"Register Response: {json.dumps(register_response.json(), indent=2)}")
    
    if register_response.status_code != 200:
        print("❌ Registration failed!")
        return
    
    token = register_response.json()["access_token"]
    print(f"\n✅ Got JWT Token: {token[:50]}...")
    
    print("\n" + "=" * 60)
    print("STEP 2: Call GET /api/tasks/ with JWT Token")
    print("=" * 60)
    
    # Call tasks endpoint with the token
    tasks_response = requests.get(
        f"{BASE_URL}/api/tasks/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Tasks Status: {tasks_response.status_code}")
    print(f"Tasks Response: {json.dumps(tasks_response.json(), indent=2)}")
    
    if tasks_response.status_code == 200:
        print(f"\n✅ SUCCESS! Got {len(tasks_response.json())} tasks for user")
    else:
        print(f"❌ Failed to get tasks: {tasks_response.json()}")
    
    print("\n" + "=" * 60)
    print("STEP 3: Create a Task")
    print("=" * 60)
    
    create_payload = {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "medium"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/tasks/",
        json=create_payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Create Task Status: {create_response.status_code}")
    print(f"Create Task Response: {json.dumps(create_response.json(), indent=2)}")
    
    if create_response.status_code == 200:
        print(f"\n✅ Task created successfully!")
        task_id = create_response.json()["id"]
        
        print("\n" + "=" * 60)
        print("STEP 4: List Tasks Again (should see the new task)")
        print("=" * 60)
        
        tasks_response = requests.get(
            f"{BASE_URL}/api/tasks/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Tasks Status: {tasks_response.status_code}")
        print(f"Tasks Response: {json.dumps(tasks_response.json(), indent=2)}")
        print(f"\n✅ SUCCESS! Now have {len(tasks_response.json())} tasks")

if __name__ == "__main__":
    try:
        test_tasks_with_auth()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
