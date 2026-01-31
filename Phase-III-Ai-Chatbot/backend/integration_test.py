import asyncio
import httpx
import json

async def test_auth_flow():
    """
    Integration test to verify the complete authentication and task flow.
    """
    base_url = "http://127.0.0.1:8000"

    print("Testing authentication flow...")

    # Test 1: Signup
    print("\n1. Testing signup...")
    async with httpx.AsyncClient() as client:
        signup_response = await client.post(
            f"{base_url}/api/auth/sign-up/email",
            json={
                "name": "Integration Test User",
                "email": "integration@test.com",
                "password": "securepassword123"
            }
        )
        print(f"Signup response: {signup_response.status_code}")

        if signup_response.status_code == 200:
            signup_data = signup_response.json()
            token = signup_data.get("access_token")
            print(f"Token received: {bool(token)}")

            if token:
                # Test 2: Use token to access protected endpoint
                print("\n2. Testing task creation with token...")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                task_response = await client.post(
                    f"{base_url}/api/tasks/",
                    json={
                        "title": "Integration Test Task",
                        "description": "This is a test task created during integration test",
                        "priority": 1,
                        "status": "pending"
                    },
                    headers=headers
                )

                print(f"Task creation response: {task_response.status_code}")

                if task_response.status_code == 200:
                    task_data = task_response.json()
                    print(f"Task created successfully: {task_data.get('title', 'Unknown')}")

                    # Test 3: Get tasks
                    print("\n3. Testing task listing...")
                    tasks_response = await client.get(
                        f"{base_url}/api/tasks/",
                        headers=headers
                    )

                    print(f"Task listing response: {tasks_response.status_code}")

                    if tasks_response.status_code == 200:
                        tasks_data = tasks_response.json()
                        print(f"Retrieved {len(tasks_data)} tasks")
                        print("✅ All tests passed! Authentication and task flow working correctly.")
                        return True
                    else:
                        print(f"❌ Task listing failed: {tasks_response.text}")
                        return False
                else:
                    print(f"❌ Task creation failed: {task_response.text}")
                    return False
            else:
                print("❌ No token received from signup")
                return False
        else:
            print(f"❌ Signup failed: {signup_response.text}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_auth_flow())
    if success:
        print("\n🎉 Integration test PASSED!")
    else:
        print("\n❌ Integration test FAILED!")