"""
JWT token creation and validation utilities
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from jwt.exceptions import InvalidTokenError
import hashlib
import secrets

from auth_lib.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE,
    REFRESH_TOKEN_EXPIRE,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
)


class TokenError(Exception):
    """Base exception for token-related errors"""
    pass


class InvalidToken(TokenError):
    """Raised when token is invalid"""
    pass


class ExpiredToken(TokenError):
    """Raised when token is expired"""
    pass


def create_access_token(
    user_id: str,
    username: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token

    Args:
        user_id: User's unique identifier
        username: User's username
        role: User's role (user, admin, etc.)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = ACCESS_TOKEN_EXPIRE

    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,  # subject (user_id)
        "username": username,
        "role": role,
        "type": TOKEN_TYPE_ACCESS,
        "exp": expire,
        "iat": datetime.utcnow(),  # issued at
    }

    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, str]:
    """
    Create a JWT refresh token and its hash

    Args:
        user_id: User's unique identifier
        expires_delta: Optional custom expiration time

    Returns:
        Tuple of (token, token_hash) where token_hash should be stored in database
    """
    if expires_delta is None:
        expires_delta = REFRESH_TOKEN_EXPIRE

    expire = datetime.utcnow() + expires_delta

    # Generate a secure random token component
    random_component = secrets.token_urlsafe(32)

    payload = {
        "sub": user_id,
        "type": TOKEN_TYPE_REFRESH,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": random_component,  # JWT ID for uniqueness
    }

    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Create hash of token for storage in database
    token_hash = hashlib.sha256(encoded_jwt.encode()).hexdigest()

    return encoded_jwt, token_hash


def decode_token(token: str) -> Dict:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        InvalidToken: If token is invalid
        ExpiredToken: If token is expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredToken("Token has expired")
    except InvalidTokenError as e:
        raise InvalidToken(f"Invalid token: {str(e)}")


def verify_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> Dict:
    """
    Verify a JWT token and check its type

    Args:
        token: JWT token string
        token_type: Expected token type (access or refresh)

    Returns:
        Decoded token payload

    Raises:
        InvalidToken: If token is invalid or type doesn't match
        ExpiredToken: If token is expired
    """
    payload = decode_token(token)

    if payload.get("type") != token_type:
        raise InvalidToken(f"Expected {token_type} token, got {payload.get('type')}")

    return payload


def get_token_hash(token: str) -> str:
    """
    Get SHA256 hash of a token (for matching against database)

    Args:
        token: JWT token string

    Returns:
        Hex digest of token hash
    """
    return hashlib.sha256(token.encode()).hexdigest()


def extract_user_from_token(token: str) -> Dict:
    """
    Extract user information from an access token

    Args:
        token: JWT access token string

    Returns:
        Dictionary with user information (user_id, username, role)

    Raises:
        InvalidToken: If token is invalid
        ExpiredToken: If token is expired
    """
    payload = verify_token(token, TOKEN_TYPE_ACCESS)

    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role"),
    }
