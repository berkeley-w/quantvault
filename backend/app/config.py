from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    DATABASE_URL: str = "sqlite:///./quantvault.db"
    ALPHA_VANTAGE_API_KEY: str = ""
    FRONTEND_DIR: str = "../frontend"
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


def get_settings() -> Settings:
    """Return application settings instance."""

    return Settings()

