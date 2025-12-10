"""
User management methods.
"""
from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from promethium.core.database import get_db
from promethium.core.security import get_password_hash
from promethium.api.models.user import User
from promethium.api.schemas.user import UserCreate, UserRead, UserUpdate
from promethium.api.deps.auth import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=201)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    # Check if user with this email already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this user name already exists in the system.",
        )
    
    # Create new user
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        role="user" # Default role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve users.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserRead)
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await db.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user != current_user and current_user.role != "admin":
        raise HTTPException(
             status_code=400, detail="The user doesn't have enough privileges"
        )
        
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
        
    if user_in.full_name:
        user.full_name = user_in.full_name
        
    if user_in.email:
         # Check if email is taken by another user
        result = await db.execute(select(User).where(User.email == user_in.email))
        existing_user = result.scalars().first()
        if existing_user and existing_user.id != user_id:
             raise HTTPException(
                status_code=400,
                detail="The user with this user name already exists in the system.",
            )
        user.email = user_in.email

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
