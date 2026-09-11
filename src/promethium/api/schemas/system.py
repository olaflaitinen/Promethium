# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
System schemas.
"""
from typing import Dict, Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """System health status."""
    status: str
    version: str
    database: str
    redis: str
    components: Dict[str, str]


class SystemInfo(BaseModel):
    """System information."""
    app_name: str
    version: str
    api_version: str
    environment: str
    debug: bool


class SystemStats(BaseModel):
    """System statistics."""
    total_users: int
    total_datasets: int
    total_jobs: int
    active_jobs: int
    total_experiments: int
