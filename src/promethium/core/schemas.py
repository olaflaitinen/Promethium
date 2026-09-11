# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DatasetBase(BaseModel):
    name: str
    format: str

class DatasetCreate(DatasetBase):
    pass

class DatasetRead(DatasetBase):
    id: int
    file_path: str
    metadata_json: Dict[str, Any]
    upload_time: datetime

    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    dataset_id: int
    algorithm: str
    params: Dict[str, Any] = {}

class JobCreate(JobBase):
    pass

class JobRead(JobBase):
    id: str
    status: JobStatus
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Upload Schemas ---
class UploadInitRequest(BaseModel):
    filename: str
    total_size: int
    chunk_size: Optional[int] = 5 * 1024 * 1024  # 5MB default

class UploadInitResponse(BaseModel):
    upload_id: str
    chunk_size: int

class UploadFinalizeRequest(BaseModel):
    upload_id: str
    name: str
    format: str
