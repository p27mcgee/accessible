"""
Database connection and session management for auth database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from auth_lib.config import POSTGRES_AUTH_DB_URL
from auth_lib.models import Base

# Create engine with connection pooling
engine = create_engine(
    POSTGRES_AUTH_DB_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
    echo=False,  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """
    Create all tables in the database
    Should be called on application startup or via migration script
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all tables in the database
    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI that provides a database session

    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database session (useful for Flask and standalone scripts)

    Usage:
        with get_db_context() as db:
            # Use db here
            pass

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """
    Database manager class for use in Flask applications

    Usage:
        db_manager = DatabaseManager()
        db_manager.init_app(app)

        # In routes:
        db = db_manager.get_session()
        # Use db
        db_manager.close_session(db)
    """

    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def init_app(self, app):
        """
        Initialize database with Flask app

        Args:
            app: Flask application instance
        """
        # Store reference in app config
        app.config["AUTH_DB_ENGINE"] = self.engine
        app.config["AUTH_DB_SESSION_FACTORY"] = self.SessionLocal

        # Create tables if they don't exist
        create_tables()

    def get_session(self) -> Session:
        """
        Get a new database session

        Returns:
            Database session
        """
        return self.SessionLocal()

    def close_session(self, session: Session):
        """
        Close a database session

        Args:
            session: Database session to close
        """
        session.close()


# Singleton instance for Flask
db_manager = DatabaseManager()
