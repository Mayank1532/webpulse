"""Application configuration."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    anthropic_api_key: SecretStr = SecretStr("")
    claude_model: str = "claude-sonnet-4-5"
    claude_max_tokens: int = 1024
    claude_temperature: float = 0.0
    claude_timeout_seconds: float = 30.0

    webpulse_env: str = "development"
    webpulse_log_level: str = "INFO"

    web_timeout_seconds: float = 15.0
    web_max_response_bytes: int = 2_000_000
    web_max_redirects: int = 5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
