"""
CallRevive AI — Application Configuration.

All settings are loaded from environment variables via pydantic-settings.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory (backend/)
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Core Application
    # ------------------------------------------------------------------ #
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "change-me-to-a-random-secret"

    # ------------------------------------------------------------------ #
    # Database (Neon PostgreSQL)
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/callrevive"
    DATABASE_SYNC_URL: str = "postgresql://user:password@localhost:5432/callrevive"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_ECHO: bool = False

    # ------------------------------------------------------------------ #
    # Redis (Upstash)
    # ------------------------------------------------------------------ #
    REDIS_URL: str = "redis://localhost:6379"

    # ------------------------------------------------------------------ #
    # Message Queue (CloudAMQP)
    # ------------------------------------------------------------------ #
    CLOUDAMQP_URL: str = "amqp://guest:guest@localhost:5672/"

    # ------------------------------------------------------------------ #
    # AI (Google Gemini)
    # ------------------------------------------------------------------ #
    GEMINI_API_KEY: str = ""
    GEMINI_FAST_MODEL: str = "gemini-2.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-2.5-pro"

    # ------------------------------------------------------------------ #
    # Twilio
    # ------------------------------------------------------------------ #
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""

    # ------------------------------------------------------------------ #
    # Storage (Backblaze B2)
    # ------------------------------------------------------------------ #
    BACKBLAZE_KEY_ID: str = ""
    BACKBLAZE_APPLICATION_KEY: str = ""
    BACKBLAZE_BUCKET_NAME: str = "callrevive-recordings"
    BACKBLAZE_BUCKET_ID: str = ""
    BACKBLAZE_ENDPOINT_URL: str = "https://s3.us-west-002.backblazeb2.com"

    # ------------------------------------------------------------------ #
    # Auth (JWT)
    # ------------------------------------------------------------------ #
    JWT_SECRET: str = "change-me-to-a-random-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------ #
    # URLs
    # ------------------------------------------------------------------ #
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # ------------------------------------------------------------------ #
    # Monitoring
    # ------------------------------------------------------------------ #
    PROMETHEUS_ENABLED: bool = True

    # ------------------------------------------------------------------ #
    # Currency Support
    # ------------------------------------------------------------------ #
    DEFAULT_CURRENCY: str = "INR"
    SUPPORTED_CURRENCIES: list[str] = [
        "INR", "USD", "EUR", "GBP", "AED", "SGD", "AUD", "CAD", "JPY",
    ]

    # ------------------------------------------------------------------ #
    # Computed / Derived
    # ------------------------------------------------------------------ #
    @property
    def cors_origins(self) -> list[str]:
        """Allowed CORS origins."""
        origins = []
        if self.FRONTEND_URL:
            # Support comma-separated URLs in FRONTEND_URL env var
            origins.extend([org.strip() for org in self.FRONTEND_URL.split(",") if org.strip()])
        if self.APP_DEBUG:
            origins.extend([
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:8000",
            ])
        # Deduplicate while preserving order
        return list(dict.fromkeys(origins))

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if "sslmode=" in v or "channel_binding=" in v:
            import urllib.parse as urlparse
            url_parts = list(urlparse.urlparse(v))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            query.pop("sslmode", None)
            query.pop("channel_binding", None)
            url_parts[4] = urlparse.urlencode(query)
            v = urlparse.urlunparse(url_parts)
        if not v.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError("DATABASE_URL must use asyncpg or aiosqlite driver")
        return v

    @field_validator("SUPPORTED_CURRENCIES")
    @classmethod
    def validate_currencies(cls, v: list[str]) -> list[str]:
        valid = {"INR", "USD", "EUR", "GBP", "AED", "SGD", "AUD", "CAD", "JPY", "CNY", "KRW"}
        for currency in v:
            if currency not in valid:
                raise ValueError(f"Unsupported currency: {currency}")
        return v

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        """Ensure production deployments have real secrets."""
        if self.is_production:
            defaults = {"change-me-to-a-random-secret", "change-me-to-a-random-jwt-secret"}
            if self.APP_SECRET_KEY in defaults or self.JWT_SECRET in defaults:
                raise ValueError(
                    "APP_SECRET_KEY and JWT_SECRET must be changed in production!"
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
