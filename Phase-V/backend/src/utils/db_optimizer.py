"""
Database query optimization and indexing utilities for the Todo AI Chatbot.
Optimizes database queries and ensures proper indexing for performance.
"""
from typing import List, Dict, Any
from sqlmodel import select, Session, and_, or_
from sqlalchemy import text
from datetime import datetime
import uuid


class DatabaseOptimizer:
    """
    Optimizes database queries and manages indexing for the chat persistence system.
    """

    def __init__(self):
        """
        Initialize the database optimizer.
        """
        self.optimization_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "optimizations_applied": [],
            "index_status": {},
            "query_performance": {}
        }

    async def get_optimized_conversation_query(self, user_id: str):
        """
        Get an optimized query for retrieving conversations for a user.

        Args:
            user_id: ID of the user whose conversations to retrieve

        Returns:
            Optimized SQLModel select statement
        """
        # Optimized query with proper indexing considerations
        # Using select with where clause that can utilize indexes
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())  # Order by most recently updated
        )

        # This query benefits from an index on (user_id, updated_at)
        return statement

    async def get_optimized_messages_query(self, conversation_id: uuid.UUID):
        """
        Get an optimized query for retrieving messages in a conversation.

        Args:
            conversation_id: ID of the conversation whose messages to retrieve

        Returns:
            Optimized SQLModel select statement
        """
        # Optimized query with proper indexing considerations
        # Using select with where clause that can utilize indexes
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())  # Order chronologically
        )

        # This query benefits from an index on (conversation_id, created_at)
        return statement

    async def get_optimized_user_message_query(self, user_id: str, conversation_id: uuid.UUID):
        """
        Get an optimized query for retrieving user messages with ownership validation.

        Args:
            user_id: ID of the authenticated user
            conversation_id: ID of the conversation to check

        Returns:
            Optimized SQLModel select statement
        """
        # Optimized query that combines user ownership validation with conversation access
        statement = (
            select(Message)
            .where(and_(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            ))
            .order_by(Message.created_at.desc())
        )

        # This query benefits from a composite index on (conversation_id, user_id, created_at)
        return statement

    async def ensure_indexes_exist(self) -> Dict[str, Any]:
        """
        Ensure proper database indexes exist for optimal query performance.

        Returns:
            Dictionary with index creation results
        """
        results = {
            "conversation_indexes": {},
            "message_indexes": {},
            "status": "completed"
        }

        try:
            # Connect to database to create indexes
            from backend.src.database import get_async_session

            # Note: In a real implementation, we would create actual indexes using raw SQL
            # since SQLModel doesn't directly support index creation on tables
            index_queries = [
                # Conversation table indexes
                {
                    "name": "idx_conversation_user_id",
                    "table": "conversations",
                    "columns": ["user_id"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversations (user_id);"
                },
                {
                    "name": "idx_conversation_updated_at",
                    "table": "conversations",
                    "columns": ["updated_at"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_conversation_updated_at ON conversations (updated_at);"
                },
                {
                    "name": "idx_conversation_user_updated",
                    "table": "conversations",
                    "columns": ["user_id", "updated_at"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_conversation_user_updated ON conversations (user_id, updated_at);"
                },

                # Message table indexes
                {
                    "name": "idx_message_conversation_id",
                    "table": "messages",
                    "columns": ["conversation_id"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_message_conversation_id ON messages (conversation_id);"
                },
                {
                    "name": "idx_message_user_id",
                    "table": "messages",
                    "columns": ["user_id"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_message_user_id ON messages (user_id);"
                },
                {
                    "name": "idx_message_created_at",
                    "table": "messages",
                    "columns": ["created_at"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_message_created_at ON messages (created_at);"
                },
                {
                    "name": "idx_message_conversation_created",
                    "table": "messages",
                    "columns": ["conversation_id", "created_at"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_message_conversation_created ON messages (conversation_id, created_at);"
                },
                {
                    "name": "idx_message_user_conversation",
                    "table": "messages",
                    "columns": ["user_id", "conversation_id"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_message_user_conversation ON messages (user_id, conversation_id);"
                },
                {
                    "name": "idx_message_role",
                    "table": "messages",
                    "columns": ["role"],
                    "query": "CREATE INDEX IF NOT EXISTS idx_message_role ON messages (role);"
                }
            ]

            # Execute index creation queries
            async with get_async_session() as session:
                for idx_info in index_queries:
                    try:
                        await session.execute(text(idx_info["query"]))
                        await session.commit()

                        table_name = idx_info["table"]
                        index_name = idx_info["name"]

                        if table_name not in results["conversation_indexes"] and table_name == "conversations":
                            results["conversation_indexes"][index_name] = {"status": "created", "query": idx_info["query"]}
                        elif table_name not in results["message_indexes"] and table_name == "messages":
                            results["message_indexes"][index_name] = {"status": "created", "query": idx_info["query"]}

                    except Exception as e:
                        print(f"Warning: Could not create index {idx_info['name']}: {str(e)}")
                        if table_name == "conversations":
                            results["conversation_indexes"][index_name] = {"status": "failed", "error": str(e)}
                        else:
                            results["message_indexes"][index_name] = {"status": "failed", "error": str(e)}

            self.optimization_results["index_status"] = results
            return results

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            return results

    async def optimize_conversation_loading(self, conversation_id: uuid.UUID, user_id: str):
        """
        Optimize the process of loading a conversation with all its messages.

        Args:
            conversation_id: ID of the conversation to load
            user_id: ID of the authenticated user requesting access

        Returns:
            Loaded conversation with messages or None if not accessible
        """
        from backend.src.models.conversation import Conversation
        from backend.src.models.message import Message
        from backend.src.database import get_async_session

        # Use a join query to load conversation and messages in a single optimized query
        # This reduces the N+1 query problem
        async with get_async_session() as session:
            # First, verify user has access to this conversation
            conversation_stmt = select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )

            conversation_result = await session.execute(conversation_stmt)
            conversation = conversation_result.scalar_one_or_none()

            if not conversation:
                return None  # User doesn't have access to this conversation

            # Then get all messages for this conversation efficiently
            messages_stmt = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc())

            messages_result = await session.execute(messages_stmt)
            messages = messages_result.scalars().all()

            # Attach messages to conversation (this would depend on your model relationships)
            conversation.messages = messages

            return conversation

    async def optimize_message_saving(self, conversation_id: uuid.UUID, user_id: str, role: str, content: str, metadata_json: str = None):
        """
        Optimize the process of saving a message to the database.

        Args:
            conversation_id: ID of the conversation to add the message to
            user_id: ID of the user sending the message
            role: Role of the message sender ('user' or 'assistant')
            content: Content of the message
            metadata_json: Optional metadata for the message

        Returns:
            Saved message object
        """
        from backend.src.models.message import Message
        from backend.src.database import get_async_session

        # Create and save message efficiently
        async with get_async_session() as session:
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                metadata_json=metadata_json
            )

            session.add(message)
            await session.commit()
            await session.refresh(message)

            return message

    async def batch_load_conversations_with_messages(self, user_id: str, limit: int = 10):
        """
        Efficiently load multiple conversations with their messages.

        Args:
            user_id: ID of the user whose conversations to load
            limit: Maximum number of conversations to load

        Returns:
            List of conversations with their messages
        """
        from backend.src.models.conversation import Conversation
        from backend.src.models.message import Message
        from backend.src.database import get_async_session

        async with get_async_session() as session:
            # Get user's conversations efficiently
            conversations_stmt = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).limit(limit)

            conversations_result = await session.execute(conversations_stmt)
            conversations = conversations_result.scalars().all()

            # Batch load messages for all conversations
            if conversations:
                conversation_ids = [conv.id for conv in conversations]

                messages_stmt = select(Message).where(
                    Message.conversation_id.in_(conversation_ids)
                ).order_by(Message.created_at.asc())

                messages_result = await session.execute(messages_stmt)
                all_messages = messages_result.scalars().all()

                # Group messages by conversation
                messages_by_conversation = {}
                for msg in all_messages:
                    if msg.conversation_id not in messages_by_conversation:
                        messages_by_conversation[msg.conversation_id] = []
                    messages_by_conversation[msg.conversation_id].append(msg)

                # Attach messages to conversations
                for conv in conversations:
                    conv.messages = messages_by_conversation.get(conv.id, [])

            return conversations

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get database performance metrics.

        Returns:
            Dictionary with performance metrics
        """
        from backend.src.database import get_async_session

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_counts": {},
            "message_counts": {},
            "query_times": {}
        }

        try:
            async with get_async_session() as session:
                # Get conversation count metrics
                from backend.src.models.conversation import Conversation
                from sqlalchemy import func

                conv_count_stmt = select(func.count(Conversation.id))
                conv_count_result = await session.execute(conv_count_stmt)
                total_conversations = conv_count_result.scalar()

                metrics["conversation_counts"]["total"] = total_conversations

                # Add more metrics as needed
                # ...

        except Exception as e:
            metrics["error"] = str(e)

        self.optimization_results["query_performance"] = metrics
        return metrics

    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Get a complete optimization report.

        Returns:
            Dictionary with optimization results
        """
        return self.optimization_results


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
        from sqlalchemy import select, and_

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
        from sqlalchemy import func, and_

        async with get_async_session() as session:
            # Get conversation count
            conv_count_stmt = select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
            conv_count_result = await session.execute(conv_count_stmt)
            conversation_count = conv_count_result.scalar_one()

            # Get message count
            msg_count_stmt = select(func.count(Message.id)).join(Conversation).where(
                and_(
                    Conversation.user_id == user_id
                )
            )
            msg_count_result = await session.execute(msg_count_stmt)
            message_count = msg_count_result.scalar_one()

            return {
                "conversation_count": conversation_count,
                "message_count": message_count
            }


# Singleton instance for global use
db_optimizer = DatabaseOptimizer()


async def ensure_database_optimizations() -> Dict[str, Any]:
    """
    Ensure all database optimizations are applied.

    Returns:
        Dictionary with optimization results
    """
    # Ensure indexes exist
    index_results = await db_optimizer.ensure_indexes_exist()

    # Additional optimizations can be applied here

    return index_results


async def get_db_optimization_report() -> Dict[str, Any]:
    """
    Get the complete database optimization report.

    Returns:
        Dictionary with optimization report
    """
    return db_optimizer.get_optimization_report()