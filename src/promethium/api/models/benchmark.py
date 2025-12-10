from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from promethium.api.models.base import Base


class Benchmark(Base):
    """
    Benchmark model for storing benchmark run configurations and results.
    """
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Benchmark configuration
    config_json = Column(JSON, nullable=True)
    
    # Execution metrics
    status = Column(String(50), default="pending")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Results
    metrics_json = Column(JSON, nullable=True)
    
    # Foreign keys
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Benchmark(id={self.id}, name='{self.name}', status='{self.status}')>"
