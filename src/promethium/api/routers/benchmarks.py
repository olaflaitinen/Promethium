from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime

from promethium.core.database import get_db
from promethium.api.models.benchmark import Benchmark
from promethium.api.models.user import User
from promethium.api.schemas.benchmark import (
    BenchmarkRead, BenchmarkCreate, BenchmarkUpdate, 
    BenchmarkRun, BenchmarkStatus
)
from promethium.api.deps.auth import get_current_active_user
from promethium.core.logging import logger

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("/", response_model=List[BenchmarkRead])
async def list_benchmarks(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all benchmarks with optional status filtering.
    """
    query = select(Benchmark)
    
    if status:
        query = query.where(Benchmark.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Benchmark.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=BenchmarkRead, status_code=status.HTTP_201_CREATED)
async def create_benchmark(
    benchmark_in: BenchmarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new benchmark configuration.
    """
    new_benchmark = Benchmark(
        name=benchmark_in.name,
        description=benchmark_in.description,
        config_json=benchmark_in.config_json,
        dataset_id=benchmark_in.dataset_id,
        model_id=benchmark_in.model_id,
        experiment_id=benchmark_in.experiment_id,
        status=BenchmarkStatus.PENDING.value
    )
    
    db.add(new_benchmark)
    await db.commit()
    await db.refresh(new_benchmark)
    
    logger.info(f"Benchmark created: {new_benchmark.id}")
    return new_benchmark


@router.get("/{benchmark_id}", response_model=BenchmarkRead)
async def get_benchmark(
    benchmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific benchmark by ID.
    """
    benchmark = await db.get(Benchmark, benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Benchmark not found"
        )
    return benchmark


@router.put("/{benchmark_id}", response_model=BenchmarkRead)
async def update_benchmark(
    benchmark_id: int,
    benchmark_update: BenchmarkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a benchmark configuration.
    """
    benchmark = await db.get(Benchmark, benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Benchmark not found"
        )
    
    update_data = benchmark_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(benchmark, key, value)
    
    await db.commit()
    await db.refresh(benchmark)
    return benchmark


@router.delete("/{benchmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_benchmark(
    benchmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a benchmark.
    """
    benchmark = await db.get(Benchmark, benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Benchmark not found"
        )
    
    await db.delete(benchmark)
    await db.commit()
    return None


@router.post("/{benchmark_id}/run", response_model=BenchmarkRead)
async def run_benchmark(
    benchmark_id: int,
    params: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute a benchmark run. Queues the benchmark for execution.
    """
    benchmark = await db.get(Benchmark, benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Benchmark not found"
        )
    
    if benchmark.status == BenchmarkStatus.RUNNING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benchmark is already running"
        )
    
    # Update status and start time
    benchmark.status = BenchmarkStatus.RUNNING.value
    benchmark.started_at = datetime.utcnow()
    benchmark.completed_at = None
    benchmark.metrics_json = None
    
    await db.commit()
    await db.refresh(benchmark)
    
    # TODO: Trigger Celery task for actual benchmark execution
    # task = run_benchmark_task.delay(benchmark_id=benchmark_id, params=params)
    
    logger.info(f"Benchmark {benchmark_id} queued for execution")
    return benchmark


@router.get("/{benchmark_id}/results")
async def get_benchmark_results(
    benchmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed results for a completed benchmark.
    """
    benchmark = await db.get(Benchmark, benchmark_id)
    if not benchmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Benchmark not found"
        )
    
    if benchmark.status != BenchmarkStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benchmark has not completed"
        )
    
    return {
        "benchmark_id": benchmark.id,
        "name": benchmark.name,
        "status": benchmark.status,
        "started_at": benchmark.started_at,
        "completed_at": benchmark.completed_at,
        "duration_seconds": benchmark.duration_seconds,
        "metrics": benchmark.metrics_json or {}
    }
