from typing import List

# region agent log
import json
import os
import sys
from time import time as _time
import importlib.util

try:
    _log_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "debug-bb96b9.log",
    )
    _spec = importlib.util.find_spec("pydantic_settings")
    with open(_log_path, "a", encoding="utf-8") as _f:
        _f.write(
            json.dumps(
                {
                    "sessionId": "bb96b9",
                    "runId": "pre-fix-pydantic",
                    "hypothesisId": "P1-P3",
                    "location": "config.py:before_pydantic_settings_import",
                    "message": "Checking availability of pydantic_settings",
                    "data": {
                        "cwd": os.getcwd(),
                        "sysPath": sys.path,
                        "has_pydantic_settings": _spec is not None,
                    },
                    "timestamp": int(_time() * 1000),
                }
            )
            + "\n"
        )
except Exception:
    # Logging failure should not break configuration import
    pass
# endregion

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

