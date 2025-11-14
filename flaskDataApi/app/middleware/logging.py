"""
Request/Response logging middleware for Flask

Logs all HTTP requests and responses with structured data including:
- Request ID correlation
- Timing information
- Status codes
- Client information
"""
import time
import os
from flask import request, g
import structlog

from app.utils.logger import (
    generate_request_id,
    set_request_id,
    get_request_id,
    mask_sensitive_data
)

# Get logger
logger = structlog.get_logger(__name__)

# Threshold for slow request warnings (milliseconds)
SLOW_REQUEST_THRESHOLD_MS = int(
    os.getenv("SLOW_REQUEST_THRESHOLD_MS", "1000")
)


def setup_request_logging(app):
    """
    Set up request/response logging hooks for Flask app

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request():
        """
        Log incoming request and set up request context
        """
        # Generate and set request ID
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        set_request_id(request_id)

        # Store request start time
        g.request_start_time = time.time()

        # Bind logger with request ID
        request_logger = logger.bind(request_id=request_id)

        # Extract request information
        client_ip = get_client_ip()
        user_agent = request.headers.get("User-Agent", "unknown")
        method = request.method
        path = request.path
        query_string = request.query_string.decode("utf-8") if request.query_string else None

        # Log incoming request
        request_logger.info(
            "Request started",
            method=method,
            path=path,
            query_params=mask_sensitive_data(query_string) if query_string else None,
            client_ip=client_ip,
            user_agent=user_agent,
        )

    @app.after_request
    def after_request(response):
        """
        Log outgoing response

        Args:
            response: Flask response object

        Returns:
            Modified response with request ID header
        """
        # Get request ID and start time
        request_id = get_request_id()
        start_time = getattr(g, 'request_start_time', None)

        if request_id:
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Calculate duration
            if start_time:
                duration_ms = (time.time() - start_time) * 1000

                # Bind logger with request ID
                request_logger = logger.bind(request_id=request_id)

                # Determine log level based on status code and duration
                status_code = response.status_code
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
                    method=request.method,
                    path=request.path,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    is_slow=duration_ms > SLOW_REQUEST_THRESHOLD_MS
                )

        return response

    @app.teardown_request
    def teardown_request(exception=None):
        """
        Log request errors and clean up

        Args:
            exception: Exception that occurred during request (if any)
        """
        if exception:
            # Get request ID
            request_id = get_request_id()
            start_time = getattr(g, 'request_start_time', None)

            if request_id:
                # Bind logger with request ID
                request_logger = logger.bind(request_id=request_id)

                # Calculate duration if available
                duration_ms = None
                if start_time:
                    duration_ms = (time.time() - start_time) * 1000

                # Log error
                request_logger.error(
                    "Request failed with exception",
                    method=request.method,
                    path=request.path,
                    duration_ms=round(duration_ms, 2) if duration_ms else None,
                    error_type=type(exception).__name__,
                    error_message=str(exception),
                    exc_info=True
                )


def get_client_ip() -> str:
    """
    Extract client IP address, respecting proxy headers

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

    # Fall back to remote address
    return request.remote_addr or "unknown"
