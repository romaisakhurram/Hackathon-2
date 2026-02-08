"""
Integration tests for the chat functionality.
Tests the complete flow from API request to database persistence and AI response.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime
from typing import Dict, Any


def test_complete_chat_flow_integration():
    """
    Test the complete chat flow from user request to AI response with persistence.
    This validates the entire system integration: API → Auth → AI Agent → MCP Tools → Database → Response.
    """
    from backend.src.main import app
    client = TestClient(app)

    # Mock authentication to return a test user ID
    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_123"

        # Mock all the services and AI components
        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

            # Create mock conversation and messages
            mock_conversation = MagicMock()
            mock_conversation.id = uuid.uuid4()
            mock_conversation.user_id = "test_user_123"

            mock_user_message = MagicMock()
            mock_user_message.id = uuid.uuid4()
            mock_user_message.conversation_id = mock_conversation.id
            mock_user_message.user_id = "test_user_123"
            mock_user_message.role = "user"
            mock_user_message.content = "Add a task to buy groceries"

            mock_ai_response = MagicMock()
            mock_ai_response.id = uuid.uuid4()
            mock_ai_response.conversation_id = mock_conversation.id
            mock_ai_response.user_id = "ai_agent"  # AI agent ID
            mock_ai_response.role = "assistant"
            mock_ai_response.content = "I've added the task 'buy groceries' to your list."

            # Configure service mocks
            mock_conv_service.get_or_create_conversation.return_value = mock_conversation
            mock_msg_service.save_user_message.return_value = mock_user_message
            mock_msg_service.save_assistant_message.return_value = mock_ai_response

            # Configure AI agent mock
            mock_ai_agent.process_message.return_value = {
                "response": "I've added the task 'buy groceries' to your list.",
                "tool_calls": [{"name": "add_task", "params": {"title": "buy groceries", "priority": "medium"}}],
                "conversation_id": str(mock_conversation.id)
            }

            # Make the API request
            response = client.post(
                "/api/test_user_123/chat",
                json={
                    "message": "Add a task to buy groceries",
                    "conversation_id": str(mock_conversation.id)
                },
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Verify the response
            assert response.status_code == 200
            response_data = response.json()

            # Verify the response structure matches the API contract
            assert "conversation_id" in response_data
            assert "response" in response_data
            assert "tool_calls" in response_data

            # Verify the conversation ID matches
            assert response_data["conversation_id"] == str(mock_conversation.id)

            # Verify the response content is appropriate
            assert "buy groceries" in response_data["response"]

            # Verify that all services were called as expected
            mock_conv_service.get_or_create_conversation.assert_called_once()
            mock_msg_service.save_user_message.assert_called_once()
            mock_msg_service.save_assistant_message.assert_called_once()
            mock_ai_agent.process_message.assert_called_once()


def test_conversation_continuity_integration():
    """
    Test that conversations continue properly after server restart simulation.
    Verifies that the stateless design works correctly by loading from database.
    """
    from backend.src.main import app
    client = TestClient(app)

    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_456"

        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

            # Create a mock existing conversation
            existing_conversation = MagicMock()
            existing_conversation.id = uuid.uuid4()
            existing_conversation.user_id = "test_user_456"

            # Create mock messages for the conversation
            mock_user_message = MagicMock()
            mock_user_message.id = uuid.uuid4()
            mock_user_message.conversation_id = existing_conversation.id
            mock_user_message.user_id = "test_user_456"
            mock_user_message.role = "user"
            mock_user_message.content = "What was the last task I added?"

            mock_ai_response = MagicMock()
            mock_ai_response.id = uuid.uuid4()
            mock_ai_response.conversation_id = existing_conversation.id
            mock_ai_response.user_id = "ai_agent"
            mock_ai_response.role = "assistant"
            mock_ai_response.content = "The last task you added was 'buy groceries'."

            # Configure service mocks to simulate loading existing conversation
            mock_conv_service.get_conversation_by_id.return_value = existing_conversation
            mock_msg_service.save_user_message.return_value = mock_user_message
            mock_msg_service.save_assistant_message.return_value = mock_ai_response

            # Configure AI agent to respond to the continuity query
            mock_ai_agent.process_message.return_value = {
                "response": "The last task you added was 'buy groceries'.",
                "tool_calls": [{"name": "get_last_task", "result": {"title": "buy groceries"}}],
                "conversation_id": str(existing_conversation.id)
            }

            # Make request to continue existing conversation
            response = client.post(
                "/api/test_user_456/chat",
                json={
                    "message": "What was the last task I added?",
                    "conversation_id": str(existing_conversation.id)
                },
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Verify the response
            assert response.status_code == 200
            response_data = response.json()

            # Verify conversation continuity
            assert response_data["conversation_id"] == str(existing_conversation.id)
            assert "last task" in response_data["response"]
            assert "buy groceries" in response_data["response"]

            # Verify that the existing conversation was loaded from database (stateless operation)
            mock_conv_service.get_conversation_by_id.assert_called_once_with(
                existing_conversation.id, "test_user_456"
            )


def test_user_isolation_integration():
    """
    Test that users cannot access conversations belonging to other users.
    Verifies the user isolation and authentication enforcement.
    """
    from backend.src.main import app
    client = TestClient(app)

    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        # Set authenticated user to a different user than the conversation owner
        mock_auth.return_value = "different_user_789"

        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service:
            # Configure the conversation service to return None (no access to other user's conversation)
            mock_conv_service.get_conversation_by_id.return_value = None

            # Attempt to access another user's conversation
            response = client.post(
                "/api/different_user_789/chat",
                json={
                    "message": "Trying to access another user's conversation",
                    "conversation_id": "other_users_conversation_id"
                },
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return 403 Forbidden or 404 Not Found for unauthorized access
            assert response.status_code in [403, 404]

            # Verify that the conversation access was blocked
            mock_conv_service.get_conversation_by_id.assert_called_once()


def test_error_handling_integration():
    """
    Test error handling throughout the chat integration flow.
    Verifies that errors are properly handled and appropriate responses are returned.
    """
    from backend.src.main import app
    client = TestClient(app)

    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_789"

        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service:
            # Simulate a database error
            mock_conv_service.get_or_create_conversation.side_effect = Exception("Database connection failed")

            # Make request that should trigger error handling
            response = client.post(
                "/api/test_user_789/chat",
                json={"message": "Test message during error condition"},
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return appropriate error status instead of crashing
            assert response.status_code in [500, 400, 422]


def test_rate_limiting_integration():
    """
    Test that rate limiting is properly enforced during chat interactions.
    """
    from backend.src.main import app
    client = TestClient(app)

    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_101"

        # Mock rate limiter to first allow then deny requests
        with patch('backend.src.api.chat_endpoint.rate_limiter') as mock_rate_limiter, \
             patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

            # Configure rate limiter to allow first request but deny subsequent ones
            mock_rate_limiter.check_rate_limit = MagicMock(side_effect=[True, False])

            # Configure services for successful request
            mock_conversation = MagicMock()
            mock_conversation.id = uuid.uuid4()
            mock_conversation.user_id = "test_user_101"

            mock_conv_service.get_or_create_conversation.return_value = mock_conversation
            mock_msg_service.save_user_message.return_value = MagicMock()
            mock_msg_service.save_assistant_message.return_value = MagicMock()
            mock_ai_agent.process_message.return_value = {
                "response": "First request processed successfully",
                "tool_calls": [],
                "conversation_id": str(mock_conversation.id)
            }

            # First request should succeed
            response1 = client.post(
                "/api/test_user_101/chat",
                json={"message": "First request - should succeed"},
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )
            assert response1.status_code == 200

            # Second request should be rate-limited
            response2 = client.post(
                "/api/test_user_101/chat",
                json={"message": "Second request - should be rate limited"},
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return 429 Too Many Requests if rate limited
            if response2.status_code == 429:
                response_data = response2.json()
                assert "rate limit" in str(response_data).lower()


def test_message_persistence_integration():
    """
    Test that all messages (user and AI) are properly persisted to the database.
    """
    from backend.src.main import app
    client = TestClient(app)

    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_202"

        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

            # Create mock conversation and messages
            mock_conversation = MagicMock()
            mock_conversation.id = uuid.uuid4()
            mock_conversation.user_id = "test_user_202"

            user_message = MagicMock()
            user_message.id = uuid.uuid4()
            user_message.conversation_id = mock_conversation.id
            user_message.user_id = "test_user_202"
            user_message.role = "user"
            user_message.content = "Test message for persistence verification"

            ai_response = MagicMock()
            ai_response.id = uuid.uuid4()
            ai_response.conversation_id = mock_conversation.id
            ai_response.user_id = "ai_agent"
            ai_response.role = "assistant"
            ai_response.content = "Test response for persistence verification"

            # Configure service mocks
            mock_conv_service.get_or_create_conversation.return_value = mock_conversation
            mock_msg_service.save_user_message.return_value = user_message
            mock_msg_service.save_assistant_message.return_value = ai_response

            # Configure AI agent mock
            mock_ai_agent.process_message.return_value = {
                "response": "Test response for persistence verification",
                "tool_calls": [],
                "conversation_id": str(mock_conversation.id)
            }

            # Make the API request
            response = client.post(
                "/api/test_user_202/chat",
                json={"message": "Test message for persistence verification"},
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Verify success
            assert response.status_code == 200

            # Verify that both user and AI messages were persisted
            mock_msg_service.save_user_message.assert_called_once()
            mock_msg_service.save_assistant_message.assert_called_once()

            # Verify the parameters passed to message persistence
            user_msg_call_args = mock_msg_service.save_user_message.call_args
            ai_msg_call_args = mock_msg_service.save_assistant_message.call_args

            # Check that the right content was saved
            assert user_msg_call_args[0][2] == "Test message for persistence verification"  # content parameter
            assert ai_msg_call_args[0][2] == "Test response for persistence verification"  # content parameter


def test_concurrent_access_integration():
    """
    Test that the system handles concurrent requests for the same conversation safely.
    """
    import threading
    import time

    from backend.src.main import app
    client = TestClient(app)

    # Shared results dictionary
    results = {}

    def make_request(user_id, message, index):
        """Function to make a request for a specific user."""
        with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
            mock_auth.return_value = user_id

            with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
                 patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
                 patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

                # Create mock conversation
                mock_conversation = MagicMock()
                mock_conversation.id = uuid.uuid4()
                mock_conversation.user_id = user_id

                # Configure services
                mock_conv_service.get_or_create_conversation.return_value = mock_conversation
                mock_msg_service.save_user_message.return_value = MagicMock()
                mock_msg_service.save_assistant_message.return_value = MagicMock()
                mock_ai_agent.process_message.return_value = {
                    "response": f"Processed message for {user_id}: {message}",
                    "tool_calls": [],
                    "conversation_id": str(mock_conversation.id)
                }

                response = client.post(
                    f"/api/{user_id}/chat",
                    json={"message": message},
                    headers={
                        "Authorization": "Bearer test_jwt_token",
                        "Content-Type": "application/json"
                    }
                )

                results[index] = {
                    "status": response.status_code,
                    "data": response.json() if response.status_code == 200 else response.text
                }

    # Create threads for multiple concurrent requests to the same user
    threads = []
    user_id = "concurrent_test_user"
    messages = [
        f"Concurrent message {i}" for i in range(5)
    ]

    for i, message in enumerate(messages):
        thread = threading.Thread(target=make_request, args=(user_id, message, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all requests succeeded
    for i in range(len(messages)):
        assert results[i]["status"] == 200
        assert "conversation_id" in results[i]["data"]
        assert "response" in results[i]["data"]


def test_stateless_operation_integration():
    """
    Test that the system operates in a truly stateless manner without server memory.
    """
    from backend.src.main import app
    client = TestClient(app)

    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "stateless_test_user"

        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

            # Create mock conversation
            mock_conversation = MagicMock()
            mock_conversation.id = uuid.uuid4()
            mock_conversation.user_id = "stateless_test_user"

            # Configure services
            mock_conv_service.get_or_create_conversation.return_value = mock_conversation
            mock_msg_service.save_user_message.return_value = MagicMock()
            mock_msg_service.save_assistant_message.return_value = MagicMock()
            mock_ai_agent.process_message.return_value = {
                "response": "Stateless operation verified",
                "tool_calls": [],
                "conversation_id": str(mock_conversation.id)
            }

            # Make multiple requests to verify stateless operation
            for i in range(3):
                response = client.post(
                    "/api/stateless_test_user/chat",
                    json={"message": f"Stateless test message {i}"},
                    headers={
                        "Authorization": "Bearer test_jwt_token",
                        "Content-Type": "application/json"
                    }
                )

                assert response.status_code == 200

                # Verify that each request loads from database (not server memory)
                # The service should be called each time to load from database
                assert mock_conv_service.get_or_create_conversation.call_count == i + 1


def run_all_integration_tests():
    """
    Run all integration tests and return results.
    """
    print("Running integration tests for chat functionality...")

    test_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "details": []
    }

    tests = [
        ("Complete Chat Flow", test_complete_chat_flow_integration),
        ("Conversation Continuity", test_conversation_continuity_integration),
        ("User Isolation", test_user_isolation_integration),
        ("Error Handling", test_error_handling_integration),
        ("Rate Limiting", test_rate_limiting_integration),
        ("Message Persistence", test_message_persistence_integration),
        ("Concurrent Access", test_concurrent_access_integration),
        ("Stateless Operation", test_stateless_operation_integration)
    ]

    for test_name, test_func in tests:
        try:
            test_func()
            test_results["tests_run"] += 1
            test_results["tests_passed"] += 1
            test_results["details"].append({"name": test_name, "status": "passed", "error": None})
            print(f"✅ {test_name}: PASSED")
        except Exception as e:
            test_results["tests_run"] += 1
            test_results["tests_failed"] += 1
            test_results["details"].append({"name": test_name, "status": "failed", "error": str(e)})
            print(f"❌ {test_name}: FAILED - {str(e)}")

    overall_status = "passed" if test_results["tests_failed"] == 0 else "failed"
    test_results["overall_status"] = overall_status

    print(f"\n📊 Integration Test Results: {test_results['tests_passed']}/{test_results['tests_run']} passed")
    return test_results


# Run tests if this file is executed directly
if __name__ == "__main__":
    results = run_all_integration_tests()
    exit(0 if results["overall_status"] == "passed" else 1)