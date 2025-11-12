"""
Pydantic schemas for the Accessible API.
Uses Python idiomatic naming conventions (snake_case).
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class ArtistBase(BaseModel):
    """Base schema for Artist with common fields"""
    name: str


class ArtistCreate(ArtistBase):
    """Schema for creating a new Artist"""
    pass


class ArtistUpdate(ArtistBase):
    """Schema for updating an Artist"""
    pass


class Artist(ArtistBase):
    """Artist schema for API responses"""
    id: int

    model_config = ConfigDict(from_attributes=True)


class SongBase(BaseModel):
    """Base schema for Song with common fields"""
    title: str
    artist_id: Optional[int] = None
    release_date: Optional[date] = None
    url: Optional[str] = None
    distance: Optional[float] = None


class SongCreate(SongBase):
    """Schema for creating a new Song"""
    pass


class SongUpdate(SongBase):
    """Schema for updating a Song"""
    pass


class Song(SongBase):
    """
    Song schema for API responses.
    Maps database column names to Pythonic field names.
    """
    id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_orm(cls, song_model):
        """
        Convert SQLAlchemy model to Pydantic schema.
        Maps database column names to snake_case field names.
        """
        return cls(
            id=song_model.id,
            title=song_model.title,
            artist_id=song_model.artistID,
            release_date=song_model.released,
            url=song_model.URL,
            distance=song_model.distance
        )
