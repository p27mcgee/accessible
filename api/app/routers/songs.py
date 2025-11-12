"""
Song REST API endpoints
Corresponds to SongRestControllerV1.java

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
from app.models import Song, Artist
from app.schemas import SongDto, SongCreate, SongUpdate

router = APIRouter(
    prefix="/v1/songs",
    tags=["songs"]
)


def convert_song_to_dto(song: Song) -> SongDto:
    """
    Convert SQLAlchemy Song model to SongDto
    Maps database column names to DTO field names
    """
    return SongDto(
        id=song.id,
        title=song.title,
        artistId=song.artistID,
        releaseDate=song.released,
        url=song.URL,
        distance=song.distance
    )


@router.get("", response_model=List[SongDto])
def get_all_songs(db: Session = Depends(get_db)):
    """
    Get all songs
    Corresponds to: SongRestControllerV1.all()
    """
    songs = db.query(Song).all()
    return [convert_song_to_dto(song) for song in songs]


@router.get("/{id}", response_model=SongDto)
def get_song(id: int, db: Session = Depends(get_db)):
    """
    Get one song by ID
    Corresponds to: SongRestControllerV1.one(Integer id)
    """
    song = db.query(Song).filter(Song.id == id).first()
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {id} not found"
        )
    return convert_song_to_dto(song)


@router.post("", response_model=SongDto, status_code=status.HTTP_201_CREATED)
def create_song(song: SongCreate, db: Session = Depends(get_db)):
    """
    Create a new song
    Corresponds to: SongRestControllerV1.newSong(SongDto newSong)
    """
    # Validate artist exists if artistId is provided
    if song.artistId is not None:
        artist = db.query(Artist).filter(Artist.id == song.artistId).first()
        if artist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {song.artistId} not found"
            )

    # Create new song (map DTO field names to database column names)
    db_song = Song(
        title=song.title,
        artistID=song.artistId,
        released=song.releaseDate,
        URL=song.url,
        distance=song.distance
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return convert_song_to_dto(db_song)


@router.put("/{id}", response_model=SongDto)
def update_song(id: int, song: SongUpdate, db: Session = Depends(get_db)):
    """
    Update an existing song or create if not exists
    Corresponds to: SongRestControllerV1.replaceSong(SongDto newSong, Integer id)
    """
    # Validate artist exists if artistId is provided
    if song.artistId is not None:
        artist = db.query(Artist).filter(Artist.id == song.artistId).first()
        if artist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artist with id {song.artistId} not found"
            )

    db_song = db.query(Song).filter(Song.id == id).first()

    if db_song is None:
        # Create new song with specified ID (mimics Java behavior)
        db_song = Song(
            id=id,
            title=song.title,
            artistID=song.artistId,
            released=song.releaseDate,
            URL=song.url,
            distance=song.distance
        )
        db.add(db_song)
    else:
        # Update existing song
        db_song.title = song.title
        db_song.artistID = song.artistId
        db_song.released = song.releaseDate
        db_song.URL = song.url
        db_song.distance = song.distance

    db.commit()
    db.refresh(db_song)
    return convert_song_to_dto(db_song)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(id: int, db: Session = Depends(get_db)):
    """
    Delete a song
    Corresponds to: SongRestControllerV1.deleteSong(Integer id)
    """
    db_song = db.query(Song).filter(Song.id == id).first()
    if db_song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {id} not found"
        )

    db.delete(db_song)
    db.commit()
    return None
