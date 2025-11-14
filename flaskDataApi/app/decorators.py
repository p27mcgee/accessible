"""
Flask decorators for authentication and authorization
"""
from functools import wraps
from flask import request, jsonify

from auth_lib.jwt_utils import extract_user_from_token, InvalidToken, ExpiredToken
from auth_lib.database import get_db_context
from auth_lib.models import User, UserRole


def require_auth(f):
    """
    Decorator to require authentication for Flask routes

    Extracts user information from JWT token and attaches to request object.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"detail": "Missing or invalid authorization header"}), 401

        token = auth_header.split(' ')[1]

        try:
            user_data = extract_user_from_token(token)

            # Verify user exists and is active
            with get_db_context() as db:
                user = db.query(User).filter(User.id == user_data["user_id"]).first()

                if not user:
                    return jsonify({"detail": "User not found"}), 401

                if not user.is_active:
                    return jsonify({"detail": "User account is disabled"}), 403

                # Attach user information to request
                request.user_id = user_data["user_id"]
                request.username = user_data["username"]
                request.role = user_data["role"]
                request.user = user

        except ExpiredToken:
            return jsonify({"detail": "Token has expired"}), 401
        except InvalidToken as e:
            return jsonify({"detail": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """
    Decorator to require admin role for Flask routes

    Must be used after @require_auth decorator.
    """
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.role != UserRole.ADMIN.value:
            return jsonify({"detail": "Admin privileges required"}), 403

        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):
    """
    Factory function to create role-based decorator

    Args:
        *allowed_roles: One or more UserRole enum values

    Returns:
        Decorator function

    Example:
        @require_role(UserRole.ADMIN, UserRole.MODERATOR)
        def moderator_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_role = UserRole(request.role)

            if user_role not in allowed_roles:
                return jsonify({
                    "detail": f"Required role: {', '.join(role.value for role in allowed_roles)}"
                }), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator
