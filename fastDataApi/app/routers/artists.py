"""
Artist REST API endpoints

API endpoints:
- GET    /v1/artists      - List all artists (paginated)
- GET    /v1/artists/{id} - Get one artist
- POST   /v1/artists      - Create new artist
- PUT    /v1/artists/{id} - Update artist
- DELETE /v1/artists/{id} - Delete artist
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from math import ceil

from app.database import get_db
from app.models import Artist as ArtistModel
from app.schemas import (
    Artist, ArtistCreate, ArtistUpdate,
    PaginatedArtists, PaginationMetadata
)
from app.utils.logger import get_logger_with_context

# Get logger
logger = get_logger_with_context(__name__)

router = APIRouter(
    prefix="/v1/artists",
    tags=["artists"]
)


@router.get("", response_model=PaginatedArtists)
def get_all_artists(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    db: Session = Depends(get_db)
):
    """
    Get all artists with pagination

    - **page**: Page number starting from 1
    - **page_size**: Number of items per page (default: 10, max: 100)

    Returns paginated list of artists with pagination metadata.
    """
    # Log operation
    logger.info(
        "Fetching paginated artists",
        operation="list",
        entity_type="artist",
        page=page,
        page_size=page_size
    )

    # Get total count
    total_items = db.query(ArtistModel).count()

    # Calculate pagination
    total_pages = ceil(total_items / page_size) if total_items > 0 else 0
    offset = (page - 1) * page_size

    # Get paginated items
    artists = db.query(ArtistModel).offset(offset).limit(page_size).all()

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
        "Artists retrieved successfully",
        operation="list",
        entity_type="artist",
        items_returned=len(artists),
        total_items=total_items,
        page=page
    )

    return PaginatedArtists(items=artists, pagination=pagination)


@router.get("/{id}", response_model=Artist)
def get_artist(id: int, db: Session = Depends(get_db)):
    """Get one artist by ID"""
    logger.info(
        "Fetching artist by ID",
        operation="read",
        entity_type="artist",
        entity_id=id
    )

    artist = db.query(ArtistModel).filter(ArtistModel.id == id).first()
    if artist is None:
        logger.warning(
            "Artist not found",
            operation="read",
            entity_type="artist",
            entity_id=id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {id} not found"
        )

    logger.info(
        "Artist retrieved successfully",
        operation="read",
        entity_type="artist",
        entity_id=id,
        name=artist.name
    )
    return artist


@router.post("", response_model=Artist, status_code=status.HTTP_201_CREATED)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    """Create a new artist"""
    logger.info(
        "Creating new artist",
        operation="create",
        entity_type="artist",
        name=artist.name
    )

    db_artist = ArtistModel(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)

    logger.info(
        "Artist created successfully",
        operation="create",
        entity_type="artist",
        entity_id=db_artist.id,
        name=db_artist.name
    )
    return db_artist


@router.put("/{id}", response_model=Artist)
def update_artist(id: int, artist: ArtistUpdate, db: Session = Depends(get_db)):
    """Update an existing artist or create if not exists"""
    logger.info(
        "Updating artist",
        operation="update",
        entity_type="artist",
        entity_id=id,
        name=artist.name
    )

    db_artist = db.query(ArtistModel).filter(ArtistModel.id == id).first()

    if db_artist is None:
        # Create new artist with specified ID
        logger.info(
            "Artist not found, creating new artist with specified ID",
            operation="update",
            entity_type="artist",
            entity_id=id,
            upsert=True
        )
        db_artist = ArtistModel(id=id, name=artist.name)
        db.add(db_artist)
    else:
        # Update existing artist
        db_artist.name = artist.name

    db.commit()
    db.refresh(db_artist)

    logger.info(
        "Artist updated successfully",
        operation="update",
        entity_type="artist",
        entity_id=db_artist.id,
        name=db_artist.name
    )
    return db_artist


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(id: int, db: Session = Depends(get_db)):
    """Delete an artist"""
    logger.info(
        "Deleting artist",
        operation="delete",
        entity_type="artist",
        entity_id=id
    )

    db_artist = db.query(ArtistModel).filter(ArtistModel.id == id).first()
    if db_artist is None:
        logger.warning(
            "Artist not found for deletion",
            operation="delete",
            entity_type="artist",
            entity_id=id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {id} not found"
        )

    artist_name = db_artist.name
    db.delete(db_artist)
    db.commit()

    logger.info(
        "Artist deleted successfully",
        operation="delete",
        entity_type="artist",
        entity_id=id,
        name=artist_name
    )
    return None
