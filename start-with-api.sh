#!/bin/bash
# Convenient wrapper to start Accessible services with a specific API
# Usage: ./start-with-api.sh [fastapi|flask|both]

set -e

API_TYPE=${1:-fastapi}

case $API_TYPE in
    fastapi|fast)
        echo "=== Starting with FastAPI ==="
        export API_SERVICE_URL=http://fastDataApi:8000
        echo "✓ Frontend will use: $API_SERVICE_URL"
        echo ""
        docker compose --profile fastapi up -d
        ;;
    flask)
        echo "=== Starting with Flask ==="
        export API_SERVICE_URL=http://flaskDataApi:8001
        echo "✓ Frontend will use: $API_SERVICE_URL"
        echo ""
        docker compose --profile flask up -d
        ;;
    both)
        echo "=== Starting with BOTH APIs ==="
        export API_SERVICE_URL=http://fastDataApi:8000
        echo "✓ Frontend will use: $API_SERVICE_URL (change API_SERVICE_URL in .env to switch)"
        echo ""
        docker compose --profile both up -d
        ;;
    *)
        echo "Usage: ./start-with-api.sh [fastapi|flask|both]"
        echo ""
        echo "Options:"
        echo "  fastapi - Start with FastAPI backend (port 8000)"
        echo "  flask   - Start with Flask backend (port 8001)"
        echo "  both    - Start both APIs for comparison"
        echo ""
        echo "Examples:"
        echo "  ./start-with-api.sh fastapi"
        echo "  ./start-with-api.sh flask"
        echo "  ./start-with-api.sh both"
        exit 1
        ;;
esac

echo ""
echo "=== Services Started ==="
echo ""
docker compose ps

echo ""
echo "Access points:"
if [ "$API_TYPE" = "both" ]; then
    echo "  - Frontend:    http://localhost"
    echo "  - FastAPI:     http://localhost:8000"
    echo "  - FastAPI Docs: http://localhost:8000/swagger-ui.html"
    echo "  - Flask API:   http://localhost:8001"
    echo "  - Flask Docs:  http://localhost:8001/apidocs"
elif [ "$API_TYPE" = "flask" ]; then
    echo "  - Frontend:    http://localhost"
    echo "  - Flask API:   http://localhost:8001"
    echo "  - Flask Docs:  http://localhost:8001/apidocs"
else
    echo "  - Frontend:    http://localhost"
    echo "  - FastAPI:     http://localhost:8000"
    echo "  - FastAPI Docs: http://localhost:8000/swagger-ui.html"
fi
echo ""
