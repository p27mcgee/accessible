# fastDataApi - Python Microservice

Python FastAPI microservice providing CRUD access to SQL Server.

### Artist Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/artists` | List all artists |
| GET | `/v1/artists/{id}` | Get one artist |
| POST | `/v1/artists` | Create new artist |
| PUT | `/v1/artists/{id}` | Update artist |
| DELETE | `/v1/artists/{id}` | Delete artist |

### Song Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/songs` | List all songs |
| GET | `/v1/songs/{id}` | Get one song |
| POST | `/v1/songs` | Create new song |
| PUT | `/v1/songs/{id}` | Update song |
| DELETE | `/v1/songs/{id}` | Delete song |

## Data Model

### Artist
```json
{
  "id": 1,
  "name": "David Bowie"
}
```

### Song
```json
{
  "id": 1,
  "title": "Space Oddity",
  "artistId": 1,
  "releaseDate": "1969-07-11",
  "url": "https://www.youtube.com/watch?v=iYYRH4apXDo",
  "distance": 238900.0
}
```

## Technology Stack

- **FastAPI** - Modern, high-performance web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization
- **pyodbc** - SQL Server database driver
- **Uvicorn** - ASGI server

## Project Structure

```
fastDataApi/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── database.py       # Database connection and session management
│   ├── models.py         # SQLAlchemy ORM models (Artist, Song)
│   ├── schemas.py        # Pydantic schemas (DTOs)
│   └── routers/
│       ├── __init__.py
│       ├── artists.py    # Artist CRUD endpoints
│       └── songs.py      # Song CRUD endpoints
├── Dockerfile
└── requirements.txt
```

## Running Locally (Without Docker)

### Prerequisites
- Python 3.11+
- SQL Server running (via Docker or local install)
- ODBC Driver 18 for SQL Server

### Setup

1. Install dependencies:
```bash
cd api
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DB_SERVER=localhost
export DB_PORT=1433
export DB_NAME=starsongs
export DB_USER=sa
export DB_PASSWORD=YourStrong@Passw0rd
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/swagger-ui.html
- **ReDoc**: http://localhost:8000/api-docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Example API Calls

### Create an Artist
```bash
curl -X POST http://localhost:8000/v1/artists \
  -H "Content-Type: application/json" \
  -d '{"name": "The Beatles"}'
```

### Get All Artists
```bash
curl http://localhost:8000/v1/artists
```

### Create a Song
```bash
curl -X POST http://localhost:8000/v1/songs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Across the Universe",
    "artistId": 1,
    "releaseDate": "1970-02-06",
    "url": "https://www.youtube.com/watch?v=90M60PzmxEE",
    "distance": 40000000.0
  }'
```

### Get All Songs
```bash
curl http://localhost:8000/v1/songs
```

### Update a Song
```bash
curl -X PUT http://localhost:8000/v1/songs/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Space Oddity (Updated)",
    "artistId": 1,
    "releaseDate": "1969-07-11",
    "url": "https://www.youtube.com/watch?v=iYYRH4apXDo",
    "distance": 238900.0
  }'
```

### Delete a Song
```bash
curl -X DELETE http://localhost:8000/v1/songs/1
```

## Development

### Adding New Endpoints

1. Create new router in `app/routers/`
2. Add ORM model in `app/models.py`
3. Add Pydantic schema in `app/schemas.py`
4. Include router in `app/main.py`

### Database Migrations

This project uses direct SQL scripts for schema management. To modify the schema:

1. Update `sql/schema.sql`
2. Run the init script to recreate the database
3. Update SQLAlchemy models in `app/models.py`

## License

Based on the star-songs project by McGee Cahill
