"""
Song REST API endpoints

API endpoints:
- GET    /v1/songs      - List all songs (paginated)
- GET    /v1/songs/{id} - Get one song
- POST   /v1/songs      - Create new song
- PUT    /v1/songs/{id} - Update song
- DELETE /v1/songs/{id} - Delete song
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from math import ceil

from app.database import get_db
from app.models import Song as SongModel, Artist as ArtistModel
from app.schemas import (
    Song, SongCreate, SongUpdate,
    PaginatedSongs, PaginationMetadata
)
from app.utils.logger import get_logger_with_context, log_operation

# Get logger
logger = get_logger_with_context(__name__)

router = APIRouter(
    prefix="/v1/songs",
    tags=["songs"]
)


@router.get("", response_model=PaginatedSongs)
def get_all_songs(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    db: Session = Depends(get_db)
):
    """
    Get all songs with pagination

    - **page**: Page number starting from 1
    - **page_size**: Number of items per page (default: 10, max: 100)

    Returns paginated list of songs with pagination metadata.
    """
    # Log operation
    logger.info(
        "Fetching paginated songs",
        operation="list",
        entity_type="song",
        page=page,
        page_size=page_size
    )

    # Get total count
    total_items = db.query(SongModel).count()

    # Calculate pagination
    total_pages = ceil(total_items / page_size) if total_items > 0 else 0
    offset = (page - 1) * page_size

    # Get paginated items
    songs = db.query(SongModel).offset(offset).limit(page_size).all()

    # Convert to schema
    items = [Song.from_orm(song) for song in songs]

    # Build pagination metadata
    pagination = PaginationMetadata(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )

    # Log result
    logger.info(
        "Songs retrieved successfully",
        operation="list",
        entity_type="song",
        items_returned=len(items),
        total_items=total_items,
        page=page
    )

    return PaginatedSongs(items=items, pagination=pagination)


@router.get("/{id}", response_model=Song)
def get_song(id: int, db: Session = Depends(get_db)):
    """Get one song by ID"""
    logger.info(
        "Fetching song by ID",
        operation="read",
        entity_type="song",
        entity_id=id
    )

    song = db.query(SongModel).filter(SongModel.id == id).first()
    if song is None:
        logger.warning(
            "Song not found",
            operation="read",
            entity_type="song",
            entity_id=id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {id} not found"
        )

    logger.info(
        "Song retrieved successfully",
        operation="read",
        entity_type="song",
        entity_id=id,
        title=song.title
    )
    return Song.from_orm(song)


@router.post("", response_model=Song, status_code=status.HTTP_201_CREATED)
def create_song(song: SongCreate, db: Session = Depends(get_db)):
    """Create a new song"""
    logger.info(
        "Creating new song",
        operation="create",
        entity_type="song",
        title=song.title,
        artist_id=song.artist_id
    )

    # Validate artist exists if artist_id is provided
    if song.artist_id is not None:
        artist = db.query(ArtistModel).filter(ArtistModel.id == song.artist_id).first()
        if artist is None:
            logger.warning(
                "Artist not found for song creation",
                operation="create",
                entity_type="song",
                artist_id=song.artist_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {song.artist_id} not found"
            )

    # Create new song - map schema fields to database columns
    db_song = SongModel(
        title=song.title,
        artistID=song.artist_id,
        released=song.release_date,
        URL=song.url,
        distance=song.distance
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)

    logger.info(
        "Song created successfully",
        operation="create",
        entity_type="song",
        entity_id=db_song.id,
        title=db_song.title
    )
    return Song.from_orm(db_song)


@router.put("/{id}", response_model=Song)
def update_song(id: int, song: SongUpdate, db: Session = Depends(get_db)):
    """Update an existing song or create if not exists"""
    logger.info(
        "Updating song",
        operation="update",
        entity_type="song",
        entity_id=id,
        title=song.title
    )

    # Validate artist exists if artist_id is provided
    if song.artist_id is not None:
        artist = db.query(ArtistModel).filter(ArtistModel.id == song.artist_id).first()
        if artist is None:
            logger.warning(
                "Artist not found for song update",
                operation="update",
                entity_type="song",
                entity_id=id,
                artist_id=song.artist_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {song.artist_id} not found"
            )

    db_song = db.query(SongModel).filter(SongModel.id == id).first()

    if db_song is None:
        # Create new song with specified ID
        logger.info(
            "Song not found, creating new song with specified ID",
            operation="update",
            entity_type="song",
            entity_id=id,
            upsert=True
        )
        db_song = SongModel(
            id=id,
            title=song.title,
            artistID=song.artist_id,
            released=song.release_date,
            URL=song.url,
            distance=song.distance
        )
        db.add(db_song)
    else:
        # Update existing song
        db_song.title = song.title
        db_song.artistID = song.artist_id
        db_song.released = song.release_date
        db_song.URL = song.url
        db_song.distance = song.distance

    db.commit()
    db.refresh(db_song)

    logger.info(
        "Song updated successfully",
        operation="update",
        entity_type="song",
        entity_id=db_song.id,
        title=db_song.title
    )
    return Song.from_orm(db_song)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(id: int, db: Session = Depends(get_db)):
    """Delete a song"""
    logger.info(
        "Deleting song",
        operation="delete",
        entity_type="song",
        entity_id=id
    )

    db_song = db.query(SongModel).filter(SongModel.id == id).first()
    if db_song is None:
        logger.warning(
            "Song not found for deletion",
            operation="delete",
            entity_type="song",
            entity_id=id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {id} not found"
        )

    song_title = db_song.title
    db.delete(db_song)
    db.commit()

    logger.info(
        "Song deleted successfully",
        operation="delete",
        entity_type="song",
        entity_id=id,
        title=song_title
    )
    return None
