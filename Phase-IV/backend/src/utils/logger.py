"""
Comprehensive logging utilities for the Todo AI Chatbot.
Provides structured logging for all system components.
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict
import sys


class StructuredLogger:
    """
    A structured logger that outputs logs in a consistent, machine-readable format.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize the structured logger.

        Args:
            name: Name of the logger (typically module name)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create formatter that outputs structured logs
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log_structured(self, level: int, event: str, **kwargs):
        """
        Log a structured message with additional context.

        Args:
            level: Logging level
            event: Event name/description
            **kwargs: Additional context to include in the log
        """
        # Add timestamp to the context
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **kwargs
        }

        # Log the structured data as JSON
        self.logger.log(level, json.dumps(log_data))

    def info(self, event: str, **kwargs):
        """Log an info-level event with structured data."""
        self._log_structured(logging.INFO, event, **kwargs)

    def error(self, event: str, **kwargs):
        """Log an error-level event with structured data."""
        self._log_structured(logging.ERROR, event, **kwargs)

    def warning(self, event: str, **kwargs):
        """Log a warning-level event with structured data."""
        self._log_structured(logging.WARNING, event, **kwargs)

    def debug(self, event: str, **kwargs):
        """Log a debug-level event with structured data."""
        self._log_structured(logging.DEBUG, event, **kwargs)


# Global logger instances for different components
chat_logger = StructuredLogger("chat_api")
auth_logger = StructuredLogger("auth")
database_logger = StructuredLogger("database")
ai_agent_logger = StructuredLogger("ai_agent")
mcp_logger = StructuredLogger("mcp_tools")


def get_component_logger(component_name: str) -> StructuredLogger:
    """
    Get a logger instance for a specific component.

    Args:
        component_name: Name of the component (chat, auth, database, ai_agent, mcp)

    Returns:
        StructuredLogger instance for the component
    """
    loggers = {
        "chat": chat_logger,
        "auth": auth_logger,
        "database": database_logger,
        "ai_agent": ai_agent_logger,
        "mcp": mcp_logger
    }

    return loggers.get(component_name, StructuredLogger(component_name))


def log_api_request(
    user_id: str,
    endpoint: str,
    method: str,
    conversation_id: str = None,
    message_content: str = None
):
    """
    Log an API request with relevant context.

    Args:
        user_id: ID of the user making the request
        endpoint: API endpoint being accessed
        method: HTTP method (GET, POST, PUT, etc.)
        conversation_id: Associated conversation ID (if applicable)
        message_content: Message content being processed (if applicable)
    """
    chat_logger.info(
        "api_request",
        user_id=user_id,
        endpoint=endpoint,
        method=method,
        conversation_id=conversation_id,
        has_message=bool(message_content)
    )


def log_conversation_event(
    user_id: str,
    conversation_id: str,
    event_type: str,
    details: Dict[str, Any] = None
):
    """
    Log a conversation-related event.

    Args:
        user_id: ID of the user associated with the conversation
        conversation_id: ID of the conversation
        event_type: Type of event (created, accessed, updated, etc.)
        details: Additional details about the event
    """
    chat_logger.info(
        "conversation_event",
        user_id=user_id,
        conversation_id=conversation_id,
        event_type=event_type,
        details=details or {}
    )


def log_message_event(
    user_id: str,
    conversation_id: str,
    message_id: str,
    role: str,
    event_type: str,
    content_preview: str = None
):
    """
    Log a message-related event.

    Args:
        user_id: ID of the user who sent/received the message
        conversation_id: ID of the conversation containing the message
        message_id: ID of the message
        role: Role of the message sender (user, assistant)
        event_type: Type of event (saved, retrieved, processed, etc.)
        content_preview: First few characters of the message content (for debugging)
    """
    chat_logger.info(
        "message_event",
        user_id=user_id,
        conversation_id=conversation_id,
        message_id=message_id,
        role=role,
        event_type=event_type,
        content_preview=content_preview[:50] if content_preview else None
    )


def log_error(
    error_type: str,
    error_message: str,
    user_id: str = None,
    conversation_id: str = None,
    additional_context: Dict[str, Any] = None
):
    """
    Log an error with structured context.

    Args:
        error_type: Type/classification of the error
        error_message: Error message or description
        user_id: User ID associated with the error (if applicable)
        conversation_id: Conversation ID associated with the error (if applicable)
        additional_context: Additional context about the error
    """
    error_context = {
        "error_type": error_type,
        "error_message": error_message,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "additional_context": additional_context or {},
        "timestamp": datetime.utcnow().isoformat()
    }

    chat_logger.error("system_error", **error_context)


def log_auth_event(event_type: str, user_id: str = None, details: Dict[str, Any] = None):
    """
    Log an authentication-related event.

    Args:
        event_type: Type of auth event (login, token_validated, unauthorized_access, etc.)
        user_id: User ID associated with the event (if available)
        details: Additional details about the auth event
    """
    auth_logger.info(
        "auth_event",
        event_type=event_type,
        user_id=user_id,
        details=details or {}
    )


def log_database_operation(operation: str, table: str, user_id: str = None, success: bool = True):
    """
    Log a database operation with relevant context.

    Args:
        operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table being operated on
        user_id: User ID associated with the operation (if applicable)
        success: Whether the operation was successful
    """
    database_logger.info(
        "database_operation",
        operation=operation,
        table=table,
        user_id=user_id,
        success=success
    )