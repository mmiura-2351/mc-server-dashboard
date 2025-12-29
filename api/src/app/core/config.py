"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://mcsd_user:password@localhost:5432/mcsd"

    # Security
    SECRET_KEY: str = "your-secret-key-min-32-characters-long-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # API
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()
