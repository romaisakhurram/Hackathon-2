"""
Unit tests for the Conversation model.
Tests the Conversation model's attributes, validation, and basic functionality.
"""
import pytest
from datetime import datetime
from uuid import UUID
import uuid

from backend.src.models.conversation import Conversation


def test_conversation_creation_with_required_fields():
    """Test creating a conversation with only required fields."""
    user_id = "test_user_123"
    conversation = Conversation(
        user_id=user_id
    )

    # Verify the conversation was created with the correct user_id
    assert conversation.user_id == user_id

    # Verify that an ID was automatically generated
    assert isinstance(conversation.id, UUID)

    # Verify that timestamps were set
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_creation_with_optional_fields():
    """Test creating a conversation with optional fields."""
    user_id = "test_user_123"
    title = "Test Conversation Title"

    conversation = Conversation(
        user_id=user_id,
        title=title
    )

    assert conversation.user_id == user_id
    assert conversation.title == title
    assert isinstance(conversation.id, UUID)
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_timestamps_are_set_on_creation():
    """Test that created_at and updated_at are automatically set during creation."""
    user_id = "test_user_123"
    conversation = Conversation(user_id=user_id)

    # Both timestamps should be set during creation
    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_id_is_unique():
    """Test that each conversation gets a unique ID."""
    user_id = "test_user_123"

    conversation1 = Conversation(user_id=user_id)
    conversation2 = Conversation(user_id=user_id)

    # Each conversation should have a unique ID
    assert conversation1.id != conversation2.id
    assert isinstance(conversation1.id, UUID)
    assert isinstance(conversation2.id, UUID)


def test_conversation_user_id_cannot_be_none():
    """Test that creating a conversation without user_id raises an error."""
    # According to the model definition, user_id is required (nullable=False)
    with pytest.raises(TypeError):
        Conversation()  # Missing required user_id


def test_conversation_table_name():
    """Test that the conversation model has the correct table name."""
    # Verify the table name is set as expected
    conversation = Conversation(user_id="test")
    # The table name is set as __tablename__ in the model, but not directly accessible as an attribute
    # This test ensures the model is properly defined
    assert hasattr(Conversation, '__tablename__')
    assert Conversation.__tablename__ == "conversations"


def test_conversation_field_constraints():
    """Test that conversation fields have the expected constraints."""
    conversation = Conversation(user_id="test_user_123")

    # Verify user_id field properties
    assert conversation.user_id is not None
    assert isinstance(conversation.user_id, str)

    # Verify title can be None (optional)
    assert conversation.title is None  # Default value should be None if not provided

    # Verify ID is properly set
    assert isinstance(conversation.id, uuid.UUID)