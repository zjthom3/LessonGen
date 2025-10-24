"""Application configuration settings."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import List, Sequence

from pydantic import AnyHttpUrl, Field, field_validator
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

    frontend_app_url: AnyHttpUrl | str = Field(
        default="http://localhost:5173", env="FRONTEND_APP_URL"
    )

    session_cookie_name: str = Field(default="lessongen_session", env="SESSION_COOKIE_NAME")
    session_cookie_max_age_seconds: int = Field(
        default=60 * 60 * 24 * 7, env="SESSION_COOKIE_MAX_AGE_SECONDS"
    )

    google_client_id: str = Field(default="GOOGLE_CLIENT_ID_PLACEHOLDER", env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(
        default="GOOGLE_CLIENT_SECRET_PLACEHOLDER", env="GOOGLE_CLIENT_SECRET"
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8000/auth/callback", env="GOOGLE_REDIRECT_URI"
    )
    google_allowed_domains: List[str] = Field(default_factory=list, env="GOOGLE_ALLOWED_DOMAINS")

    default_tenant_name: str = Field(default="Demo District", env="DEFAULT_TENANT_NAME")

    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    generation_prompt_template: str = Field(
        default="app/ai/prompts/lesson_v1.md", env="GENERATION_PROMPT_TEMPLATE"
    )

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> Sequence[str] | object:
        """Allow comma-separated strings for CORS origins."""

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("google_allowed_domains", mode="before")
    @classmethod
    def parse_allowed_domains(cls, value: object) -> Sequence[str] | object:
        """Normalize allowed domain list from env strings."""

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            cleaned = [entry.strip() for entry in value.split(",") if entry.strip()]
            return cleaned
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings instance."""

    return Settings()


settings = get_settings()
