"""
Conversation context management utility for the AI agent.
Manages conversation history with a 5-10 turn window as specified in requirements.
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
import uuid


class ConversationContextManager:
    """
    Manages conversation context with a limited window (5-10 turns) as specified in requirements.
    Provides methods to add, retrieve, and maintain conversation history for the AI agent.
    """

    def __init__(self, max_context_window: int = 10):
        """
        Initialize the conversation context manager.

        Args:
            max_context_window: Maximum number of conversation turns to maintain (default: 10)
        """
        self.max_context_window = max_context_window
        self.context_windows: Dict[UUID, List[Dict[str, Any]]] = {}

    def add_message_to_context(self, conversation_id: UUID, message: Dict[str, Any]):
        """
        Add a message to the conversation context window.

        Args:
            conversation_id: ID of the conversation to add the message to
            message: Message dictionary with role, content, and metadata
        """
        if conversation_id not in self.context_windows:
            self.context_windows[conversation_id] = []

        # Add timestamp to the message if not already present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.utcnow().isoformat()

        # Add the message to the context
        self.context_windows[conversation_id].append(message)

        # Maintain the context window size by removing older messages if needed
        if len(self.context_windows[conversation_id]) > self.max_context_window:
            # Keep only the most recent messages within the window
            self.context_windows[conversation_id] = self.context_windows[conversation_id][-self.max_context_window:]

    def get_context_window(self, conversation_id: UUID) -> List[Dict[str, Any]]:
        """
        Get the current context window for a conversation.

        Args:
            conversation_id: ID of the conversation to get context for

        Returns:
            List of messages in the current context window (most recent first)
        """
        return self.context_windows.get(conversation_id, [])

    def get_recent_messages(self, conversation_id: UUID, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent messages from a conversation context.

        Args:
            conversation_id: ID of the conversation to get messages from
            count: Number of recent messages to return (default: 5)

        Returns:
            List of most recent messages (up to the specified count)
        """
        context = self.get_context_window(conversation_id)
        return context[-count:] if len(context) >= count else context

    def clear_context(self, conversation_id: UUID):
        """
        Clear the context for a specific conversation.

        Args:
            conversation_id: ID of the conversation to clear context for
        """
        if conversation_id in self.context_windows:
            del self.context_windows[conversation_id]

    def create_new_conversation_context(self) -> UUID:
        """
        Create a new conversation context and return its ID.

        Returns:
            UUID of the new conversation context
        """
        conversation_id = uuid.uuid4()
        self.context_windows[conversation_id] = []
        return conversation_id

    def has_context(self, conversation_id: UUID) -> bool:
        """
        Check if a conversation has any context messages.

        Args:
            conversation_id: ID of the conversation to check

        Returns:
            True if conversation has context, False otherwise
        """
        return conversation_id in self.context_windows and len(self.context_windows[conversation_id]) > 0

    def get_context_size(self, conversation_id: UUID) -> int:
        """
        Get the current size of the context window for a conversation.

        Args:
            conversation_id: ID of the conversation to check

        Returns:
            Number of messages in the context window
        """
        return len(self.context_windows.get(conversation_id, []))

    def trim_context_if_needed(self, conversation_id: UUID):
        """
        Trim the context window if it exceeds the maximum size.

        Args:
            conversation_id: ID of the conversation to trim if needed
        """
        if conversation_id in self.context_windows:
            if len(self.context_windows[conversation_id]) > self.max_context_window:
                self.context_windows[conversation_id] = self.context_windows[conversation_id][-self.max_context_window:]


class GlobalContextManager:
    """
    Global singleton instance of the conversation context manager.
    """
    _instance: Optional['GlobalContextManager'] = None
    _lock = asyncio.Lock()

    def __init__(self):
        """
        Initialize the global context manager.
        """
        if GlobalContextManager._instance is not None:
            raise RuntimeError("GlobalContextManager is a singleton. Use get_instance() instead.")

        self.manager = ConversationContextManager(max_context_window=10)  # Default to 10 as per spec

    @classmethod
    async def get_instance(cls) -> 'GlobalContextManager':
        """
        Get the singleton instance of the context manager.

        Returns:
            GlobalContextManager instance
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = GlobalContextManager()
        return cls._instance

    def add_message(self, conversation_id: UUID, message: Dict[str, Any]):
        """
        Add a message to the conversation context.

        Args:
            conversation_id: ID of the conversation
            message: Message to add to context
        """
        self.manager.add_message_to_context(conversation_id, message)

    def get_context(self, conversation_id: UUID) -> List[Dict[str, Any]]:
        """
        Get the context for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of messages in the context window
        """
        return self.manager.get_context_window(conversation_id)

    def get_recent_messages(self, conversation_id: UUID, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent messages from a conversation.

        Args:
            conversation_id: ID of the conversation
            count: Number of recent messages to retrieve

        Returns:
            List of recent messages
        """
        return self.manager.get_recent_messages(conversation_id, count)

    def create_conversation(self) -> UUID:
        """
        Create a new conversation context.

        Returns:
            UUID of the new conversation
        """
        return self.manager.create_new_conversation_context()


# Global instance for easy access
conversation_context_manager = ConversationContextManager(max_context_window=10)


def get_conversation_context_manager() -> ConversationContextManager:
    """
    Get the conversation context manager instance.

    Returns:
        ConversationContextManager instance
    """
    return conversation_context_manager