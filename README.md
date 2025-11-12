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
# Start SQL Server and API
docker compose up -d

# Wait for SQL Server to be ready (about 30 seconds)
# Then initialize the database
./init-database.sh
```

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

## Next Steps

- Customize the Next.js frontend in the `nextui/` directory
- Add authentication/authorization
- Implement additional features and endpoints
- Deploy to production environment
