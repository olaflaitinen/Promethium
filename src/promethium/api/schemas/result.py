# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Result schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ResultBase(BaseModel):
    """Base result schema."""
    job_id: str
    dataset_id: Optional[int] = None
    model_id: Optional[int] = None
    result_path: str
    metrics: Dict[str, Any] = {}
    metadata_json: Dict[str, Any] = {}


class ResultCreate(ResultBase):
    """Result creation schema."""
    pass


class ResultRead(ResultBase):
    """Result response schema."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
