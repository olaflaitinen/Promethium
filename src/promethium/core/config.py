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
    DATABASE_URL: str = "sqlite+aiosqlite:///./promethium.db"
    
    # Redis (Optional in Local Mode)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage
    DATA_STORAGE_PATH: str = "./data"
    
    # Worker
    CELERY_BROKER_URL: str = "memory://"
    CELERY_RESULT_BACKEND: str = "db+sqlite:///./celery_results.db"
    CELERY_TASK_ALWAYS_EAGER: bool = True

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    return Settings()
