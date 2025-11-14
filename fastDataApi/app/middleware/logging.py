"""
Request/Response logging middleware for FastAPI

Logs all HTTP requests and responses with structured data including:
- Request ID correlation
- Timing information
- Status codes
- Client information
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog

from app.utils.logger import (
    generate_request_id,
    set_request_id,
    clear_context,
    mask_sensitive_data
)

# Get logger
logger = structlog.get_logger(__name__)

# Threshold for slow request warnings (milliseconds)
SLOW_REQUEST_THRESHOLD_MS = int(
    __import__("os").getenv("SLOW_REQUEST_THRESHOLD_MS", "1000")
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log it

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            HTTP response
        """
        # Generate and set request ID
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        set_request_id(request_id)

        # Bind logger with request ID
        request_logger = logger.bind(request_id=request_id)

        # Extract request information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        query_params = str(request.url.query) if request.url.query else None

        # Log incoming request
        request_logger.info(
            "Request started",
            method=method,
            path=path,
            query_params=mask_sensitive_data(query_params) if query_params else None,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        # Start timing
        start_time = time.time()

        # Process request and handle exceptions
        try:
            response = await call_next(request)
            status_code = response.status_code

        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            request_logger.error(
                "Request failed with exception",
                method=method,
                path=path,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            # Re-raise to let error handlers deal with it
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Determine log level based on status code and duration
        log_level = "info"
        if status_code >= 500:
            log_level = "error"
        elif status_code >= 400:
            log_level = "warning"
        elif duration_ms > SLOW_REQUEST_THRESHOLD_MS:
            log_level = "warning"

        # Log response
        log_method = getattr(request_logger, log_level)
        log_method(
            "Request completed",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            is_slow=duration_ms > SLOW_REQUEST_THRESHOLD_MS
        )

        # Clear context variables
        clear_context()

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """
        Extract client IP address, respecting proxy headers

        Args:
            request: HTTP request

        Returns:
            Client IP address
        """
        # Check for X-Forwarded-For header (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"
