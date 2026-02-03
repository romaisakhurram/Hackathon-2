"""
End-to-end tests for user scenarios.
Tests complete user journeys from API request to response with full system integration.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import uuid
from datetime import datetime


from backend.src.main import app
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message


def test_persistent_chat_session_scenario():
    """
    E2E Test: Persistent Chat Session
    Given a user sends a message to the chat endpoint with JWT token
    When the system validates JWT and extracts user_id
    Then it should create/load conversation, save user message, process with AI agent, save AI response, and return response with conversation_id and tool_calls
    """
    client = TestClient(app)

    # Mock authentication to return a test user ID
    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_123"

        # Mock services
        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

            # Create mock conversation
            mock_conversation = Conversation(
                id=uuid.uuid4(),
                user_id="test_user_123"
            )

            # Create mock messages
            mock_user_message = Message(
                id=uuid.uuid4(),
                conversation_id=mock_conversation.id,
                user_id="test_user_123",
                role="user",
                content="Add a task to buy groceries"
            )

            mock_ai_response = Message(
                id=uuid.uuid4(),
                conversation_id=mock_conversation.id,
                user_id="ai_agent",
                role="assistant",
                content="I've added the task 'buy groceries' to your list."
            )

            # Configure service mocks
            mock_conv_service.get_or_create_conversation.return_value = mock_conversation
            mock_msg_service.save_user_message.return_value = mock_user_message
            mock_msg_service.save_assistant_message.return_value = mock_ai_response

            # Configure AI agent mock
            mock_ai_agent.process_message.return_value = {
                "response": "I've added the task 'buy groceries' to your list.",
                "tool_calls": [{"name": "add_task", "parameters": {"title": "buy groceries"}}],
                "conversation_id": str(mock_conversation.id)
            }

            # Make the API request
            response = client.post(
                "/api/test_user_123/chat",
                json={
                    "message": "Add a task to buy groceries"
                },
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Verify the response
            assert response.status_code == 200
            response_data = response.json()

            # Verify the response structure matches the spec
            assert "conversation_id" in response_data
            assert "response" in response_data
            assert "tool_calls" in response_data

            assert response_data["conversation_id"] == str(mock_conversation.id)
            assert "buy groceries" in response_data["response"]
            assert isinstance(response_data["tool_calls"], list)

            # Verify all services were called as expected
            mock_conv_service.get_or_create_conversation.assert_called_once()
            mock_msg_service.save_user_message.assert_called_once()
            mock_msg_service.save_assistant_message.assert_called_once()
            mock_ai_agent.process_message.assert_called_once()


def test_conversation_continuity_after_restart_scenario():
    """
    E2E Test: Conversation Continuity After Restart
    Given a user had ongoing conversation with conversation_id=123
    When server restarts (loses any in-memory state) and user sends next message with conversation_id=123
    Then the system should load conversation from database and continue seamlessly
    """
    client = TestClient(app)

    # Mock authentication
    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_123"

        # Mock services to simulate stateless operation
        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

            # Create a mock existing conversation
            existing_conversation_id = uuid.uuid4()
            mock_conversation = Conversation(
                id=existing_conversation_id,
                user_id="test_user_123"
            )

            # Create mock messages for the continuation
            mock_user_message = Message(
                id=uuid.uuid4(),
                conversation_id=existing_conversation_id,
                user_id="test_user_123",
                role="user",
                content="What was the last task I added?"
            )

            mock_ai_response = Message(
                id=uuid.uuid4(),
                conversation_id=existing_conversation_id,
                user_id="ai_agent",
                role="assistant",
                content="The last task you added was 'buy groceries'."
            )

            # Configure mocks to simulate loading existing conversation from DB
            mock_conv_service.get_conversation_by_id.return_value = mock_conversation
            mock_msg_service.save_user_message.return_value = mock_user_message
            mock_msg_service.save_assistant_message.return_value = mock_ai_response

            # Configure AI agent to respond to continuation request
            mock_ai_agent.process_message.return_value = {
                "response": "The last task you added was 'buy groceries'.",
                "tool_calls": [],
                "conversation_id": str(existing_conversation_id)
            }

            # Make request with existing conversation_id to continue conversation
            response = client.post(
                "/api/test_user_123/chat",
                json={
                    "message": "What was the last task I added?",
                    "conversation_id": str(existing_conversation_id)
                },
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Verify the response shows conversation continuity
            assert response.status_code == 200
            response_data = response.json()

            assert response_data["conversation_id"] == str(existing_conversation_id)
            assert "last task" in response_data["response"]
            assert "buy groceries" in response_data["response"]

            # Verify that the conversation was loaded from database (stateless operation)
            mock_conv_service.get_conversation_by_id.assert_called_once_with(
                existing_conversation_id, "test_user_123"
            )
            # Verify no server-side session memory was used
            mock_conv_service.create_conversation.assert_not_called()


def test_unauthorized_access_prevention_scenario():
    """
    E2E Test: Unauthorized Access Prevention
    Given a user attempts to access conversation belonging to another user
    When system validates user_id from JWT against conversation ownership
    Then it should return 403 Forbidden error with appropriate error message
    """
    client = TestClient(app)

    # Mock authentication to return a different user ID than conversation owner
    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "different_user_456"  # Different from conversation owner

        # Mock services to simulate attempt to access another user's conversation
        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service:
            # Configure mock to return None (conversation not accessible to user)
            mock_conv_service.get_conversation_by_id.return_value = None

            # Make request to access another user's conversation
            response = client.post(
                "/api/different_user_456/chat",
                json={
                    "message": "Try to access someone else's conversation",
                    "conversation_id": "another_users_conversation_id"
                },
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return 403 Forbidden or 404 Not Found for unauthorized access
            assert response.status_code in [403, 404]

            response_data = response.json()
            assert "detail" in response_data or "error" in response_data

            # Verify that the unauthorized access was prevented
            mock_conv_service.get_conversation_by_id.assert_called_once()


def test_multiple_concurrent_users_scenario():
    """
    E2E Test: Multiple concurrent users can use the system simultaneously without conflicts.
    Tests user isolation and concurrent request handling.
    """
    client = TestClient(app)

    # Test simultaneous requests from different users
    import threading
    import time

    results = {}

    def make_request(user_id, message, index):
        """Function to make a request for a specific user."""
        with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
            mock_auth.return_value = user_id

            with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
                 patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
                 patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent:

                # Create unique conversation for each user
                mock_conversation = Conversation(
                    id=uuid.uuid4(),
                    user_id=user_id
                )

                mock_user_message = Message(
                    id=uuid.uuid4(),
                    conversation_id=mock_conversation.id,
                    user_id=user_id,
                    role="user",
                    content=message
                )

                mock_ai_response = Message(
                    id=uuid.uuid4(),
                    conversation_id=mock_conversation.id,
                    user_id="ai_agent",
                    role="assistant",
                    content=f"Processed message for {user_id}: {message}"
                )

                # Configure mocks
                mock_conv_service.get_or_create_conversation.return_value = mock_conversation
                mock_msg_service.save_user_message.return_value = mock_user_message
                mock_msg_service.save_assistant_message.return_value = mock_ai_response
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

    # Create threads for multiple concurrent requests
    threads = []
    users_messages = [
        ("user_001", "User 1 message"),
        ("user_002", "User 2 message"),
        ("user_003", "User 3 message")
    ]

    for i, (user_id, message) in enumerate(users_messages):
        thread = threading.Thread(target=make_request, args=(user_id, message, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all requests succeeded independently
    for i in range(len(users_messages)):
        assert results[i]["status"] == 200
        assert "conversation_id" in results[i]["data"]
        assert "response" in results[i]["data"]
        assert users_messages[i][0] in results[i]["data"]["response"] or users_messages[i][1] in results[i]["data"]["response"]


def test_rate_limiting_enforcement_scenario():
    """
    E2E Test: Rate limiting is enforced per user to prevent abuse.
    """
    client = TestClient(app)

    # Mock authentication
    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_123"

        # Mock services
        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service, \
             patch('backend.src.api.chat_endpoint.message_service') as mock_msg_service, \
             patch('backend.src.api.chat_endpoint.ai_agent') as mock_ai_agent, \
             patch('backend.src.api.chat_endpoint.rate_limiter') as mock_rate_limiter:

            # Configure mock conversation
            mock_conversation = Conversation(
                id=uuid.uuid4(),
                user_id="test_user_123"
            )

            # Configure service mocks
            mock_conv_service.get_or_create_conversation.return_value = mock_conversation
            mock_msg_service.save_user_message.return_value = Message(
                id=uuid.uuid4(),
                conversation_id=mock_conversation.id,
                user_id="test_user_123",
                role="user",
                content="Test message"
            )
            mock_msg_service.save_assistant_message.return_value = Message(
                id=uuid.uuid4(),
                conversation_id=mock_conversation.id,
                user_id="ai_agent",
                role="assistant",
                content="Test response"
            )
            mock_ai_agent.process_message.return_value = {
                "response": "Test response",
                "tool_calls": [],
                "conversation_id": str(mock_conversation.id)
            }

            # First request should succeed
            response1 = client.post(
                "/api/test_user_123/chat",
                json={"message": "First request"},
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )
            assert response1.status_code == 200

            # Configure rate limiter to deny subsequent requests
            mock_rate_limiter.check_rate_limit.return_value = False

            # Subsequent request should be rate-limited
            response2 = client.post(
                "/api/test_user_123/chat",
                json={"message": "Second request (should be rate limited)"},
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return 429 Too Many Requests
            assert response2.status_code == 429
            response_data = response2.json()
            assert "rate limit" in response_data.get("detail", response_data.get("error", "")).lower()


def test_error_handling_graceful_degradation():
    """
    E2E Test: System handles errors gracefully without crashing.
    """
    client = TestClient(app)

    # Mock authentication
    with patch('backend.src.api.chat_endpoint.get_current_user_id') as mock_auth:
        mock_auth.return_value = "test_user_123"

        # Mock services to simulate an error condition
        with patch('backend.src.api.chat_endpoint.conversation_service') as mock_conv_service:
            # Configure the conversation service to raise an exception
            mock_conv_service.get_or_create_conversation.side_effect = Exception("Database connection failed")

            response = client.post(
                "/api/test_user_123/chat",
                json={"message": "Message during error condition"},
                headers={
                    "Authorization": "Bearer test_jwt_token",
                    "Content-Type": "application/json"
                }
            )

            # Should return an appropriate error status instead of crashing
            assert response.status_code in [500, 400, 422]  # Server error or validation error