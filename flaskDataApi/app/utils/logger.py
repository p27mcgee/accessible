"""
Logger utility functions and helpers for flaskDataApi

Provides context management and helper functions for structured logging.
"""
import uuid
import re
from typing import Optional, Dict, Any
from flask import g, has_request_context
import structlog

# Sensitive data patterns to mask in logs
SENSITIVE_PATTERNS = [
    (re.compile(r'"password"\s*:\s*"[^"]*"', re.IGNORECASE), '"password": "***"'),
    (re.compile(r'"token"\s*:\s*"[^"]*"', re.IGNORECASE), '"token": "***"'),
    (re.compile(r'"api_key"\s*:\s*"[^"]*"', re.IGNORECASE), '"api_key": "***"'),
    (re.compile(r'"authorization"\s*:\s*"[^"]*"', re.IGNORECASE), '"authorization": "***"'),
    (re.compile(r'password=([^&\s]+)', re.IGNORECASE), 'password=***'),
]


def generate_request_id() -> str:
    """
    Generate a unique request ID (UUID4)

    Returns:
        UUID string for request correlation
    """
    return str(uuid.uuid4())


def set_request_id(request_id: str):
    """
    Set the request ID in Flask's g object

    Args:
        request_id: Request correlation ID
    """
    if has_request_context():
        g.request_id = request_id


def get_request_id() -> Optional[str]:
    """
    Get the current request ID from Flask's g object

    Returns:
        Request ID or None if not set
    """
    if has_request_context():
        return getattr(g, 'request_id', None)
    return None


def set_user_context(user_data: Dict[str, Any]):
    """
    Set user context data for logging

    Args:
        user_data: User information to include in logs
    """
    if has_request_context():
        g.user_context = user_data


def get_user_context() -> Optional[Dict[str, Any]]:
    """
    Get user context from current request

    Returns:
        User context dict or None
    """
    if has_request_context():
        return getattr(g, 'user_context', None)
    return None


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive data in log messages

    Args:
        text: Text that may contain sensitive data

    Returns:
        Text with sensitive patterns masked
    """
    if not text:
        return text

    masked_text = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked_text = pattern.sub(replacement, masked_text)

    return masked_text


def get_logger_with_context(name: str = None):
    """
    Get a logger with current request context bound

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger with context bound
    """
    logger = structlog.get_logger(name)

    # Bind request ID if available
    request_id = get_request_id()
    if request_id:
        logger = logger.bind(request_id=request_id)

    # Bind user context if available
    user_context = get_user_context()
    if user_context:
        logger = logger.bind(**user_context)

    return logger


def log_operation(
    logger,
    operation: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    level: str = "info"
):
    """
    Log a business operation with consistent format

    Args:
        logger: Logger instance
        operation: Operation name (create, read, update, delete, list)
        entity_type: Type of entity (artist, song)
        entity_id: ID of the entity (if applicable)
        details: Additional details to log
        level: Log level (info, warning, error)
    """
    log_data = {
        "operation": operation,
        "entity_type": entity_type,
    }

    if entity_id is not None:
        log_data["entity_id"] = entity_id

    if details:
        log_data.update(details)

    log_method = getattr(logger, level, logger.info)
    log_method(f"{entity_type.capitalize()} {operation}", **log_data)


def log_error_with_context(
    logger,
    error: Exception,
    message: str = "An error occurred",
    extra_context: Optional[Dict[str, Any]] = None
):
    """
    Log an error with full context and stack trace

    Args:
        logger: Logger instance
        error: Exception that occurred
        message: Human-readable error message
        extra_context: Additional context to include
    """
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if extra_context:
        error_data.update(extra_context)

    logger.error(
        message,
        **error_data,
        exc_info=True
    )
