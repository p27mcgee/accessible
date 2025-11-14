"""
Pydantic schemas for authentication API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from auth_lib.models import UserRole


# Request schemas
class UserRegisterRequest(BaseModel):
    """Schema for user registration request"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username is alphanumeric with optional underscore/hyphen"""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscore and hyphen allowed)")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Basic password strength validation"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str = Field(..., description="Refresh token")


class UserUpdateRequest(BaseModel):
    """Schema for updating user information (admin only)"""
    email: Optional[EmailStr] = Field(None, description="New email address")
    role: Optional[UserRole] = Field(None, description="New role")
    is_active: Optional[bool] = Field(None, description="Account active status")


class UserPasswordChangeRequest(BaseModel):
    """Schema for password change request"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Basic password strength validation"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# Response schemas
class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(..., description="User UUID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    created_at: str = Field(..., description="Account creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True  # Allows creation from ORM models


class UserListResponse(BaseModel):
    """Schema for list of users response"""
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")


class MessageResponse(BaseModel):
    """Schema for generic message response"""
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Schema for error response"""
    detail: str = Field(..., description="Error detail message")


class CurrentUserResponse(BaseModel):
    """Schema for current user info response"""
    id: str = Field(..., description="User UUID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
