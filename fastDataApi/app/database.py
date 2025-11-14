"""
Database configuration and session management for SQL Server
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import os
import time
from typing import Dict, Any
import structlog

# Get structured logger
logger = structlog.get_logger(__name__)

# Slow query threshold in milliseconds
SLOW_QUERY_THRESHOLD_MS = int(os.getenv("SLOW_QUERY_THRESHOLD_MS", "100"))

# Dictionary to track query start times
_query_start_times: Dict[Any, float] = {}

# SQL Server connection parameters
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "starsongs")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "YourStrong@Passw0rd")

# Connection pool parameters
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_POOL_MAX_OVERFLOW = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
DB_POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
DB_SQL_ECHO = os.getenv("DB_SQL_ECHO", "false").lower() == "true"

# SQL Server connection string using pyodbc
# TrustServerCertificate=yes is needed for self-signed certificates in Docker
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={DB_SERVER},{DB_PORT};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
    f"TrustServerCertificate=yes"
)
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=DB_SQL_ECHO,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_POOL_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=DB_POOL_PRE_PING,
)

# Log connection pool configuration
logger.info(f"Database pool configured: size={DB_POOL_SIZE}, "
            f"max_overflow={DB_POOL_MAX_OVERFLOW}, "
            f"timeout={DB_POOL_TIMEOUT}s, "
            f"recycle={DB_POOL_RECYCLE}s, "
            f"pre_ping={DB_POOL_PRE_PING}")


# Add connection pool event listeners for monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when a new connection is created"""
    logger.debug(
        "Database connection established",
        connection_id=id(connection_record)
    )


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool"""
    pool = engine.pool
    logger.debug(
        "Connection checked out from pool",
        connection_id=id(connection_record),
        pool_size=pool.size(),
        checked_out=pool.checkedout(),
        overflow=pool.overflow()
    )


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log when a connection is returned to the pool"""
    pool = engine.pool
    logger.debug(
        "Connection returned to pool",
        connection_id=id(connection_record),
        pool_size=pool.size(),
        checked_out=pool.checkedout()
    )


# Query performance monitoring
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """
    Track query start time for performance monitoring
    """
    conn.info.setdefault('query_start_time', []).append(time.time())

    # Log query start (debug level)
    logger.debug(
        "Executing SQL query",
        statement=statement[:200] if len(statement) > 200 else statement,  # Truncate long queries
        parameters=str(parameters)[:100] if parameters else None
    )


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """
    Log query execution time and detect slow queries
    """
    # Calculate query duration
    query_start_times = conn.info.get('query_start_time', [])
    if query_start_times:
        start_time = query_start_times.pop()
        duration_ms = (time.time() - start_time) * 1000

        # Determine log level based on duration
        if duration_ms > SLOW_QUERY_THRESHOLD_MS:
            logger.warning(
                "Slow query detected",
                duration_ms=round(duration_ms, 2),
                statement=statement[:200] if len(statement) > 200 else statement,
                threshold_ms=SLOW_QUERY_THRESHOLD_MS,
                is_slow=True
            )
        else:
            logger.debug(
                "Query completed",
                duration_ms=round(duration_ms, 2)
            )


# Handle database errors
@event.listens_for(engine, "handle_error")
def handle_error(exception_context):
    """
    Log database errors with context
    """
    logger.error(
        "Database error occurred",
        error_type=type(exception_context.original_exception).__name__,
        error_message=str(exception_context.original_exception),
        statement=exception_context.statement[:200] if exception_context.statement else None,
        parameters=str(exception_context.parameters)[:100] if exception_context.parameters else None,
        exc_info=True
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
