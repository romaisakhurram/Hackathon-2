"""
Unit tests for the authentication dependencies.
Tests the JWT validation and user_id extraction functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
import uuid
from datetime import datetime, timedelta
from jose import jwt


from backend.src.dependencies.auth_dependencies import get_current_user_id, validate_user_owns_conversation, validate_user_owns_message


def test_get_current_user_id_valid_token():
    """Test extracting user_id from a valid JWT token."""
    # Create a mock request with a valid JWT in the Authorization header
    mock_request = Mock(spec=Request)
    mock_request.headers = {"authorization": "Bearer valid_jwt_token"}

    # Mock the JWT decoding to return a payload with a user_id
    mock_payload = {"user_id": "test_user_123"}

    with patch('backend.src.dependencies.auth_dependencies.jwt.decode', return_value=mock_payload):
        with patch('backend.src.dependencies.auth_dependencies.SECRET_KEY', 'test_secret'):
            result = get_current_user_id(mock_request)

            # Verify the user_id was extracted correctly
            assert result == "test_user_123"


def test_get_current_user_id_missing_authorization_header():
    """Test handling of requests without Authorization header."""
    # Create a mock request without an Authorization header
    mock_request = Mock(spec=Request)
    mock_request.headers = {}

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(mock_request)

    # Verify that a 401 error is raised
    assert exc_info.value.status_code == 401
    assert "No authentication token provided" in exc_info.value.detail


def test_get_current_user_id_invalid_token():
    """Test handling of requests with invalid JWT token."""
    # Create a mock request with an invalid JWT
    mock_request = Mock(spec=Request)
    mock_request.headers = {"authorization": "Bearer invalid_token"}

    # Mock the JWT decoding to raise an exception
    with patch('backend.src.dependencies.auth_dependencies.jwt.decode', side_effect=Exception("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(mock_request)

        # Verify that a 401 error is raised
        assert exc_info.value.status_code == 401
        assert "could not validate credentials" in exc_info.value.detail.lower()


def test_get_current_user_id_no_user_id_in_payload():
    """Test handling of JWT tokens without user_id in payload."""
    # Create a mock request with a JWT that has no user_id
    mock_request = Mock(spec=Request)
    mock_request.headers = {"authorization": "Bearer token_without_user_id"}

    # Mock the JWT decoding to return a payload without user_id
    mock_payload = {"some_other_claim": "value"}

    with patch('backend.src.dependencies.auth_dependencies.jwt.decode', return_value=mock_payload):
        with patch('backend.src.dependencies.auth_dependencies.SECRET_KEY', 'test_secret'):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user_id(mock_request)

            # Verify that a 401 error is raised
            assert exc_info.value.status_code == 401
            assert "could not validate credentials" in exc_info.value.detail.lower()


def test_get_current_user_id_bearer_prefix_missing():
    """Test extracting token from Authorization header without 'Bearer ' prefix."""
    # Create a mock request with a token that doesn't have the 'Bearer ' prefix
    mock_request = Mock(spec=Request)
    mock_request.headers = {"authorization": "just_the_token"}

    # Mock the JWT decoding to return a payload with a user_id
    mock_payload = {"user_id": "test_user_123"}

    with patch('backend.src.dependencies.auth_dependencies.jwt.decode', return_value=mock_payload):
        with patch('backend.src.dependencies.auth_dependencies.SECRET_KEY', 'test_secret'):
            result = get_current_user_id(mock_request)

            # Verify the user_id was extracted correctly
            assert result == "test_user_123"


def test_validate_user_owns_conversation_valid():
    """Test validating that a user owns a conversation."""
    user_id = "test_user_123"
    conversation_user_id = "test_user_123"  # Same user ID

    result = validate_user_owns_conversation(user_id, conversation_user_id)

    # Should return True when user owns the conversation
    assert result is True


def test_validate_user_owns_conversation_invalid():
    """Test validating that a user doesn't own a conversation."""
    user_id = "test_user_123"
    conversation_user_id = "other_user_456"  # Different user ID

    result = validate_user_owns_conversation(user_id, conversation_user_id)

    # Should return False when user doesn't own the conversation
    assert result is False


def test_validate_user_owns_message_valid():
    """Test validating that a user owns a message."""
    user_id = "test_user_123"
    message_user_id = "test_user_123"  # Same user ID

    result = validate_user_owns_message(user_id, message_user_id)

    # Should return True when user owns the message
    assert result is True


def test_validate_user_owns_message_invalid():
    """Test validating that a user doesn't own a message."""
    user_id = "test_user_123"
    message_user_id = "other_user_456"  # Different user ID

    result = validate_user_owns_message(user_id, message_user_id)

    # Should return False when user doesn't own the message
    assert result is False


def test_get_current_user_id_with_expired_token():
    """Test handling of expired JWT tokens."""
    # Create a mock request with an expired JWT
    mock_request = Mock(spec=Request)
    mock_request.headers = {"authorization": "Bearer expired_token"}

    # Create a payload with an expired timestamp
    expired_time = datetime.utcnow() - timedelta(hours=1)
    mock_payload = {"user_id": "test_user_123", "exp": expired_time.timestamp()}

    with patch('backend.src.dependencies.auth_dependencies.jwt.decode', return_value=mock_payload):
        with patch('backend.src.dependencies.auth_dependencies.SECRET_KEY', 'test_secret'):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user_id(mock_request)

            # Verify that a 401 error is raised for expired token
            assert exc_info.value.status_code == 401
            assert "could not validate credentials" in exc_info.value.detail.lower()


def test_get_current_user_id_with_different_algorithm():
    """Test extracting user_id from a JWT with different algorithm."""
    # Create a mock request with a valid JWT
    mock_request = Mock(spec=Request)
    mock_request.headers = {"authorization": "Bearer valid_jwt_token"}

    # Mock the JWT decoding to return a payload with a user_id
    mock_payload = {"user_id": "test_user_123", "sub": "test_subject"}

    with patch('backend.src.dependencies.auth_dependencies.jwt.decode', return_value=mock_payload):
        with patch('backend.src.dependencies.auth_dependencies.SECRET_KEY', 'test_secret'):
            result = get_current_user_id(mock_request)

            # Verify the user_id was extracted correctly
            assert result == "test_user_123"