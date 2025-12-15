from __future__ import annotations

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

DEFAULT_LOCAL_CORS_ORIGINS = [
    "http://localhost:8000/",   
    "http://localhost:5173",
    "https://news-aggregator-frontend-delta.vercel.app/"
]


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
    ENVIRONMENT: str = Field(default=os.getenv("ENV", "development"))
    LOG_LEVEL: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))

    # Backward-compatible lowercase accessors
    @property
    def environment(self) -> str:
        return self.ENVIRONMENT

    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL

    # -------------------------------------------------------------------------
    # Web / API settings
    # -------------------------------------------------------------------------
    CORS_ORIGINS_RAW: str = Field(default=os.getenv("CORS_ORIGINS", ""))

    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = (self.CORS_ORIGINS_RAW or "").strip()
        if raw == "*":
            return ["*"]

        origins = _split_csv(raw)
        merged_origins = origins.copy()

        # Always allow common localhost origins for local development
        for origin in DEFAULT_LOCAL_CORS_ORIGINS:
            if origin not in merged_origins:
                merged_origins.append(origin)

        return merged_origins or DEFAULT_LOCAL_CORS_ORIGINS

    # Backward-compatible lowercase property
    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS

    SENTRY_DSN: Optional[str] = Field(default=os.getenv("SENTRY_DSN"))
    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    )

    @property
    def sentry_dsn(self) -> Optional[str]:
        return self.SENTRY_DSN

    @property
    def sentry_traces_sample_rate(self) -> float:
        return self.SENTRY_TRACES_SAMPLE_RATE

    # -------------------------------------------------------------------------
    # Database settings
    # -------------------------------------------------------------------------
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./app.db"))
    DB_POOL_SIZE: int = Field(default=int(os.getenv("DB_POOL_SIZE", "5")))
    DB_MAX_OVERFLOW: int = Field(default=int(os.getenv("DB_MAX_OVERFLOW", "10")))

    ENABLE_AUTO_CREATE_TABLES: bool = Field(
        default=os.getenv("AUTO_CREATE_TABLES", "false").lower() in ("1", "true", "yes")
    )

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def db_pool_size(self) -> int:
        return self.DB_POOL_SIZE

    @property
    def db_max_overflow(self) -> int:
        return self.DB_MAX_OVERFLOW

    @property
    def enable_auto_create_tables(self) -> bool:
        return self.ENABLE_AUTO_CREATE_TABLES

    # -------------------------------------------------------------------------
    # Redis / Celery settings
    # -------------------------------------------------------------------------
    REDIS_URL: str = Field(default=os.getenv("REDIS_URL", "redis://redis:6379/0"))
    SCRAPE_SCHEDULE_SECONDS: float = Field(default=float(os.getenv("SCRAPE_SCHEDULE_SECONDS", "360")))

    @property
    def redis_url(self) -> str:
        return self.REDIS_URL

    @property
    def scrape_schedule_seconds(self) -> float:
        return self.SCRAPE_SCHEDULE_SECONDS

    # -------------------------------------------------------------------------
    # JWT / Authentication settings
    # -------------------------------------------------------------------------
    JWT_SECRET_KEY: str = Field(default=os.getenv("JWT_SECRET_KEY", "CHANGE_ME"))
    JWT_ALGORITHM: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
    JWT_ISSUER: str = Field(default=os.getenv("JWT_ISSUER", "news-api"))
    JWT_REFRESH_TOKEN_EXPIRES_MINUTES: int = Field(
        default=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_MINUTES", str(60 * 24 * 7)))
    )

    @property
    def jwt_secret_key(self) -> str:
        return self.JWT_SECRET_KEY

    @property
    def jwt_algorithm(self) -> str:
        return self.JWT_ALGORITHM

    @property
    def jwt_access_token_expires_minutes(self) -> int:
        return self.JWT_ACCESS_TOKEN_EXPIRES_MINUTES

    @property
    def jwt_refresh_token_expires_minutes(self) -> int:
        return self.JWT_REFRESH_TOKEN_EXPIRES_MINUTES

    @property
    def jwt_issuer(self) -> str:
        return self.JWT_ISSUER

    # -------------------------------------------------------------------------
    # Gemini / Google and summarization settings
    # -------------------------------------------------------------------------
    GOOGLE_API_KEY: Optional[str] = Field(default=os.getenv("GOOGLE_API_KEY"))
    GEMINI_API_KEY: Optional[str] = Field(default=os.getenv("GEMINI_API_KEY"))
    GEMINI_EMBEDDING_MODEL: str = Field(default=os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004"))
    TAVILY_API_KEY: Optional[str] = Field(default=os.getenv("TAVILY_API_KEY"))

    SUMMARY_RETRY_ATTEMPTS: int = Field(default=int(os.getenv("SUMMARY_RETRY_ATTEMPTS", "3")))
    SUMMARY_RETRY_BACKOFF_SECONDS: float = Field(default=float(os.getenv("SUMMARY_RETRY_BACKOFF_SECONDS", "1.0")))
    SUMMARY_RETRY_MAX_BACKOFF_SECONDS: float = Field(default=float(os.getenv("SUMMARY_RETRY_MAX_BACKOFF_SECONDS", "8.0")))
    SUMMARY_RETRY_JITTER: bool = Field(default=os.getenv("SUMMARY_RETRY_JITTER", "true").lower() in ("1", "true", "yes"))

    @property
    def google_api_key(self) -> Optional[str]:
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY

    @property
    def gemini_api_key(self) -> Optional[str]:
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY

    @property
    def tavily_api_key(self) -> Optional[str]:
        return self.TAVILY_API_KEY

    @property
    def gemini_embedding_model(self) -> str:
        return self.GEMINI_EMBEDDING_MODEL

    @property
    def summary_retry_attempts(self) -> int:
        return self.SUMMARY_RETRY_ATTEMPTS

    @property
    def summary_retry_backoff_seconds(self) -> float:
        return self.SUMMARY_RETRY_BACKOFF_SECONDS

    @property
    def summary_retry_max_backoff_seconds(self) -> float:
        return self.SUMMARY_RETRY_MAX_BACKOFF_SECONDS

    @property
    def summary_retry_jitter(self) -> bool:
        return self.SUMMARY_RETRY_JITTER


# Initialize global settings instance
settings = Settings()
