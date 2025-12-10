"""
Job schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobBase(BaseModel):
    """Base job schema."""
    type: str = Field(..., max_length=100)
    dataset_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    model_id: Optional[int] = None
    experiment_id: Optional[int] = None
    algorithm: Optional[str] = None
    params: Dict[str, Any] = {}


class JobCreate(JobBase):
    """Job creation schema."""
    pass


class JobUpdate(BaseModel):
    """Job update schema (for canceling or updating metadata)."""
    status: Optional[str] = None
    error_message: Optional[str] = None


class JobRead(JobBase):
    """Job response schema."""
    id: str
    status: str
    result_path: Optional[str] = None
    logs_path: Optional[str] = None
    error_message: Optional[str] = None
    progress: int = 0
    metrics: Dict[str, Any] = {}
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobProgress(BaseModel):
    """WebSocket progress update schema."""
    job_id: str
    status: str
    progress: int
    metrics: Optional[Dict[str, Any]] = None
    logs: Optional[List[str]] = None
