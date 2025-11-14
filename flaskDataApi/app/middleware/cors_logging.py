"""
CORS logging middleware for Flask

Logs CORS-related events including:
- Preflight OPTIONS requests
- CORS violations
- Origin validation
"""
from flask import request
import structlog

from app.utils.logger import get_request_id

# Get logger
logger = structlog.get_logger(__name__)


def setup_cors_logging(app, allowed_origins):
    """
    Set up CORS logging hooks for Flask app

    Args:
        app: Flask application instance
        allowed_origins: List of allowed CORS origins
    """

    @app.before_request
    def log_cors_request():
        """
        Log CORS-related requests
        """
        origin = request.headers.get("Origin")
        request_id = get_request_id()
        request_logger = logger.bind(request_id=request_id) if request_id else logger

        # Log preflight requests
        if request.method == "OPTIONS":
            request_logger.info(
                "CORS preflight request",
                origin=origin,
                method=request.method,
                path=request.path,
                requested_method=request.headers.get("Access-Control-Request-Method"),
                requested_headers=request.headers.get("Access-Control-Request-Headers")
            )

        # Check if origin is allowed
        if origin:
            is_allowed = _is_origin_allowed(origin, allowed_origins)

            if not is_allowed:
                request_logger.warning(
                    "CORS request from disallowed origin",
                    origin=origin,
                    allowed_origins=allowed_origins,
                    method=request.method,
                    path=request.path,
                    cors_violation=True
                )
            else:
                request_logger.debug(
                    "CORS request from allowed origin",
                    origin=origin,
                    method=request.method,
                    path=request.path
                )


def _is_origin_allowed(origin: str, allowed_origins: list) -> bool:
    """
    Check if origin is in the allowed list

    Args:
        origin: Origin header value
        allowed_origins: List of allowed origins

    Returns:
        True if origin is allowed, False otherwise
    """
    # Wildcard allows all origins
    if "*" in allowed_origins:
        return True

    # Check exact match
    if origin in allowed_origins:
        return True

    # Check without trailing slash
    origin_without_slash = origin.rstrip("/")
    for allowed in allowed_origins:
        if origin_without_slash == allowed.rstrip("/"):
            return True

    return False
