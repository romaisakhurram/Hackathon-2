"""
Conversation service for the Todo AI Chatbot.
Handles conversation creation, loading, and management operations.
"""
import uuid
from typing import Optional, List
from datetime import datetime
from sqlmodel import select
from sqlalchemy import and_

from ..models.conversation import Conversation
from ..database import get_async_session, get_async_session_context
from ..utils.logger import log_conversation_event


class ConversationService:
    """
    Service class for handling conversation-related operations.
    """

    def __init__(self):
        """
        Initialize the conversation service.
        """
        pass

    async def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for the specified user.

        Args:
            user_id: The ID of the user creating the conversation
            title: Optional title for the conversation

        Returns:
            The created Conversation object
        """
        async with get_async_session_context() as session:
            conversation = Conversation(
                user_id=user_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

            # Log the conversation creation event
            log_conversation_event(
                user_id=user_id,
                conversation_id=str(conversation.id),
                event_type="created",
                details={"title": title}
            )

            return conversation

    async def get_conversation_by_id(self, conversation_id: uuid.UUID, user_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID for the specified user.

        Args:
            conversation_id: The ID of the conversation to retrieve
            user_id: The ID of the user requesting the conversation

        Returns:
            The Conversation object if found and owned by the user, None otherwise
        """
        async with get_async_session_context() as session:
            statement = select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            result = await session.execute(statement)
            conversation = result.scalar_one_or_none()

            if conversation:
                # Log the conversation access event
                log_conversation_event(
                    user_id=user_id,
                    conversation_id=str(conversation.id),
                    event_type="accessed"
                )

            return conversation

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """
        Retrieve all conversations for the specified user.

        Args:
            user_id: The ID of the user whose conversations to retrieve

        Returns:
            List of Conversation objects belonging to the user
        """
        async with get_async_session_context() as session:
            statement = select(Conversation).where(Conversation.user_id == user_id)
            result = await session.execute(statement)
            conversations = result.scalars().all()

            return conversations

    async def validate_conversation_ownership(self, conversation_id: uuid.UUID, user_id: str) -> bool:
        """
        Validate that the specified user owns the conversation.

        Args:
            conversation_id: The ID of the conversation to validate
            user_id: The ID of the user to validate ownership for

        Returns:
            True if the user owns the conversation, False otherwise
        """
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        return conversation is not None

    async def update_conversation_title(self, conversation_id: uuid.UUID, user_id: str, new_title: str) -> Optional[Conversation]:
        """
        Update the title of a conversation if the user owns it.

        Args:
            conversation_id: The ID of the conversation to update
            user_id: The ID of the user requesting the update
            new_title: The new title for the conversation

        Returns:
            The updated Conversation object if successful, None if user doesn't own the conversation
        """
        async with get_async_session_context() as session:
            conversation = await self.get_conversation_by_id(conversation_id, user_id)
            if conversation:
                conversation.title = new_title
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                await session.commit()
                await session.refresh(conversation)

                # Log the conversation update event
                log_conversation_event(
                    user_id=user_id,
                    conversation_id=str(conversation.id),
                    event_type="updated",
                    details={"title_change": True}
                )

                return conversation
            return None

    async def delete_conversation(self, conversation_id: uuid.UUID, user_id: str) -> bool:
        """
        Delete a conversation if the user owns it.

        Args:
            conversation_id: The ID of the conversation to delete
            user_id: The ID of the user requesting the deletion

        Returns:
            True if the conversation was deleted, False if user doesn't own the conversation
        """
        from .message_service import MessageService  # Import here to avoid circular dependency
        message_service = MessageService()

        # First delete all messages in the conversation
        await message_service.delete_messages_by_conversation(conversation_id, user_id)

        async with get_async_session_context() as session:
            conversation = await self.get_conversation_by_id(conversation_id, user_id)
            if conversation:
                await session.delete(conversation)
                await session.commit()

                # Log the conversation deletion event
                log_conversation_event(
                    user_id=user_id,
                    conversation_id=str(conversation_id),
                    event_type="deleted"
                )

                return True
            return False

    async def get_conversation_messages(self, conversation_id: uuid.UUID, user_id: str):
        """
        Retrieve all messages for a conversation if the user has access to it.

        Args:
            conversation_id: The ID of the conversation whose messages to retrieve
            user_id: The ID of the user requesting the messages

        Returns:
            List of Message objects if user has access to the conversation, None otherwise
        """
        from .message_service import MessageService  # Import here to avoid circular dependency
        message_service = MessageService()

        # Validate that user owns the conversation
        if not await self.validate_conversation_ownership(conversation_id, user_id):
            return None

        messages = await message_service.get_messages_by_conversation(conversation_id)
        return messages