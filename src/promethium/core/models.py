# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    size_bytes = Column(Integer)
    metadata_json = Column(JSON, default={})
    
    jobs = relationship("Job", back_populates="dataset")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"))
    type = Column(String) # 'training', 'inference'
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    config = Column(JSON) # Detailed parameters
    parameters = Column(JSON, nullable=True) # Legacy support
    result_path = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True) # SNR, MSE, etc.
    
    dataset = relationship("Dataset", back_populates="jobs")

class ModelArtifact(Base):
    """
    Registry for trained model weights.
    """
    __tablename__ = "models"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    version = Column(String)
    family = Column(String) # 'unet', 'pinn'
    created_at = Column(DateTime, default=datetime.utcnow)
    path = Column(String)
    config = Column(JSON)
    metrics = Column(JSON)
