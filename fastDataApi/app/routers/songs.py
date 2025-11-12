"""
Song REST API endpoints

API endpoints:
- GET    /v1/songs      - List all songs
- GET    /v1/songs/{id} - Get one song
- POST   /v1/songs      - Create new song
- PUT    /v1/songs/{id} - Update song
- DELETE /v1/songs/{id} - Delete song
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Song as SongModel, Artist as ArtistModel
from app.schemas import Song, SongCreate, SongUpdate

router = APIRouter(
    prefix="/v1/songs",
    tags=["songs"]
)


@router.get("", response_model=List[Song])
def get_all_songs(db: Session = Depends(get_db)):
    """Get all songs"""
    songs = db.query(SongModel).all()
    return [Song.from_orm(song) for song in songs]


@router.get("/{id}", response_model=Song)
def get_song(id: int, db: Session = Depends(get_db)):
    """Get one song by ID"""
    song = db.query(SongModel).filter(SongModel.id == id).first()
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {id} not found"
        )
    return Song.from_orm(song)


@router.post("", response_model=Song, status_code=status.HTTP_201_CREATED)
def create_song(song: SongCreate, db: Session = Depends(get_db)):
    """Create a new song"""
    # Validate artist exists if artist_id is provided
    if song.artist_id is not None:
        artist = db.query(ArtistModel).filter(ArtistModel.id == song.artist_id).first()
        if artist is None:
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
    return Song.from_orm(db_song)


@router.put("/{id}", response_model=Song)
def update_song(id: int, song: SongUpdate, db: Session = Depends(get_db)):
    """Update an existing song or create if not exists"""
    # Validate artist exists if artist_id is provided
    if song.artist_id is not None:
        artist = db.query(ArtistModel).filter(ArtistModel.id == song.artist_id).first()
        if artist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {song.artist_id} not found"
            )

    db_song = db.query(SongModel).filter(SongModel.id == id).first()

    if db_song is None:
        # Create new song with specified ID
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
    return Song.from_orm(db_song)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(id: int, db: Session = Depends(get_db)):
    """Delete a song"""
    db_song = db.query(SongModel).filter(SongModel.id == id).first()
    if db_song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {id} not found"
        )

    db.delete(db_song)
    db.commit()
    return None
