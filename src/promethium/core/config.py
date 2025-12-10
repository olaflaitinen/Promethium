"""
Configuration module with optional pydantic-settings support.

For core library usage (pip install promethium-seismic), basic defaults are used.
For server deployment (pip install promethium-seismic[server]), pydantic-settings
provides full configuration from environment variables and .env files.
"""

from typing import List
from functools import lru_cache
from pathlib import Path
import os

# Try to import pydantic_settings, fall back to simple dataclass if not available
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_SETTINGS_AVAILABLE = True
except ImportError:
    PYDANTIC_SETTINGS_AVAILABLE = False
    BaseSettings = object
    SettingsConfigDict = None


if PYDANTIC_SETTINGS_AVAILABLE:
    class Settings(BaseSettings):
        """
        Centralized application configuration.
        Reads from environment variables and .env file.
        """
        APP_NAME: str = "Promethium"
        APP_VERSION: str = "1.0.4"
        DEBUG: bool = False
        
        # API
        API_HOST: str = "0.0.0.0"
        API_PORT: int = 8000
        API_PREFIX: str = "/api/v1"
        CORS_ORIGINS: List[str] = ["*"]

        # Database & Storage
        DATABASE_URL: str = "sqlite+aiosqlite:///./promethium.db"
        REDIS_URL: str = "redis://localhost:6379/0"
        DATA_STORAGE_PATH: Path = Path("./data")
        ARTIFACT_STORAGE_PATH: Path = Path("./artifacts")

        # Security
        SECRET_KEY: str = "dev_secret_key_change_me_in_prod"
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

        # ML Configuration
        DEFAULT_DEVICE: str = "auto"  # auto, cuda, or cpu
        PRECISION: str = "float32"

        # Worker
        CELERY_BROKER_URL: str = "redis://localhost:6379/0"
        CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
        CELERY_TASK_ALWAYS_EAGER: bool = True
        
        model_config = SettingsConfigDict(
            env_file=".env", 
            case_sensitive=True,
            extra="ignore"
        )
else:
    # Simple settings class for core library usage without pydantic-settings
    class Settings:
        """
        Basic settings for core library usage.
        For full configuration support, install with: pip install promethium-seismic[server]
        """
        def __init__(self):
            self.APP_NAME = "Promethium"
            self.APP_VERSION = "1.0.4"
            self.DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")
            
            self.API_HOST = "0.0.0.0"
            self.API_PORT = 8000
            self.API_PREFIX = "/api/v1"
            self.CORS_ORIGINS = ["*"]

            self.DATABASE_URL = "sqlite+aiosqlite:///./promethium.db"
            self.REDIS_URL = "redis://localhost:6379/0"
            self.DATA_STORAGE_PATH = Path("./data")
            self.ARTIFACT_STORAGE_PATH = Path("./artifacts")

            self.DEFAULT_DEVICE = os.environ.get("PROMETHIUM_DEVICE", "auto")
            self.PRECISION = "float32"

            self.CELERY_BROKER_URL = "redis://localhost:6379/0"
            self.CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
            self.CELERY_TASK_ALWAYS_EAGER = True


@lru_cache
def get_settings() -> Settings:
    return Settings()

# Module-level settings instance
settings = get_settings()


