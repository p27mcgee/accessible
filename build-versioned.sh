#!/bin/bash
# Build Docker images with semantic version from version.json
# This script automatically reads version.json, updates .env, and builds images

set -e

echo "=== Building Accessible Docker Images ==="
echo ""

# Set version in .env
./set-version.sh

# Source the .env file to get VERSION
if [ -f ".env" ]; then
    export $(grep "^VERSION=" .env | xargs)
    echo ""
    echo "Building with VERSION=$VERSION"
else
    echo "Error: .env file not found"
    exit 1
fi

# Build the images
echo ""
echo "Building images for linux/amd64..."
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose build

echo ""
echo "=== Build Complete ==="
echo "Images created:"
docker images | grep -E "accessible-(fast-data-api|flask-data-api|nextui)" | head -10

echo ""
echo "To start the services:"
echo "  docker compose up -d"
echo ""
echo "To publish images:"
echo "  docker push accessible-fast-data-api:$VERSION"
echo "  docker push accessible-flask-data-api:$VERSION"
echo "  docker push accessible-nextui:$VERSION"
