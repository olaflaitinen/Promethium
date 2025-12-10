from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select
import platform
import psutil
import os

from promethium.core.database import get_db, engine
from promethium.core.config import get_settings
from promethium.api.schemas.system import HealthResponse, SystemInfo, SystemStats
from promethium.core.logging import logger
from promethium.api.models.user import User
from promethium.api.models.dataset import Dataset
from promethium.api.models.job import Job
from promethium.api.models.experiment import Experiment

router = APIRouter(prefix="/system", tags=["system"])
settings = get_settings()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check system health and database connectivity.
    """
    status = "ok"
    db_status = "connected"
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        status = "degraded"
        
    return {
        "status": status,
        "version": settings.APP_VERSION,
        "database": db_status,
        "redis": "configured", # TODO: Implement actual Redis check
        "components": {
            "api": "running",
            "database": db_status,
            "worker": "unknown" 
        }
    }

@router.get("/info", response_model=SystemInfo)
async def system_info():
    """
    Get system environment information.
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_version": "v1",
        "environment": "development" if settings.DEBUG else "production",
        "debug": settings.DEBUG
    }

@router.get("/stats", response_model=SystemStats)
async def system_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get current system statistics.
    """
    # Helper to count table rows
    async def count(model):
        result = await db.execute(select(func.count()).select_from(model))
        return result.scalar()

    total_users = await count(User)
    total_datasets = await count(Dataset)
    total_jobs = await count(Job)
    total_experiments = await count(Experiment)
    
    # Count active jobs (running or queued)
    # result = await db.execute(select(func.count()).select_from(Job).where(Job.status.in_(["running", "queued"])))
    # active_jobs = result.scalar()
    
    return {
        "total_users": total_users,
        "total_datasets": total_datasets,
        "total_jobs": total_jobs,
        "active_jobs": 0, # Placeholder for optimization or complex query
        "total_experiments": total_experiments
    }
