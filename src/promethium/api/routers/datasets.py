from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import shutil
import os
import glob
from uuid import uuid4

from promethium.core.database import get_db, Dataset
from promethium.core.schemas import (
    DatasetRead, DatasetCreate, 
    UploadInitRequest, UploadInitResponse, UploadFinalizeRequest
)
from promethium.core.config import get_settings
from promethium.core.logging import logger

router = APIRouter(prefix="/datasets", tags=["datasets"])
settings = get_settings()

@router.post("/upload/init", response_model=UploadInitResponse)
async def init_upload(request: UploadInitRequest):
    """
    Initialize a chunked upload session.
    """
    upload_id = str(uuid4())
    temp_dir = os.path.join(settings.DATA_STORAGE_PATH, "temp", upload_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    logger.info(f"Initialized upload session: {upload_id}")
    return UploadInitResponse(upload_id=upload_id, chunk_size=request.chunk_size)

@router.post("/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...)
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
    db: AsyncSession = Depends(get_db)
):
    """
    Merge chunks and create dataset record.
    """
    temp_dir = os.path.join(settings.DATA_STORAGE_PATH, "temp", request.upload_id)
    if not os.path.exists(temp_dir):
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    # Target file
    # unique file ID is already the upload_id for simplicity, or we generate new one
    filename = f"{request.upload_id}_{request.name}"
    # Sanitize filename if needed, but uuid prefix makes it safe-ish
    # Ideally keep original extension if possible or infer from format
    # But user didn't send extension in params explicitly, assume strictly binary content
    
    # We might want to fix extension based on format (segy -> .sgy)
    if request.format.upper() == "SEGY" and not filename.lower().endswith(('.sgy', '.segy')):
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
    
    # DB Record
    new_dataset = Dataset(
        name=request.name,
        format=request.format,
        file_path=final_path,
        metadata_json={}
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    
    logger.info(f"Dataset finalized: {new_dataset.id}")
    return new_dataset

# Keep legacy endpoint for backwards init compatibility or small files if needed
@router.post("/", response_model=DatasetRead, status_code=201)
async def create_dataset_legacy(
    name: str = Form(...),
    format: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Ensure storage exists
    os.makedirs(settings.DATA_STORAGE_PATH, exist_ok=True)
    
    file_id = str(uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.DATA_STORAGE_PATH, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

    new_dataset = Dataset(
        name=name,
        format=format,
        file_path=file_path,
        metadata_json={}
    )
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    return new_dataset

@router.get("/", response_model=List[DatasetRead])
async def list_datasets(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).offset(skip).limit(limit))
    datasets = result.scalars().all()
    return datasets

@router.get("/{dataset_id}", response_model=DatasetRead)
async def get_dataset(dataset_id: int, db: AsyncSession = Depends(get_db)):
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a dataset and its associated file.
    """
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Delete the file if it exists
    if dataset.file_path and os.path.exists(dataset.file_path):
        try:
            os.remove(dataset.file_path)
            logger.info(f"Deleted file: {dataset.file_path}")
        except Exception as e:
            logger.warning(f"Could not delete file {dataset.file_path}: {e}")
    
    await db.delete(dataset)
    await db.commit()
    logger.info(f"Dataset deleted: {dataset_id}")
    return None
