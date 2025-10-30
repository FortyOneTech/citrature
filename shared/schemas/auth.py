"""Authentication schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    name: str
    picture_url: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    name: str
    picture_url: Optional[str]
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str
    expires_in: int


class GoogleAuthRequest(BaseModel):
    """Google authentication request schema."""
    id_token: str
