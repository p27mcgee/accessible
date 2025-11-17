# Accessible - Full Stack Development Environment

Docker Compose setup for running SQL Server on macOS (including Apple Silicon) with Python API backends (FastAPI and Flask) and Next.js frontend.

## Services

- **fastDataApi** - Python FastAPI backend (port 8000) - High-performance ASGI
- **flaskDataApi** - Python Flask backend (port 8001) - Traditional WSGI
- **nextui** - Next.js frontend (port 80)
- **SQL Server 2022** - Database (port 1433) - Managed independently for dev/test

Both APIs provide identical CRUD endpoints for artists and songs. Choose which one to use or run both simultaneously for comparison.

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### Core Guides
- **[DATABASE.md](docs/DATABASE.md)** - Database management (backup, restore, migrations)
- **[BUILD.md](docs/BUILD.md)** - Building, versioning, and publishing Docker images
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Project architecture and technology stack
- **[SWITCHING_APIS.md](docs/SWITCHING_APIS.md)** - How to switch between FastAPI and Flask

### Configuration
- **[CONFIGURATION.md](docs/CONFIGURATION.md)** - Environment variables, CORS, and database pooling
- **[API.md](docs/API.md)** - API features including pagination

### Production
- **[TODO.md](docs/TODO.md)** - Production readiness assessment and roadmap

---

## Development Setup

For local development with PyCharm, VS Code, or other IDEs, set up a Python virtual environment:

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Create Virtual Environment

```bash
# Navigate to project root
cd /path/to/accessible

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Install Dependencies

Install dependencies for the API you want to work on:

**For FastAPI development:**
```bash
pip install --upgrade pip
pip install -r fastDataApi/requirements.txt
```

**For Flask development:**
```bash
pip install --upgrade pip
pip install -r flaskDataApi/requirements.txt
```

**For both APIs:**
```bash
pip install -r fastDataApi/requirements.txt
pip install -r flaskDataApi/requirements.txt
```

### PyCharm Configuration

1. **Set Project Interpreter:**
   - Open PyCharm Settings/Preferences (Cmd+, on macOS, Ctrl+Alt+S on Windows/Linux)
   - Navigate to: Project: accessible → Python Interpreter
   - Click the gear icon → Add Interpreter → Add Local Interpreter
   - Select "Virtualenv Environment" → "Existing"
   - Browse to: `<project-root>/venv/bin/python` (macOS/Linux) or `<project-root>\venv\Scripts\python.exe` (Windows)
   - Click OK

2. **Mark Source Roots:**
   - Right-click on `fastDataApi/app` → Mark Directory as → Sources Root
   - Right-click on `flaskDataApi/app` → Mark Directory as → Sources Root

3. **Configure Run/Debug:**
   - PyCharm should now provide autocomplete, type checking, and debugging
   - You can create run configurations for the APIs if needed

### VS Code Configuration

Create `.vscode/settings.json` in the project root:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.analysis.extraPaths": [
    "${workspaceFolder}/fastDataApi",
    "${workspaceFolder}/flaskDataApi"
  ]
}
```

### Verify Installation

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Check Python version
python --version  # Should be 3.11 or higher

# Verify packages are installed
pip list | grep fastapi
pip list | grep flask
```

### Running Locally (Outside Docker)

While the project is designed to run in Docker, you can run the APIs locally for debugging:

**FastAPI:**
```bash
cd fastDataApi
uvicorn app.main:app --reload --port 8000
```

**Flask:**
```bash
cd flaskDataApi
python -m flask --app app run --port 8001 --debug
```

**Note:** Ensure the SQL Server database is running (via `make db-start`) and accessible at `localhost:1433`.

---

## Quick Start

### 1. Start and Initialize Database

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
# Start with FastAPI (recommended)
./start-with-api.sh fastapi

# Or start with Flask
./start-with-api.sh flask

# Or start both APIs simultaneously
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

**Note:** The project uses pre-built images from Docker Hub. The first run will pull these images automatically.

### 3. Access the Services

**Frontend:**
- Web UI: http://localhost (port 80)

**FastAPI (if using fastapi or both profile):**
- Base URL: http://localhost:8000
- Swagger UI: http://localhost:8000/swagger-ui.html
- Health Check: http://localhost:8000/health

**Flask API (if using flask or both profile):**
- Base URL: http://localhost:8001
- Swagger UI: http://localhost:8001/apidocs
- Health Check: http://localhost:8001/health

**SQL Server:**
- Host: localhost, Port: 1433
- Database: starsongs
- Username: sa, Password: YourStrong@Passw0rd (⚠️ change this!)

### 4. Test the API

```bash
# Get all artists (paginated)
curl http://localhost:8000/v1/artists

# Expected response
{
  "items": [
    {"id": 1, "name": "David Bowie"},
    {"id": 2, "name": "The Beatles"}
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 5,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}

# Get all songs
curl http://localhost:8000/v1/songs

# Create a new artist
curl -X POST http://localhost:8000/v1/artists \
  -H "Content-Type: application/json" \
  -d '{"name": "Led Zeppelin"}'

# Create a new song
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

### 5. Using Swagger UI

The easiest way to test the API:

**FastAPI:** http://localhost:8000/swagger-ui.html
**Flask:** http://localhost:8001/apidocs

1. Open Swagger UI in your browser
2. Click on an endpoint to expand it
3. Click "Try it out" to test
4. Fill in parameters and click "Execute"
5. View the response

---

## Configuration

### Environment Variables

Create a `.env` file to configure the application:

```bash
# Copy template
cp .env.example .env

# Edit configuration
vim .env
```

**Key configuration options:**

```bash
# CORS Configuration
CORS_ORIGINS=http://localhost,http://localhost:80,http://localhost:3000

# Database Connection Pool
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_SQL_ECHO=false
```

See [CONFIGURATION.md](docs/CONFIGURATION.md) for complete reference.

---

## Database Management

```bash
make db-start    # Start database container
make db-stop     # Stop database container
make db-status   # Check database state (absent/empty/ready)
make db-init     # Initialize database
make db-clean    # Remove container and data (destructive)
make db-logs     # View database logs
make db-shell    # Open sqlcmd shell
```

### Using Azure Data Studio

1. Download from: https://docs.microsoft.com/en-us/sql/azure-data-studio/download
2. Connect with:
   - Server: localhost,1433
   - Authentication: SQL Login
   - Username: sa
   - Password: YourStrong@Passw0rd

See [DATABASE.md](docs/DATABASE.md) for comprehensive database documentation.

---

## Managing Services

### View Logs

```bash
# All application services
docker compose logs -f

# Individual services
docker compose logs -f fastDataApi
docker compose logs -f flaskDataApi
docker compose logs -f nextui

# Database logs
make db-logs
```

### Restart Services

```bash
# Restart application services
docker compose restart

# Restart individual service
docker compose restart fastDataApi

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

---

## Architecture Support

### Application Services

All application Docker images are built for **linux/amd64** architecture:

- ✅ Native on Intel/AMD x86_64 servers
- ✅ Compatible with most cloud platforms (AWS, Azure, GCP)
- ✅ Works on Apple Silicon via Rosetta 2 emulation
- ✅ Standard for Docker Hub and container registries

### SQL Server

| Architecture | Image | Performance | Notes |
|-------------|-------|-------------|-------|
| **Apple Silicon (M1/M2/M3)** | SQL Server 2022 | Rosetta 2 (excellent) | Recommended - Most stable |
| **Intel/AMD (x86_64)** | SQL Server 2022 | Native (best) | Full compatibility |

**Why SQL Server 2022?**
- ✅ Stable on Apple Silicon with Rosetta 2
- ✅ Full feature set
- ✅ Production-ready
- ⚠️ Azure SQL Edge has compatibility issues on ARM64

---

## Docker Image Management

### Semantic Versioning

Version is defined in `pyproject.toml`:

```toml
[project]
name = "accessible"
version = "1.0.0"  # Edit this to update version
```

### Building Images Locally

The project uses pre-built images from Docker Hub by default. To build locally:

```bash
# Build all services
make build

# Build specific service
make build-fast-data-api
make build-flask-data-api
make build-ui

# Display current version
make version

# Remove all images
make clean

# Show all commands
make help
```

### Publishing to Docker Hub

```bash
# 1. Update version in pyproject.toml
vim pyproject.toml  # Change version = "1.1.0"

# 2. Build all services
make build

# 3. Tag for Docker Hub registry
make tag

# 4. Login to Docker Hub
docker login

# 5. Push to Docker Hub
make push
```

Images are published to the `pmcgee` namespace on Docker Hub:
- `pmcgee/accessible-fast-data-api:latest`
- `pmcgee/accessible-flask-data-api:latest`
- `pmcgee/accessible-nextui:latest`

See [BUILD.md](docs/BUILD.md) for complete documentation.

---

## Project Structure

```
accessible/
├── fastDataApi/          # Python FastAPI backend (port 8000)
│   ├── app/
│   │   ├── main.py      # FastAPI application
│   │   ├── database.py  # Database connection with pooling
│   │   ├── models.py    # SQLAlchemy ORM models
│   │   ├── schemas.py   # Pydantic schemas
│   │   └── routers/     # API endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── flaskDataApi/        # Python Flask backend (port 8001)
│   ├── app/
│   │   ├── __init__.py  # Flask application factory
│   │   ├── database.py  # Database connection with pooling
│   │   ├── models.py    # SQLAlchemy ORM models
│   │   ├── schemas.py   # Marshmallow schemas
│   │   └── routes/      # API endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── nextui/              # Next.js frontend
│   ├── app/            # Next.js App Router
│   ├── components/     # React components
│   ├── lib/           # API client and utilities
│   ├── Dockerfile
│   └── package.json
├── sql/                # Database scripts
│   ├── init_db.sql    # Create database
│   ├── schema.sql     # Create tables
│   └── seed_data.sql  # Sample data
├── docs/              # Documentation
├── compose.yaml       # Docker Compose config
├── Makefile          # Build and database management
└── pyproject.toml    # Version and project metadata
```

See [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed architecture.

---

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
# Check logs
docker compose logs fastDataApi
docker compose logs flaskDataApi

# Verify database is ready first
make db-status

# Restart services
docker compose restart
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
- For database: Change Makefile DB_PORT

### Switching between APIs

See [SWITCHING_APIS.md](docs/SWITCHING_APIS.md) for detailed instructions.

---

## Next Steps

- **Add authentication** - Implement JWT or OAuth2 (see TODO.md)
- **Configure CORS** - Set allowed origins for your domain (see CONFIGURATION.md)
- **Tune database pool** - Optimize for your workload (see CONFIGURATION.md)
- **Write tests** - Add pytest tests for API and Vitest for frontend
- **Deploy to production** - Review TODO.md for production readiness checklist

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Flask Documentation**: https://flask.palletsprojects.com
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **SQL Server Documentation**: https://docs.microsoft.com/en-us/sql/
