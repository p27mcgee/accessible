# Flask Unit Tests

Comprehensive unit tests for the flaskDataApi microservice.

## Test Coverage

### Endpoints Tested

#### Artist Endpoints (`test_artists.py`)
- ✅ GET `/v1/artists` - List all artists with pagination
- ✅ GET `/v1/artists/{id}` - Get single artist
- ✅ POST `/v1/artists` - Create artist
- ✅ PUT `/v1/artists/{id}` - Update artist (with upsert behavior)
- ✅ DELETE `/v1/artists/{id}` - Delete artist

**Test Coverage:**
- Pagination (default, custom page size, multiple pages)
- Validation (invalid IDs, missing fields, boundary cases)
- Edge cases (empty database, Unicode characters, concurrent creation)
- Error handling (404 Not Found, 400 Bad Request, validation errors)

#### Song Endpoints (`test_songs.py`)
- ✅ GET `/v1/songs` - List all songs with pagination
- ✅ GET `/v1/songs/{id}` - Get single song
- ✅ POST `/v1/songs` - Create song
- ✅ PUT `/v1/songs/{id}` - Update song (with upsert behavior)
- ✅ DELETE `/v1/songs/{id}` - Delete song

**Test Coverage:**
- Foreign key validation (artist_id must exist)
- Field mapping (database columns to API fields)
- Null handling (optional fields)
- Date and numeric validation
- Complex scenarios (multiple songs per artist, changing artist)

#### Health Endpoints (`test_health.py`)
- ✅ GET `/health` - Basic health check
- ✅ GET `/` - Root endpoint (API info)
- ✅ CORS configuration tests
- ✅ Error handler tests

**Test Coverage:**
- Response structure validation
- Content type verification
- HTTP method validation
- CORS preflight handling

## Setup

### 1. Install Dependencies

```bash
cd flaskDataApi

# Install production dependencies
pip install -r requirements.txt

# Install development/test dependencies
pip install -r requirements-dev.txt
```

### 2. Verify Installation

```bash
pytest --version
# Should output: pytest 8.0.0 or higher
```

## Running Tests

### Run All Tests

```bash
# From flaskDataApi directory
pytest

# Or from project root
cd flaskDataApi && pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
# Run only artist tests
pytest tests/test_artists.py

# Run only song tests
pytest tests/test_songs.py

# Run only health check tests
pytest tests/test_health.py
```

### Run Specific Test Class

```bash
# Run only GET endpoint tests for artists
pytest tests/test_artists.py::TestGetAllArtists

# Run only create song tests
pytest tests/test_songs.py::TestCreateSong
```

### Run Specific Test Function

```bash
# Run a single test
pytest tests/test_artists.py::TestGetAllArtists::test_get_all_artists_empty_database
```

### Run Tests Matching Pattern

```bash
# Run all tests with "pagination" in the name
pytest -k pagination

# Run all tests with "create" in the name
pytest -k create

# Run all tests with "invalid" in the name
pytest -k invalid
```

## Code Coverage

### Generate Coverage Report

```bash
# Run tests with coverage (HTML report)
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Report in Terminal

```bash
# Show coverage in terminal
pytest --cov=app --cov-report=term-missing
```

### Coverage Summary

```bash
# Quick coverage summary
pytest --cov=app --cov-report=term
```

### Generate XML Report (for CI/CD)

```bash
pytest --cov=app --cov-report=xml
```

## Test Markers

Tests are organized using pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Debugging Tests

### Run with Print Statements

```bash
# Show print statements during test execution
pytest -s

# Or
pytest --capture=no
```

### Stop on First Failure

```bash
pytest -x
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Run Last Failed Tests

```bash
# Rerun only tests that failed last time
pytest --lf

# Or
pytest --last-failed
```

### Run Failed Tests First

```bash
pytest --ff
```

## Test Configuration

Tests are configured via `pytest.ini`:

- **Test Discovery**: Automatically finds files matching `test_*.py`
- **Database**: Uses in-memory SQLite database (no SQL Server required)
- **Coverage**: Excludes test files and virtual environments
- **Environment Variables**: Test-specific settings pre-configured

## Test Database

Tests use an **in-memory SQLite database** for speed and isolation:

- ✅ No external database required
- ✅ Each test gets a fresh database
- ✅ Tests are independent and can run in any order
- ✅ Fast execution (no network I/O)

**Important:** SQLite has some differences from SQL Server:
- Auto-increment IDs may behave differently
- Some SQL Server-specific features aren't available
- Foreign key constraints work differently

For **integration tests with actual SQL Server**, see the main project documentation.

## Continuous Integration

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd flaskDataApi
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: |
          cd flaskDataApi
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./flaskDataApi/coverage.xml
```

## Writing New Tests

### Test Structure

```python
# tests/test_example.py
import pytest
import json


class TestMyFeature:
    """Tests for my feature"""

    def test_something(self, client):
        """Test description"""
        # Arrange
        data = {"field": "value"}

        # Act
        response = client.post(
            '/endpoint',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 201
        assert response.get_json()["field"] == "value"
```

### Using Fixtures

```python
def test_with_artist(self, client, sample_artist):
    """Use sample_artist fixture"""
    response = client.get(f'/v1/artists/{sample_artist.id}')
    assert response.status_code == 200
```

### Available Fixtures

From `conftest.py`:

- `app` - Flask application
- `client` - Flask test client
- `db_session` - SQLAlchemy database session
- `sample_artist` - Single artist in database
- `sample_artists` - Multiple artists (12 total)
- `sample_song` - Single song with artist
- `sample_songs` - Multiple songs (5 total)
- `song_without_artist` - Song with no artist

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear test function names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **One Assertion Per Concept**: Keep tests focused
5. **Test Edge Cases**: Include boundary values and error conditions
6. **Use Fixtures**: Reuse test data setup
7. **Document Intent**: Add docstrings to test functions

## Troubleshooting

### Tests Fail with Import Errors

```bash
# Make sure you're in the correct directory
cd /home/pmcgee/_dev/accessible/flaskDataApi

# Make sure dependencies are installed
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Tests Fail with Database Errors

The test suite uses SQLite, which should work out of the box. If you see database errors:

1. Check that SQLite is available: `python -c "import sqlite3; print(sqlite3.version)"`
2. Verify test configuration in `pytest.ini`
3. Check that fixtures are being used correctly

### Slow Test Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

### Coverage Not Generated

```bash
# Make sure pytest-cov is installed
pip install pytest-cov

# Run with explicit coverage options
pytest --cov=app --cov-report=term-missing
```

## Test Statistics

Current test coverage:

```
Test Files: 3
Test Classes: 18
Test Functions: 82

Endpoints Covered: 13
- Artist endpoints: 5
- Song endpoints: 5
- Health endpoints: 2
- Error handlers: 1

Coverage: 81%
```

## Key Differences from FastAPI Tests

1. **Test Client**: Uses Flask's `test_client()` instead of FastAPI's `TestClient`
2. **JSON Handling**: Must use `json.dumps()` for request bodies and `response.get_json()` for responses
3. **Content Type**: Must explicitly set `content_type='application/json'` for POST/PUT requests
4. **Error Responses**: Flask uses `{"detail": "..."}` format
5. **Method Routing**: Flask doesn't enforce HTTP methods as strictly as FastAPI

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing Guide](https://flask.palletsprojects.com/en/latest/testing/)
- [pytest-flask Documentation](https://pytest-flask.readthedocs.io/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)

## Next Steps

- [ ] Add integration tests with real SQL Server database
- [ ] Add performance/load tests
- [ ] Add E2E tests
- [ ] Add API contract tests (OpenAPI schema validation)
- [ ] Set up automated coverage reporting
- [ ] Add mutation testing
