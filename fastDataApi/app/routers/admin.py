"""
Admin router for user management

Provides CRUD endpoints for managing users in the authentication database.
All endpoints require admin role.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from auth_lib.database import get_db
from auth_lib.models import User, UserRole
from auth_lib.schemas import (
    UserResponse,
    UserListResponse,
    UserUpdateRequest,
    UserRegisterRequest,
    MessageResponse,
)
from auth_lib.security import hash_password
from fastDataApi.app.dependencies import require_admin

router = APIRouter(prefix="/admin/users", tags=["Admin - User Management"])


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    role: Optional[str] = Query(None, description="Filter by role (user, admin)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    List all users (admin only)

    Returns paginated list of users with optional filters.
    """
    query = db.query(User)

    # Apply filters
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}"
            )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    users = query.offset(skip).limit(limit).all()

    return UserListResponse(
        users=[UserResponse(**user.to_dict()) for user in users],
        total=total
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get user by ID (admin only)

    Returns detailed information about a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(**user.to_dict())


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserRegisterRequest,
    role: UserRole = Query(UserRole.USER, description="User role"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new user (admin only)

    Allows admin to create users with any role (user or admin).
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with specified role
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(**new_user.to_dict())


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update user information (admin only)

    Allows admin to update user email, role, and active status.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    if update_data.email is not None:
        # Check if email is already used by another user
        existing_email = db.query(User).filter(
            User.email == update_data.email,
            User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = update_data.email

    if update_data.role is not None:
        user.role = update_data.role

    if update_data.is_active is not None:
        user.is_active = update_data.is_active

    db.commit()
    db.refresh(user)

    return UserResponse(**user.to_dict())


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete user (admin only)

    Permanently deletes a user and all associated refresh tokens.
    Admins cannot delete themselves.
    """
    # Prevent admin from deleting themselves
    if str(admin.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return MessageResponse(message=f"User {user.username} deleted successfully")


@router.get("/search/username/{username}", response_model=UserResponse)
async def search_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Search for user by username (admin only)

    Returns user information if found.
    """
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(**user.to_dict())
