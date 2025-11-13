# flaskDataApi - Flask Microservice

A Flask-based REST API microservice for CRUD operations on SQL Server, created for demonstration and comparison purposes with the FastAPI implementation (fastDataApi).

## Purpose

This service demonstrates an alternative implementation of the same REST API using Flask instead of FastAPI. It is functionally equivalent to fastDataApi but uses different Python web framework technologies.

⚠️ **Note**: This is for demonstration purposes, not production use. For production workloads, fastDataApi (FastAPI) is recommended for better performance and modern features.

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | Flask 3.0 | WSGI-based web framework |
| **WSGI Server** | Gunicorn | Production-grade WSGI server |
| **ORM** | SQLAlchemy via Flask-SQLAlchemy | Database abstraction |
| **Serialization** | Marshmallow | Data validation and serialization |
| **API Docs** | Flasgger | Swagger/OpenAPI documentation |
| **Database** | SQL Server 2022 | Relational database |
| **Driver** | pyodbc | ODBC driver for SQL Server |

## Key Differences from fastDataApi

| Aspect | FastAPI (fastDataApi) | Flask (flaskDataApi) |
|--------|---------------------|---------------------|
| **Framework Type** | ASGI (async) | WSGI (sync) |
| **Server** | Uvicorn | Gunicorn |
| **Validation** | Pydantic (automatic) | Marshmallow (manual) |
| **Documentation** | Auto-generated from types | Docstring annotations |
| **Performance** | Faster (~20-40%) | Adequate for most use cases |
| **Code Style** | Type hints everywhere | More traditional Python |
| **Dependency Injection** | `Depends()` pattern | Flask app context |

## API Endpoints

All endpoints are identical to fastDataApi for compatibility:

### Artists API (`/v1/artists`)
- `GET /v1/artists` - List all artists
- `GET /v1/artists/{id}` - Get artist by ID
- `POST /v1/artists` - Create new artist
- `PUT /v1/artists/{id}` - Update artist
- `DELETE /v1/artists/{id}` - Delete artist

### Songs API (`/v1/songs`)
- `GET /v1/songs` - List all songs
- `GET /v1/songs/{id}` - Get song by ID
- `POST /v1/songs` - Create new song
- `PUT /v1/songs/{id}` - Update song
- `DELETE /v1/songs/{id}` - Delete song

## API Documentation

- **Swagger UI**: http://localhost:8001/apidocs
- **API JSON**: http://localhost:8001/apispec.json
- **Health Check**: http://localhost:8001/health

## Running the Service

### With Docker Compose (Recommended)

```bash
# Start all services including flaskDataApi
docker compose up -d

# View logs
docker compose logs -f flaskDataApi

# Restart the service
docker compose restart flaskDataApi

# Rebuild after code changes
docker compose up -d --build flaskDataApi
```

### Standalone Development

```bash
cd flaskDataApi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_SERVER=localhost
export DB_PORT=1433
export DB_NAME=starsongs
export DB_USER=sa
export DB_PASSWORD=YourStrong@Passw0rd

# Run with Flask development server
python run.py

# Or run with Gunicorn (production)
gunicorn --bind 0.0.0.0:8001 --workers 4 run:app
```

## Testing the API

### Get all artists
```bash
curl http://localhost:8001/v1/artists
```

### Get all songs
```bash
curl http://localhost:8001/v1/songs
```

### Create a new artist
```bash
curl -X POST http://localhost:8001/v1/artists \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Artist"}'
```

### Create a new song
```bash
curl -X POST http://localhost:8001/v1/songs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Song",
    "artist_id": 1,
    "release_date": "2024-01-01",
    "url": "https://example.com",
    "distance": 100.0
  }'
```

## Project Structure

```
flaskDataApi/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── database.py          # Flask-SQLAlchemy setup
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Marshmallow schemas
│   ├── errors.py            # Error handlers
│   └── routes/              # Flask blueprints
│       ├── __init__.py
│       ├── artists.py       # Artist CRUD endpoints
│       └── songs.py         # Song CRUD endpoints
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container build instructions
└── README.md               # This file
```

## Comparison: Code Examples

### Creating an Endpoint

**FastAPI (fastDataApi):**
```python
@router.post("", response_model=Artist, status_code=status.HTTP_201_CREATED)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = ArtistModel(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist
```

**Flask (flaskDataApi):**
```python
@artists_bp.route('', methods=['POST'])
def create_artist():
    try:
        data = artist_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"detail": "Validation error", "errors": err.messages}), 400

    db_artist = Artist(name=data['name'])
    db.session.add(db_artist)
    db.session.commit()
    db.session.refresh(db_artist)

    return jsonify(artist_schema.dump(db_artist)), 201
```

### Key Observations

1. **FastAPI**: Validation happens automatically via type hints
2. **Flask**: Manual validation with explicit error handling
3. **FastAPI**: Response serialization is automatic
4. **Flask**: Manual serialization with schema.dump()
5. **FastAPI**: Dependencies injected via `Depends()`
6. **Flask**: Database accessed via `db.session` (app context)

## Performance Considerations

- **Request Throughput**: FastAPI typically handles 20-40% more requests/second
- **Latency**: Similar for simple CRUD operations
- **Concurrency**: FastAPI's async support better for I/O-bound operations
- **For this use case**: Performance difference is negligible for typical workloads

## When to Use Flask vs FastAPI

**Use Flask (this service) when:**
- You prefer traditional WSGI deployment
- Your team is more familiar with Flask
- You need extensive Flask plugin ecosystem
- Performance requirements are moderate

**Use FastAPI (fastDataApi) when:**
- You want modern Python async/await support
- You need automatic API documentation
- You prioritize performance and type safety
- You're building a new greenfield project

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_SERVER` | localhost | SQL Server host |
| `DB_PORT` | 1433 | SQL Server port |
| `DB_NAME` | starsongs | Database name |
| `DB_USER` | sa | Database username |
| `DB_PASSWORD` | YourStrong@Passw0rd | Database password |

## License

Apache 2 License
