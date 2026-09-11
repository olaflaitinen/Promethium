# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Pipeline schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PipelineBase(BaseModel):
    """Base pipeline schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Dict[str, Any] = {}


class PipelineCreate(PipelineBase):
    """Pipeline creation schema."""
    pass


class PipelineUpdate(BaseModel):
    """Pipeline update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class PipelineRead(PipelineBase):
    """Pipeline response schema."""
    id: int
    config_path: Optional[str] = None
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
