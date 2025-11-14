"""
Database configuration and session management for SQL Server with Flask
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase
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

# Create base class for models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with custom base
db = SQLAlchemy(model_class=Base)


def init_db(app):
    """
    Initialize database with Flask app and configure connection pooling
    """
    # SQL Server connection parameters
    db_server = os.getenv("DB_SERVER", "localhost")
    db_port = os.getenv("DB_PORT", "1433")
    db_name = os.getenv("DB_NAME", "starsongs")
    db_user = os.getenv("DB_USER", "sa")
    db_password = os.getenv("DB_PASSWORD", "YourStrong@Passw0rd")

    # Connection pool parameters
    db_pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
    db_pool_max_overflow = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))
    db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    db_pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    db_pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
    db_sql_echo = os.getenv("DB_SQL_ECHO", "false").lower() == "true"

    # SQL Server connection string using pyodbc
    # TrustServerCertificate=yes is needed for self-signed certificates in Docker
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={db_server},{db_port};"
        f"DATABASE={db_name};"
        f"UID={db_user};"
        f"PWD={db_password};"
        f"TrustServerCertificate=yes"
    )

    sqlalchemy_database_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"

    # Configure Flask-SQLAlchemy with connection pooling
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = db_sql_echo
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': db_pool_size,
        'max_overflow': db_pool_max_overflow,
        'pool_timeout': db_pool_timeout,
        'pool_recycle': db_pool_recycle,
        'pool_pre_ping': db_pool_pre_ping,
    }

    # Log connection pool configuration
    logger.info(f"Database pool configured: size={db_pool_size}, "
                f"max_overflow={db_pool_max_overflow}, "
                f"timeout={db_pool_timeout}s, "
                f"recycle={db_pool_recycle}s, "
                f"pre_ping={db_pool_pre_ping}")

    # Initialize db with app
    db.init_app(app)

    # Add connection pool event listeners for monitoring
    @event.listens_for(db.engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Log when a new connection is created"""
        logger.debug(
            "Database connection established",
            connection_id=id(connection_record)
        )

    @event.listens_for(db.engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Log when a connection is checked out from the pool"""
        pool = db.engine.pool
        logger.debug(
            "Connection checked out from pool",
            connection_id=id(connection_record),
            pool_size=pool.size(),
            checked_out=pool.checkedout(),
            overflow=pool.overflow()
        )

    @event.listens_for(db.engine, "checkin")
    def receive_checkin(dbapi_conn, connection_record):
        """Log when a connection is returned to the pool"""
        pool = db.engine.pool
        logger.debug(
            "Connection returned to pool",
            connection_id=id(connection_record),
            pool_size=pool.size(),
            checked_out=pool.checkedout()
        )

    # Query performance monitoring
    @event.listens_for(db.engine, "before_cursor_execute")
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

    @event.listens_for(db.engine, "after_cursor_execute")
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
    @event.listens_for(db.engine, "handle_error")
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
