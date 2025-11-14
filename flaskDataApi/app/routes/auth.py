"""
Authentication routes for Flask

Provides endpoints for user registration, login, token refresh, and logout
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from auth_lib.database import get_db_context
from auth_lib.models import User, RefreshToken, UserRole
from auth_lib.security import hash_password, verify_password
from auth_lib.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_token_hash,
    TOKEN_TYPE_REFRESH,
)
from auth_lib.config import ACCESS_TOKEN_EXPIRE_MINUTES

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account"""
    data = request.json

    # Validate required fields
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({"detail": "Missing required fields"}), 400

    with get_db_context() as db:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == data['username']).first()
        if existing_user:
            return jsonify({"detail": "Username already registered"}), 400

        # Check if email already exists
        existing_email = db.query(User).filter(User.email == data['email']).first()
        if existing_email:
            return jsonify({"detail": "Email already registered"}), 400

        # Create new user with 'user' role (default)
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            role=UserRole.USER,
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
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(refresh_token_record)
        db.commit()

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with username and password"""
    data = request.json

    if not all(k in data for k in ('username', 'password')):
        return jsonify({"detail": "Missing username or password"}), 400

    with get_db_context() as db:
        # Find user by username
        user = db.query(User).filter(User.username == data['username']).first()

        if not user or not verify_password(data['password'], user.password_hash):
            return jsonify({"detail": "Invalid username or password"}), 401

        if not user.is_active:
            return jsonify({"detail": "Account is disabled"}), 403

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
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(refresh_token_record)
        db.commit()

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        })


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token_endpoint():
    """Refresh access token using refresh token"""
    data = request.json

    if 'refresh_token' not in data:
        return jsonify({"detail": "Missing refresh token"}), 400

    try:
        with get_db_context() as db:
            # Verify refresh token
            payload = verify_token(data['refresh_token'], TOKEN_TYPE_REFRESH)
            user_id = payload.get("sub")

            # Check if refresh token exists in database and is valid
            token_hash = get_token_hash(data['refresh_token'])
            refresh_record = db.query(RefreshToken).filter(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == user_id
            ).first()

            if not refresh_record or not refresh_record.is_valid():
                return jsonify({"detail": "Invalid or expired refresh token"}), 401

            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return jsonify({"detail": "User not found or inactive"}), 401

            # Generate new access token
            access_token = create_access_token(
                user_id=str(user.id),
                username=user.username,
                role=user.role.value
            )

            # Rotate refresh token
            refresh_record.revoked = True

            new_refresh_token, new_token_hash = create_refresh_token(user_id=str(user.id))
            new_refresh_record = RefreshToken(
                user_id=user.id,
                token_hash=new_token_hash,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.add(new_refresh_record)
            db.commit()

            return jsonify({
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            })

    except Exception:
        return jsonify({"detail": "Invalid refresh token"}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout and revoke refresh token"""
    data = request.json

    if 'refresh_token' not in data:
        return jsonify({"message": "Logged out successfully"})

    try:
        with get_db_context() as db:
            token_hash = get_token_hash(data['refresh_token'])
            refresh_record = db.query(RefreshToken).filter(
                RefreshToken.token_hash == token_hash
            ).first()

            if refresh_record:
                refresh_record.revoked = True
                db.commit()

    except Exception:
        pass

    return jsonify({"message": "Logged out successfully"})


@auth_bp.route('/me', methods=['GET'])
def get_current_user_info():
    """Get current authenticated user information"""
    from flaskDataApi.app.decorators import require_auth

    # This will be wrapped by the decorator
    user_id = request.user_id  # Set by decorator
    username = request.username  # Set by decorator
    role = request.role  # Set by decorator

    return jsonify({
        "id": user_id,
        "username": username,
        "role": role
    })
