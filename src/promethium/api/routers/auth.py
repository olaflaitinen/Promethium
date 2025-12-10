"""
Auth router.
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from promethium.core.database import get_db
from promethium.core.config import get_settings
from promethium.api.services.auth_service import AuthService
from promethium.api.schemas.auth import Token
from promethium.api.schemas.user import UserRead
from promethium.api.deps.auth import get_current_active_user
from promethium.api.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await AuthService.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(
        minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 8) # 8 days default
    )
    
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
