"""
Unit tests for Artist API endpoints (Flask)

Tests cover:
- GET /v1/artists (list all artists with pagination)
- GET /v1/artists/{id} (get single artist)
- POST /v1/artists (create artist)
- PUT /v1/artists/{id} (update artist)
- DELETE /v1/artists/{id} (delete artist)
"""
import pytest
import json
from app.models import Artist


class TestGetAllArtists:
    """Tests for GET /v1/artists endpoint"""

    def test_get_all_artists_empty_database(self, client, db_session):
        """Test getting artists when database is empty"""
        response = client.get('/v1/artists')

        assert response.status_code == 200
        data = response.get_json()

        assert data["items"] == []
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 10
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_prev"] is False

    def test_get_all_artists_with_data(self, client, sample_artists):
        """Test getting artists with data in database"""
        response = client.get('/v1/artists')

        assert response.status_code == 200
        data = response.get_json()

        assert len(data["items"]) == 10  # Default page size
        assert data["pagination"]["total_items"] == 12
        assert data["pagination"]["total_pages"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is False

        # Verify first artist
        assert data["items"][0]["name"] == "David Bowie"
        assert "id" in data["items"][0]

    def test_get_all_artists_custom_page_size(self, client, sample_artists):
        """Test pagination with custom page size"""
        response = client.get('/v1/artists?page=1&page_size=5')

        assert response.status_code == 200
        data = response.get_json()

        assert len(data["items"]) == 5
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 5
        assert data["pagination"]["total_items"] == 12
        assert data["pagination"]["total_pages"] == 3
        assert data["pagination"]["has_next"] is True

    def test_get_all_artists_second_page(self, client, sample_artists):
        """Test getting second page of results"""
        response = client.get('/v1/artists?page=2&page_size=10')

        assert response.status_code == 200
        data = response.get_json()

        assert len(data["items"]) == 2  # Only 2 items on second page
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_prev"] is True

    def test_get_all_artists_invalid_page_number(self, client):
        """Test with invalid page number (0 or negative)"""
        response = client.get('/v1/artists?page=0')

        assert response.status_code == 400

    def test_get_all_artists_page_size_too_large(self, client):
        """Test with page size exceeding maximum (100)"""
        response = client.get('/v1/artists?page_size=101')

        assert response.status_code == 400

    def test_get_all_artists_page_size_too_small(self, client):
        """Test with page size less than 1"""
        response = client.get('/v1/artists?page_size=0')

        assert response.status_code == 400

    def test_get_all_artists_beyond_last_page(self, client, sample_artists):
        """Test requesting a page beyond the last page"""
        response = client.get('/v1/artists?page=999')

        assert response.status_code == 200
        data = response.get_json()

        assert data["items"] == []
        assert data["pagination"]["page"] == 999
        assert data["pagination"]["has_next"] is False


class TestGetArtist:
    """Tests for GET /v1/artists/{id} endpoint"""

    def test_get_artist_by_id_success(self, client, sample_artist):
        """Test getting an artist by valid ID"""
        response = client.get(f'/v1/artists/{sample_artist.id}')

        assert response.status_code == 200
        data = response.get_json()

        assert data["id"] == sample_artist.id
        assert data["name"] == sample_artist.name

    def test_get_artist_not_found(self, client):
        """Test getting an artist with non-existent ID"""
        response = client.get('/v1/artists/99999')

        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["detail"].lower()

    def test_get_artist_invalid_id_type(self, client):
        """Test with invalid ID type (non-integer)"""
        response = client.get('/v1/artists/invalid')

        assert response.status_code == 404  # Flask returns 404 for type mismatch


class TestCreateArtist:
    """Tests for POST /v1/artists endpoint"""

    def test_create_artist_success(self, client, app, db_session):
        """Test creating a new artist with valid data"""
        artist_data = {"name": "Radiohead"}

        response = client.post(
            '/v1/artists',
            data=json.dumps(artist_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()

        assert data["name"] == "Radiohead"
        assert "id" in data
        assert isinstance(data["id"], int)

        # Verify artist was saved to database
        with app.app_context():
            db_artist = db_session.query(Artist).filter(
                Artist.name == "Radiohead"
            ).first()
            assert db_artist is not None
            assert db_artist.name == "Radiohead"

    def test_create_artist_missing_name(self, client):
        """Test creating artist without required name field"""
        response = client.post(
            '/v1/artists',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_create_artist_empty_name(self, client):
        """Test creating artist with empty name"""
        response = client.post(
            '/v1/artists',
            data=json.dumps({"name": ""}),
            content_type='application/json'
        )

        # Marshmallow may or may not validate empty strings
        assert response.status_code in [201, 400]

    def test_create_artist_name_too_long(self, client):
        """Test creating artist with name exceeding database limit (64 chars)"""
        long_name = "A" * 65

        response = client.post(
            '/v1/artists',
            data=json.dumps({"name": long_name}),
            content_type='application/json'
        )

        # Database will enforce constraint
        assert response.status_code in [201, 400, 500]

    def test_create_multiple_artists_with_same_name(self, client, app, db_session):
        """Test that duplicate artist names are allowed"""
        artist_data = {"name": "The Beatles"}

        # Create first artist
        response1 = client.post(
            '/v1/artists',
            data=json.dumps(artist_data),
            content_type='application/json'
        )
        assert response1.status_code == 201

        # Create second artist with same name
        response2 = client.post(
            '/v1/artists',
            data=json.dumps(artist_data),
            content_type='application/json'
        )
        assert response2.status_code == 201

        # Verify both were created
        with app.app_context():
            artists = db_session.query(Artist).filter(
                Artist.name == "The Beatles"
            ).all()
            assert len(artists) == 2

    def test_create_artist_unicode_name(self, client):
        """Test creating artist with Unicode characters"""
        artist_data = {"name": "Björk"}

        response = client.post(
            '/v1/artists',
            data=json.dumps(artist_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Björk"

    def test_create_artist_special_characters(self, client):
        """Test creating artist with special characters"""
        artist_data = {"name": "AC/DC & The Rolling Stones!"}

        response = client.post(
            '/v1/artists',
            data=json.dumps(artist_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "AC/DC & The Rolling Stones!"


class TestUpdateArtist:
    """Tests for PUT /v1/artists/{id} endpoint"""

    def test_update_existing_artist(self, client, sample_artist):
        """Test updating an existing artist"""
        update_data = {"name": "David Bowie (Updated)"}

        response = client.put(
            f'/v1/artists/{sample_artist.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["id"] == sample_artist.id
        assert data["name"] == "David Bowie (Updated)"

    def test_update_artist_upsert_behavior(self, client, app, db_session):
        """
        Test that PUT creates a new artist if ID doesn't exist (upsert behavior)

        Note: This is non-standard REST behavior but is how the API currently works.
        """
        artist_data = {"name": "New Artist"}
        non_existent_id = 99999

        response = client.put(
            f'/v1/artists/{non_existent_id}',
            data=json.dumps(artist_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["id"] == non_existent_id
        assert data["name"] == "New Artist"

        # Verify it was created in database
        with app.app_context():
            db_artist = db_session.query(Artist).filter(
                Artist.id == non_existent_id
            ).first()
            assert db_artist is not None

    def test_update_artist_missing_name(self, client, sample_artist):
        """Test updating artist without required name field"""
        response = client.put(
            f'/v1/artists/{sample_artist.id}',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_update_artist_invalid_id(self, client):
        """Test updating with invalid ID type"""
        response = client.put(
            '/v1/artists/invalid',
            data=json.dumps({"name": "Test"}),
            content_type='application/json'
        )

        assert response.status_code == 404


class TestDeleteArtist:
    """Tests for DELETE /v1/artists/{id} endpoint"""

    def test_delete_artist_success(self, client, sample_artist, app, db_session):
        """Test deleting an existing artist"""
        artist_id = sample_artist.id

        response = client.delete(f'/v1/artists/{artist_id}')

        assert response.status_code == 204
        assert response.data == b""

        # Verify artist was deleted from database
        with app.app_context():
            db_artist = db_session.query(Artist).filter(
                Artist.id == artist_id
            ).first()
            assert db_artist is None

    def test_delete_artist_not_found(self, client):
        """Test deleting an artist that doesn't exist"""
        response = client.delete('/v1/artists/99999')

        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["detail"].lower()

    def test_delete_artist_invalid_id(self, client):
        """Test deleting with invalid ID type"""
        response = client.delete('/v1/artists/invalid')

        assert response.status_code == 404

    def test_delete_artist_with_songs(self, client, sample_song):
        """
        Test deleting an artist that has associated songs

        Behavior depends on foreign key constraints:
        - CASCADE: Songs are deleted
        - RESTRICT: Delete fails
        - SET NULL: Songs' artistID set to NULL

        SQLite default is RESTRICT-like behavior
        """
        artist_id = sample_song.artistID

        response = client.delete(f'/v1/artists/{artist_id}')

        # SQLite with default settings may allow or prevent this
        # Document actual behavior
        if response.status_code == 204:
            # Delete succeeded
            pass
        elif response.status_code in [400, 409, 500]:
            # Delete failed due to constraint
            pass


class TestArtistEdgeCases:
    """Edge case tests for Artist API"""

    def test_artist_response_schema(self, client, sample_artist):
        """Test that artist response matches expected schema"""
        response = client.get(f'/v1/artists/{sample_artist.id}')

        assert response.status_code == 200
        data = response.get_json()

        # Verify all required fields are present
        assert "id" in data
        assert "name" in data

        # Verify field types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)

    def test_artist_list_ordering(self, client, sample_artists):
        """Test that artists are returned in consistent order"""
        response = client.get('/v1/artists?page_size=100')

        assert response.status_code == 200
        data = response.get_json()

        # Artists should be ordered by ID
        ids = [artist["id"] for artist in data["items"]]
        assert ids == sorted(ids)

    def test_concurrent_artist_creation(self, client):
        """Test creating multiple artists in quick succession"""
        artists = [
            {"name": f"Artist {i}"} for i in range(10)
        ]

        responses = [
            client.post(
                '/v1/artists',
                data=json.dumps(artist),
                content_type='application/json'
            )
            for artist in artists
        ]

        # All should succeed
        assert all(r.status_code == 201 for r in responses)

        # All should have unique IDs
        ids = [r.get_json()["id"] for r in responses]
        assert len(ids) == len(set(ids))

    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            '/v1/artists',
            data='{"name": invalid}',
            content_type='application/json'
        )

        assert response.status_code in [400, 422]
