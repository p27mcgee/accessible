"""
Artist REST API endpoints

API endpoints:
- GET    /v1/artists      - List all artists
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
    artist_create_schema, artist_update_schema
)
from marshmallow import ValidationError
from flasgger import swag_from

artists_bp = Blueprint('artists', __name__, url_prefix='/v1/artists')


@artists_bp.route('', methods=['GET'])
def get_all_artists():
    """
    Get all artists
    ---
    tags:
      - artists
    responses:
      200:
        description: List of all artists
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
    """
    artists = db.session.query(Artist).all()
    return jsonify(artists_schema.dump(artists)), 200


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
    artist = db.session.query(Artist).filter(Artist.id == id).first()
    if artist is None:
        abort(404, description=f"Artist with id {id} not found")
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

    db_artist = Artist(name=data['name'])
    db.session.add(db_artist)
    db.session.commit()
    db.session.refresh(db_artist)

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

    db_artist = db.session.query(Artist).filter(Artist.id == id).first()

    if db_artist is None:
        # Create new artist with specified ID
        db_artist = Artist(id=id, name=data['name'])
        db.session.add(db_artist)
    else:
        # Update existing artist
        db_artist.name = data['name']

    db.session.commit()
    db.session.refresh(db_artist)

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
    db_artist = db.session.query(Artist).filter(Artist.id == id).first()
    if db_artist is None:
        abort(404, description=f"Artist with id {id} not found")

    db.session.delete(db_artist)
    db.session.commit()

    return '', 204
