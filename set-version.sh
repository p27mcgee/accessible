#!/bin/bash
# Set project version from version.json into .env file
# This script reads the semantic version from version.json and updates .env

set -e

# Check if version.json exists
if [ ! -f "version.json" ]; then
    echo "Error: version.json not found"
    exit 1
fi

# Check if jq is available (for JSON parsing)
if command -v jq &> /dev/null; then
    # Use jq for robust JSON parsing
    VERSION=$(jq -r '.version' version.json)
else
    # Fallback to grep/sed if jq not available
    echo "Note: jq not found, using basic parsing (install jq for better reliability)"
    VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' version.json | sed 's/.*"\([^"]*\)".*/\1/')
fi

if [ -z "$VERSION" ]; then
    echo "Error: Could not read version from version.json"
    exit 1
fi

echo "Read version: $VERSION"

# Update or add VERSION in .env file
if [ -f ".env" ]; then
    if grep -q "^VERSION=" .env; then
        # Update existing VERSION line
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS sed syntax
            sed -i '' "s/^VERSION=.*/VERSION=$VERSION/" .env
        else
            # Linux sed syntax
            sed -i "s/^VERSION=.*/VERSION=$VERSION/" .env
        fi
        echo "Updated VERSION=$VERSION in .env"
    else
        # Add VERSION if not present
        echo "VERSION=$VERSION" >> .env
        echo "Added VERSION=$VERSION to .env"
    fi
else
    echo "Warning: .env file not found, creating from .env.example"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/^VERSION=.*/VERSION=$VERSION/" .env
        else
            sed -i "s/^VERSION=.*/VERSION=$VERSION/" .env
        fi
        echo "Created .env with VERSION=$VERSION"
    else
        echo "Error: .env.example not found"
        exit 1
    fi
fi

echo "Version set successfully!"
echo "You can now build with: docker compose build"
echo "Images will be tagged as:"
echo "  - accessible-fast-data-api:$VERSION"
echo "  - accessible-nextui:$VERSION"
