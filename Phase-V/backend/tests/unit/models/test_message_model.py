"""
Unit tests for the Message model.
Tests the Message model's attributes, validation, and basic functionality.
"""
import pytest
from datetime import datetime
from uuid import UUID
import uuid

from backend.src.models.message import Message


def test_message_creation_with_required_fields():
    """Test creating a message with only required fields."""
    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    role = "user"
    content = "This is a test message content."

    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )

    # Verify the message was created with the correct attributes
    assert message.conversation_id == conversation_id
    assert message.user_id == user_id
    assert message.role == role
    assert message.content == content

    # Verify that an ID was automatically generated
    assert isinstance(message.id, UUID)

    # Verify that timestamp was set
    assert isinstance(message.created_at, datetime)


def test_message_creation_with_optional_fields():
    """Test creating a message with optional fields."""
    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    role = "assistant"
    content = "This is an AI response message."
    metadata_json = '{"tool_calls": [{"name": "add_task", "params": {"title": "test"}}]}'

    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        metadata_json=metadata_json
    )

    assert message.conversation_id == conversation_id
    assert message.user_id == user_id
    assert message.role == role
    assert message.content == content
    assert message.metadata_json == metadata_json
    assert isinstance(message.id, UUID)
    assert isinstance(message.created_at, datetime)


def test_message_timestamps_are_set_on_creation():
    """Test that created_at is automatically set during message creation."""
    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    role = "user"
    content = "Test message content"

    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )

    # Timestamp should be set during creation
    assert message.created_at is not None
    assert isinstance(message.created_at, datetime)


def test_message_id_is_unique():
    """Test that each message gets a unique ID."""
    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    role = "user"

    message1 = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content="First message"
    )

    message2 = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content="Second message"
    )

    # Each message should have a unique ID
    assert message1.id != message2.id
    assert isinstance(message1.id, UUID)
    assert isinstance(message2.id, UUID)


def test_message_role_validation():
    """Test that message roles are properly validated."""
    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    content = "Test message content"

    # Test valid roles
    user_message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=content
    )
    assert user_message.role == "user"

    assistant_message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=content
    )
    assert assistant_message.role == "assistant"


def test_message_table_name():
    """Test that the message model has the correct table name."""
    message = Message(
        conversation_id=uuid.uuid4(),
        user_id="test_user_123",
        role="user",
        content="Test content"
    )

    # The table name is set as __tablename__ in the model, but not directly accessible as an attribute
    # This test ensures the model is properly defined
    assert hasattr(Message, '__tablename__')
    assert Message.__tablename__ == "messages"


def test_message_field_constraints():
    """Test that message fields have the expected constraints."""
    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    role = "user"
    content = "Test message content"

    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )

    # Verify required fields
    assert message.conversation_id is not None
    assert message.user_id is not None
    assert message.role is not None
    assert message.content is not None

    # Verify ID is properly set
    assert isinstance(message.id, uuid.UUID)

    # Verify timestamp is set
    assert isinstance(message.created_at, datetime)

    # Verify optional field defaults to None
    assert message.metadata_json is None