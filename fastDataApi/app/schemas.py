"""
Pydantic schemas (DTOs) matching the Java DTOs from star-songs project
- ArtistDto corresponds to com.mcgeecahill.starsongs.songdata.dto.ArtistDto
- SongDto corresponds to com.mcgeecahill.starsongs.songdata.dto.SongDto
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


class ArtistDto(ArtistBase):
    """
    Artist DTO - corresponds to ArtistDto.java
    Used for responses
    """
    id: int

    model_config = ConfigDict(from_attributes=True)


class SongBase(BaseModel):
    """Base schema for Song with common fields"""
    title: str
    artistId: Optional[int] = None
    releaseDate: Optional[date] = None
    url: Optional[str] = None
    distance: Optional[float] = None


class SongCreate(SongBase):
    """Schema for creating a new Song"""
    pass


class SongUpdate(SongBase):
    """Schema for updating a Song"""
    pass


class SongDto(SongBase):
    """
    Song DTO - corresponds to SongDto.java
    Used for responses

    Note: The Java DTO uses 'artistId', 'releaseDate', and 'url'
    which we match here for API compatibility
    """
    id: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_model(cls, song_model):
        """
        Convert SQLAlchemy model to DTO
        Maps database column names to DTO field names
        """
        return cls(
            id=song_model.id,
            title=song_model.title,
            artistId=song_model.artistID,
            releaseDate=song_model.released,
            url=song_model.URL,
            distance=song_model.distance
        )
