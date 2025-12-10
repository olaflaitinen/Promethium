from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class BenchmarkStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BenchmarkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None
    dataset_id: Optional[int] = None
    model_id: Optional[int] = None
    experiment_id: Optional[int] = None


class BenchmarkCreate(BenchmarkBase):
    pass


class BenchmarkUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class BenchmarkRead(BenchmarkBase):
    id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    metrics_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BenchmarkRun(BaseModel):
    """Request to execute a benchmark."""
    benchmark_id: int
    params: Optional[Dict[str, Any]] = None


class BenchmarkResult(BaseModel):
    """Benchmark execution result."""
    benchmark_id: int
    status: str
    metrics: Dict[str, Any]
    duration_seconds: float
