"""
SQLAlchemy ORM models for the Accessible API (Flask version)
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import db


class Artist(db.Model):
    """Artist entity representing a music artist"""
    __tablename__ = "Artist"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), nullable=False)

    # Relationship to songs (one-to-many)
    songs = relationship("Song", back_populates="artist")

    def __repr__(self):
        return f"<Artist(id={self.id}, name='{self.name}')>"


class Song(db.Model):
    """Song entity representing a music song with space-themed distance"""
    __tablename__ = "Song"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(64), nullable=False)
    artistID = Column(Integer, ForeignKey("Artist.id"), nullable=True)
    released = Column(Date, nullable=True)
    URL = Column(String(1024), nullable=True)
    distance = Column(Float, nullable=True)

    # Relationship to artist (many-to-one)
    artist = relationship("Artist", back_populates="songs")

    def __repr__(self):
        return f"<Song(id={self.id}, title='{self.title}', artistID={self.artistID})>"
