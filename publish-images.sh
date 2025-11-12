#!/bin/bash
# Publish Docker images to a registry with semantic versioning
# Usage: ./publish-images.sh [registry] [username]
#   registry: dockerhub, ghcr, or custom URL (default: dockerhub)
#   username: your registry username (default: current user)

set -e

# Get version from .env
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Run ./set-version.sh first"
    exit 1
fi

export $(grep "^VERSION=" .env | xargs)

if [ -z "$VERSION" ]; then
    echo "Error: VERSION not found in .env"
    exit 1
fi

# Parse arguments
REGISTRY=${1:-dockerhub}
USERNAME=${2:-$USER}

echo "=== Publishing Accessible Docker Images ==="
echo "Version: $VERSION"
echo "Registry: $REGISTRY"
echo "Username: $USERNAME"
echo ""

# Local image names
LOCAL_API="accessible-fast-data-api:$VERSION"
LOCAL_UI="accessible-nextui:$VERSION"

# Determine registry prefix
case $REGISTRY in
    dockerhub)
        PREFIX="$USERNAME"
        REGISTRY_URL="Docker Hub"
        ;;
    ghcr)
        PREFIX="ghcr.io/$USERNAME"
        REGISTRY_URL="GitHub Container Registry"
        echo "Note: Make sure you're logged in with:"
        echo "  echo \$GITHUB_TOKEN | docker login ghcr.io -u $USERNAME --password-stdin"
        ;;
    *)
        PREFIX="$REGISTRY/$USERNAME"
        REGISTRY_URL="$REGISTRY"
        echo "Note: Make sure you're logged in to $REGISTRY"
        ;;
esac

echo "Publishing to: $REGISTRY_URL"
echo ""

# Tag images
API_TAG="$PREFIX/accessible-fast-data-api"
UI_TAG="$PREFIX/accessible-nextui"

echo "Tagging images..."
docker tag $LOCAL_API $API_TAG:$VERSION
docker tag $LOCAL_API $API_TAG:latest
docker tag $LOCAL_UI $UI_TAG:$VERSION
docker tag $LOCAL_UI $UI_TAG:latest

echo "✓ Tagged: $API_TAG:$VERSION"
echo "✓ Tagged: $API_TAG:latest"
echo "✓ Tagged: $UI_TAG:$VERSION"
echo "✓ Tagged: $UI_TAG:latest"
echo ""

# Confirm before pushing
read -p "Push images to $REGISTRY_URL? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled. Images are tagged locally."
    exit 0
fi

# Push images
echo ""
echo "Pushing images..."

echo "Pushing $API_TAG:$VERSION..."
docker push $API_TAG:$VERSION

echo "Pushing $API_TAG:latest..."
docker push $API_TAG:latest

echo "Pushing $UI_TAG:$VERSION..."
docker push $UI_TAG:$VERSION

echo "Pushing $UI_TAG:latest..."
docker push $UI_TAG:latest

echo ""
echo "=== Publish Complete ==="
echo "Images published:"
echo "  $API_TAG:$VERSION"
echo "  $API_TAG:latest"
echo "  $UI_TAG:$VERSION"
echo "  $UI_TAG:latest"
echo ""
echo "To use these images, update compose.yaml:"
echo "  image: $API_TAG:$VERSION"
echo "  image: $UI_TAG:$VERSION"
