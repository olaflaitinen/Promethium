"""
System schemas.
"""
from typing import Dict, Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """System health status."""
    status: str
    version: str
    database: str
    redis: str
    components: Dict[str, str]


class SystemInfo(BaseModel):
    """System information."""
    app_name: str
    version: str
    api_version: str
    environment: str
    debug: bool


class SystemStats(BaseModel):
    """System statistics."""
    total_users: int
    total_datasets: int
    total_jobs: int
    active_jobs: int
    total_experiments: int
