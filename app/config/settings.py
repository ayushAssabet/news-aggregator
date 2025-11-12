from __future__ import annotations

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


def _split_csv(value: str) -> List[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",")]
    return [p for p in parts if p]


class Settings(BaseSettings):
    # Core
    environment: str = Field(default=os.getenv("ENV", "development"))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))

    # Web/API
    cors_origins_raw: str = Field(default=os.getenv("CORS_ORIGINS", "*"))
    @property
    def cors_origins(self) -> List[str]:
        origins = _split_csv(self.cors_origins_raw)
        return origins or ["*"]

    sentry_dsn: Optional[str] = Field(default=os.getenv("SENTRY_DSN"))
    sentry_traces_sample_rate: float = Field(default=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")))

    # Database
    database_url: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./app.db"))
    db_pool_size: int = Field(default=int(os.getenv("DB_POOL_SIZE", "5")))
    db_max_overflow: int = Field(default=int(os.getenv("DB_MAX_OVERFLOW", "10")))

    # Feature flags / ops toggles
    enable_auto_create_tables: bool = Field(default=os.getenv("AUTO_CREATE_TABLES", "false").lower() in ("1", "true", "yes"))

    # Redis / Celery
    redis_url: str = Field(default=os.getenv("REDIS_URL", "redis://redis:6379/0"))

    # Auth / JWT
    jwt_secret_key: str = Field(default=os.getenv("JWT_SECRET_KEY", "CHANGE_ME"))
    jwt_algorithm: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_access_token_expires_minutes: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
    jwt_issuer: str = Field(default=os.getenv("JWT_ISSUER", "news-api"))
    jwt_refresh_token_expires_minutes: int = Field(
        default=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_MINUTES", str(60 * 24 * 7)))
    )


settings = Settings()
