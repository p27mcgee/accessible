"""
CORS logging middleware for FastAPI

Logs CORS-related events including:
- Preflight OPTIONS requests
- CORS violations
- Origin validation
"""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog

from app.utils.logger import get_request_id

# Get logger
logger = structlog.get_logger(__name__)


class CORSLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log CORS-related events
    """

    def __init__(self, app: ASGIApp, allowed_origins: list):
        super().__init__(app)
        self.allowed_origins = allowed_origins

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log CORS-related requests and validate origins

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            HTTP response
        """
        origin = request.headers.get("origin")
        request_id = get_request_id()
        request_logger = logger.bind(request_id=request_id) if request_id else logger

        # Log preflight requests
        if request.method == "OPTIONS":
            request_logger.info(
                "CORS preflight request",
                origin=origin,
                method=request.method,
                path=request.url.path,
                requested_method=request.headers.get("access-control-request-method"),
                requested_headers=request.headers.get("access-control-request-headers")
            )

        # Check if origin is allowed
        if origin:
            is_allowed = self._is_origin_allowed(origin)

            if not is_allowed:
                request_logger.warning(
                    "CORS request from disallowed origin",
                    origin=origin,
                    allowed_origins=self.allowed_origins,
                    method=request.method,
                    path=request.url.path,
                    cors_violation=True
                )
            else:
                request_logger.debug(
                    "CORS request from allowed origin",
                    origin=origin,
                    method=request.method,
                    path=request.url.path
                )

        # Process request
        response = await call_next(request)

        return response

    def _is_origin_allowed(self, origin: str) -> bool:
        """
        Check if origin is in the allowed list

        Args:
            origin: Origin header value

        Returns:
            True if origin is allowed, False otherwise
        """
        # Wildcard allows all origins
        if "*" in self.allowed_origins:
            return True

        # Check exact match
        if origin in self.allowed_origins:
            return True

        # Check without trailing slash
        origin_without_slash = origin.rstrip("/")
        for allowed in self.allowed_origins:
            if origin_without_slash == allowed.rstrip("/"):
                return True

        return False
