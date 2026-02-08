from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    database_url: str
    better_auth_secret: str
    better_auth_url: str
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = False

    # AI Configuration
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1/"
    openai_model: str = "mistralai/mistral-7b-instruct:free"

    # Additional AI settings
    backend_api_url: str = "http://localhost:8000"
    mcp_tool_timeout: int = 30
    intent_confidence_threshold: float = 0.8
    conversation_context_window: int = 10
    ai_rate_limit_requests: int = 10
    ai_rate_limit_window: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()