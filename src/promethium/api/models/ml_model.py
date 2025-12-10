"""
MLModel model for machine learning model registry.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from promethium.api.models.base import Base


class MLModel(Base):
    """
    Machine learning model registry.
    
    Attributes:
        id: Primary key.
        name: Model name.
        type: Model architecture (unet, autoencoder, gan, pinn).
        version: Model version string.
        description: Optional description.
        artifact_path: Path to model weights/artifacts.
        config: Model configuration as JSON.
        metrics: Evaluation metrics as JSON.
        created_at: Creation timestamp.
    """
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    artifact_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="model")
    results: Mapped[List["Result"]] = relationship("Result", back_populates="model")

    def __repr__(self) -> str:
        return f"<MLModel(id={self.id}, name='{self.name}', type='{self.type}', version='{self.version}')>"
