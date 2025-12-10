"""
Pipeline model for processing configurations.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from promethium.api.models.base import Base


class Pipeline(Base):
    """
    Pipeline configuration for seismic data processing.
    
    Attributes:
        id: Primary key.
        name: Pipeline name.
        description: Optional description.
        config_json: Pipeline configuration as JSON.
        config_path: Optional path to YAML config file.
        owner_id: Foreign key to users table.
        created_at: Creation timestamp.
        updated_at: Last modification timestamp.
    """
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    config_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="pipelines")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="pipeline")

    def __repr__(self) -> str:
        return f"<Pipeline(id={self.id}, name='{self.name}')>"
