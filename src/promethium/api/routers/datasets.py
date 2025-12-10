from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import shutil
import os
from uuid import uuid4

from promethium.core.database import get_db
from promethium.api.models.dataset import Dataset
from promethium.api.models.user import User
from promethium.api.schemas.dataset import (
    DatasetRead, DatasetCreate, DatasetUpdate,
    UploadInitRequest, UploadInitResponse, UploadFinalizeRequest
)
from promethium.api.deps.auth import get_current_active_user
from promethium.core.config import get_settings
from promethium.core.logging import logger

router = APIRouter(prefix="/datasets", tags=["datasets"])
settings = get_settings()

@router.post("/upload/init", response_model=UploadInitResponse)
async def init_upload(
    request: UploadInitRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Initialize a chunked upload session.
    """
    upload_id = str(uuid4())
    temp_dir = os.path.join(settings.DATA_STORAGE_PATH, "temp", upload_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    logger.info(f"Initialized upload session: {upload_id} by user {current_user.id}")
    return UploadInitResponse(upload_id=upload_id, chunk_size=request.chunk_size)

@router.post("/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a single chunk of the file.
    """
    temp_dir = os.path.join(settings.DATA_STORAGE_PATH, "temp", upload_id)
    if not os.path.exists(temp_dir):
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    chunk_path = os.path.join(temp_dir, str(chunk_index))
    
    try:
        with open(chunk_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Chunk upload failed: {e}")
        raise HTTPException(status_code=500, detail="Chunk write failed")
        
    return {"status": "success", "chunk_index": chunk_index}

@router.post("/upload/finalize", response_model=DatasetRead)
async def finalize_upload(
    request: UploadFinalizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Merge chunks and create dataset record.
    """
    temp_dir = os.path.join(settings.DATA_STORAGE_PATH, "temp", request.upload_id)
    if not os.path.exists(temp_dir):
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    filename = f"{request.upload_id}_{request.name}"
    
    # Auto-append extension if missing and format is known
    if request.format and request.format.upper() == "SEGY" and not filename.lower().endswith(('.sgy', '.segy')):
        filename += ".sgy"
        
    final_path = os.path.join(settings.DATA_STORAGE_PATH, filename)
    
    # Merge chunks
    chunks = sorted([int(f) for f in os.listdir(temp_dir) if f.isdigit()])
    
    if not chunks:
         raise HTTPException(status_code=400, detail="No chunks found")

    try:
        with open(final_path, "wb") as outfile:
            for i in chunks:
                chunk_path = os.path.join(temp_dir, str(i))
                with open(chunk_path, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise HTTPException(status_code=500, detail="File merge failed")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    # Calculate size
    size_bytes = os.path.getsize(final_path)

    # Create DB Record
    new_dataset = Dataset(
        name=request.name,
        format=request.format,
        file_path=final_path,
        size_bytes=size_bytes,
        owner_id=current_user.id,
        metadata_json={}
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    
    logger.info(f"Dataset finalized: {new_dataset.id}")
    return new_dataset

@router.get("/", response_model=List[DatasetRead])
async def list_datasets(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # TODO: Filter by owner or public? For now list all for authenticated users
    result = await db.execute(select(Dataset).offset(skip).limit(limit))
    datasets = result.scalars().all()
    return datasets

@router.get("/{dataset_id}", response_model=DatasetRead)
async def get_dataset(
    dataset_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Check ownership or admin
    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this dataset")
    
    if dataset.file_path and os.path.exists(dataset.file_path):
        try:
            os.remove(dataset.file_path)
        except Exception as e:
            logger.warning(f"Could not delete file {dataset.file_path}: {e}")
    
    await db.delete(dataset)
    await db.commit()
    return None
