"""
MLModel schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class MLModelBase(BaseModel):
    """Base ML model schema."""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., max_length=100)
    version: str = Field(default="1.0.0", max_length=50)
    description: Optional[str] = None
    config: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}


class MLModelCreate(MLModelBase):
    """ML model creation schema."""
    pass


class MLModelUpdate(BaseModel):
    """ML model update schema."""
    description: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class MLModelRead(MLModelBase):
    """ML model response schema."""
    id: int
    artifact_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
