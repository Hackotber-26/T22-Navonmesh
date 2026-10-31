import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "local-dev-secret-key-32-chars-minimum-scamshield-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database: SQLite fallback for zero-dependency local dev, Postgres for prod
    DATABASE_URL: str = "sqlite+aiosqlite:///./scamshield.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # Auth
    GOOGLE_CLIENT_ID: str = ""
    ADMIN_EMAILS: str = "admin@scamshield.org"

    # Versions
    MODEL_VERSION: str = "indicbert-v2-scam-v1"
    RULES_VERSION: str = "v1.0.0"

    # Security & limits
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    MAX_INPUT_CHARS: int = 5000
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def admin_emails_list(self) -> List[str]:
        return [email.strip().lower() for email in self.ADMIN_EMAILS.split(",") if email.strip()]

    # Convert sync driver URL for alembic if needed
    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("sqlite+aiosqlite://"):
            return url.replace("sqlite+aiosqlite://", "sqlite://")
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://")
        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

