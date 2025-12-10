from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from promethium.core.database import get_db
from promethium.api.models.result import Result
from promethium.api.models.user import User
from promethium.api.schemas.result import ResultRead, ResultCreate
from promethium.api.deps.auth import get_current_active_user
from promethium.core.logging import logger

router = APIRouter(prefix="/results", tags=["results"])

@router.post("/", response_model=ResultRead, status_code=201)
async def create_result(
    result_in: ResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Determine result_path defaults if not provided, or logic here
    new_result = Result(
        job_id=result_in.job_id,
        dataset_id=result_in.dataset_id,
        model_id=result_in.model_id,
        result_path=result_in.result_path,
        metrics=result_in.metrics,
        metadata_json=result_in.metadata_json
    )
    db.add(new_result)
    await db.commit()
    await db.refresh(new_result)
    return new_result

@router.get("/", response_model=List[ResultRead])
async def list_results(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Result).offset(skip).limit(limit))
    results = result.scalars().all()
    return results

@router.get("/{result_id}", response_model=ResultRead)
async def get_result(
    result_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result
