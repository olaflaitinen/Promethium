"""
Dataset model for seismic data registry.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from promethium.api.models.base import Base


class Dataset(Base):
    """
    Registry for seismic datasets.
    
    Attributes:
        id: Primary key.
        name: Human-readable dataset name.
        description: Optional description.
        file_path: Path to the data file on disk.
        format: File format (SEGY, SAC, miniSEED, HDF5, NPY).
        size_bytes: File size in bytes.
        sample_rate: Sample rate in Hz.
        channels: Number of channels/traces.
        metadata_json: Additional metadata as JSON.
        owner_id: Foreign key to users table.
        created_at: Upload timestamp.
    """
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    format: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sample_rate: Mapped[Optional[float]] = mapped_column(nullable=True)
    channels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="datasets")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="dataset")
    results: Mapped[List["Result"]] = relationship("Result", back_populates="dataset")

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name='{self.name}', format='{self.format}')>"
