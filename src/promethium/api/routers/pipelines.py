from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from promethium.core.database import get_db
from promethium.api.models.pipeline import Pipeline
from promethium.api.models.user import User
from promethium.api.schemas.pipeline import PipelineRead, PipelineCreate, PipelineUpdate
from promethium.api.deps.auth import get_current_active_user
from promethium.core.logging import logger

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

@router.post("/", response_model=PipelineRead, status_code=201)
async def create_pipeline(
    pipeline_in: PipelineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_pipeline = Pipeline(
        name=pipeline_in.name,
        description=pipeline_in.description,
        config_json=pipeline_in.config_json,
        owner_id=current_user.id
    )
    db.add(new_pipeline)
    await db.commit()
    await db.refresh(new_pipeline)
    return new_pipeline

@router.get("/", response_model=List[PipelineRead])
async def list_pipelines(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Pipeline).offset(skip).limit(limit))
    pipelines = result.scalars().all()
    return pipelines

@router.get("/{pipeline_id}", response_model=PipelineRead)
async def get_pipeline(
    pipeline_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    pipeline = await db.get(Pipeline, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline
