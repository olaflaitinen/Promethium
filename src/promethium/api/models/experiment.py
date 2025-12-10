"""
Experiment model for grouping related jobs.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from promethium.api.models.base import Base


class Experiment(Base):
    """
    Experiment for grouping related processing jobs.
    
    Attributes:
        id: Primary key.
        name: Experiment name.
        description: Optional description.
        tags: Tags as JSON array.
        metadata_json: Additional metadata.
        owner_id: Foreign key to users table.
        created_at: Creation timestamp.
    """
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Dict[str, Any]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="experiments")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="experiment")

    def __repr__(self) -> str:
        return f"<Experiment(id={self.id}, name='{self.name}')>"
