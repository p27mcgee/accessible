"""
Marshmallow schemas for the Accessible API.
Uses Python idiomatic naming conventions (snake_case) for API fields.
"""
from marshmallow import Schema, fields, post_load, EXCLUDE
from datetime import date


def song_model_to_dict(song_model):
    """
    Convert SQLAlchemy Song model to dict with snake_case field names.
    Maps database column names (artistID, released, URL) to API field names.
    """
    return {
        'id': song_model.id,
        'title': song_model.title,
        'artist_id': song_model.artistID,
        'release_date': song_model.released,
        'url': song_model.URL,
        'distance': song_model.distance
    }


class ArtistSchema(Schema):
    """Artist schema for API responses and requests"""
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class ArtistCreateSchema(Schema):
    """Schema for creating a new Artist"""
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True)


class ArtistUpdateSchema(Schema):
    """Schema for updating an Artist"""
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True)


class SongSchema(Schema):
    """
    Song schema for API responses.
    Maps database column names to Pythonic field names.
    """
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    artist_id = fields.Int(allow_none=True)
    release_date = fields.Date(allow_none=True)
    url = fields.Str(allow_none=True)
    distance = fields.Float(allow_none=True)


class SongCreateSchema(Schema):
    """Schema for creating a new Song"""
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=True)
    artist_id = fields.Int(allow_none=True, data_key='artist_id')
    release_date = fields.Date(allow_none=True, data_key='release_date')
    url = fields.Str(allow_none=True)
    distance = fields.Float(allow_none=True)


class SongUpdateSchema(Schema):
    """Schema for updating a Song"""
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=True)
    artist_id = fields.Int(allow_none=True, data_key='artist_id')
    release_date = fields.Date(allow_none=True, data_key='release_date')
    url = fields.Str(allow_none=True)
    distance = fields.Float(allow_none=True)


# Create schema instances for reuse
artist_schema = ArtistSchema()
artists_schema = ArtistSchema(many=True)
artist_create_schema = ArtistCreateSchema()
artist_update_schema = ArtistUpdateSchema()

song_schema = SongSchema()
songs_schema = SongSchema(many=True)
song_create_schema = SongCreateSchema()
song_update_schema = SongUpdateSchema()
