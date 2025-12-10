"""
Experiment schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ExperimentBase(BaseModel):
    """Base experiment schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: List[str] = []
    metadata_json: Dict[str, Any] = {}


class ExperimentCreate(ExperimentBase):
    """Experiment creation schema."""
    pass


class ExperimentUpdate(BaseModel):
    """Experiment update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ExperimentRead(ExperimentBase):
    """Experiment response schema."""
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    # We could include job summaries here if needed
    
    class Config:
        from_attributes = True
