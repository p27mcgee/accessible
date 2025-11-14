"""
FastAPI dependency functions for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth_lib.database import get_db
from auth_lib.models import User, UserRole
from auth_lib.jwt_utils import extract_user_from_token, InvalidToken, ExpiredToken

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user_data(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract and validate user data from JWT token

    Returns:
        Dictionary with user_id, username, and role

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        user_data = extract_user_from_token(token)
        return user_data
    except ExpiredToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidToken as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_data: dict = Depends(get_current_user_data),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from database

    Returns:
        User model instance

    Raises:
        HTTPException: If user not found or inactive
    """
    user = db.query(User).filter(User.id == user_data["user_id"]).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def require_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require authenticated user (any role)

    Use this dependency for routes that require authentication
    but don't need specific role privileges.

    Returns:
        User model instance

    Example:
        @router.get("/profile")
        async def get_profile(user: User = Depends(require_user)):
            return user.to_dict()
    """
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require authenticated user with admin role

    Use this dependency for routes that require admin privileges.

    Returns:
        User model instance

    Raises:
        HTTPException: If user is not an admin

    Example:
        @router.get("/admin/users")
        async def list_users(user: User = Depends(require_admin)):
            # Only admins can access this
            pass
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Factory function to create role-based dependency

    Use this for custom role requirements (extensible for future roles).

    Args:
        *allowed_roles: One or more UserRole enum values

    Returns:
        Dependency function

    Example:
        @router.get("/moderator-only")
        async def moderator_endpoint(
            user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR))
        ):
            # Only admins and moderators can access this
            pass
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(role.value for role in allowed_roles)}"
            )
        return current_user

    return role_checker
