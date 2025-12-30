"""Authentication and user schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration request."""

    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login request."""

    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    username: str
    email: str
    role: str
    is_active: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
