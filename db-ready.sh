#!/bin/bash
#
# Database Ready Check Script
#
# Checks the state of the SQL Server development database.
# Returns different exit codes based on database state:
#   0 = READY   - Database exists and is initialized with tables
#   1 = EMPTY   - Container running but starsongs database not initialized
#   2 = ABSENT  - Container doesn't exist
#
# Usage:
#   ./db-ready.sh           # Check and display status
#   ./db-ready.sh --quiet   # Check without output (for scripts)
#

set -e

CONTAINER_NAME="sqlserver-dev"
DB_NAME="starsongs"
DB_PASSWORD="${DB_PASSWORD:-YourStrong@Passw0rd}"
QUIET=false

# Parse arguments
if [ "$1" = "--quiet" ] || [ "$1" = "-q" ]; then
    QUIET=true
fi

# Function to print status messages
print_status() {
    if [ "$QUIET" = false ]; then
        echo "$@"
    fi
}

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_status "❌ Database state: ABSENT"
    print_status "   Container '${CONTAINER_NAME}' does not exist."
    print_status "   Run: make db-start"
    exit 2
fi

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_status "⚠️  Database state: STOPPED"
    print_status "   Container '${CONTAINER_NAME}' exists but is not running."
    print_status "   Run: docker start ${CONTAINER_NAME}"
    exit 2
fi

# Wait a moment for SQL Server to be responsive (if just started)
sleep 1

# Check if SQL Server is accepting connections
if ! docker exec ${CONTAINER_NAME} /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "${DB_PASSWORD}" -C \
    -Q "SELECT 1" -h -1 > /dev/null 2>&1; then
    print_status "⚠️  Database state: STARTING"
    print_status "   SQL Server is not yet accepting connections."
    print_status "   Wait a few seconds and try again."
    exit 1
fi

# Check if starsongs database exists
DB_EXISTS=$(docker exec ${CONTAINER_NAME} /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "${DB_PASSWORD}" -C \
    -Q "SELECT COUNT(*) FROM sys.databases WHERE name = '${DB_NAME}'" -h -1 2>/dev/null | head -1 | tr -d '[:space:]')

if [ "$DB_EXISTS" = "0" ]; then
    print_status "⚠️  Database state: EMPTY"
    print_status "   SQL Server is running but '${DB_NAME}' database does not exist."
    print_status "   Run: make db-init"
    exit 1
fi

# Check if tables exist in the database
TABLE_COUNT=$(docker exec ${CONTAINER_NAME} /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "${DB_PASSWORD}" -C -d "${DB_NAME}" \
    -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'" -h -1 2>/dev/null | head -1 | tr -d '[:space:]')

if [ "$TABLE_COUNT" = "0" ]; then
    print_status "⚠️  Database state: EMPTY"
    print_status "   Database '${DB_NAME}' exists but has no tables."
    print_status "   Run: make db-init"
    exit 1
fi

# Check if we have the expected tables (Artist and Song)
ARTIST_EXISTS=$(docker exec ${CONTAINER_NAME} /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "${DB_PASSWORD}" -C -d "${DB_NAME}" \
    -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Artist'" -h -1 2>/dev/null | head -1 | tr -d '[:space:]')

SONG_EXISTS=$(docker exec ${CONTAINER_NAME} /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "${DB_PASSWORD}" -C -d "${DB_NAME}" \
    -Q "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Song'" -h -1 2>/dev/null | head -1 | tr -d '[:space:]')

if [ "$ARTIST_EXISTS" = "0" ] || [ "$SONG_EXISTS" = "0" ]; then
    print_status "⚠️  Database state: INCOMPLETE"
    print_status "   Database '${DB_NAME}' exists but is missing expected tables."
    print_status "   Run: make db-init"
    exit 1
fi

# Everything looks good!
print_status "✅ Database state: READY"
print_status "   Database '${DB_NAME}' is initialized and ready for use."
print_status "   Tables: Artist, Song"

# Optional: Show row counts
if [ "$QUIET" = false ]; then
    ARTIST_COUNT=$(docker exec ${CONTAINER_NAME} /opt/mssql-tools18/bin/sqlcmd \
        -S localhost -U sa -P "${DB_PASSWORD}" -C -d "${DB_NAME}" \
        -Q "SELECT COUNT(*) FROM dbo.Artist" -h -1 2>/dev/null | head -1 | tr -d '[:space:]')

    SONG_COUNT=$(docker exec ${CONTAINER_NAME} /opt/mssql-tools18/bin/sqlcmd \
        -S localhost -U sa -P "${DB_PASSWORD}" -C -d "${DB_NAME}" \
        -Q "SELECT COUNT(*) FROM dbo.Song" -h -1 2>/dev/null | head -1 | tr -d '[:space:]')

    print_status "   Data: ${ARTIST_COUNT} artists, ${SONG_COUNT} songs"
fi

exit 0
