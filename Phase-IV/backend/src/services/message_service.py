"""
Message service for the Todo AI Chatbot.
Handles message persistence, retrieval, and atomic operations.
"""
import uuid
from typing import Optional, List
from datetime import datetime
from sqlmodel import select
from sqlalchemy import and_

from ..models.message import Message
from ..database import get_async_session, get_async_session_context
from ..utils.logger import log_message_event


class MessageService:
    """
    Service class for handling message-related operations.
    """

    def __init__(self):
        """
        Initialize the message service.
        """
        pass

    async def create_message(self, conversation_id: uuid.UUID, user_id: str, role: str, content: str, metadata_json: Optional[str] = None) -> Message:
        """
        Create a new message in the specified conversation.

        Args:
            conversation_id: The ID of the conversation to add the message to
            user_id: The ID of the user sending the message (sender)
            role: The role of the message sender ('user' or 'assistant')
            content: The content of the message
            metadata_json: Optional metadata for the message (e.g., tool calls, response details)

        Returns:
            The created Message object
        """
        async with get_async_session_context() as session:
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                metadata_json=metadata_json,
                created_at=datetime.utcnow()
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)

            # Log the message creation event
            log_message_event(
                user_id=user_id,
                conversation_id=str(conversation_id),
                message_id=str(message.id),
                role=role,
                event_type="created",
                content_preview=content[:50]
            )

            return message

    async def get_message_by_id(self, message_id: uuid.UUID, user_id: str) -> Optional[Message]:
        """
        Retrieve a message by its ID for the specified user.

        Args:
            message_id: The ID of the message to retrieve
            user_id: The ID of the user requesting the message

        Returns:
            The Message object if found and owned by the user, None otherwise
        """
        async with get_async_session_context() as session:
            # We need to join with Conversation to ensure user can only access messages in conversations they own
            from sqlmodel import select
            from sqlalchemy import join
            from ..models.conversation import Conversation

            statement = select(Message).join(Conversation).where(
                and_(
                    Message.id == message_id,
                    Conversation.user_id == user_id
                )
            )

            result = await session.execute(statement)
            message = result.scalar_one_or_none()

            if message:
                # Log the message access event
                log_message_event(
                    user_id=user_id,
                    conversation_id=str(message.conversation_id),
                    message_id=str(message.id),
                    role=message.role,
                    event_type="accessed"
                )

            return message

    async def get_messages_by_conversation(self, conversation_id: uuid.UUID) -> List[Message]:
        """
        Retrieve all messages for the specified conversation.

        Args:
            conversation_id: The ID of the conversation whose messages to retrieve

        Returns:
            List of Message objects in the conversation
        """
        async with get_async_session_context() as session:
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc())

            result = await session.execute(statement)
            messages = result.scalars().all()

            return messages

    async def get_messages_by_conversation_and_user(self, conversation_id: uuid.UUID, user_id: str) -> Optional[List[Message]]:
        """
        Retrieve all messages for a conversation if the user has access to it.

        Args:
            conversation_id: The ID of the conversation whose messages to retrieve
            user_id: The ID of the user requesting the messages

        Returns:
            List of Message objects if user has access to the conversation, None otherwise
        """
        from .conversation_service import ConversationService  # Import to avoid circular dependency
        conversation_service = ConversationService()

        # Verify user owns the conversation before allowing message access
        if not await conversation_service.validate_conversation_ownership(conversation_id, user_id):
            return None

        return await self.get_messages_by_conversation(conversation_id)

    async def update_message_content(self, message_id: uuid.UUID, user_id: str, new_content: str) -> Optional[Message]:
        """
        Update the content of a message if the user owns it.

        Args:
            message_id: The ID of the message to update
            user_id: The ID of the user requesting the update
            new_content: The new content for the message

        Returns:
            The updated Message object if successful, None if user doesn't own the message
        """
        async with get_async_session_context() as session:
            message = await self.get_message_by_id(message_id, user_id)
            if message:
                message.content = new_content
                message.updated_at = datetime.utcnow()

                session.add(message)
                await session.commit()
                await session.refresh(message)

                # Log the message update event
                log_message_event(
                    user_id=user_id,
                    conversation_id=str(message.conversation_id),
                    message_id=str(message.id),
                    role=message.role,
                    event_type="updated",
                    content_preview=new_content[:50]
                )

                return message
            return None

    async def delete_message(self, message_id: uuid.UUID, user_id: str) -> bool:
        """
        Delete a message if the user owns it.

        Args:
            message_id: The ID of the message to delete
            user_id: The ID of the user requesting the deletion

        Returns:
            True if the message was deleted, False if user doesn't own the message
        """
        async with get_async_session_context() as session:
            message = await self.get_message_by_id(message_id, user_id)
            if message:
                await session.delete(message)
                await session.commit()

                # Log the message deletion event
                log_message_event(
                    user_id=user_id,
                    conversation_id=str(message.conversation_id),
                    message_id=str(message.id),
                    role=message.role,
                    event_type="deleted"
                )

                return True
            return False

    async def delete_messages_by_conversation(self, conversation_id: uuid.UUID, user_id: str) -> bool:
        """
        Delete all messages in a conversation if the user owns it.

        Args:
            conversation_id: The ID of the conversation whose messages to delete
            user_id: The ID of the user requesting the deletion

        Returns:
            True if messages were deleted, False if user doesn't own the conversation
        """
        from .conversation_service import ConversationService  # Import to avoid circular dependency
        conversation_service = ConversationService()

        # Verify user owns the conversation before allowing message deletion
        if not await conversation_service.validate_conversation_ownership(conversation_id, user_id):
            return False

        async with get_async_session_context() as session:
            # Get all messages in the conversation
            messages = await self.get_messages_by_conversation(conversation_id)

            for message in messages:
                await session.delete(message)

            await session.commit()

            # Log the bulk message deletion event
            log_message_event(
                user_id=user_id,
                conversation_id=str(conversation_id),
                message_id="bulk_delete",
                role="system",
                event_type="deleted_all",
                content_preview=f"Deleted {len(messages)} messages"
            )

            return True

    async def save_user_message(self, conversation_id: uuid.UUID, user_id: str, content: str) -> Message:
        """
        Save a user message to the database with atomic operation.

        Args:
            conversation_id: The ID of the conversation to save the message to
            user_id: The ID of the user sending the message
            content: The content of the user message

        Returns:
            The saved Message object
        """
        return await self.create_message(conversation_id, user_id, "user", content)

    async def save_assistant_message(self, conversation_id: uuid.UUID, user_id: str, content: str, metadata_json: Optional[str] = None) -> Message:
        """
        Save an AI assistant message to the database with atomic operation.

        Args:
            conversation_id: The ID of the conversation to save the message to
            user_id: The ID of the user the message is for (AI responses are for users)
            content: The content of the AI assistant message
            metadata_json: Optional metadata containing tool calls or other AI response details

        Returns:
            The saved Message object
        """
        return await self.create_message(conversation_id, "ai_agent", "assistant", content, metadata_json)

    async def get_recent_messages(self, user_id: str, limit: int = 10) -> List[Message]:
        """
        Retrieve the most recent messages for the specified user.

        Args:
            user_id: The ID of the user whose messages to retrieve
            limit: Maximum number of messages to return (default: 10)

        Returns:
            List of the most recent Message objects for the user
        """
        async with get_async_session_context() as session:
            from ..models.conversation import Conversation

            # Join messages with conversations to ensure we only get messages from conversations owned by the user
            statement = (
                select(Message)
                .join(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )

            result = await session.execute(statement)
            messages = result.scalars().all()

            return messages