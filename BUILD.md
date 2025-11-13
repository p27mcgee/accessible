# Build Guide

This guide covers building and publishing Docker images for the Accessible project using the Makefile-based build system.

## Overview

The build system uses:
- **pyproject.toml**: Central version and project metadata management (Python packaging standards)
- **Makefile**: Primary build interface with direct `docker build` commands
- **Docker Hub**: Registry for published images (pmcgee namespace)

This approach provides:
- CI/CD friendly builds (standard Makefile)
- Per-service build capability
- Kubernetes-ready image naming
- No dependency on docker compose for building
- Independent database management for dev/test

**Note:** The database is managed separately via Makefile for development/testing. In production, the database is external (managed service). See [DATABASE.md](DATABASE.md) for database management.

## Prerequisites

- Docker Desktop (with Rosetta 2 enabled on Apple Silicon)
- Python 3.11+ (for version extraction from pyproject.toml)
- GNU Make
- Docker Hub account (for publishing)

## Quick Start

### Build and Publish

```bash
# 1. Set version in pyproject.toml
vim pyproject.toml  # Edit version = "1.0.0"

# 2. Build all services
make build

# 3. Tag images for registry
make tag

# 4. Login to Docker Hub
docker login

# 5. Push to Docker Hub
make push
```

### Database Setup (Development)

```bash
# Start database
make db-start

# Initialize database
make db-init

# Check status
make db-status
```

See [DATABASE.md](DATABASE.md) for comprehensive database management.

## Image Naming

### Local Build
During `make build`, images are created with local names:
- `accessible-fast-data-api:1.0.0` and `accessible-fast-data-api:latest`
- `accessible-flask-data-api:1.0.0` and `accessible-flask-data-api:latest`
- `accessible-nextui:1.0.0` and `accessible-nextui:latest`

### Registry Names
After `make tag`, registry-prefixed aliases are created:
- `pmcgee/accessible-fast-data-api:1.0.0` and `pmcgee/accessible-fast-data-api:latest`
- `pmcgee/accessible-flask-data-api:1.0.0` and `pmcgee/accessible-flask-data-api:latest`
- `pmcgee/accessible-nextui:1.0.0` and `pmcgee/accessible-nextui:latest`

This two-step approach:
- Keeps local development separate from published images
- Allows testing before pushing
- Follows standard Docker/Kubernetes patterns

## Version Management

### Setting Version

Edit `pyproject.toml` directly:

```toml
[project]
name = "accessible"
version = "1.0.0"  # Change this
```

The Makefile automatically extracts the version using Python's `tomllib` (Python 3.11+) or falls back to `grep`.

### Versioning Strategy

All services share the same version tag from pyproject.toml. This:
- Simplifies deployment coordination
- Makes it clear which services are compatible
- Follows semantic versioning (MAJOR.MINOR.PATCH)

Example version progression:
- `1.0.0` - Initial release
- `1.0.1` - Patch (bug fixes)
- `1.1.0` - Minor (new features, backward compatible)
- `2.0.0` - Major (breaking changes)

## Makefile Commands

### Help

```bash
make help
```

Shows all available targets and typical workflow.

### Version

```bash
make version
```

Displays the current version from pyproject.toml.

### Build All Services

```bash
make build
```

Builds all three services (FastAPI, Flask, Next.js) with version tags from pyproject.toml.

This creates both versioned tags (e.g., `1.0.0`) and `latest` tags locally.

### Build Individual Services

```bash
# Build only FastAPI data service
make build-fast-data-api

# Build only Flask data service
make build-flask-data-api

# Build only Next.js UI
make build-ui
```

Useful for:
- Iterative development on a single service
- CI/CD pipelines that build services independently
- Faster builds when only one service changed

### Tag for Registry

```bash
make tag
```

Creates registry-prefixed tags for all images:
- Tags local images with `pmcgee/` namespace
- Creates both versioned and `latest` tags
- Does not push (allows verification first)

### Push to Docker Hub

```bash
# Login first
docker login

# Push all services
make push
```

Pushes only the registry-prefixed images (pmcgee/*) to Docker Hub.

Both version tags (e.g., `1.0.0`) and `latest` tags are pushed.

### Clean

```bash
make clean
```

Removes all local Docker images (both local and registry-prefixed):
- Frees disk space
- Forces fresh builds
- Useful after version changes

## Platform Architecture

All images are built for **linux/amd64** architecture:

```makefile
PLATFORM := linux/amd64
```

This ensures:
- Native performance on Intel/AMD servers (production)
- Compatibility with cloud platforms (AWS, Azure, GCP)
- Works on Apple Silicon via Rosetta 2 emulation
- Standard for Docker Hub and container registries

## Typical Workflows

### Development Build

```bash
# Start database first
make db-start && make db-init

# Build single service during development
make build-fast-data-api

# Test locally with docker compose
docker compose --profile fastapi up -d
```

### Version Release

```bash
# 1. Update version
vim pyproject.toml  # Change version = "1.1.0"

# 2. Build everything
make build

# 3. Verify images
docker images | grep accessible

# 4. Tag for registry
make tag

# 5. Test locally
docker compose --profile both up -d

# 6. Push to Docker Hub
docker login
make push

# 7. Verify on Docker Hub
# Visit https://hub.docker.com/u/pmcgee
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
- name: Extract version
  run: make version

- name: Build images
  run: make build

- name: Run tests
  run: docker compose --profile both up -d && ./run-tests.sh

- name: Tag for registry
  run: make tag

- name: Login to Docker Hub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Push to Docker Hub
  run: make push
```

### Kubernetes Deployment Prep

```bash
# Build with specific version
vim pyproject.toml  # version = "1.2.0"
make build
make tag
make push

# Create Kubernetes deployment manifests
# Use image: pmcgee/accessible-fast-data-api:1.2.0
```

The registry-prefixed naming convention (pmcgee/accessible-*:version) is ready for Kubernetes deployments.

## Docker Compose Integration

### Development (Local Builds)

If you want to build locally using docker compose:

```bash
# Not recommended - use Makefile instead
docker compose build
```

However, `compose.yaml` now references **published images** from Docker Hub, not local builds.

### Deployment (Published Images)

The recommended approach:

```bash
# Pull pre-built images from Docker Hub
docker compose pull

# Start services
docker compose --profile fastapi up -d
```

This is faster and ensures consistency across environments.

## Troubleshooting

### Version Not Updating

**Problem**: Built image shows old version tag

**Solution**: Version is baked into the Makefile when `make` runs. If you change pyproject.toml, run `make build` again.

```bash
# Verify version is correct
make version

# Clean old images
make clean

# Rebuild
make build
```

### Permission Denied on Docker Push

**Problem**: `make push` fails with authentication error

**Solution**: Login to Docker Hub first

```bash
docker login
# Enter username: pmcgee
# Enter password: (your Docker Hub token)

make push
```

### Wrong Architecture

**Problem**: Image shows wrong platform

**Solution**: Verify platform specification

```bash
# Check image architecture
docker inspect accessible-fast-data-api:latest --format '{{.Architecture}}'
# Should output: amd64

# Force clean rebuild
make clean
make build
```

### Rosetta 2 Warning on Apple Silicon

**Problem**: Warning about platform mismatch on M1/M2/M3 Macs

**Solution**: This is expected. Enable Rosetta 2 in Docker Desktop:
- Settings → General → "Use Rosetta for x86/amd64 emulation on Apple Silicon"

## Advanced Usage

### Custom Registry

To use a different registry (not pmcgee), edit pyproject.toml:

```toml
[tool.accessible]
registry = "your-username"  # or "registry.example.com/your-org"
```

Then rebuild:

```bash
make clean
make build
make tag
make push
```

### Multiple Versions

To maintain multiple versions simultaneously:

```bash
# Build version 1.0.0
vim pyproject.toml  # version = "1.0.0"
make build
make tag

# Build version 1.1.0
vim pyproject.toml  # version = "1.1.0"
make build
make tag

# Push both
make push

# Both tags available:
# pmcgee/accessible-fast-data-api:1.0.0
# pmcgee/accessible-fast-data-api:1.1.0
# pmcgee/accessible-fast-data-api:latest (points to 1.1.0)
```

### Build with Docker BuildKit

For faster builds and better caching:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with BuildKit features
make build
```

### Cross-Platform Builds

To build for multiple platforms:

```bash
# Create builder
docker buildx create --name multiplatform --use

# Build for both amd64 and arm64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag pmcgee/accessible-fast-data-api:1.0.0 \
  --push \
  ./fastDataApi
```

Note: This requires manual docker buildx commands, not currently supported by Makefile.

## Migration from Old Build System

### What Changed

| Old System | New System |
|------------|------------|
| version.json | pyproject.toml |
| build-versioned.sh | make build |
| publish-images.sh | make push |
| set-version.sh | (removed - edit pyproject.toml) |
| bump-version.sh | (removed - edit pyproject.toml) |
| docker compose build | make build |

### Migration Steps

If you have local images from the old system:

```bash
# Clean old images
docker rmi accessible-fast-data-api:latest
docker rmi accessible-nextui:latest

# Build with new system
make build
make tag

# Verify
docker images | grep accessible
```

## Best Practices

1. **Version Control**: Always commit pyproject.toml changes when updating version
2. **Test Before Push**: Run services locally with `docker compose up` before pushing
3. **Semantic Versioning**: Use MAJOR.MINOR.PATCH consistently
4. **Tag Before Push**: Always run `make tag` before `make push`
5. **CI/CD**: Use `make` commands in pipelines for consistency
6. **Documentation**: Update CHANGELOG.md when releasing new versions

## Next Steps

- See [README.md](README.md) for deployment instructions
- See [SWITCHING_APIS.md](SWITCHING_APIS.md) for API selection
- See [GETTING_STARTED.md](GETTING_STARTED.md) for quick start guide
- See [DATABASE.md](DATABASE.md) for database management
