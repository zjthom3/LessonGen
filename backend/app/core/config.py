"""Application configuration settings."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic settings for the FastAPI application."""

    app_name: str = Field(default="LessonGen API", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    api_prefix: str = Field(default="/api", env="API_PREFIX")

    database_url: str = Field(
        default="postgresql+psycopg2://lessongen:lessongen@localhost:5432/lessongen",
        env="DATABASE_URL",
    )

    secret_key: str = Field(default="change_me", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60 * 24,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    backend_cors_origins: List[AnyHttpUrl] | List[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        env="BACKEND_CORS_ORIGINS",
    )

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings instance."""

    return Settings()


settings = get_settings()
