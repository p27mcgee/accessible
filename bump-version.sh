#!/bin/bash
# Bump semantic version in version.json
# Usage: ./bump-version.sh [major|minor|patch]
#   major: 1.0.0 -> 2.0.0
#   minor: 1.0.0 -> 1.1.0
#   patch: 1.0.0 -> 1.0.1 (default)

set -e

BUMP_TYPE=${1:-patch}

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Error: Invalid bump type '$BUMP_TYPE'"
    echo "Usage: ./bump-version.sh [major|minor|patch]"
    exit 1
fi

# Check if version.json exists
if [ ! -f "version.json" ]; then
    echo "Error: version.json not found"
    exit 1
fi

# Get current version
if command -v jq &> /dev/null; then
    CURRENT_VERSION=$(jq -r '.version' version.json)
else
    CURRENT_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' version.json | sed 's/.*"\([^"]*\)".*/\1/')
fi

if [ -z "$CURRENT_VERSION" ]; then
    echo "Error: Could not read current version from version.json"
    exit 1
fi

echo "Current version: $CURRENT_VERSION"

# Parse version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Bump version based on type
case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version:     $NEW_VERSION"

# Update version.json
if command -v jq &> /dev/null; then
    # Use jq to update version while preserving formatting
    jq --arg version "$NEW_VERSION" \
       '.version = $version |
        .services.fastDataApi.version = $version |
        .services.nextui.version = $version' \
       version.json > version.json.tmp
    mv version.json.tmp version.json
else
    # Fallback to sed (less robust but works without jq)
    echo "Note: jq not found, using basic replacement (install jq for better reliability)"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$NEW_VERSION\"/g" version.json
    else
        sed -i "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$NEW_VERSION\"/g" version.json
    fi
fi

echo "✓ Updated version.json"

# Optionally update .env
read -p "Update .env file with new version? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    ./set-version.sh
fi

echo ""
echo "=== Version Bump Complete ==="
echo "Version: $CURRENT_VERSION -> $NEW_VERSION"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff version.json"
echo "  2. Build images: ./build-versioned.sh"
echo "  3. Commit: git add version.json .env && git commit -m 'Bump version to $NEW_VERSION'"
echo "  4. Tag: git tag v$NEW_VERSION"
echo "  5. Push: git push && git push --tags"
