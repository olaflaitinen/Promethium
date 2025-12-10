"""
Job model for processing tasks.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from promethium.api.models.base import Base


class Job(Base):
    """
    Processing job record.
    
    Attributes:
        id: Primary key (UUID string).
        type: Job type (ingestion, pipeline_run, training, evaluation).
        status: Current status (queued, running, completed, failed, cancelled).
        dataset_id: Foreign key to datasets table.
        pipeline_id: Foreign key to pipelines table.
        model_id: Foreign key to models table.
        experiment_id: Foreign key to experiments table.
        params: Job parameters as JSON.
        result_path: Path to result file.
        logs_path: Path to logs file.
        error_message: Error message if failed.
        progress: Progress percentage (0-100).
        metrics: Computed metrics as JSON.
        created_at: Creation timestamp.
        started_at: Job start timestamp.
        completed_at: Completion timestamp.
    """
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[str] = mapped_column(String(100), default="pipeline_run", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False, index=True)
    
    # Foreign keys
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("datasets.id"), nullable=True)
    pipeline_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pipelines.id"), nullable=True)
    model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("models.id"), nullable=True)
    experiment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("experiments.id"), nullable=True)
    
    # Job configuration
    algorithm: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    params: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    # Results
    result_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    logs_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    dataset: Mapped[Optional["Dataset"]] = relationship("Dataset", back_populates="jobs")
    pipeline: Mapped[Optional["Pipeline"]] = relationship("Pipeline", back_populates="jobs")
    model: Mapped[Optional["MLModel"]] = relationship("MLModel", back_populates="jobs")
    experiment: Mapped[Optional["Experiment"]] = relationship("Experiment", back_populates="jobs")
    results: Mapped[list["Result"]] = relationship("Result", back_populates="job")

    def __repr__(self) -> str:
        return f"<Job(id='{self.id}', type='{self.type}', status='{self.status}')>"
