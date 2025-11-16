"""
Unit tests for Song API endpoints

Tests cover:
- GET /v1/songs (list all songs with pagination)
- GET /v1/songs/{id} (get single song)
- POST /v1/songs (create song)
- PUT /v1/songs/{id} (update song)
- DELETE /v1/songs/{id} (delete song)
- Foreign key validation (artist_id must exist)
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Song as SongModel


class TestGetAllSongs:
    """Tests for GET /v1/songs endpoint"""

    def test_get_all_songs_empty_database(self, client: TestClient):
        """Test getting songs when database is empty"""
        response = client.get("/v1/songs")

        assert response.status_code == 200
        data = response.json()

        assert data["items"] == []
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 10
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_prev"] is False

    def test_get_all_songs_with_data(self, client: TestClient, sample_songs):
        """Test getting songs with data in database"""
        response = client.get("/v1/songs")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 5
        assert data["pagination"]["total_items"] == 5
        assert data["pagination"]["total_pages"] == 1
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_prev"] is False

        # Verify first song structure
        first_song = data["items"][0]
        assert "id" in first_song
        assert "title" in first_song
        assert "artist_id" in first_song
        assert "release_date" in first_song
        assert "url" in first_song
        assert "distance" in first_song

    def test_get_all_songs_pagination(self, client: TestClient, sample_songs):
        """Test songs pagination with custom page size"""
        response = client.get("/v1/songs?page=1&page_size=2")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 2
        assert data["pagination"]["total_items"] == 5
        assert data["pagination"]["total_pages"] == 3
        assert data["pagination"]["has_next"] is True

    def test_get_all_songs_second_page(self, client: TestClient, sample_songs):
        """Test getting second page of results"""
        response = client.get("/v1/songs?page=2&page_size=2")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is True

    def test_get_all_songs_invalid_parameters(self, client: TestClient):
        """Test with invalid pagination parameters"""
        # Page number 0
        response = client.get("/v1/songs?page=0")
        assert response.status_code == 422

        # Negative page size
        response = client.get("/v1/songs?page_size=-1")
        assert response.status_code == 422

        # Page size exceeding maximum
        response = client.get("/v1/songs?page_size=101")
        assert response.status_code == 422


class TestGetSong:
    """Tests for GET /v1/songs/{id} endpoint"""

    def test_get_song_by_id_success(self, client: TestClient, sample_song):
        """Test getting a song by valid ID"""
        response = client.get(f"/v1/songs/{sample_song.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_song.id
        assert data["title"] == sample_song.title
        assert data["artist_id"] == sample_song.artistID
        assert data["release_date"] == str(sample_song.released)
        assert data["url"] == sample_song.URL
        assert data["distance"] == sample_song.distance

    def test_get_song_field_mapping(self, client: TestClient, sample_song):
        """Test that database fields are correctly mapped to API fields"""
        response = client.get(f"/v1/songs/{sample_song.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify snake_case field names in response
        assert "artist_id" in data  # Not artistID
        assert "release_date" in data  # Not released
        assert "url" in data  # Not URL

    def test_get_song_without_artist(self, client: TestClient, song_without_artist):
        """Test getting a song that has no associated artist"""
        response = client.get(f"/v1/songs/{song_without_artist.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["artist_id"] is None

    def test_get_song_not_found(self, client: TestClient):
        """Test getting a song with non-existent ID"""
        response = client.get("/v1/songs/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_song_invalid_id_type(self, client: TestClient):
        """Test with invalid ID type"""
        response = client.get("/v1/songs/invalid")

        assert response.status_code == 422


class TestCreateSong:
    """Tests for POST /v1/songs endpoint"""

    def test_create_song_with_all_fields(self, client: TestClient, sample_artist, db_session: Session):
        """Test creating a song with all fields populated"""
        song_data = {
            "title": "Rocket Man",
            "artist_id": sample_artist.id,
            "release_date": "1972-04-14",
            "url": "https://www.youtube.com/watch?v=DtVBCG6ThDk",
            "distance": 250.5
        }

        response = client.post("/v1/songs", json=song_data)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "Rocket Man"
        assert data["artist_id"] == sample_artist.id
        assert data["release_date"] == "1972-04-14"
        assert data["url"] == song_data["url"]
        assert data["distance"] == 250.5
        assert "id" in data

        # Verify song was saved to database
        db_song = db_session.query(SongModel).filter(
            SongModel.title == "Rocket Man"
        ).first()
        assert db_song is not None

    def test_create_song_minimal_fields(self, client: TestClient):
        """Test creating a song with only required fields"""
        song_data = {
            "title": "Minimal Song"
        }

        response = client.post("/v1/songs", json=song_data)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "Minimal Song"
        assert data["artist_id"] is None
        assert data["release_date"] is None
        assert data["url"] is None
        assert data["distance"] is None

    def test_create_song_without_artist(self, client: TestClient):
        """Test creating a song without an artist_id"""
        song_data = {
            "title": "Song Without Artist",
            "release_date": "2023-01-01",
            "url": "https://example.com",
            "distance": 100.0
        }

        response = client.post("/v1/songs", json=song_data)

        assert response.status_code == 201
        data = response.json()

        assert data["artist_id"] is None

    def test_create_song_invalid_artist_id(self, client: TestClient):
        """Test creating a song with non-existent artist_id"""
        song_data = {
            "title": "Test Song",
            "artist_id": 99999
        }

        response = client.post("/v1/songs", json=song_data)

        # Should fail because artist doesn't exist
        assert response.status_code == 404
        assert "Artist" in response.json()["detail"]
        assert "not found" in response.json()["detail"].lower()

    def test_create_song_missing_title(self, client: TestClient):
        """Test creating a song without required title field"""
        song_data = {
            "artist_id": 1
        }

        response = client.post("/v1/songs", json=song_data)

        assert response.status_code == 422

    def test_create_song_invalid_date_format(self, client: TestClient):
        """Test creating a song with invalid date format"""
        song_data = {
            "title": "Test Song",
            "release_date": "invalid-date"
        }

        response = client.post("/v1/songs", json=song_data)

        assert response.status_code == 422

    def test_create_song_invalid_distance_type(self, client: TestClient):
        """Test creating a song with invalid distance type"""
        song_data = {
            "title": "Test Song",
            "distance": "not-a-number"
        }

        response = client.post("/v1/songs", json=song_data)

        assert response.status_code == 422

    def test_create_song_future_date(self, client: TestClient):
        """Test creating a song with future release date"""
        song_data = {
            "title": "Future Song",
            "release_date": "2099-12-31"
        }

        response = client.post("/v1/songs", json=song_data)

        # Future dates are allowed (no validation constraint)
        assert response.status_code == 201

    def test_create_song_negative_distance(self, client: TestClient):
        """Test creating a song with negative distance"""
        song_data = {
            "title": "Test Song",
            "distance": -100.0
        }

        response = client.post("/v1/songs", json=song_data)

        # Negative distances are allowed (no validation constraint)
        assert response.status_code == 201
        assert response.json()["distance"] == -100.0

    def test_create_song_unicode_title(self, client: TestClient):
        """Test creating a song with Unicode characters in title"""
        song_data = {
            "title": "Café del Mar 🎵"
        }

        response = client.post("/v1/songs", json=song_data)

        assert response.status_code == 201
        assert response.json()["title"] == "Café del Mar 🎵"


class TestUpdateSong:
    """Tests for PUT /v1/songs/{id} endpoint"""

    def test_update_existing_song(self, client: TestClient, sample_song):
        """Test updating an existing song"""
        update_data = {
            "title": "Space Oddity (Remastered)",
            "artist_id": sample_song.artistID,
            "release_date": "1969-07-11",
            "url": "https://example.com/updated",
            "distance": 200.0
        }

        response = client.put(f"/v1/songs/{sample_song.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_song.id
        assert data["title"] == "Space Oddity (Remastered)"
        assert data["distance"] == 200.0
        assert data["url"] == "https://example.com/updated"

    def test_update_song_change_artist(self, client: TestClient, sample_song, db_session: Session):
        """Test changing a song's artist"""
        # Create a new artist
        from app.models import Artist as ArtistModel
        new_artist = ArtistModel(name="New Artist")
        db_session.add(new_artist)
        db_session.commit()
        db_session.refresh(new_artist)

        update_data = {
            "title": sample_song.title,
            "artist_id": new_artist.id
        }

        response = client.put(f"/v1/songs/{sample_song.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["artist_id"] == new_artist.id

    def test_update_song_remove_artist(self, client: TestClient, sample_song):
        """Test removing artist from a song (set to null)"""
        update_data = {
            "title": sample_song.title,
            "artist_id": None
        }

        response = client.put(f"/v1/songs/{sample_song.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["artist_id"] is None

    def test_update_song_invalid_artist_id(self, client: TestClient, sample_song):
        """Test updating with non-existent artist_id"""
        update_data = {
            "title": sample_song.title,
            "artist_id": 99999
        }

        response = client.put(f"/v1/songs/{sample_song.id}", json=update_data)

        assert response.status_code == 404
        assert "Artist" in response.json()["detail"]

    def test_update_song_upsert_behavior(self, client: TestClient, sample_artist):
        """
        Test that PUT creates a new song if ID doesn't exist (upsert behavior)

        Note: This is non-standard REST behavior but is how the API currently works.
        """
        song_data = {
            "title": "New Song",
            "artist_id": sample_artist.id
        }
        non_existent_id = 99999

        response = client.put(f"/v1/songs/{non_existent_id}", json=song_data)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == non_existent_id
        assert data["title"] == "New Song"

    def test_update_song_missing_title(self, client: TestClient, sample_song):
        """Test updating without required title field"""
        response = client.put(f"/v1/songs/{sample_song.id}", json={})

        assert response.status_code == 422


class TestDeleteSong:
    """Tests for DELETE /v1/songs/{id} endpoint"""

    def test_delete_song_success(self, client: TestClient, sample_song, db_session: Session):
        """Test deleting an existing song"""
        song_id = sample_song.id

        response = client.delete(f"/v1/songs/{song_id}")

        assert response.status_code == 204
        assert response.content == b""

        # Verify song was deleted from database
        db_song = db_session.query(SongModel).filter(
            SongModel.id == song_id
        ).first()
        assert db_song is None

    def test_delete_song_not_found(self, client: TestClient):
        """Test deleting a song that doesn't exist"""
        response = client.delete("/v1/songs/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_song_invalid_id(self, client: TestClient):
        """Test deleting with invalid ID type"""
        response = client.delete("/v1/songs/invalid")

        assert response.status_code == 422

    def test_delete_song_with_artist_preserved(
        self, client: TestClient, sample_song, db_session: Session
    ):
        """Test that deleting a song doesn't delete the associated artist"""
        from app.models import Artist as ArtistModel

        artist_id = sample_song.artistID
        song_id = sample_song.id

        response = client.delete(f"/v1/songs/{song_id}")

        assert response.status_code == 204

        # Verify artist still exists
        db_artist = db_session.query(ArtistModel).filter(
            ArtistModel.id == artist_id
        ).first()
        assert db_artist is not None


class TestSongEdgeCases:
    """Edge case tests for Song API"""

    def test_song_response_schema(self, client: TestClient, sample_song):
        """Test that song response matches expected schema"""
        response = client.get(f"/v1/songs/{sample_song.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify all fields are present
        required_fields = ["id", "title", "artist_id", "release_date", "url", "distance"]
        for field in required_fields:
            assert field in data

        # Verify field types
        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert data["artist_id"] is None or isinstance(data["artist_id"], int)
        assert data["release_date"] is None or isinstance(data["release_date"], str)
        assert data["url"] is None or isinstance(data["url"], str)
        assert data["distance"] is None or isinstance(data["distance"], (int, float))

    def test_song_list_ordering(self, client: TestClient, sample_songs):
        """Test that songs are returned in consistent order"""
        response = client.get("/v1/songs?page_size=100")

        assert response.status_code == 200
        data = response.json()

        # Songs should be ordered by ID
        ids = [song["id"] for song in data["items"]]
        assert ids == sorted(ids)

    def test_song_with_very_long_url(self, client: TestClient):
        """Test creating a song with very long URL"""
        long_url = "https://example.com/" + "a" * 1000

        song_data = {
            "title": "Test Song",
            "url": long_url
        }

        response = client.post("/v1/songs", json=song_data)

        # URL field has 1024 char limit
        if len(long_url) <= 1024:
            assert response.status_code == 201
        else:
            assert response.status_code in [400, 422, 500]

    def test_create_multiple_songs_for_same_artist(
        self, client: TestClient, sample_artist
    ):
        """Test creating multiple songs for the same artist"""
        songs = [
            {"title": f"Song {i}", "artist_id": sample_artist.id}
            for i in range(5)
        ]

        responses = [
            client.post("/v1/songs", json=song)
            for song in songs
        ]

        # All should succeed
        assert all(r.status_code == 201 for r in responses)

        # All should have unique IDs
        ids = [r.json()["id"] for r in responses]
        assert len(ids) == len(set(ids))

        # All should reference the same artist
        artist_ids = [r.json()["artist_id"] for r in responses]
        assert all(aid == sample_artist.id for aid in artist_ids)

    def test_song_date_boundary_values(self, client: TestClient):
        """Test songs with boundary date values"""
        # Very old date
        old_song = {
            "title": "Ancient Song",
            "release_date": "1900-01-01"
        }
        response = client.post("/v1/songs", json=old_song)
        assert response.status_code == 201

        # Recent date
        recent_song = {
            "title": "Recent Song",
            "release_date": "2024-12-31"
        }
        response = client.post("/v1/songs", json=recent_song)
        assert response.status_code == 201

    def test_song_distance_boundary_values(self, client: TestClient):
        """Test songs with boundary distance values"""
        # Zero distance
        zero_distance = {"title": "Zero", "distance": 0.0}
        response = client.post("/v1/songs", json=zero_distance)
        assert response.status_code == 201

        # Very large distance
        large_distance = {"title": "Far", "distance": 999999999.99}
        response = client.post("/v1/songs", json=large_distance)
        assert response.status_code == 201

        # Very small decimal
        small_distance = {"title": "Close", "distance": 0.000001}
        response = client.post("/v1/songs", json=small_distance)
        assert response.status_code == 201
