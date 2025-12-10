"""
Authentication service.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

from promethium.core.config import get_settings
from promethium.core.security import verify_password, get_password_hash
from promethium.api.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

settings = get_settings()

class AuthService:
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user by email and password.
        """
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            return None
            
        if not verify_password(password, user.hashed_password):
            return None
            
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        
        # Use settings or defaults
        secret_key = getattr(settings, "SECRET_KEY", "dev_secret_key_change_me")
        algorithm = getattr(settings, "ALGORITHM", "HS256")
        
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt
