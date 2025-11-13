from __future__ import annotations

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


def _split_csv(value: str) -> List[str]:
    """Helper function to split comma-separated values into a list."""
    if not value:
        return []
    parts = [p.strip() for p in value.split(",")]
    return [p for p in parts if p]


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    # -------------------------------------------------------------------------
    # Core settings
    # -------------------------------------------------------------------------
    ENVIRONMENT: str = Field(
        default=os.getenv("ENV", "development"),
        description="Application environment (e.g., development, staging, production)",
    )
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level for the application",
    )

    # -------------------------------------------------------------------------
    # Web / API settings
    # -------------------------------------------------------------------------
    CORS_ORIGINS_RAW: str = Field(
        default=os.getenv("CORS_ORIGINS", "*"),
        description="Comma-separated list of allowed CORS origins",
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Return allowed CORS origins as a list."""
        origins = _split_csv(self.CORS_ORIGINS_RAW)
        return origins or ["*"]

    SENTRY_DSN: Optional[str] = Field(
        default=os.getenv("SENTRY_DSN"),
        description="Sentry DSN for error tracking",
    )
    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        description="Sampling rate for Sentry traces",
    )

    # -------------------------------------------------------------------------
    # Database settings
    # -------------------------------------------------------------------------
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite:///./app.db"),
        description="SQLAlchemy database connection URL",
    )
    DB_POOL_SIZE: int = Field(
        default=int(os.getenv("DB_POOL_SIZE", "5")),
        description="Database connection pool size",
    )
    DB_MAX_OVERFLOW: int = Field(
        default=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        description="Maximum number of connections to overflow beyond pool size",
    )

    ENABLE_AUTO_CREATE_TABLES: bool = Field(
        default=os.getenv("AUTO_CREATE_TABLES", "false").lower()
        in ("1", "true", "yes"),
        description="Automatically create database tables if they don't exist",
    )

    # -------------------------------------------------------------------------
    # Redis / Celery settings
    # -------------------------------------------------------------------------
    REDIS_URL: str = Field(
        default=os.getenv("REDIS_URL", "redis://redis:6379/0"),
        description="Redis connection URL for Celery and caching",
    )

    # -------------------------------------------------------------------------
    # JWT / Authentication settings
    # -------------------------------------------------------------------------
    JWT_SECRET_KEY: str = Field(
        default=os.getenv("JWT_SECRET_KEY", "CHANGE_ME"),
        description="Secret key used for signing JWT tokens",
    )
    JWT_ALGORITHM: str = Field(
        default=os.getenv("JWT_ALGORITHM", "HS256"),
        description="Algorithm used for JWT encoding",
    )
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60")),
        description="Access token expiration time in minutes",
    )
    JWT_ISSUER: str = Field(
        default=os.getenv("JWT_ISSUER", "news-api"),
        description="JWT issuer name",
    )
    JWT_REFRESH_TOKEN_EXPIRES_MINUTES: int = Field(
        default=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_MINUTES", str(60 * 24 * 7))),
        description="Refresh token expiration time in minutes",
    )


# Initialize global settings instance
settings = Settings()
