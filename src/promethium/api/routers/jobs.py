from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from promethium.core.database import get_db
from promethium.api.models.job import Job
from promethium.api.models.dataset import Dataset
from promethium.api.models.user import User
from promethium.api.schemas.job import JobRead, JobCreate, JobStatus
from promethium.api.deps.auth import get_current_active_user
from promethium.core.logging import logger

# Import Celery task (stub for now if not existing)
# from promethium.workflows.tasks import run_reconstruction_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobRead, status_code=201)
async def create_job(
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a new processing job.
    """
    # Verify dataset exists if provided
    if job_in.dataset_id:
        dataset = await db.get(Dataset, job_in.dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

    job_id = str(uuid4())
    new_job = Job(
        id=job_id,
        dataset_id=job_in.dataset_id,
        pipeline_id=job_in.pipeline_id,
        model_id=job_in.model_id,
        experiment_id=job_in.experiment_id,
        status=JobStatus.QUEUED.value,
        params=job_in.params,
        created_at=datetime.utcnow()
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Trigger Celery task (Placeholder for now)
    # task = run_reconstruction_job.delay(job_id=job_id, ...)
    logger.info(f"Job submitted to queue: {job_id}")
    
    return new_job

@router.get("/{job_id}", response_model=JobRead)
async def get_job(
    job_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/", response_model=List[JobRead])
async def list_jobs(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Job).offset(skip).limit(limit))
    jobs = result.scalars().all()
    return jobs
