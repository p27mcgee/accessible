# Switching Between FastAPI and Flask

This project includes two data API implementations:
- **fastDataApi** - FastAPI implementation (port 8000)
- **flaskDataApi** - Flask implementation (port 8001)

You can easily switch between them or run both simultaneously for comparison.

## Quick Start

### Option 1: Using the Wrapper Script (Recommended)

The easiest way to start services with a specific API:

```bash
# Start with FastAPI
./start-with-api.sh fastapi

# Start with Flask
./start-with-api.sh flask

# Start with both APIs for comparison
./start-with-api.sh both
```

### Option 2: Using Docker Compose Profiles Directly

You can also use Docker Compose profiles directly:

```bash
# Start with FastAPI (default)
docker compose --profile fastapi up -d

# Start with Flask
docker compose --profile flask up -d

# Start with both APIs
docker compose --profile both up -d
```

## Switching Between APIs

To switch from one API to another:

```bash
# Stop all services
docker compose down

# Start with the desired API
./start-with-api.sh flask  # or fastapi
```

## Configuring Which API the Frontend Uses

The frontend (nextui) can be configured to connect to either API by setting the `API_SERVICE_URL` environment variable.

### Method 1: Edit .env file (Persistent)

Edit `.env` and change:

```bash
# For FastAPI
API_SERVICE_URL=http://fastDataApi:8000

# For Flask
API_SERVICE_URL=http://flaskDataApi:8001
```

Then restart the frontend:

```bash
docker compose restart nextui
```

### Method 2: Environment Variable (Temporary)

Set the variable when starting:

```bash
# Use Flask API for frontend
export API_SERVICE_URL=http://flaskDataApi:8001
docker compose up -d nextui

# Use FastAPI for frontend
export API_SERVICE_URL=http://fastDataApi:8000
docker compose up -d nextui
```

## Running Both APIs Simultaneously

You can run both APIs at the same time for comparison:

```bash
# Start both
./start-with-api.sh both

# Or with docker compose
docker compose --profile both up -d
```

Then access:
- **FastAPI**: http://localhost:8000 (docs at /swagger-ui.html)
- **Flask API**: http://localhost:8001 (docs at /apidocs)
- **Frontend**: http://localhost (uses whichever API_SERVICE_URL is set)

## Available Profiles

The compose.yaml defines three profiles:

| Profile | Services Started | Use Case |
|---------|-----------------|----------|
| `fastapi` | sqlserver + fastDataApi + nextui | Use FastAPI backend |
| `flask` | sqlserver + flaskDataApi + nextui | Use Flask backend |
| `both` | sqlserver + both APIs + nextui | Compare both implementations |

## Examples

### Typical Workflow

```bash
# Start with FastAPI
./start-with-api.sh fastapi

# Check it works
curl http://localhost:8000/v1/songs

# Switch to Flask
docker compose down
./start-with-api.sh flask

# Check it works
curl http://localhost:8001/v1/songs
```

### Testing Both APIs

```bash
# Start both
./start-with-api.sh both

# Test FastAPI
curl http://localhost:8000/v1/songs | jq

# Test Flask
curl http://localhost:8001/v1/songs | jq

# Compare performance, responses, etc.
```

### Development: Frontend with Specific API

```bash
# Start just the APIs (no frontend)
docker compose --profile both up -d sqlserver fastDataApi flaskDataApi

# Run frontend locally pointing to Flask
cd nextui
NEXT_PUBLIC_SONGDATA_API_URL=http://localhost:8001 npm run dev
```

## Default Behavior

If you don't specify a profile, **only the common services run** (sqlserver, nextui) - no API will start. This is intentional to force you to choose which API to use.

To always use a specific profile by default, you can set it in your shell profile:

```bash
# Add to ~/.bashrc or ~/.zshrc
export COMPOSE_PROFILES=fastapi
```

## Troubleshooting

### "No services to start"

If you see this message, you haven't specified a profile:

```bash
# Wrong
docker compose up -d

# Correct
docker compose --profile fastapi up -d
# or
./start-with-api.sh fastapi
```

### Port conflicts

If you get port conflicts, check what's running:

```bash
docker compose ps
```

Stop specific services:

```bash
docker compose stop fastDataApi
docker compose stop flaskDataApi
```

### Frontend showing "Connection refused"

Check that the API is running and that `API_SERVICE_URL` in `.env` matches the running service:

```bash
# Check running services
docker compose ps

# Check frontend environment
docker compose exec nextui env | grep API_SERVICE_URL

# Verify API is accessible
docker compose exec nextui wget -qO- http://fastDataApi:8000/health
```
