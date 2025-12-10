"""
Result model for storing job outputs.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from promethium.api.models.base import Base


class Result(Base):
    """
    Result storage for completed jobs.
    
    Attributes:
        id: Primary key.
        job_id: Foreign key to jobs table.
        dataset_id: Foreign key to datasets table.
        model_id: Foreign key to models table.
        result_path: Path to result file (HDF5, NPY, etc.).
        metrics: Computed metrics (SNR, MSE, SSIM, etc.).
        metadata_json: Additional result metadata.
        created_at: Creation timestamp.
    """
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("datasets.id"), nullable=True)
    model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("models.id"), nullable=True)
    result_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="results")
    dataset: Mapped[Optional["Dataset"]] = relationship("Dataset", back_populates="results")
    model: Mapped[Optional["MLModel"]] = relationship("MLModel", back_populates="results")

    def __repr__(self) -> str:
        return f"<Result(id={self.id}, job_id='{self.job_id}')>"
