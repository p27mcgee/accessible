#!/bin/bash

# Initialize Star Songs Database
# This script creates the database, schema, and loads seed data

set -e

echo "Initializing Star Songs database..."

# Wait for SQL Server to be ready
echo "Waiting for SQL Server to be ready..."
sleep 5

# Create database
echo "Creating database..."
docker exec sqlserver-dev /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "YourStrong@Passw0rd" -C \
    -i /docker-entrypoint-initdb.d/init_db.sql

# Create schema
echo "Creating schema..."
docker exec sqlserver-dev /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "YourStrong@Passw0rd" -C \
    -d starsongs \
    -i /docker-entrypoint-initdb.d/schema.sql

# Load seed data
echo "Loading seed data..."
docker exec sqlserver-dev /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "YourStrong@Passw0rd" -C \
    -d starsongs \
    -i /docker-entrypoint-initdb.d/seed_data.sql

echo "Database initialization complete!"
echo ""
echo "You can now access the API at http://localhost:8000"
echo "API Documentation: http://localhost:8000/swagger-ui.html"
