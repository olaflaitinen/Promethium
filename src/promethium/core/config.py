from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings and configuration.
    """
    # Application
    APP_NAME: str = "Promethium"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/promethium"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage
    DATA_STORAGE_PATH: str = "/var/lib/promethium/data"
    
    # Worker
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    return Settings()
