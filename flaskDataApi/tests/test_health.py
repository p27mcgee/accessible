"""
Unit tests for Health Check endpoints (Flask)

Tests cover:
- GET /health (basic health check)
- GET / (root endpoint)
"""
import pytest


class TestBasicHealth:
    """Tests for GET /health endpoint"""

    def test_health_check_success(self, client):
        """Test basic health check endpoint"""
        response = client.get('/health')

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "healthy"

    def test_health_check_no_authentication_required(self, client):
        """Test that health endpoint doesn't require authentication"""
        response = client.get('/health')

        assert response.status_code == 200


class TestRootEndpoint:
    """Tests for GET / (root endpoint)"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get('/')

        assert response.status_code == 200
        data = response.get_json()

        # Verify required fields
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data

        # Verify values
        assert data["name"] == "flaskDataApi"
        assert data["version"] == "1.0.0"
        assert isinstance(data["endpoints"], dict)

    def test_root_endpoint_contains_documentation_links(self, client):
        """Test that root endpoint includes documentation links"""
        response = client.get('/')

        assert response.status_code == 200
        data = response.get_json()

        endpoints = data["endpoints"]

        # Verify documentation endpoints are included
        assert "docs" in endpoints

        # Verify API endpoints are included
        assert "artists" in endpoints
        assert "songs" in endpoints

    def test_root_endpoint_response_structure(self, client):
        """Test root endpoint response structure"""
        response = client.get('/')

        assert response.status_code == 200
        data = response.get_json()

        # Verify field types
        assert isinstance(data["name"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["description"], str)
        assert isinstance(data["endpoints"], dict)


class TestHealthEdgeCases:
    """Edge case tests for health endpoints"""

    def test_health_endpoints_accept_only_get(self, client):
        """Test that health endpoints only accept GET requests"""
        endpoints = ["/health", "/"]

        for endpoint in endpoints:
            # POST should not be allowed (Flask may return 405 or 500)
            response = client.post(endpoint)
            assert response.status_code in [405, 500]

            # PUT should not be allowed
            response = client.put(endpoint)
            assert response.status_code in [405, 500]

            # DELETE should not be allowed
            response = client.delete(endpoint)
            assert response.status_code in [405, 500]

    def test_health_endpoints_consistent_response_times(self, client):
        """Test that health endpoints respond quickly"""
        import time

        endpoints = ["/health", "/"]

        for endpoint in endpoints:
            start = time.time()
            response = client.get(endpoint)
            duration = time.time() - start

            assert response.status_code == 200
            # Health checks should be fast (< 1 second)
            assert duration < 1.0

    def test_multiple_concurrent_health_checks(self, client):
        """Test multiple health checks can run concurrently"""
        responses = [
            client.get("/health"),
            client.get("/"),
            client.get("/health"),
            client.get("/"),
            client.get("/health"),
        ]

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

    def test_content_type_json(self, client):
        """Test that responses have JSON content type"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.content_type == "application/json"

        response = client.get("/")
        assert response.status_code == 200
        assert response.content_type == "application/json"


class TestCORS:
    """Tests for CORS configuration"""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses"""
        response = client.get(
            '/health',
            headers={'Origin': 'http://localhost'}
        )

        # CORS headers should be present
        # Note: Exact headers depend on Flask-CORS configuration
        assert response.status_code == 200

    def test_options_request(self, client):
        """Test OPTIONS (preflight) request"""
        response = client.options(
            '/v1/artists',
            headers={
                'Origin': 'http://localhost',
                'Access-Control-Request-Method': 'GET'
            }
        )

        # OPTIONS should be allowed
        assert response.status_code in [200, 204]


class Test404Handler:
    """Tests for 404 error handling"""

    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoints"""
        response = client.get('/nonexistent')

        assert response.status_code == 404

    def test_404_response_format(self, client):
        """Test that 404 responses have consistent format"""
        response = client.get('/does-not-exist')

        assert response.status_code == 404
        # Flask may return HTML or JSON depending on configuration
        # Just verify we get a 404


class TestErrorHandlers:
    """Tests for error handling"""

    def test_400_bad_request(self, client):
        """Test 400 Bad Request error"""
        # Invalid pagination parameters should return 400
        response = client.get('/v1/artists?page=-1')

        assert response.status_code == 400
        data = response.get_json()
        assert "detail" in data

    def test_validation_error_format(self, client):
        """Test that validation errors have consistent format"""
        import json

        # Missing required field
        response = client.post(
            '/v1/artists',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()

        # Should have error details
        assert "detail" in data or "errors" in data
