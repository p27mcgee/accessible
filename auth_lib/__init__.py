"""
Shared Authentication Library

This library provides authentication and authorization functionality
that can be used by both FastAPI and Flask applications.

Modules:
- models: SQLAlchemy models for User and RefreshToken
- database: Database connection and session management
- jwt_utils: JWT token creation and validation
- schemas: Pydantic schemas for request/response validation
- security: Password hashing and verification
"""

__version__ = "1.0.0"

from auth_lib.models import User, RefreshToken, UserRole
from auth_lib.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token,
)
from auth_lib.security import hash_password, verify_password

__all__ = [
    "User",
    "RefreshToken",
    "UserRole",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
