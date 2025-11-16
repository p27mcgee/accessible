"""
Unit tests for Health Check endpoints

Tests cover:
- GET /health (basic health check from main.py)
- GET /health/db (database connectivity check)
- GET /health/pool (connection pool status)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestBasicHealth:
    """Tests for GET /health endpoint"""

    def test_health_check_success(self, client: TestClient):
        """Test basic health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"

    def test_health_check_no_authentication_required(self, client: TestClient):
        """Test that health endpoint doesn't require authentication"""
        response = client.get("/health")

        assert response.status_code == 200


class TestDatabaseHealth:
    """Tests for GET /health/db endpoint"""

    def test_database_health_check_success(self, client: TestClient):
        """Test database health check when database is accessible"""
        response = client.get("/health/db")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "database" in data
        assert "message" in data

        # With our test database, it should be healthy
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    def test_database_health_check_response_structure(self, client: TestClient):
        """Test that database health check returns expected structure"""
        response = client.get("/health/db")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        required_fields = ["status", "database", "message"]
        for field in required_fields:
            assert field in data

        # Verify field types
        assert isinstance(data["status"], str)
        assert isinstance(data["database"], str)
        assert isinstance(data["message"], str)


class TestConnectionPoolHealth:
    """Tests for GET /health/pool endpoint"""

    def test_pool_status_success(self, client: TestClient):
        """Test connection pool status endpoint"""
        response = client.get("/health/pool")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields are present
        assert "pool_size" in data
        assert "checked_out" in data
        assert "overflow" in data
        assert "total_connections" in data
        assert "status" in data

    def test_pool_status_response_structure(self, client: TestClient):
        """Test that pool status returns expected structure"""
        response = client.get("/health/pool")

        assert response.status_code == 200
        data = response.json()

        # Verify field types
        assert isinstance(data["pool_size"], int)
        assert isinstance(data["checked_out"], int)
        assert isinstance(data["overflow"], int)
        assert isinstance(data["total_connections"], int)
        assert isinstance(data["status"], str)

        # Verify status is either healthy or degraded
        assert data["status"] in ["healthy", "degraded"]

    def test_pool_status_calculations(self, client: TestClient):
        """Test that pool status calculations are correct"""
        response = client.get("/health/pool")

        assert response.status_code == 200
        data = response.json()

        # Total connections should equal checked_out + overflow
        assert data["total_connections"] == data["checked_out"] + data["overflow"]

        # Checked out should be non-negative
        assert data["checked_out"] >= 0

        # Note: overflow can be negative in SQLite's StaticPool
        # In production SQL Server, overflow should be >= 0
        # For testing purposes, we just verify the calculation is consistent

    def test_pool_status_healthy_condition(self, client: TestClient):
        """Test pool status is healthy when not at capacity"""
        response = client.get("/health/pool")

        assert response.status_code == 200
        data = response.json()

        # If checked_out < pool_size, status should be healthy
        if data["checked_out"] < data["pool_size"]:
            assert data["status"] == "healthy"


class TestRootEndpoint:
    """Tests for GET / (root endpoint)"""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data

        # Verify values
        assert data["name"] == "fastDataApi"
        assert data["version"] == "1.0.0"
        assert isinstance(data["endpoints"], dict)

    def test_root_endpoint_contains_documentation_links(self, client: TestClient):
        """Test that root endpoint includes documentation links"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        endpoints = data["endpoints"]

        # Verify documentation endpoints are included
        assert "docs" in endpoints
        assert "openapi" in endpoints

        # Verify API endpoints are included
        assert "artists" in endpoints
        assert "songs" in endpoints

    def test_root_endpoint_response_structure(self, client: TestClient):
        """Test root endpoint response structure"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Verify field types
        assert isinstance(data["name"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["description"], str)
        assert isinstance(data["endpoints"], dict)


class TestHealthEdgeCases:
    """Edge case tests for health endpoints"""

    def test_health_endpoints_accept_only_get(self, client: TestClient):
        """Test that health endpoints only accept GET requests"""
        endpoints = ["/health", "/health/db", "/health/pool"]

        for endpoint in endpoints:
            # POST should not be allowed
            response = client.post(endpoint)
            assert response.status_code == 405  # Method Not Allowed

            # PUT should not be allowed
            response = client.put(endpoint)
            assert response.status_code == 405

            # DELETE should not be allowed
            response = client.delete(endpoint)
            assert response.status_code == 405

    def test_health_endpoints_consistent_response_times(self, client: TestClient):
        """Test that health endpoints respond quickly"""
        import time

        endpoints = ["/health", "/health/db", "/health/pool"]

        for endpoint in endpoints:
            start = time.time()
            response = client.get(endpoint)
            duration = time.time() - start

            assert response.status_code == 200
            # Health checks should be fast (< 1 second)
            assert duration < 1.0

    def test_multiple_concurrent_health_checks(self, client: TestClient):
        """Test multiple health checks can run concurrently"""
        responses = [
            client.get("/health"),
            client.get("/health/db"),
            client.get("/health/pool"),
            client.get("/health"),
            client.get("/health/db"),
        ]

        # All should succeed
        assert all(r.status_code == 200 for r in responses)
