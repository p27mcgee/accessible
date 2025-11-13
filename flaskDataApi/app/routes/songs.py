"""
Song REST API endpoints

API endpoints:
- GET    /v1/songs      - List all songs
- GET    /v1/songs/{id} - Get one song
- POST   /v1/songs      - Create new song
- PUT    /v1/songs/{id} - Update song
- DELETE /v1/songs/{id} - Delete song
"""
from flask import Blueprint, request, jsonify, abort
from app.database import db
from app.models import Song, Artist
from app.schemas import (
    song_schema, songs_schema,
    song_create_schema, song_update_schema,
    song_model_to_dict
)
from marshmallow import ValidationError

songs_bp = Blueprint('songs', __name__, url_prefix='/v1/songs')


@songs_bp.route('', methods=['GET'])
def get_all_songs():
    """
    Get all songs
    ---
    tags:
      - songs
    responses:
      200:
        description: List of all songs
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              artist_id:
                type: integer
              release_date:
                type: string
                format: date
              url:
                type: string
              distance:
                type: number
    """
    songs = db.session.query(Song).all()
    songs_dict = [song_model_to_dict(song) for song in songs]
    return jsonify(songs_schema.dump(songs_dict)), 200


@songs_bp.route('/<int:id>', methods=['GET'])
def get_song(id):
    """
    Get one song by ID
    ---
    tags:
      - songs
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Song ID
    responses:
      200:
        description: Song found
      404:
        description: Song not found
    """
    song = db.session.query(Song).filter(Song.id == id).first()
    if song is None:
        abort(404, description=f"Song with id {id} not found")
    return jsonify(song_schema.dump(song_model_to_dict(song))), 200


@songs_bp.route('', methods=['POST'])
def create_song():
    """
    Create a new song
    ---
    tags:
      - songs
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
            artist_id:
              type: integer
            release_date:
              type: string
              format: date
            url:
              type: string
            distance:
              type: number
    responses:
      201:
        description: Song created
      400:
        description: Validation error
      404:
        description: Artist not found
    """
    try:
        data = song_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"detail": "Validation error", "errors": err.messages}), 400

    # Validate artist exists if artist_id is provided
    if data.get('artist_id') is not None:
        artist = db.session.query(Artist).filter(Artist.id == data['artist_id']).first()
        if artist is None:
            abort(404, description=f"Artist with id {data['artist_id']} not found")

    # Create new song - map schema fields to database columns
    db_song = Song(
        title=data['title'],
        artistID=data.get('artist_id'),
        released=data.get('release_date'),
        URL=data.get('url'),
        distance=data.get('distance')
    )
    db.session.add(db_song)
    db.session.commit()
    db.session.refresh(db_song)

    return jsonify(song_schema.dump(song_model_to_dict(db_song))), 201


@songs_bp.route('/<int:id>', methods=['PUT'])
def update_song(id):
    """
    Update an existing song or create if not exists
    ---
    tags:
      - songs
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Song ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
            artist_id:
              type: integer
            release_date:
              type: string
              format: date
            url:
              type: string
            distance:
              type: number
    responses:
      200:
        description: Song updated
      400:
        description: Validation error
      404:
        description: Artist not found
    """
    try:
        data = song_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"detail": "Validation error", "errors": err.messages}), 400

    # Validate artist exists if artist_id is provided
    if data.get('artist_id') is not None:
        artist = db.session.query(Artist).filter(Artist.id == data['artist_id']).first()
        if artist is None:
            abort(404, description=f"Artist with id {data['artist_id']} not found")

    db_song = db.session.query(Song).filter(Song.id == id).first()

    if db_song is None:
        # Create new song with specified ID
        db_song = Song(
            id=id,
            title=data['title'],
            artistID=data.get('artist_id'),
            released=data.get('release_date'),
            URL=data.get('url'),
            distance=data.get('distance')
        )
        db.session.add(db_song)
    else:
        # Update existing song
        db_song.title = data['title']
        db_song.artistID = data.get('artist_id')
        db_song.released = data.get('release_date')
        db_song.URL = data.get('url')
        db_song.distance = data.get('distance')

    db.session.commit()
    db.session.refresh(db_song)

    return jsonify(song_schema.dump(song_model_to_dict(db_song))), 200


@songs_bp.route('/<int:id>', methods=['DELETE'])
def delete_song(id):
    """
    Delete a song
    ---
    tags:
      - songs
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Song ID
    responses:
      204:
        description: Song deleted
      404:
        description: Song not found
    """
    db_song = db.session.query(Song).filter(Song.id == id).first()
    if db_song is None:
        abort(404, description=f"Song with id {id} not found")

    db.session.delete(db_song)
    db.session.commit()

    return '', 204
