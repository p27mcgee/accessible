"""
Authentication router for FastAPI

Provides endpoints for user registration, login, token refresh, and logout
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from auth_lib.database import get_db
from auth_lib.models import User, RefreshToken, UserRole
from auth_lib.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
    CurrentUserResponse,
)
from auth_lib.security import hash_password, verify_password
from auth_lib.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_token_hash,
    TOKEN_TYPE_REFRESH,
)
from auth_lib.config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastDataApi.app.dependencies import require_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account

    Creates a new user with role 'user' by default.
    Returns access and refresh tokens upon successful registration.
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

    # Create new user with 'user' role (default)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=UserRole.USER,  # All UI registrations get 'user' role
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate tokens
    access_token = create_access_token(
        user_id=str(new_user.id),
        username=new_user.username,
        role=new_user.role.value
    )

    refresh_token, token_hash = create_refresh_token(user_id=str(new_user.id))

    # Store refresh token in database
    refresh_token_record = RefreshToken(
        user_id=new_user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + datetime.timedelta(days=7)
    )
    db.add(refresh_token_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username and password

    Returns access and refresh tokens upon successful authentication.
    """
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Generate tokens
    access_token = create_access_token(
        user_id=str(user.id),
        username=user.username,
        role=user.role.value
    )

    refresh_token, token_hash = create_refresh_token(user_id=str(user.id))

    # Store refresh token in database
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + datetime.timedelta(days=7)
    )
    db.add(refresh_token_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    token_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Validates the refresh token and issues a new access token.
    Optionally rotates the refresh token for enhanced security.
    """
    try:
        # Verify refresh token
        payload = verify_token(token_data.refresh_token, TOKEN_TYPE_REFRESH)
        user_id = payload.get("sub")

        # Check if refresh token exists in database and is valid
        token_hash = get_token_hash(token_data.refresh_token)
        refresh_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id
        ).first()

        if not refresh_record or not refresh_record.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new access token
        access_token = create_access_token(
            user_id=str(user.id),
            username=user.username,
            role=user.role.value
        )

        # Optional: Rotate refresh token (recommended for production)
        # Revoke old refresh token
        refresh_record.revoked = True

        # Create new refresh token
        new_refresh_token, new_token_hash = create_refresh_token(user_id=str(user.id))
        new_refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=datetime.utcnow() + datetime.timedelta(days=7)
        )
        db.add(new_refresh_record)
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    token_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Logout and revoke refresh token

    Invalidates the refresh token to prevent future use.
    """
    try:
        token_hash = get_token_hash(token_data.refresh_token)
        refresh_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()

        if refresh_record:
            refresh_record.revoked = True
            db.commit()

        return MessageResponse(message="Logged out successfully")

    except Exception:
        # Even if token is invalid, return success
        return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_user)
):
    """
    Get current authenticated user information

    Returns information about the currently logged-in user.
    Requires valid access token.
    """
    return CurrentUserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active
    )
