import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))


@lru_cache
def get_settings() -> Settings:
    return Settings()

