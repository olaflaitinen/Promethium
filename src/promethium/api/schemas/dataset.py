"""
Dataset schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class UploadInitRequest(BaseModel):
    """Request to initialize chunked upload."""
    filename: str
    size_bytes: int
    chunk_size: int = 10 * 1024 * 1024  # 10MB default


class UploadInitResponse(BaseModel):
    """Response for upload initialization."""
    upload_id: str
    chunk_size: int


class UploadFinalizeRequest(BaseModel):
    """Request to finalize upload."""
    upload_id: str
    name: str
    format: str


class DatasetBase(BaseModel):
    """Base dataset schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)
    format: str = Field(..., max_length=50)
    metadata_json: Dict[str, Any] = {}


class DatasetCreate(DatasetBase):
    """Dataset creation schema."""
    pass


class DatasetUpdate(BaseModel):
    """Dataset update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)
    metadata_json: Optional[Dict[str, Any]] = None


class DatasetRead(DatasetBase):
    """Dataset response schema."""
    id: int
    file_path: str
    size_bytes: Optional[int] = None
    sample_rate: Optional[float] = None
    channels: Optional[int] = None
    owner_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
