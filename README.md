# Accessible - Full Stack Development Environment

Docker Compose setup for running SQL Server on macOS (including Apple Silicon) with a Python FastAPI backend and Next.js frontend.

## Services

- **SQL Server 2022** - Database server (port 1433)
- **fastDataApi** - Python FastAPI backend (port 8000)
- **nextui** - Next.js frontend (port 80)

The API provides CRUD endpoints for artists and songs, with a modern React-based user interface.

## Quick Start

### 1. Start the Services

```bash
# Start all services (builds amd64 images automatically)
docker compose up -d

# Wait for SQL Server to be ready (about 30 seconds)
# Then initialize the database
./init-database.sh
```

**Note:** Images are built for linux/amd64 architecture and will run via Rosetta 2 on Apple Silicon Macs.

### 2. Access the Services

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

### 3. Test the API

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

### Option 2: Architecture-Specific Setup

Auto-detect your CPU architecture and configure accordingly:

```bash
./setup-env.sh
docker compose -f compose.arch-specific.yaml up -d
```

This will create a `.env` file with the appropriate SQL Server image for your system.

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

### Connection String
```
Server=localhost,1433;Database=master;User Id=sa;Password=YourStrong@Passw0rd;TrustServerCertificate=True
```

### Using Azure Data Studio (Recommended)
1. Download from: https://docs.microsoft.com/en-us/sql/azure-data-studio/download
2. Connect with hostname `localhost`, port `1433`, user `sa`

### Using sqlcmd (Command Line)
```bash
docker exec -it sqlserver-dev /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P YourStrong@Passw0rd
```

## Managing the Container

### Start SQL Server
```bash
docker compose up -d
```

### Stop SQL Server
```bash
docker compose down
```

### View logs
```bash
# All services
docker compose logs -f

# Individual services
docker compose logs -f nextui
docker compose logs -f fastDataApi
docker compose logs -f sqlserver
```

### Reset database (⚠️ deletes all data)
```bash
docker compose down -v
docker compose up -d
```

## Data Persistence

Database files are stored in a Docker volume named `sqlserver-data`. This persists data between container restarts.

To backup/restore:
```bash
# Backup
docker run --rm -v sqlserver-data:/data -v $(pwd):/backup alpine tar czf /backup/sqlserver-backup.tar.gz /data

# Restore
docker run --rm -v sqlserver-data:/data -v $(pwd):/backup alpine tar xzf /backup/sqlserver-backup.tar.gz -C /
```

## Docker Image Management

### Semantic Versioning

The project uses semantic versioning (MAJOR.MINOR.PATCH) defined in `version.json`. This version is automatically applied as a Docker image tag during build and publish operations.

**Version configuration file:**
```json
{
  "version": "1.0.0",
  "description": "Accessible project version - used for Docker image tagging",
  "services": {
    "fastDataApi": {
      "version": "1.0.0",
      "image": "accessible-fast-data-api"
    },
    "nextui": {
      "version": "1.0.0",
      "image": "accessible-nextui"
    }
  }
}
```

**Quick version workflow:**

1. **Bump version** - Run `./bump-version.sh [major|minor|patch]` to increment version
2. **Build** - Run `./build-versioned.sh` to build images with version tag
3. **Publish** - Run `./publish-images.sh [registry] [username]` to publish

**Version management scripts:**
```bash
# Bump version automatically (updates version.json and .env)
./bump-version.sh patch    # 1.0.0 -> 1.0.1
./bump-version.sh minor    # 1.0.1 -> 1.1.0
./bump-version.sh major    # 1.1.0 -> 2.0.0

# Or manually update version.json, then apply
./set-version.sh           # Reads version.json, updates .env
```

**Manual version management:**
```bash
# Set version from version.json into .env
./set-version.sh

# Build with version tag (reads from .env)
docker compose build

# Or use the all-in-one build script
./build-versioned.sh
```

**Publish images with version:**
```bash
# Publish to Docker Hub (default)
./publish-images.sh dockerhub your-username

# Publish to GitHub Container Registry
./publish-images.sh ghcr your-username

# Publish to custom registry
./publish-images.sh registry.example.com your-username
```

The publish script automatically tags images with both the semantic version (e.g., `1.0.0`) and `latest`.

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
# Remove all project images
docker rmi accessible-fast-data-api:latest
docker rmi accessible-nextui:latest

# Or force remove if containers are using them
docker rmi -f accessible-fast-data-api:latest accessible-nextui:latest
```

**Clean and rebuild everything:**
```bash
# Stop and remove containers, networks, and volumes
docker compose down -v

# Remove project images
docker rmi accessible-fast-data-api:latest accessible-nextui:latest

# Rebuild and start fresh
docker compose up -d --build
```

### Building Docker Images

**Platform Architecture:**
All images are built for **linux/amd64** architecture. This ensures compatibility across:
- Production servers (typically amd64)
- Cloud platforms (AWS, Azure, GCP)
- Development on both Intel and Apple Silicon Macs

**Build all images:**
```bash
# Build without starting
docker compose build

# Build with no cache (fresh build)
docker compose build --no-cache

# Build and start
docker compose up -d --build

# Verify platform
docker inspect accessible-fast-data-api:latest --format '{{.Os}}/{{.Architecture}}'
# Should output: linux/amd64
```

**Note:** You may see a warning during build about `FROM --platform flag should not use constant value`. This is expected and can be ignored - we intentionally build for amd64 architecture.

**Build specific service:**
```bash
# Build only the API
docker compose build fastDataApi

# Build only the frontend
docker compose build nextui

# Rebuild and restart specific service
docker compose up -d --build fastDataApi
```

**Build with custom tags:**
```bash
# Build with version tag
docker build -t accessible-fast-data-api:1.0.0 ./fastDataApi
docker build -t accessible-nextui:1.0.0 ./nextui

# Build with multiple tags
docker build -t accessible-fast-data-api:latest -t accessible-fast-data-api:1.0.0 ./fastDataApi
```

### Publishing Docker Images

#### 1. Docker Hub

**Login and push:**
```bash
# Login to Docker Hub
docker login

# Tag images with your username
docker tag accessible-fast-data-api:latest your-username/accessible-fast-data-api:latest
docker tag accessible-nextui:latest your-username/accessible-nextui:latest

# Push to Docker Hub
docker push your-username/accessible-fast-data-api:latest
docker push your-username/accessible-nextui:latest

# Push with version tag
docker tag accessible-fast-data-api:latest your-username/accessible-fast-data-api:1.0.0
docker push your-username/accessible-fast-data-api:1.0.0
```

#### 2. GitHub Container Registry

**Login and push:**
```bash
# Create a Personal Access Token (PAT) with write:packages scope
# https://github.com/settings/tokens

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u your-username --password-stdin

# Tag images with GitHub registry
docker tag accessible-fast-data-api:latest ghcr.io/your-username/accessible-fast-data-api:latest
docker tag accessible-nextui:latest ghcr.io/your-username/accessible-nextui:latest

# Push to GitHub Container Registry
docker push ghcr.io/your-username/accessible-fast-data-api:latest
docker push ghcr.io/your-username/accessible-nextui:latest
```

#### 3. Private Registry

**Using a private registry:**
```bash
# Login to private registry
docker login registry.example.com

# Tag images
docker tag accessible-fast-data-api:latest registry.example.com/accessible-fast-data-api:latest
docker tag accessible-nextui:latest registry.example.com/accessible-nextui:latest

# Push to private registry
docker push registry.example.com/accessible-fast-data-api:latest
docker push registry.example.com/accessible-nextui:latest
```

### Using Published Images

**Update compose.yaml to use published images:**
```yaml
services:
  fastDataApi:
    image: your-username/accessible-fast-data-api:latest
    # Remove build section to use pre-built image

  nextui:
    image: your-username/accessible-nextui:latest
    # Remove build section to use pre-built image
```

**Pull and run published images:**
```bash
# Pull latest images
docker compose pull

# Start with pulled images
docker compose up -d
```

### Image Versioning Best Practices

**Semantic versioning:**
```bash
# Tag with version
docker tag accessible-fast-data-api:latest accessible-fast-data-api:1.2.3

# Push multiple tags
docker push accessible-fast-data-api:latest
docker push accessible-fast-data-api:1.2.3
docker push accessible-fast-data-api:1.2
docker push accessible-fast-data-api:1
```

**Git commit-based tagging:**
```bash
# Tag with git commit hash
GIT_HASH=$(git rev-parse --short HEAD)
docker tag accessible-fast-data-api:latest accessible-fast-data-api:$GIT_HASH
docker push accessible-fast-data-api:$GIT_HASH
```

**Development vs Production:**
```bash
# Tag for different environments
docker tag accessible-fast-data-api:latest accessible-fast-data-api:dev
docker tag accessible-fast-data-api:latest accessible-fast-data-api:prod

# Or use branches
docker tag accessible-fast-data-api:latest accessible-fast-data-api:main
docker tag accessible-fast-data-api:latest accessible-fast-data-api:develop
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

### Health check failing
Wait 30-60 seconds for SQL Server to fully start. Check logs:
```bash
docker compose logs sqlserver
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
