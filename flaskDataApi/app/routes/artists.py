"""
Artist REST API endpoints

API endpoints:
- GET    /v1/artists      - List all artists (paginated)
- GET    /v1/artists/{id} - Get one artist
- POST   /v1/artists      - Create new artist
- PUT    /v1/artists/{id} - Update artist
- DELETE /v1/artists/{id} - Delete artist
"""
from flask import Blueprint, request, jsonify, abort
from app.database import db
from app.models import Artist
from app.schemas import (
    artist_schema, artists_schema,
    artist_create_schema, artist_update_schema,
    create_paginated_response
)
from marshmallow import ValidationError
from flasgger import swag_from
from app.utils.logger import get_logger_with_context

# Get logger
logger = get_logger_with_context(__name__)

artists_bp = Blueprint('artists', __name__, url_prefix='/v1/artists')


@artists_bp.route('', methods=['GET'])
def get_all_artists():
    """
    Get all artists with pagination
    ---
    tags:
      - artists
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
        description: Paginated list of artists
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
                  name:
                    type: string
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
        "Fetching paginated artists",
        operation="list",
        entity_type="artist",
        page=page,
        page_size=page_size
    )

    # Validate parameters
    if page < 1:
        return jsonify({"detail": "Page must be >= 1"}), 400
    if page_size < 1 or page_size > 100:
        return jsonify({"detail": "Page size must be between 1 and 100"}), 400

    # Get total count
    total_items = db.session.query(Artist).count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Get paginated items (SQL Server requires ORDER BY with OFFSET/LIMIT)
    artists = db.session.query(Artist).order_by(Artist.id).offset(offset).limit(page_size).all()

    # Create paginated response
    response = create_paginated_response(artists, artists_schema, page, page_size, total_items)

    # Log result
    logger.info(
        "Artists retrieved successfully",
        operation="list",
        entity_type="artist",
        items_returned=len(artists),
        total_items=total_items,
        page=page
    )

    return jsonify(response), 200


@artists_bp.route('/<int:id>', methods=['GET'])
def get_artist(id):
    """
    Get one artist by ID
    ---
    tags:
      - artists
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Artist ID
    responses:
      200:
        description: Artist found
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
      404:
        description: Artist not found
    """
    logger.info(
        "Fetching artist by ID",
        operation="read",
        entity_type="artist",
        entity_id=id
    )

    artist = db.session.query(Artist).filter(Artist.id == id).first()
    if artist is None:
        logger.warning(
            "Artist not found",
            operation="read",
            entity_type="artist",
            entity_id=id
        )
        abort(404, description=f"Artist with id {id} not found")

    logger.info(
        "Artist retrieved successfully",
        operation="read",
        entity_type="artist",
        entity_id=id,
        name=artist.name
    )
    return jsonify(artist_schema.dump(artist)), 200


@artists_bp.route('', methods=['POST'])
def create_artist():
    """
    Create a new artist
    ---
    tags:
      - artists
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
    responses:
      201:
        description: Artist created
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
      400:
        description: Validation error
    """
    try:
        data = artist_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"detail": "Validation error", "errors": err.messages}), 400

    logger.info(
        "Creating new artist",
        operation="create",
        entity_type="artist",
        name=data['name']
    )

    db_artist = Artist(name=data['name'])
    db.session.add(db_artist)
    db.session.commit()
    db.session.refresh(db_artist)

    logger.info(
        "Artist created successfully",
        operation="create",
        entity_type="artist",
        entity_id=db_artist.id,
        name=db_artist.name
    )

    return jsonify(artist_schema.dump(db_artist)), 201


@artists_bp.route('/<int:id>', methods=['PUT'])
def update_artist(id):
    """
    Update an existing artist or create if not exists
    ---
    tags:
      - artists
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Artist ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
    responses:
      200:
        description: Artist updated
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
      400:
        description: Validation error
    """
    try:
        data = artist_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"detail": "Validation error", "errors": err.messages}), 400

    logger.info(
        "Updating artist",
        operation="update",
        entity_type="artist",
        entity_id=id,
        name=data['name']
    )

    db_artist = db.session.query(Artist).filter(Artist.id == id).first()

    if db_artist is None:
        # Create new artist with specified ID
        logger.info(
            "Artist not found, creating new artist with specified ID",
            operation="update",
            entity_type="artist",
            entity_id=id,
            upsert=True
        )
        db_artist = Artist(id=id, name=data['name'])
        db.session.add(db_artist)
    else:
        # Update existing artist
        db_artist.name = data['name']

    db.session.commit()
    db.session.refresh(db_artist)

    logger.info(
        "Artist updated successfully",
        operation="update",
        entity_type="artist",
        entity_id=db_artist.id,
        name=db_artist.name
    )

    return jsonify(artist_schema.dump(db_artist)), 200


@artists_bp.route('/<int:id>', methods=['DELETE'])
def delete_artist(id):
    """
    Delete an artist
    ---
    tags:
      - artists
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Artist ID
    responses:
      204:
        description: Artist deleted
      404:
        description: Artist not found
    """
    logger.info(
        "Deleting artist",
        operation="delete",
        entity_type="artist",
        entity_id=id
    )

    db_artist = db.session.query(Artist).filter(Artist.id == id).first()
    if db_artist is None:
        logger.warning(
            "Artist not found for deletion",
            operation="delete",
            entity_type="artist",
            entity_id=id
        )
        abort(404, description=f"Artist with id {id} not found")

    artist_name = db_artist.name
    db.session.delete(db_artist)
    db.session.commit()

    logger.info(
        "Artist deleted successfully",
        operation="delete",
        entity_type="artist",
        entity_id=id,
        name=artist_name
    )

    return '', 204
