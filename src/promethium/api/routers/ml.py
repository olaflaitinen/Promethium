from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from promethium.core.database import get_db
from promethium.api.models.ml_model import MLModel
from promethium.api.models.user import User
from promethium.api.schemas.ml_model import MLModelRead, MLModelCreate, MLModelUpdate
from promethium.api.deps.auth import get_current_active_user
from promethium.core.logging import logger

router = APIRouter(prefix="/ml/models", tags=["ml-models"])

@router.post("/", response_model=MLModelRead, status_code=201)
async def create_model(
    model_in: MLModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_model = MLModel(
        name=model_in.name,
        type=model_in.type,
        version=model_in.version,
        description=model_in.description,
        config=model_in.config,
        metrics=model_in.metrics
    )
    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)
    return new_model

@router.get("/", response_model=List[MLModelRead])
async def list_models(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(MLModel).offset(skip).limit(limit))
    models = result.scalars().all()
    return models

@router.get("/{model_id}", response_model=MLModelRead)
async def get_model(
    model_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    model = await db.get(MLModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model
