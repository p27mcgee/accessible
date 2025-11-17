"""
Pytest configuration and shared fixtures for fastDataApi tests

This module provides:
- Test database setup with SQLite in-memory database
- FastAPI TestClient fixture
- Database session fixtures
- Test data factories
"""
import os
import sys
from unittest.mock import MagicMock

# Mock pyodbc before any app imports to prevent ODBC driver requirements
mock_pyodbc = MagicMock()
mock_pyodbc.version = "5.0.1"  # Pretend we have pyodbc version 5.0.1
mock_pyodbc.pooling = False
sys.modules['pyodbc'] = mock_pyodbc

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ["DB_SQL_ECHO"] = "false"
os.environ["CORS_ORIGINS"] = "http://localhost"

# Import after mocking pyodbc
from app.main import app
from app.database import Base, get_db
from app.models import Artist as ArtistModel, Song as SongModel


# Create in-memory SQLite database for testing
# Using StaticPool to ensure the same connection is reused across requests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.

    This fixture:
    1. Creates all tables in the test database
    2. Yields a database session
    3. Rolls back any changes and drops all tables after the test

    Yields:
        Session: SQLAlchemy database session
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Drop all tables to ensure clean state
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI TestClient with overridden database dependency.

    Args:
        db_session: Database session from db_session fixture

    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_artist(db_session: Session) -> ArtistModel:
    """
    Create a sample artist in the database.

    Args:
        db_session: Database session

    Returns:
        ArtistModel: Created artist
    """
    artist = ArtistModel(name="David Bowie")
    db_session.add(artist)
    db_session.commit()
    db_session.refresh(artist)
    return artist


@pytest.fixture
def sample_artists(db_session: Session) -> list[ArtistModel]:
    """
    Create multiple sample artists for pagination testing.

    Args:
        db_session: Database session

    Returns:
        list[ArtistModel]: List of created artists
    """
    artists = [
        ArtistModel(name="David Bowie"),
        ArtistModel(name="The Beatles"),
        ArtistModel(name="Pink Floyd"),
        ArtistModel(name="Led Zeppelin"),
        ArtistModel(name="Queen"),
        ArtistModel(name="The Rolling Stones"),
        ArtistModel(name="Nirvana"),
        ArtistModel(name="Radiohead"),
        ArtistModel(name="Coldplay"),
        ArtistModel(name="U2"),
        ArtistModel(name="The Who"),
        ArtistModel(name="AC/DC"),
    ]

    for artist in artists:
        db_session.add(artist)

    db_session.commit()

    for artist in artists:
        db_session.refresh(artist)

    return artists


@pytest.fixture
def sample_song(db_session: Session, sample_artist: ArtistModel) -> SongModel:
    """
    Create a sample song in the database.

    Args:
        db_session: Database session
        sample_artist: Artist fixture

    Returns:
        SongModel: Created song
    """
    from datetime import date

    song = SongModel(
        title="Space Oddity",
        artistID=sample_artist.id,
        released=date(1969, 7, 11),
        URL="https://www.youtube.com/watch?v=iYYRH4apXDo",
        distance=100.5
    )
    db_session.add(song)
    db_session.commit()
    db_session.refresh(song)
    return song


@pytest.fixture
def sample_songs(db_session: Session, sample_artist: ArtistModel) -> list[SongModel]:
    """
    Create multiple sample songs for pagination testing.

    Args:
        db_session: Database session
        sample_artist: Artist fixture

    Returns:
        list[SongModel]: List of created songs
    """
    from datetime import date

    songs = [
        SongModel(
            title="Space Oddity",
            artistID=sample_artist.id,
            released=date(1969, 7, 11),
            URL="https://www.youtube.com/watch?v=iYYRH4apXDo",
            distance=100.5
        ),
        SongModel(
            title="Life on Mars?",
            artistID=sample_artist.id,
            released=date(1971, 12, 17),
            URL="https://www.youtube.com/watch?v=AZKcl4-tcuo",
            distance=225.3
        ),
        SongModel(
            title="Starman",
            artistID=sample_artist.id,
            released=date(1972, 4, 28),
            URL="https://www.youtube.com/watch?v=tRcPA7Fzebw",
            distance=300.0
        ),
        SongModel(
            title="Heroes",
            artistID=sample_artist.id,
            released=date(1977, 9, 23),
            URL="https://www.youtube.com/watch?v=lXgkuM2NhYI",
            distance=150.7
        ),
        SongModel(
            title="Ashes to Ashes",
            artistID=sample_artist.id,
            released=date(1980, 8, 1),
            URL="https://www.youtube.com/watch?v=CMThz7eQ6K0",
            distance=420.9
        ),
    ]

    for song in songs:
        db_session.add(song)

    db_session.commit()

    for song in songs:
        db_session.refresh(song)

    return songs


@pytest.fixture
def song_without_artist(db_session: Session) -> SongModel:
    """
    Create a song without an associated artist.

    Args:
        db_session: Database session

    Returns:
        SongModel: Created song with no artist
    """
    from datetime import date

    song = SongModel(
        title="Unknown Song",
        artistID=None,
        released=date(2000, 1, 1),
        URL="https://example.com/song",
        distance=50.0
    )
    db_session.add(song)
    db_session.commit()
    db_session.refresh(song)
    return song
