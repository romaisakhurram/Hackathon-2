"""
Unit tests for the MessageService.
Tests the MessageService's functionality without external dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID
import uuid


from backend.src.models.message import Message
from backend.src.services.message_service import MessageService


@pytest.mark.asyncio
async def test_create_message():
    """Test creating a new message."""
    service = MessageService()

    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    role = "user"
    content = "This is a test message content."

    # Mock the database session
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.create_message(conversation_id, user_id, role, content)

        # Verify the message was created with the correct attributes
        assert result.conversation_id == conversation_id
        assert result.user_id == user_id
        assert result.role == role
        assert result.content == content
        assert isinstance(result.id, UUID)
        assert isinstance(result.created_at, datetime)

        # Verify session methods were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_message_with_metadata():
    """Test creating a message with metadata."""
    service = MessageService()

    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    role = "assistant"
    content = "This is an AI response message."
    metadata_json = '{"tool_calls": [{"name": "add_task", "params": {"title": "test"}}]}'

    # Mock the database session
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.create_message(conversation_id, user_id, role, content, metadata_json)

        # Verify the message was created with all attributes
        assert result.conversation_id == conversation_id
        assert result.user_id == user_id
        assert result.role == role
        assert result.content == content
        assert result.metadata_json == metadata_json
        assert isinstance(result.id, UUID)
        assert isinstance(result.created_at, datetime)


@pytest.mark.asyncio
async def test_get_message_by_id_success():
    """Test retrieving an existing message by ID."""
    service = MessageService()

    message_id = uuid.uuid4()
    user_id = "test_user_123"

    # Create a mock message to return
    mock_message = Message(
        id=message_id,
        conversation_id=uuid.uuid4(),
        user_id=user_id,
        role="user",
        content="Test message content"
    )

    # Mock the database session and execute method
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_message
    mock_session.execute.return_value = mock_result

    with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.get_message_by_id(message_id, user_id)

        # Verify the result is the expected message
        assert result == mock_message
        assert result.user_id == user_id


@pytest.mark.asyncio
async def test_get_message_by_id_not_found():
    """Test retrieving a message that doesn't exist."""
    service = MessageService()

    message_id = uuid.uuid4()
    user_id = "test_user_123"

    # Mock the database session to return None
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.get_message_by_id(message_id, user_id)

        # Should return None when message is not found
        assert result is None


@pytest.mark.asyncio
async def test_get_messages_by_conversation_success():
    """Test retrieving all messages for a conversation."""
    service = MessageService()

    conversation_id = uuid.uuid4()
    user_id = "test_user_123"

    # Create mock messages
    mock_message1 = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content="First message"
    )
    mock_message2 = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content="AI response"
    )
    mock_messages = [mock_message1, mock_message2]

    # Mock the database session and execute method
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_messages
    mock_session.execute.return_value = mock_result

    # Mock the validate_conversation_ownership method to return True
    with patch.object(service, 'validate_conversation_ownership', return_value=True):
        with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.get_messages_by_conversation(conversation_id, user_id)

            # Verify the result contains the expected messages
            assert len(result) == 2
            assert all(msg.conversation_id == conversation_id for msg in result)
            assert all(msg.user_id == user_id for msg in result)


@pytest.mark.asyncio
async def test_get_messages_by_conversation_unauthorized():
    """Test retrieving messages when user doesn't own the conversation."""
    service = MessageService()

    conversation_id = uuid.uuid4()
    user_id = "test_user_123"

    # Mock the validate_conversation_ownership method to return False
    with patch.object(service, 'validate_conversation_ownership', return_value=False):
        result = await service.get_messages_by_conversation(conversation_id, user_id)

        # Should return None when user doesn't own the conversation
        assert result is None


@pytest.mark.asyncio
async def test_update_message_content():
    """Test updating the content of a message."""
    service = MessageService()

    message_id = uuid.uuid4()
    user_id = "test_user_123"
    new_content = "Updated message content"

    # Create a mock message
    mock_message = Message(
        id=message_id,
        conversation_id=uuid.uuid4(),
        user_id=user_id,
        role="user",
        content="Original content"
    )

    # Mock the get_message_by_id method to return the mock message
    with patch.object(service, 'get_message_by_id', return_value=mock_message):
        # Mock the database session
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.update_message_content(message_id, user_id, new_content)

            # Verify the message was updated correctly
            assert result.content == new_content
            assert result.updated_at is not None
            assert isinstance(result.updated_at, datetime)


@pytest.mark.asyncio
async def test_update_message_content_unauthorized():
    """Test updating a message when user doesn't own it."""
    service = MessageService()

    message_id = uuid.uuid4()
    user_id = "test_user_123"
    new_content = "Updated content"

    # Mock the get_message_by_id method to return None (message not found/owned)
    with patch.object(service, 'get_message_by_id', return_value=None):
        result = await service.update_message_content(message_id, user_id, new_content)

        # Should return None when user doesn't own the message
        assert result is None


@pytest.mark.asyncio
async def test_delete_message_success():
    """Test successfully deleting a message."""
    service = MessageService()

    message_id = uuid.uuid4()
    user_id = "test_user_123"

    # Create a mock message
    mock_message = Message(
        id=message_id,
        conversation_id=uuid.uuid4(),
        user_id=user_id,
        role="user",
        content="Message to delete"
    )

    # Mock the get_message_by_id method to return the mock message
    with patch.object(service, 'get_message_by_id', return_value=mock_message):
        # Mock the database session
        mock_session = AsyncMock()
        mock_session.delete = MagicMock()
        mock_session.commit = AsyncMock()

        with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.delete_message(message_id, user_id)

            # Should return True on successful deletion
            assert result is True

            # Verify session methods were called
            mock_session.delete.assert_called_once_with(mock_message)
            mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_message_unauthorized():
    """Test deleting a message when user doesn't own it."""
    service = MessageService()

    message_id = uuid.uuid4()
    user_id = "test_user_123"

    # Mock the get_message_by_id method to return None (message not found/owned)
    with patch.object(service, 'get_message_by_id', return_value=None):
        # Mock the database session
        mock_session = AsyncMock()
        mock_session.delete = MagicMock()
        mock_session.commit = AsyncMock()

        with patch('backend.src.services.message_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.delete_message(message_id, user_id)

            # Should return False when user doesn't own the message
            assert result is False

            # Verify session methods were NOT called (no deletion occurred)
            mock_session.delete.assert_not_called()
            mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_save_user_message():
    """Test saving a user message."""
    service = MessageService()

    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    content = "User message content"

    # Mock the create_message method
    mock_created_message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=content
    )

    with patch.object(service, 'create_message', return_value=mock_created_message):
        result = await service.save_user_message(conversation_id, user_id, content)

        # Verify the message was created with correct attributes
        assert result.conversation_id == conversation_id
        assert result.user_id == user_id
        assert result.role == "user"
        assert result.content == content


@pytest.mark.asyncio
async def test_save_assistant_message():
    """Test saving an AI assistant message."""
    service = MessageService()

    conversation_id = uuid.uuid4()
    user_id = "test_user_123"
    content = "AI assistant response content"
    metadata_json = '{"tool_calls": [{"name": "list_tasks", "result": {"count": 3}}]}'

    # Mock the create_message method
    mock_created_message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        user_id=user_id,  # For AI responses, this would be the user the message is for
        role="assistant",
        content=content,
        metadata_json=metadata_json
    )

    with patch.object(service, 'create_message', return_value=mock_created_message):
        result = await service.save_assistant_message(conversation_id, user_id, content, metadata_json)

        # Verify the message was created with correct attributes
        assert result.conversation_id == conversation_id
        assert result.user_id == user_id
        assert result.role == "assistant"
        assert result.content == content
        assert result.metadata_json == metadata_json