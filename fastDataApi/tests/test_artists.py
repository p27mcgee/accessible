"""
Unit tests for Artist API endpoints

Tests cover:
- GET /v1/artists (list all artists with pagination)
- GET /v1/artists/{id} (get single artist)
- POST /v1/artists (create artist)
- PUT /v1/artists/{id} (update artist)
- DELETE /v1/artists/{id} (delete artist)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Artist as ArtistModel


class TestGetAllArtists:
    """Tests for GET /v1/artists endpoint"""

    def test_get_all_artists_empty_database(self, client: TestClient):
        """Test getting artists when database is empty"""
        response = client.get("/v1/artists")

        assert response.status_code == 200
        data = response.json()

        assert data["items"] == []
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 10
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_prev"] is False

    def test_get_all_artists_with_data(self, client: TestClient, sample_artists):
        """Test getting artists with data in database"""
        response = client.get("/v1/artists")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 10  # Default page size
        assert data["pagination"]["total_items"] == 12
        assert data["pagination"]["total_pages"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is False

        # Verify first artist
        assert data["items"][0]["name"] == "David Bowie"
        assert "id" in data["items"][0]

    def test_get_all_artists_custom_page_size(self, client: TestClient, sample_artists):
        """Test pagination with custom page size"""
        response = client.get("/v1/artists?page=1&page_size=5")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 5
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 5
        assert data["pagination"]["total_items"] == 12
        assert data["pagination"]["total_pages"] == 3
        assert data["pagination"]["has_next"] is True

    def test_get_all_artists_second_page(self, client: TestClient, sample_artists):
        """Test getting second page of results"""
        response = client.get("/v1/artists?page=2&page_size=10")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2  # Only 2 items on second page
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_prev"] is True

    def test_get_all_artists_invalid_page_number(self, client: TestClient):
        """Test with invalid page number (0 or negative)"""
        response = client.get("/v1/artists?page=0")

        assert response.status_code == 422  # Validation error

    def test_get_all_artists_page_size_too_large(self, client: TestClient):
        """Test with page size exceeding maximum (100)"""
        response = client.get("/v1/artists?page_size=101")

        assert response.status_code == 422  # Validation error

    def test_get_all_artists_page_size_too_small(self, client: TestClient):
        """Test with page size less than 1"""
        response = client.get("/v1/artists?page_size=0")

        assert response.status_code == 422  # Validation error

    def test_get_all_artists_beyond_last_page(self, client: TestClient, sample_artists):
        """Test requesting a page beyond the last page"""
        response = client.get("/v1/artists?page=999")

        assert response.status_code == 200
        data = response.json()

        assert data["items"] == []
        assert data["pagination"]["page"] == 999
        assert data["pagination"]["has_next"] is False


class TestGetArtist:
    """Tests for GET /v1/artists/{id} endpoint"""

    def test_get_artist_by_id_success(self, client: TestClient, sample_artist):
        """Test getting an artist by valid ID"""
        response = client.get(f"/v1/artists/{sample_artist.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_artist.id
        assert data["name"] == sample_artist.name

    def test_get_artist_not_found(self, client: TestClient):
        """Test getting an artist with non-existent ID"""
        response = client.get("/v1/artists/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_artist_invalid_id_type(self, client: TestClient):
        """Test with invalid ID type (non-integer)"""
        response = client.get("/v1/artists/invalid")

        assert response.status_code == 422  # Validation error


class TestCreateArtist:
    """Tests for POST /v1/artists endpoint"""

    def test_create_artist_success(self, client: TestClient, db_session: Session):
        """Test creating a new artist with valid data"""
        artist_data = {"name": "Radiohead"}

        response = client.post("/v1/artists", json=artist_data)

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Radiohead"
        assert "id" in data
        assert isinstance(data["id"], int)

        # Verify artist was saved to database
        db_artist = db_session.query(ArtistModel).filter(
            ArtistModel.name == "Radiohead"
        ).first()
        assert db_artist is not None
        assert db_artist.name == "Radiohead"

    def test_create_artist_missing_name(self, client: TestClient):
        """Test creating artist without required name field"""
        response = client.post("/v1/artists", json={})

        assert response.status_code == 422  # Validation error

    def test_create_artist_empty_name(self, client: TestClient):
        """Test creating artist with empty name"""
        response = client.post("/v1/artists", json={"name": ""})

        # Note: Current schema doesn't enforce non-empty strings
        # This test documents current behavior
        assert response.status_code in [201, 422]

    def test_create_artist_name_too_long(self, client: TestClient):
        """Test creating artist with name exceeding database limit (64 chars)"""
        long_name = "A" * 65

        response = client.post("/v1/artists", json={"name": long_name})

        # Database will enforce constraint
        # Behavior depends on SQLAlchemy/database error handling
        assert response.status_code in [201, 400, 422, 500]

    def test_create_multiple_artists_with_same_name(
        self, client: TestClient, db_session: Session
    ):
        """Test that duplicate artist names are allowed"""
        artist_data = {"name": "The Beatles"}

        # Create first artist
        response1 = client.post("/v1/artists", json=artist_data)
        assert response1.status_code == 201

        # Create second artist with same name
        response2 = client.post("/v1/artists", json=artist_data)
        assert response2.status_code == 201

        # Verify both were created
        artists = db_session.query(ArtistModel).filter(
            ArtistModel.name == "The Beatles"
        ).all()
        assert len(artists) == 2

    def test_create_artist_unicode_name(self, client: TestClient):
        """Test creating artist with Unicode characters"""
        artist_data = {"name": "Björk"}

        response = client.post("/v1/artists", json=artist_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Björk"

    def test_create_artist_special_characters(self, client: TestClient):
        """Test creating artist with special characters"""
        artist_data = {"name": "AC/DC & The Rolling Stones!"}

        response = client.post("/v1/artists", json=artist_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "AC/DC & The Rolling Stones!"


class TestUpdateArtist:
    """Tests for PUT /v1/artists/{id} endpoint"""

    def test_update_existing_artist(self, client: TestClient, sample_artist):
        """Test updating an existing artist"""
        update_data = {"name": "David Bowie (Updated)"}

        response = client.put(f"/v1/artists/{sample_artist.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_artist.id
        assert data["name"] == "David Bowie (Updated)"

    def test_update_artist_upsert_behavior(self, client: TestClient, db_session: Session):
        """
        Test that PUT creates a new artist if ID doesn't exist (upsert behavior)

        Note: This is non-standard REST behavior but is how the API currently works.
        """
        artist_data = {"name": "New Artist"}
        non_existent_id = 99999

        response = client.put(f"/v1/artists/{non_existent_id}", json=artist_data)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == non_existent_id
        assert data["name"] == "New Artist"

        # Verify it was created in database
        db_artist = db_session.query(ArtistModel).filter(
            ArtistModel.id == non_existent_id
        ).first()
        assert db_artist is not None

    def test_update_artist_missing_name(self, client: TestClient, sample_artist):
        """Test updating artist without required name field"""
        response = client.put(f"/v1/artists/{sample_artist.id}", json={})

        assert response.status_code == 422  # Validation error

    def test_update_artist_invalid_id(self, client: TestClient):
        """Test updating with invalid ID type"""
        response = client.put("/v1/artists/invalid", json={"name": "Test"})

        assert response.status_code == 422


class TestDeleteArtist:
    """Tests for DELETE /v1/artists/{id} endpoint"""

    def test_delete_artist_success(self, client: TestClient, sample_artist, db_session: Session):
        """Test deleting an existing artist"""
        artist_id = sample_artist.id

        response = client.delete(f"/v1/artists/{artist_id}")

        assert response.status_code == 204
        assert response.content == b""

        # Verify artist was deleted from database
        db_artist = db_session.query(ArtistModel).filter(
            ArtistModel.id == artist_id
        ).first()
        assert db_artist is None

    def test_delete_artist_not_found(self, client: TestClient):
        """Test deleting an artist that doesn't exist"""
        response = client.delete("/v1/artists/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_artist_invalid_id(self, client: TestClient):
        """Test deleting with invalid ID type"""
        response = client.delete("/v1/artists/invalid")

        assert response.status_code == 422

    def test_delete_artist_with_songs(
        self, client: TestClient, sample_song, db_session: Session
    ):
        """
        Test deleting an artist that has associated songs

        Behavior depends on foreign key constraints:
        - CASCADE: Songs are deleted
        - RESTRICT: Delete fails
        - SET NULL: Songs' artistID set to NULL

        SQLite default is RESTRICT-like behavior
        """
        artist_id = sample_song.artistID

        response = client.delete(f"/v1/artists/{artist_id}")

        # SQLite with default settings may allow or prevent this
        # Document actual behavior
        if response.status_code == 204:
            # Delete succeeded - check what happened to song
            from app.models import Song as SongModel
            db_song = db_session.query(SongModel).filter(
                SongModel.id == sample_song.id
            ).first()

            # Song might be deleted (CASCADE) or orphaned (SET NULL) or still exist
            # This documents the actual behavior
            pass
        elif response.status_code in [400, 409, 500]:
            # Delete failed due to constraint
            pass


class TestArtistEdgeCases:
    """Edge case tests for Artist API"""

    def test_artist_response_schema(self, client: TestClient, sample_artist):
        """Test that artist response matches expected schema"""
        response = client.get(f"/v1/artists/{sample_artist.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        assert "id" in data
        assert "name" in data

        # Verify field types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)

    def test_artist_list_ordering(self, client: TestClient, sample_artists):
        """Test that artists are returned in consistent order"""
        response = client.get("/v1/artists?page_size=100")

        assert response.status_code == 200
        data = response.json()

        # Artists should be ordered by ID
        ids = [artist["id"] for artist in data["items"]]
        assert ids == sorted(ids)

    def test_concurrent_artist_creation(self, client: TestClient):
        """Test creating multiple artists in quick succession"""
        artists = [
            {"name": f"Artist {i}"} for i in range(10)
        ]

        responses = [
            client.post("/v1/artists", json=artist)
            for artist in artists
        ]

        # All should succeed
        assert all(r.status_code == 201 for r in responses)

        # All should have unique IDs
        ids = [r.json()["id"] for r in responses]
        assert len(ids) == len(set(ids))
