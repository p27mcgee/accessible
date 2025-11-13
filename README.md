# Accessible - Full Stack Development Environment

Docker Compose setup for running SQL Server on macOS (including Apple Silicon) with Python API backends (FastAPI and Flask) and Next.js frontend.

## Services

- **fastDataApi** - Python FastAPI backend (port 8000) - High-performance ASGI
- **flaskDataApi** - Python Flask backend (port 8001) - Traditional WSGI (demonstration)
- **nextui** - Next.js frontend (port 80)
- **SQL Server 2022** - Database (port 1433) - Managed independently for dev/test

Both APIs provide identical CRUD endpoints for artists and songs. You can choose which one to use or run both simultaneously for comparison.

**Note:** The database runs independently via Makefile for dev/test. In production, the database is external (managed service).

## Quick Start

### 1. Start and Initialize Database

```bash
# Start database container
make db-start

# Initialize database (create DB, schema, seed data)
make db-init

# Verify database is ready
make db-status
```

### 2. Start Application Services

```bash
# Start with FastAPI (recommended)
./start-with-api.sh fastapi

# Or start with Flask
./start-with-api.sh flask

# Or start both for comparison
./start-with-api.sh both
```

**Note:** See [SWITCHING_APIS.md](SWITCHING_APIS.md) for detailed instructions on switching between APIs.

**Note:** Images are built for linux/amd64 architecture and will run via Rosetta 2 on Apple Silicon Macs.

### 3. Access the Services

**Frontend:**
- Web UI: http://localhost (port 80)

**SQL Server:**
- Server: `localhost,1433`
- Username: `sa`
- Password: `YourStrong@Passw0rd` (⚠️ change this!)

**API:**
- API Base URL: http://localhost:8000
- Swagger UI: http://localhost:8000/swagger-ui.html
- API Docs: http://localhost:8000/api-docs

### 4. Test the API

```bash
# Get all artists
curl http://localhost:8000/v1/artists

# Get all songs
curl http://localhost:8000/v1/songs

# Create a new artist
curl -X POST http://localhost:8000/v1/artists \
  -H "Content-Type: application/json" \
  -d '{"name": "New Artist"}'
```

## Database Management

The database is managed independently via Makefile for development and testing:

```bash
make db-start    # Start database container
make db-stop     # Stop database container
make db-status   # Check database state (absent/empty/ready)
make db-init     # Initialize database
make db-clean    # Remove container and data (destructive)
make db-logs     # View database logs
make db-shell    # Open sqlcmd shell
```

See [DATABASE.md](DATABASE.md) for comprehensive database management documentation.

## Architecture Support

### Application Services (fastDataApi, nextui)

All application Docker images are built for **linux/amd64** architecture for maximum compatibility across deployment platforms:

- ✅ **Native** on Intel/AMD x86_64 servers
- ✅ **Compatible** with most cloud platforms (AWS, Azure, GCP)
- ✅ **Works** on Apple Silicon via Rosetta 2 emulation
- ✅ **Standard** for Docker Hub and container registries

**Note:** On Apple Silicon (M1/M2/M3), Docker Desktop will automatically use Rosetta 2 to run amd64 images with excellent performance.

### SQL Server

| Architecture | Image | Performance | Notes |
|-------------|-------|-------------|-------|
| **Apple Silicon (M1/M2/M3)** | SQL Server 2022 | Rosetta 2 (excellent) | **Recommended** - Most stable |
| **Intel/AMD (x86_64)** | SQL Server 2022 | Native (best) | Full compatibility |

### Why SQL Server 2022 (Not Azure SQL Edge)?

**SQL Server 2022** (current configuration):
- ✅ **Stable** - No compatibility issues on Apple Silicon
- ✅ **Full feature set** - Complete SQL Server functionality
- ✅ **Well-tested** - Production-ready with Rosetta 2 emulation
- ⚠️ Larger image size (~500MB compressed)

**Azure SQL Edge** (not recommended):
- ❌ `latest` tag has database path bugs
- ❌ Version `1.0.7` crashes on Apple Silicon with ARM64 instruction errors
- ⚠️ Limited feature set compared to full SQL Server

## Connecting to SQL Server

### Direct Connection (from host machine)
```
Server: localhost,1433
Database: starsongs
User Id: sa
Password: YourStrong@Passw0rd
TrustServerCertificate: True
```

### Using Azure Data Studio (Recommended)
1. Download from: https://docs.microsoft.com/en-us/sql/azure-data-studio/download
2. Connect with hostname `localhost`, port `1433`, user `sa`

### Using sqlcmd (via Makefile)
```bash
make db-shell
```

## Managing Services

### View logs
```bash
# All application services
docker compose logs -f

# Individual services
docker compose logs -f nextui
docker compose logs -f fastDataApi
docker compose logs -f flaskDataApi

# Database logs
make db-logs
```

### Stop Services
```bash
# Stop application services
docker compose down

# Stop database
make db-stop
```

### Reset database (⚠️ deletes all data)
```bash
make db-clean      # Remove database container and volume
make db-start      # Start fresh
make db-init       # Initialize
```

## Data Persistence

Database files are stored in a Docker volume named `sqlserver-data`. This persists data between container restarts.

See [DATABASE.md](DATABASE.md#backup-and-restore) for backup and restore procedures.

## Docker Image Management

### Semantic Versioning

The project uses semantic versioning (MAJOR.MINOR.PATCH) defined in `pyproject.toml`. This follows Python packaging standards (PEP 621).

**Version configuration:**
```toml
[project]
name = "accessible"
version = "1.0.0"  # Edit this to update version
```

**Quick version workflow:**

1. **Set version** - Edit `pyproject.toml` directly
2. **Build** - Run `make build` to build all images with version tag
3. **Tag** - Run `make tag` to create registry-prefixed tags
4. **Publish** - Run `make push` to publish to Docker Hub

**Detailed commands:**
```bash
# 1. Update version
vim pyproject.toml  # Change version = "1.1.0"

# 2. Build all services
make build

# 3. Tag for Docker Hub registry (pmcgee namespace)
make tag

# 4. Login to Docker Hub
docker login

# 5. Push to Docker Hub
make push
```

**Additional make commands:**
```bash
# Display current version
make version

# Build individual services
make build-fast-data-api
make build-flask-data-api
make build-ui

# Remove all images (free disk space)
make clean

# Show all available commands
make help
```

For complete build documentation, see [BUILD.md](BUILD.md).

### Cleaning Docker Resources

**Remove stopped containers and unused images:**
```bash
# Clean up stopped containers
docker compose down

# Remove unused images (frees disk space)
docker image prune -a

# Remove all unused containers, networks, images, and volumes
docker system prune -a --volumes
```

**Remove specific project images:**
```bash
# Remove all project images (using Makefile)
make clean

# Or manually remove specific images
docker rmi pmcgee/accessible-fast-data-api:latest
docker rmi pmcgee/accessible-flask-data-api:latest
docker rmi pmcgee/accessible-nextui:latest
```

**Clean and rebuild everything:**
```bash
# Stop and remove containers, networks, and volumes
docker compose down -v

# Remove project images
make clean

# Rebuild fresh
make build
make tag
```

### Building Docker Images

**Platform Architecture:**
All images are built for **linux/amd64** architecture. This ensures compatibility across:
- Production servers (typically amd64)
- Cloud platforms (AWS, Azure, GCP)
- Development on both Intel and Apple Silicon Macs

**Build all images:**
```bash
# Build all services with version from pyproject.toml
make build

# Verify platform
docker inspect accessible-fast-data-api:latest --format '{{.Os}}/{{.Architecture}}'
# Should output: linux/amd64
```

**Build specific service:**
```bash
# Build only FastAPI service
make build-fast-data-api

# Build only Flask service
make build-flask-data-api

# Build only the frontend
make build-ui
```

**Image naming:**
- Local build creates: `accessible-fast-data-api:1.0.0` and `accessible-fast-data-api:latest`
- After `make tag`: `pmcgee/accessible-fast-data-api:1.0.0` and `pmcgee/accessible-fast-data-api:latest`

For complete build documentation, see [BUILD.md](BUILD.md).

### Publishing Docker Images

**Quick publish to Docker Hub:**
```bash
# 1. Build images
make build

# 2. Tag for registry
make tag

# 3. Login to Docker Hub
docker login

# 4. Push all images
make push
```

This publishes all three services (FastAPI, Flask, Next.js) to Docker Hub under the `pmcgee` namespace.

**Verify published images:**
Visit https://hub.docker.com/u/pmcgee to see:
- `pmcgee/accessible-fast-data-api:1.0.0` and `:latest`
- `pmcgee/accessible-flask-data-api:1.0.0` and `:latest`
- `pmcgee/accessible-nextui:1.0.0` and `:latest`

### Using Published Images

The `compose.yaml` is configured to use published images from Docker Hub:

```yaml
services:
  fastDataApi:
    image: pmcgee/accessible-fast-data-api:latest
    # No build section - uses pre-built image

  flaskDataApi:
    image: pmcgee/accessible-flask-data-api:latest
    # No build section - uses pre-built image

  nextui:
    image: pmcgee/accessible-nextui:latest
    # No build section - uses pre-built image
```

**Pull and run published images:**
```bash
# Pull latest images from Docker Hub
docker compose pull

# Start with pulled images
docker compose --profile fastapi up -d
```

## Troubleshooting

### Password requirements
SA password must be at least 8 characters and contain:
- Uppercase letters
- Lowercase letters
- Numbers
- Symbols

### Port already in use
Change the port in `compose.yaml` or `.env`:
```yaml
ports:
  - "1434:1433"  # Use port 1434 on host
```

### Database not ready
Wait 30-60 seconds for SQL Server to fully start. Check status:
```bash
make db-status
make db-logs
```

### Verifying image architecture
To confirm images are built for amd64:
```bash
# Check fastDataApi
docker inspect accessible-fast-data-api:latest --format '{{.Architecture}}'
# Should output: amd64

# Check nextui
docker inspect accessible-nextui:latest --format '{{.Architecture}}'
# Should output: amd64

# List all images with architecture
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.ID}}" | grep accessible
```

## Next Steps

- Customize the Next.js frontend in the `nextui/` directory
- Add authentication/authorization
- Implement additional features and endpoints
- Deploy to production environment
