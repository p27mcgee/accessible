"""
Song REST API endpoints

API endpoints:
- GET    /v1/songs      - List all songs (paginated)
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
    song_model_to_dict, create_paginated_response
)
from marshmallow import ValidationError
from app.utils.logger import get_logger_with_context

# Get logger
logger = get_logger_with_context(__name__)

songs_bp = Blueprint('songs', __name__, url_prefix='/v1/songs')


@songs_bp.route('', methods=['GET'])
def get_all_songs():
    """
    Get all songs with pagination
    ---
    tags:
      - songs
    parameters:
      - name: page
        in: query
        type: integer
        minimum: 1
        default: 1
        description: Page number (1-indexed)
      - name: page_size
        in: query
        type: integer
        minimum: 1
        maximum: 100
        default: 10
        description: Number of items per page (max 100)
    responses:
      200:
        description: Paginated list of songs
        schema:
          type: object
          properties:
            items:
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
            pagination:
              type: object
              properties:
                page:
                  type: integer
                page_size:
                  type: integer
                total_items:
                  type: integer
                total_pages:
                  type: integer
                has_next:
                  type: boolean
                has_prev:
                  type: boolean
    """
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    # Log operation
    logger.info(
        "Fetching paginated songs",
        operation="list",
        entity_type="song",
        page=page,
        page_size=page_size
    )

    # Validate parameters
    if page < 1:
        return jsonify({"detail": "Page must be >= 1"}), 400
    if page_size < 1 or page_size > 100:
        return jsonify({"detail": "Page size must be between 1 and 100"}), 400

    # Get total count
    total_items = db.session.query(Song).count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Get paginated items
    songs = db.session.query(Song).offset(offset).limit(page_size).all()

    # Convert to dict format
    songs_dict = [song_model_to_dict(song) for song in songs]

    # Create paginated response
    response = create_paginated_response(songs_dict, songs_schema, page, page_size, total_items)

    # Log result
    logger.info(
        "Songs retrieved successfully",
        operation="list",
        entity_type="song",
        items_returned=len(songs_dict),
        total_items=total_items,
        page=page
    )

    return jsonify(response), 200


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
    logger.info(
        "Fetching song by ID",
        operation="read",
        entity_type="song",
        entity_id=id
    )

    song = db.session.query(Song).filter(Song.id == id).first()
    if song is None:
        logger.warning(
            "Song not found",
            operation="read",
            entity_type="song",
            entity_id=id
        )
        abort(404, description=f"Song with id {id} not found")

    logger.info(
        "Song retrieved successfully",
        operation="read",
        entity_type="song",
        entity_id=id,
        title=song.title
    )
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

    logger.info(
        "Creating new song",
        operation="create",
        entity_type="song",
        title=data['title'],
        artist_id=data.get('artist_id')
    )

    # Validate artist exists if artist_id is provided
    if data.get('artist_id') is not None:
        artist = db.session.query(Artist).filter(Artist.id == data['artist_id']).first()
        if artist is None:
            logger.warning(
                "Artist not found for song creation",
                operation="create",
                entity_type="song",
                artist_id=data['artist_id']
            )
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

    logger.info(
        "Song created successfully",
        operation="create",
        entity_type="song",
        entity_id=db_song.id,
        title=db_song.title
    )

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

    logger.info(
        "Updating song",
        operation="update",
        entity_type="song",
        entity_id=id,
        title=data['title']
    )

    # Validate artist exists if artist_id is provided
    if data.get('artist_id') is not None:
        artist = db.session.query(Artist).filter(Artist.id == data['artist_id']).first()
        if artist is None:
            logger.warning(
                "Artist not found for song update",
                operation="update",
                entity_type="song",
                entity_id=id,
                artist_id=data['artist_id']
            )
            abort(404, description=f"Artist with id {data['artist_id']} not found")

    db_song = db.session.query(Song).filter(Song.id == id).first()

    if db_song is None:
        # Create new song with specified ID
        logger.info(
            "Song not found, creating new song with specified ID",
            operation="update",
            entity_type="song",
            entity_id=id,
            upsert=True
        )
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

    logger.info(
        "Song updated successfully",
        operation="update",
        entity_type="song",
        entity_id=db_song.id,
        title=db_song.title
    )

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
    logger.info(
        "Deleting song",
        operation="delete",
        entity_type="song",
        entity_id=id
    )

    db_song = db.session.query(Song).filter(Song.id == id).first()
    if db_song is None:
        logger.warning(
            "Song not found for deletion",
            operation="delete",
            entity_type="song",
            entity_id=id
        )
        abort(404, description=f"Song with id {id} not found")

    song_title = db_song.title
    db.session.delete(db_song)
    db.session.commit()

    logger.info(
        "Song deleted successfully",
        operation="delete",
        entity_type="song",
        entity_id=id,
        title=song_title
    )

    return '', 204
