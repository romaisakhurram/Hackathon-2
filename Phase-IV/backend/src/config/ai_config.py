"""
Configuration module for AI agent settings.
Handles OpenRouter configuration and AI provider settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class AIConfig(BaseSettings):
    """
    Configuration settings for AI integration with OpenRouter.
    """
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra environment variables not defined here
    )

    # OpenRouter settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # Backend API settings
    backend_api_url: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")

    # Task operation timeouts
    mcp_tool_timeout: int = int(os.getenv("MCP_TOOL_TIMEOUT", "30"))  # seconds

    # AI confidence threshold
    intent_confidence_threshold: float = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.5"))

    # Conversation context window size
    conversation_context_window: int = int(os.getenv("CONVERSATION_CONTEXT_WINDOW", "10"))  # number of turns

    # Rate limiting for AI provider
    ai_rate_limit_requests: int = int(os.getenv("AI_RATE_LIMIT_REQUESTS", "10"))
    ai_rate_limit_window: int = int(os.getenv("AI_RATE_LIMIT_WINDOW", "60"))  # seconds


# Global instance
ai_config = AIConfig()