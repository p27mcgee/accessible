# Getting Started with Accessible

## Summary

This project provides a **full-stack application** with **SQL Server backend**, **Python API backends** (both **FastAPI** and **Flask**), and **Next.js frontend**.

**What's included:**
- SQL Server 2022 running in Docker (with Rosetta 2 emulation on Apple Silicon)
- Python FastAPI backend with CRUD endpoints (fastDataApi, port 8000)
- Python Flask backend with identical CRUD endpoints (flaskDataApi, port 8001)
- Next.js frontend with React Server Components (nextui)
- Database schema and sample data
- Swagger/OpenAPI documentation for both APIs

## Quick Start

### 1. Start and Initialize the Database

The database is managed independently for dev/test:

```bash
# Start database container
make db-start

# Initialize database (create DB, schema, seed data)
make db-init

# Verify database is ready
make db-status
```

You should see:
```
✅ Database state: READY
   Database 'starsongs' is initialized and ready for use.
   Tables: Artist, Song
   Data: 5 artists, 6 songs
```

### 2. Start Application Services

**Option A: Using the wrapper script (Recommended)**
```bash
# Start with FastAPI (recommended for production)
./start-with-api.sh fastapi

# Or start with Flask (for demonstration)
./start-with-api.sh flask

# Or start both APIs simultaneously (for comparison)
./start-with-api.sh both
```

**Option B: Using Docker Compose profiles directly**
```bash
# Start with FastAPI
docker compose --profile fastapi up -d

# Or start with Flask
docker compose --profile flask up -d

# Or start both APIs
docker compose --profile both up -d
```

**Note:** The project uses **pre-built images** from Docker Hub (pmcgee namespace). The first run will pull these images automatically.

### 3. Load Additional Sample Data (Optional)

If you need to manually add data:

```bash
# Open database shell
make db-shell

# Then run SQL commands
INSERT INTO dbo.Artist (name) VALUES ('New Artist');
GO

SELECT * FROM dbo.Artist;
GO

quit
```

### 4. Access the Services

**Frontend:**
- Web UI: http://localhost (port 80)

**FastAPI Endpoints (if using fastapi or both profile):**
- Base URL: http://localhost:8000
- Swagger UI: http://localhost:8000/swagger-ui.html
- API Documentation: http://localhost:8000/api-docs
- Health Check: http://localhost:8000/health

**Flask API Endpoints (if using flask or both profile):**
- Base URL: http://localhost:8001
- Swagger UI: http://localhost:8001/apidocs
- Health Check: http://localhost:8001/health

**SQL Server:**
- Host: localhost
- Port: 1433
- Database: starsongs
- Username: sa
- Password: YourStrong@Passw0rd

## Testing the API

These examples use port 8000 (FastAPI). If using Flask, change to port 8001.

### Get All Artists
```bash
# FastAPI
curl http://localhost:8000/v1/artists

# Flask
curl http://localhost:8001/v1/artists
```

**Expected Response:**
```json
[
    {
        "name": "David Bowie",
        "id": 1
    },
    {
        "name": "The Beatles",
        "id": 2
    }
]
```

### Get All Songs
```bash
curl http://localhost:8000/v1/songs
```

**Expected Response:**
```json
[
    {
        "title": "Space Oddity",
        "artist_id": 1,
        "release_date": "1969-07-11",
        "url": "https://www.youtube.com/watch?v=iYYRH4apXDo",
        "distance": 238900.0,
        "id": 1
    }
]
```

### Create a New Artist
```bash
curl -X POST http://localhost:8000/v1/artists \
  -H "Content-Type: application/json" \
  -d '{"name": "Led Zeppelin"}'
```

**Expected Response:**
```json
{
    "name": "Led Zeppelin",
    "id": 6
}
```

### Create a New Song
```bash
curl -X POST http://localhost:8000/v1/songs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Stairway to Heaven",
    "artist_id": 6,
    "release_date": "1971-11-08",
    "url": "https://www.youtube.com/watch?v=QkF3oxziUI4",
    "distance": 100.0
  }'
```

### Update an Artist
```bash
curl -X PUT http://localhost:8000/v1/artists/6 \
  -H "Content-Type: application/json" \
  -d '{"name": "Led Zeppelin (Updated)"}'
```

### Delete a Song
```bash
curl -X DELETE http://localhost:8000/v1/songs/1
```

## Using Swagger UI

The easiest way to test the API is through the Swagger UI:

**FastAPI Swagger UI:**
1. Open your browser to: http://localhost:8000/swagger-ui.html
2. You'll see all available endpoints with descriptions
3. Click on an endpoint to expand it
4. Click "Try it out" to test the endpoint
5. Fill in parameters and click "Execute"
6. View the response below

**Flask API Swagger UI:**
1. Open your browser to: http://localhost:8001/apidocs
2. Follow same steps as FastAPI

Both APIs provide identical endpoints and responses.

## Managing the Environment

### View Logs
```bash
# Application services
docker compose logs -f

# Individual application services
docker compose logs -f nextui
docker compose logs -f fastDataApi
docker compose logs -f flaskDataApi

# Database logs
make db-logs
```

### Restart Services
```bash
# Restart application services
docker compose restart

# Restart individual services
docker compose restart nextui
docker compose restart fastDataApi
docker compose restart flaskDataApi

# Restart database
make db-stop
make db-start
```

### Stop Services
```bash
# Stop application services
docker compose down

# Stop database
make db-stop
```

### Stop and Remove Data
```bash
# Stop and remove application services
docker compose down

# Remove database and all data
make db-clean
```

## Connecting to SQL Server Directly

### Using Azure Data Studio (Recommended)
1. Download from: https://docs.microsoft.com/en-us/sql/azure-data-studio/download
2. Connect with:
   - Server: localhost,1433
   - Authentication: SQL Login
   - Username: sa
   - Password: YourStrong@Passw0rd

### Using sqlcmd (via Makefile)
```bash
make db-shell
```

This opens an interactive SQL shell where you can run queries:
```sql
USE starsongs;
GO

SELECT * FROM dbo.Artist;
GO

quit
```

## Project Structure

```
accessible/
├── fastDataApi/            # Python FastAPI backend (port 8000)
│   ├── app/
│   │   ├── main.py        # FastAPI application
│   │   ├── database.py    # Database connection
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── schemas.py     # Pydantic schemas
│   │   └── routers/       # API endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── flaskDataApi/          # Python Flask backend (port 8001)
│   ├── app/
│   │   ├── __init__.py    # Flask application factory
│   │   ├── database.py    # Database connection
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── schemas.py     # Marshmallow schemas
│   │   └── routes/        # API endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── nextui/                # Next.js frontend
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/             # API client and utilities
│   ├── types/           # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── sql/                  # Database scripts
│   ├── init_db.sql      # Create database
│   ├── schema.sql       # Create tables
│   └── seed_data.sql    # Sample data
├── compose.yaml         # Docker Compose config (uses pre-built images)
├── Makefile             # Build system (for building images)
├── pyproject.toml       # Version management and project metadata
└── init-database.sh     # Database setup script
```

## Troubleshooting

### Database won't start
```bash
# Check database status
make db-status

# Check database logs
make db-logs

# Clean and restart
make db-clean
make db-start
make db-init
```

### Database not ready
```bash
# Check status
make db-status

# If EMPTY, initialize it
make db-init

# If ABSENT, start it first
make db-start
make db-init
```

### API won't start
```bash
# Check logs for FastAPI
docker compose logs fastDataApi

# Check logs for Flask
docker compose logs flaskDataApi

# Verify database is ready first
make db-status

# Restart services
docker compose restart fastDataApi
docker compose restart flaskDataApi
```

### Can't connect to database
```bash
# Verify database is ready
make db-status

# Test database shell
make db-shell

# Check API environment variables
docker compose exec fastDataApi env | grep DB_
```

### Port conflicts
If port 8000, 8001, or 1433 is already in use:
- For APIs: Edit `compose.yaml` port mappings
- For database: Stop conflicting service or change Makefile DB_PORT

### Switching between APIs
See [SWITCHING_APIS.md](SWITCHING_APIS.md) for detailed instructions on switching between FastAPI and Flask.

## Next Steps

- **Add authentication**: Implement JWT or OAuth2 in both API and frontend
- **Add pagination**: Implement pagination for list endpoints
- **Add filtering**: Add query parameters and search functionality
- **Write tests**: Add pytest tests for the API and Vitest tests for frontend
- **Deploy**: Deploy to a cloud provider (AWS, Azure, or Vercel)

## Database Management

For comprehensive database management documentation:

```bash
make db-start    # Start database container
make db-stop     # Stop database container
make db-status   # Check state (absent/empty/ready)
make db-init     # Initialize database
make db-clean    # Remove container and data
make db-logs     # View logs
make db-shell    # Open SQL shell
```

See [DATABASE.md](DATABASE.md) for complete database documentation.

## Building Images Locally

The project uses pre-built images from Docker Hub by default. If you want to build images locally (for development or customization):

```bash
# Build all services
make build

# Tag for local testing
make tag

# See BUILD.md for complete build documentation
```

See [BUILD.md](BUILD.md) for comprehensive build and publishing instructions.

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Flask Documentation**: https://flask.palletsprojects.com
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **SQL Server Documentation**: https://docs.microsoft.com/en-us/sql/
- **Switching APIs Guide**: [SWITCHING_APIS.md](SWITCHING_APIS.md)
- **Build Guide**: [BUILD.md](BUILD.md)
- **Database Management**: [DATABASE.md](DATABASE.md)
