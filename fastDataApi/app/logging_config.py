"""
Centralized logging configuration for fastDataApi

Configures structured logging with JSON output for production
and human-readable output for development.
"""
import logging
import os
import sys
from typing import Any
import structlog
from pythonjsonlogger import jsonlogger


# Environment variables for logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json").lower()  # json or console
LOG_OUTPUT = os.getenv("LOG_OUTPUT", "stdout").lower()  # stdout, file, or both
LOG_FILE = os.getenv("LOG_FILE", "/var/log/app/fastdataapi.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# Service metadata
SERVICE_NAME = "fastDataApi"
SERVICE_VERSION = "1.0.0"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def add_service_context(logger: Any, method_name: str, event_dict: dict) -> dict:
    """
    Add service-level context to all log entries
    """
    event_dict["service"] = SERVICE_NAME
    event_dict["version"] = SERVICE_VERSION
    event_dict["environment"] = ENVIRONMENT
    return event_dict


def configure_logging():
    """
    Configure structured logging for the application
    """
    # Determine numeric log level
    numeric_level = getattr(logging, LOG_LEVEL, logging.INFO)

    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_service_context,
    ]

    # Add appropriate renderer based on format
    if LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    handlers = []

    # Console/stdout handler
    if LOG_OUTPUT in ["stdout", "both"]:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)

        if LOG_FORMAT == "json":
            # JSON formatter for structured logs
            json_formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s",
                rename_fields={
                    "asctime": "timestamp",
                    "name": "logger",
                    "levelname": "level",
                }
            )
            console_handler.setFormatter(json_formatter)
        else:
            # Human-readable formatter
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_formatter)

        handlers.append(console_handler)

    # File handler
    if LOG_OUTPUT in ["file", "both"]:
        from logging.handlers import RotatingFileHandler

        # Ensure log directory exists
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setLevel(numeric_level)

        # Always use JSON format for file output
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "name": "logger",
                "levelname": "level",
            }
        )
        file_handler.setFormatter(json_formatter)
        handlers.append(file_handler)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add configured handlers
    for handler in handlers:
        root_logger.addHandler(handler)

    # Set log levels for noisy third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if os.getenv("DB_SQL_ECHO", "false").lower() == "true" else logging.WARNING
    )

    # Log configuration summary
    logger = structlog.get_logger(__name__)
    logger.info(
        "Logging configured",
        log_level=LOG_LEVEL,
        log_format=LOG_FORMAT,
        log_output=LOG_OUTPUT,
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        environment=ENVIRONMENT
    )

    return logger


def get_logger(name: str = None):
    """
    Get a configured logger instance

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        structlog logger instance
    """
    return structlog.get_logger(name)
