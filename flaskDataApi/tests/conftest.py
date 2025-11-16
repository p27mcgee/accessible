"""
Pytest configuration and shared fixtures for flaskDataApi tests

This module provides:
- Test database setup with SQLite in-memory database
- Flask test client fixture
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
from sqlalchemy.pool import StaticPool

# Set test environment variables before importing app
os.environ["DB_SQL_ECHO"] = "false"
os.environ["CORS_ORIGINS"] = "http://localhost"
os.environ["TESTING"] = "true"

from app import create_app
from app.database import db as _db
from app.models import Artist, Song


@pytest.fixture(scope='session')
def app():
    """
    Create Flask app for testing with in-memory SQLite database.

    Session-scoped to create the app once for all tests.
    """
    # Set test configuration before creating app
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['TESTING'] = 'true'

    # Create test app - it will use the environment variable for database URI
    # We need to patch the database configuration in the create_app function
    import app as app_module

    # Temporarily override the init_db function to use SQLite
    original_init_db = app_module.database.init_db

    def test_init_db(flask_app):
        """Override init_db to use SQLite for testing"""
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        flask_app.config['TESTING'] = True
        flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        flask_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool
        }
        _db.init_app(flask_app)

    # Patch and create app
    app_module.database.init_db = test_init_db
    test_app = create_app()
    app_module.database.init_db = original_init_db

    # Create tables
    with test_app.app_context():
        _db.create_all()

    yield test_app

    # Cleanup
    with test_app.app_context():
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Create Flask test client.

    Function-scoped so each test gets a fresh client.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """
    Create a fresh database session for each test.

    This fixture:
    1. Creates all tables
    2. Yields a database session
    3. Rolls back any changes and clears tables after the test
    """
    with app.app_context():
        # Clear all data from tables
        _db.session.query(Song).delete()
        _db.session.query(Artist).delete()
        _db.session.commit()

        yield _db.session

        # Rollback and clear after test
        _db.session.rollback()
        _db.session.query(Song).delete()
        _db.session.query(Artist).delete()
        _db.session.commit()


@pytest.fixture
def sample_artist(app, db_session):
    """
    Create a sample artist in the database.

    Args:
        app: Flask app
        db_session: Database session

    Returns:
        Artist: Created artist
    """
    with app.app_context():
        artist = Artist(name="David Bowie")
        db_session.add(artist)
        db_session.commit()
        db_session.refresh(artist)
        return artist


@pytest.fixture
def sample_artists(app, db_session):
    """
    Create multiple sample artists for pagination testing.

    Args:
        app: Flask app
        db_session: Database session

    Returns:
        list[Artist]: List of created artists
    """
    with app.app_context():
        artists = [
            Artist(name="David Bowie"),
            Artist(name="The Beatles"),
            Artist(name="Pink Floyd"),
            Artist(name="Led Zeppelin"),
            Artist(name="Queen"),
            Artist(name="The Rolling Stones"),
            Artist(name="Nirvana"),
            Artist(name="Radiohead"),
            Artist(name="Coldplay"),
            Artist(name="U2"),
            Artist(name="The Who"),
            Artist(name="AC/DC"),
        ]

        for artist in artists:
            db_session.add(artist)

        db_session.commit()

        for artist in artists:
            db_session.refresh(artist)

        return artists


@pytest.fixture
def sample_song(app, db_session, sample_artist):
    """
    Create a sample song in the database.

    Args:
        app: Flask app
        db_session: Database session
        sample_artist: Artist fixture

    Returns:
        Song: Created song
    """
    from datetime import date

    with app.app_context():
        song = Song(
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
def sample_songs(app, db_session, sample_artist):
    """
    Create multiple sample songs for pagination testing.

    Args:
        app: Flask app
        db_session: Database session
        sample_artist: Artist fixture

    Returns:
        list[Song]: List of created songs
    """
    from datetime import date

    with app.app_context():
        songs = [
            Song(
                title="Space Oddity",
                artistID=sample_artist.id,
                released=date(1969, 7, 11),
                URL="https://www.youtube.com/watch?v=iYYRH4apXDo",
                distance=100.5
            ),
            Song(
                title="Life on Mars?",
                artistID=sample_artist.id,
                released=date(1971, 12, 17),
                URL="https://www.youtube.com/watch?v=AZKcl4-tcuo",
                distance=225.3
            ),
            Song(
                title="Starman",
                artistID=sample_artist.id,
                released=date(1972, 4, 28),
                URL="https://www.youtube.com/watch?v=tRcPA7Fzebw",
                distance=300.0
            ),
            Song(
                title="Heroes",
                artistID=sample_artist.id,
                released=date(1977, 9, 23),
                URL="https://www.youtube.com/watch?v=lXgkuM2NhYI",
                distance=150.7
            ),
            Song(
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
def song_without_artist(app, db_session):
    """
    Create a song without an associated artist.

    Args:
        app: Flask app
        db_session: Database session

    Returns:
        Song: Created song with no artist
    """
    from datetime import date

    with app.app_context():
        song = Song(
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
