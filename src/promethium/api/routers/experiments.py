from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from promethium.core.database import get_db
from promethium.api.models.experiment import Experiment
from promethium.api.models.user import User
from promethium.api.schemas.experiment import ExperimentRead, ExperimentCreate, ExperimentUpdate
from promethium.api.deps.auth import get_current_active_user
from promethium.core.logging import logger

router = APIRouter(prefix="/experiments", tags=["experiments"])

@router.post("/", response_model=ExperimentRead, status_code=201)
async def create_experiment(
    experiment_in: ExperimentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_experiment = Experiment(
        name=experiment_in.name,
        description=experiment_in.description,
        tags=experiment_in.tags,
        metadata_json=experiment_in.metadata_json,
        owner_id=current_user.id
    )
    db.add(new_experiment)
    await db.commit()
    await db.refresh(new_experiment)
    return new_experiment

@router.get("/", response_model=List[ExperimentRead])
async def list_experiments(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Experiment).offset(skip).limit(limit))
    experiments = result.scalars().all()
    return experiments

@router.get("/{experiment_id}", response_model=ExperimentRead)
async def get_experiment(
    experiment_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    experiment = await db.get(Experiment, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@router.put("/{experiment_id}", response_model=ExperimentRead)
async def update_experiment(
    experiment_id: int,
    experiment_in: ExperimentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    experiment = await db.get(Experiment, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    if experiment.name:
        experiment.name = experiment_in.name
    if experiment_in.description is not None:
        experiment.description = experiment_in.description
    if experiment_in.tags is not None:
        experiment.tags = experiment_in.tags
    if experiment_in.metadata_json is not None:
         experiment.metadata_json = experiment_in.metadata_json

    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    return experiment
