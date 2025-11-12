"""
Artist REST API endpoints

API endpoints:
- GET    /v1/artists      - List all artists
- GET    /v1/artists/{id} - Get one artist
- POST   /v1/artists      - Create new artist
- PUT    /v1/artists/{id} - Update artist
- DELETE /v1/artists/{id} - Delete artist
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Artist
from app.schemas import ArtistDto, ArtistCreate, ArtistUpdate

router = APIRouter(
    prefix="/v1/artists",
    tags=["artists"]
)


@router.get("", response_model=List[ArtistDto])
def get_all_artists(db: Session = Depends(get_db)):
    """
    Get all artists
    """
    artists = db.query(Artist).all()
    return artists


@router.get("/{id}", response_model=ArtistDto)
def get_artist(id: int, db: Session = Depends(get_db)):
    """
    Get one artist by ID
    """
    artist = db.query(Artist).filter(Artist.id == id).first()
    if artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {id} not found"
        )
    return artist


@router.post("", response_model=ArtistDto, status_code=status.HTTP_201_CREATED)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    """
    Create a new artist
    """
    db_artist = Artist(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist


@router.put("/{id}", response_model=ArtistDto)
def update_artist(id: int, artist: ArtistUpdate, db: Session = Depends(get_db)):
    """
    Update an existing artist or create if not exists
    """
    db_artist = db.query(Artist).filter(Artist.id == id).first()

    if db_artist is None:
        # Create new artist with specified ID
        db_artist = Artist(id=id, name=artist.name)
        db.add(db_artist)
    else:
        # Update existing artist
        db_artist.name = artist.name

    db.commit()
    db.refresh(db_artist)
    return db_artist


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(id: int, db: Session = Depends(get_db)):
    """
    Delete an artist
    """
    db_artist = db.query(Artist).filter(Artist.id == id).first()
    if db_artist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {id} not found"
        )

    db.delete(db_artist)
    db.commit()
    return None
