# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
from uuid import UUID

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ModelFamily(str, Enum):
    UNET = "unet"
    AUTOENCODER = "autoencoder"
    PINN = "pinn"

class TrainingConfig(BaseModel):
    batch_size: int = Field(32, ge=1, le=512)
    lr: float = Field(1e-3, ge=1e-6, le=1.0)
    epochs: int = Field(100, ge=1)
    loss: str = "mse"

class ModelConfig(BaseModel):
    family: ModelFamily
    n_channels: int = 1
    parameters: Dict[str, Any] = Field(default_factory=dict)

class TrainingRequest(BaseModel):
    dataset_id: str
    target_dataset_id: Optional[str] = None # For supervised
    model_config: ModelConfig
    training_config: TrainingConfig

class InferenceRequest(BaseModel):
    dataset_id: str
    model_id: str # Path or UUID of trained checkpoint
    output_name: str
    patch_size: int = 128
    overlap: float = 0.25

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    error: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
