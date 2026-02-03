"""
Unit tests for the ConversationService.
Tests the ConversationService's functionality without external dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID
import uuid
from sqlmodel import select
from sqlalchemy.exc import NoResultFound


from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from backend.src.services.conversation_service import ConversationService


@pytest.fixture
def conversation_service():
    """Fixture to create a conversation service instance for testing."""
    return ConversationService()


@pytest.mark.asyncio
async def test_create_conversation():
    """Test creating a new conversation."""
    user_id = "test_user_123"
    service = ConversationService()

    # Mock the database session
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.create_conversation(user_id)

        # Verify the conversation was created with the correct user_id
        assert result.user_id == user_id
        assert isinstance(result.id, UUID)
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

        # Verify session methods were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_conversation_by_id_success():
    """Test retrieving an existing conversation by ID."""
    user_id = "test_user_123"
    conversation_id = uuid.uuid4()
    service = ConversationService()

    # Create a mock conversation to return
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=user_id
    )

    # Mock the database session and execute method
    mock_session = AsyncMock()

    # Create a mock result object that has scalar_one_or_none
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_conversation
    mock_session.execute.return_value = mock_result

    with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.get_conversation_by_id(conversation_id, user_id)

        # Verify the result is the expected conversation
        assert result == mock_conversation
        assert result.user_id == user_id

        # Verify execute was called with the right statement
        mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_conversation_by_id_not_found():
    """Test retrieving a conversation that doesn't exist."""
    user_id = "test_user_123"
    conversation_id = uuid.uuid4()
    service = ConversationService()

    # Mock the database session to return None
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.get_conversation_by_id(conversation_id, user_id)

        # Should return None when conversation is not found
        assert result is None


@pytest.mark.asyncio
async def test_validate_conversation_ownership_true():
    """Test validating conversation ownership when user owns the conversation."""
    user_id = "test_user_123"
    conversation_id = uuid.uuid4()
    service = ConversationService()

    # Create a mock conversation owned by the user
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=user_id
    )

    # Mock the get_conversation_by_id method to return the mock conversation
    with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
        result = await service.validate_conversation_ownership(conversation_id, user_id)

        # Should return True when user owns the conversation
        assert result is True


@pytest.mark.asyncio
async def test_validate_conversation_ownership_false():
    """Test validating conversation ownership when user doesn't own the conversation."""
    user_id = "test_user_123"
    other_user_id = "other_user_456"
    conversation_id = uuid.uuid4()
    service = ConversationService()

    # Create a mock conversation owned by a different user
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=other_user_id
    )

    # Mock the get_conversation_by_id method to return the mock conversation
    with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
        result = await service.validate_conversation_ownership(conversation_id, user_id)

        # Should return False when user doesn't own the conversation
        assert result is False


@pytest.mark.asyncio
async def test_get_user_conversations():
    """Test retrieving all conversations for a specific user."""
    user_id = "test_user_123"
    service = ConversationService()

    # Create mock conversations
    mock_conversation1 = Conversation(id=uuid.uuid4(), user_id=user_id)
    mock_conversation2 = Conversation(id=uuid.uuid4(), user_id=user_id)
    mock_conversations = [mock_conversation1, mock_conversation2]

    # Mock the database session and execute method
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_conversations
    mock_session.execute.return_value = mock_result

    with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session

        result = await service.get_user_conversations(user_id)

        # Verify the result contains the expected conversations
        assert len(result) == 2
        assert all(conv.user_id == user_id for conv in result)


@pytest.mark.asyncio
async def test_update_conversation_title():
    """Test updating the title of a conversation."""
    user_id = "test_user_123"
    conversation_id = uuid.uuid4()
    new_title = "Updated Conversation Title"
    service = ConversationService()

    # Create a mock conversation
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Original Title"
    )

    # Mock the get_conversation_by_id method to return the mock conversation
    with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
        # Mock the database session
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.update_conversation_title(conversation_id, user_id, new_title)

            # Verify the conversation was updated correctly
            assert result.title == new_title
            assert result.updated_at is not None
            assert isinstance(result.updated_at, datetime)

            # Verify session methods were called
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_delete_conversation_success():
    """Test successfully deleting a conversation."""
    user_id = "test_user_123"
    conversation_id = uuid.uuid4()
    service = ConversationService()

    # Create a mock conversation
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=user_id
    )

    # Mock the get_conversation_by_id method to return the mock conversation
    with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
        # Mock the database session
        mock_session = AsyncMock()
        mock_session.delete = MagicMock()
        mock_session.commit = AsyncMock()

        with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.delete_conversation(conversation_id, user_id)

            # Should return True on successful deletion
            assert result is True

            # Verify session methods were called
            mock_session.delete.assert_called_once_with(mock_conversation)
            mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_conversation_unauthorized():
    """Test deleting a conversation when user doesn't own it."""
    user_id = "test_user_123"
    other_user_id = "other_user_456"
    conversation_id = uuid.uuid4()
    service = ConversationService()

    # Create a mock conversation owned by a different user
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=other_user_id
    )

    # Mock the get_conversation_by_id method to return the mock conversation
    with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
        # Mock the database session
        mock_session = AsyncMock()
        mock_session.delete = MagicMock()
        mock_session.commit = AsyncMock()

        with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.delete_conversation(conversation_id, user_id)

            # Should return False when user doesn't own the conversation
            assert result is False

            # Verify session methods were NOT called (no deletion occurred)
            mock_session.delete.assert_not_called()
            mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_conversation_messages():
    """Test retrieving all messages for a conversation."""
    user_id = "test_user_123"
    conversation_id = uuid.uuid4()
    service = ConversationService()

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
        with patch('backend.src.services.conversation_service.get_async_session') as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            result = await service.get_conversation_messages(conversation_id, user_id)

            # Verify the result contains the expected messages
            assert len(result) == 2
            assert all(msg.conversation_id == conversation_id for msg in result)
            assert all(msg.user_id == user_id for msg in result)


@pytest.mark.asyncio
async def test_get_conversation_messages_unauthorized():
    """Test retrieving messages when user doesn't own the conversation."""
    user_id = "test_user_123"
    conversation_id = uuid.uuid4()
    service = ConversationService()

    # Mock the validate_conversation_ownership method to return False
    with patch.object(service, 'validate_conversation_ownership', return_value=False):
        result = await service.get_conversation_messages(conversation_id, user_id)

        # Should return None when user doesn't own the conversation
        assert result is None