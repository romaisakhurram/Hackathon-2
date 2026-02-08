"""
Query optimization utilities for the Todo AI Chatbot.
Provides optimized database queries for the chat persistence system.
"""
from typing import List, Dict, Any
from sqlmodel import select
from sqlalchemy import and_, func
from datetime import datetime
import uuid


class QueryOptimizer:
    """
    Provides utilities for optimizing specific queries.
    """

    @staticmethod
    async def optimize_user_conversation_access(user_id: str, conversation_id: uuid.UUID):
        """
        Optimize query for checking if a user has access to a specific conversation.

        Args:
            user_id: ID of the user requesting access
            conversation_id: ID of the conversation to check

        Returns:
            Boolean indicating if user has access
        """
        from backend.src.models.conversation import Conversation
        from backend.src.database import get_async_session

        async with get_async_session() as session:
            stmt = select(Conversation.id).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )

            result = await session.execute(stmt)
            has_access = result.scalar_one_or_none() is not None

            return has_access

    @staticmethod
    async def optimize_message_search(user_id: str, search_term: str, limit: int = 10):
        """
        Optimize query for searching messages by content.

        Args:
            user_id: ID of the user performing the search
            search_term: Term to search for in message content
            limit: Maximum number of results to return

        Returns:
            List of matching messages
        """
        from backend.src.models.message import Message
        from backend.src.models.conversation import Conversation
        from backend.src.database import get_async_session

        # Join messages with conversations to ensure user can only search their own messages
        async with get_async_session() as session:
            stmt = select(Message).join(Conversation).where(
                and_(
                    Conversation.user_id == user_id,
                    Message.content.ilike(f"%{search_term}%")  # Case-insensitive search
                )
            ).limit(limit)

            result = await session.execute(stmt)
            messages = result.scalars().all()

            return messages

    @staticmethod
    async def get_user_statistics(user_id: str) -> Dict[str, int]:
        """
        Get optimized statistics query for a user.

        Args:
            user_id: ID of the user to get statistics for

        Returns:
            Dictionary with user statistics
        """
        from backend.src.models.conversation import Conversation
        from backend.src.models.message import Message
        from backend.src.database import get_async_session

        async with get_async_session() as session:
            # Get conversation count
            conv_count_stmt = select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
            conv_count_result = await session.execute(conv_count_stmt)
            conversation_count = conv_count_result.scalar_one()

            # Get message count
            msg_count_stmt = select(func.count(Message.id)).join(Conversation).where(
                Conversation.user_id == user_id
            )
            msg_count_result = await session.execute(msg_count_stmt)
            message_count = msg_count_result.scalar_one()

            return {
                "conversation_count": conversation_count,
                "message_count": message_count
            }

    @staticmethod
    async def get_recent_conversations_with_message_count(user_id: str, limit: int = 10):
        """
        Get user's recent conversations with message counts in a single optimized query.

        Args:
            user_id: ID of the user whose conversations to get
            limit: Maximum number of conversations to return

        Returns:
            List of conversations with their message counts
        """
        from backend.src.models.conversation import Conversation
        from backend.src.models.message import Message
        from backend.src.database import get_async_session
        from sqlalchemy import func, desc

        async with get_async_session() as session:
            # Subquery to get message counts per conversation
            msg_count_subq = (
                select(Message.conversation_id, func.count(Message.id).label('message_count'))
                .group_by(Message.conversation_id)
                .subquery()
            )

            # Main query joining conversations with message counts
            stmt = (
                select(Conversation, msg_count_subq.c.message_count)
                .outerjoin(msg_count_subq, Conversation.id == msg_count_subq.c.conversation_id)
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.updated_at))
                .limit(limit)
            )

            result = await session.execute(stmt)
            rows = result.all()

            conversations_with_counts = []
            for row in rows:
                conversation = row.Conversation if hasattr(row, 'Conversation') else row[0]
                message_count = row.message_count if hasattr(row, 'message_count') else (row[1] if len(row) > 1 else 0)

                conversation.message_count = message_count
                conversations_with_counts.append(conversation)

            return conversations_with_counts

    @staticmethod
    async def get_conversation_summary(conversation_id: uuid.UUID, user_id: str):
        """
        Get a summary of a conversation with message counts and latest activity.

        Args:
            conversation_id: ID of the conversation to get summary for
            user_id: ID of the authenticated user (for ownership validation)

        Returns:
            Dictionary with conversation summary or None if not accessible
        """
        from backend.src.models.conversation import Conversation
        from backend.src.models.message import Message
        from backend.src.database import get_async_session
        from sqlalchemy import func, desc

        async with get_async_session() as session:
            # Verify user has access to this conversation
            conv_stmt = select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )

            conv_result = await session.execute(conv_stmt)
            conversation = conv_result.scalar_one_or_none()

            if not conversation:
                return None  # User doesn't have access

            # Get message count and latest message timestamp
            msg_stats_stmt = (
                select(
                    func.count(Message.id).label('message_count'),
                    func.max(Message.created_at).label('latest_message_at')
                )
                .where(Message.conversation_id == conversation_id)
            )

            msg_stats_result = await session.execute(msg_stats_stmt)
            msg_stats_row = msg_stats_result.first()

            message_count = msg_stats_row[0] if msg_stats_row else 0
            latest_message_at = msg_stats_row[1] if msg_stats_row and msg_stats_row[1] else conversation.created_at

            return {
                "id": conversation.id,
                "user_id": conversation.user_id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "message_count": message_count,
                "latest_message_at": latest_message_at
            }


# Singleton instance for global use
query_optimizer = QueryOptimizer()