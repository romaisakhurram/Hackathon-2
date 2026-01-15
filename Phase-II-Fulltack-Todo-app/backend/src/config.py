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

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()