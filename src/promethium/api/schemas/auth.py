"""
Authentication schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: Optional[int] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr
    password: str
