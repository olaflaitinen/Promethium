"""
Promethium API Schemas

Pydantic models for request/response validation.
"""

from promethium.api.schemas.auth import (
    Token,
    TokenPayload,
    LoginRequest,
)
from promethium.api.schemas.user import (
    UserCreate,
    UserUpdate,
    UserRead,
    UserInDB,
)
from promethium.api.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetRead,
    UploadInitRequest,
    UploadInitResponse,
    UploadFinalizeRequest,
)
from promethium.api.schemas.pipeline import (
    PipelineCreate,
    PipelineUpdate,
    PipelineRead,
)
from promethium.api.schemas.job import (
    JobCreate,
    JobUpdate,
    JobRead,
    JobProgress,
)
from promethium.api.schemas.ml_model import (
    MLModelCreate,
    MLModelUpdate,
    MLModelRead,
)
from promethium.api.schemas.experiment import (
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentRead,
)
from promethium.api.schemas.result import (
    ResultCreate,
    ResultRead,
)
from promethium.api.schemas.system import (
    HealthResponse,
    SystemInfo,
    SystemStats,
)

__all__ = [
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    # User
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserInDB",
    # Dataset
    "DatasetCreate",
    "DatasetUpdate",
    "DatasetRead",
    "UploadInitRequest",
    "UploadInitResponse",
    "UploadFinalizeRequest",
    # Pipeline
    "PipelineCreate",
    "PipelineUpdate",
    "PipelineRead",
    # Job
    "JobCreate",
    "JobUpdate",
    "JobRead",
    "JobProgress",
    # MLModel
    "MLModelCreate",
    "MLModelUpdate",
    "MLModelRead",
    # Experiment
    "ExperimentCreate",
    "ExperimentUpdate",
    "ExperimentRead",
    # Result
    "ResultCreate",
    "ResultRead",
    # System
    "HealthResponse",
    "SystemInfo",
    "SystemStats",
]
