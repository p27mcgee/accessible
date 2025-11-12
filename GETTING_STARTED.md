# Getting Started with Accessible

## Summary

This project provides a **full-stack application** with **SQL Server backend**, **Python FastAPI API**, and **Next.js frontend**.

**What's included:**
- SQL Server 2022 running in Docker (with Rosetta 2 emulation on Apple Silicon)
- Python FastAPI backend with CRUD endpoints (fastDataApi)
- Next.js frontend with React Server Components (nextui)
- Database schema and sample data
- Swagger/OpenAPI documentation

## Quick Start

### 1. Start the Services

```bash
cd /Users/pmcgee/_dev/accessible

# Start SQL Server and API
docker compose up -d

# Wait 30 seconds for SQL Server to be ready, then initialize database
./init-database.sh
```

### 2. Load Sample Data

The init script attempts to load sample data, but if it fails, run:

```bash
# Insert Artists
docker exec sqlserver-dev /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa \
  -P "YourStrong@Passw0rd" -C -d starsongs \
  -Q "INSERT INTO dbo.Artist (name) VALUES ('David Bowie'), ('The Beatles'), ('Elton John'), ('Queen'), ('Pink Floyd')"

# Insert Songs (one at a time due to special characters)
cat << 'EOF' | docker exec -i sqlserver-dev /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -C -d starsongs
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Space Oddity', 1, '1969-07-11', 'https://www.youtube.com/watch?v=iYYRH4apXDo', 238900.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Starman', 1, '1972-04-28', 'https://www.youtube.com/watch?v=tRcPA7Fzebw', 384400.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Across the Universe', 2, '1970-02-06', 'https://www.youtube.com/watch?v=90M60PzmxEE', 40000000.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Rocket Man', 3, '1972-04-17', 'https://www.youtube.com/watch?v=DtVBCG6ThDk', 384400.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('''39', 4, '1975-11-21', 'https://www.youtube.com/watch?v=BjuyXR5by2s', 9460730472580.8);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Astronomy Domine', 5, '1967-08-05', 'https://www.youtube.com/watch?v=pJh9OLlXenM', 4000000.0);
GO
EOF
```

### 3. Access the Services

**Frontend:**
- Web UI: http://localhost (port 80)

**API Endpoints:**
- Base URL: http://localhost:8000
- Swagger UI: http://localhost:8000/swagger-ui.html
- API Documentation: http://localhost:8000/api-docs
- Health Check: http://localhost:8000/health

**SQL Server:**
- Host: localhost
- Port: 1433
- Database: starsongs
- Username: sa
- Password: YourStrong@Passw0rd

## Testing the API

### Get All Artists
```bash
curl http://localhost:8000/v1/artists
```

**Expected Response:**
```json
[
    {
        "name": "David Bowie",
        "id": 1
    },
    {
        "name": "The Beatles",
        "id": 2
    }
]
```

### Get All Songs
```bash
curl http://localhost:8000/v1/songs
```

**Expected Response:**
```json
[
    {
        "title": "Space Oddity",
        "artist_id": 1,
        "release_date": "1969-07-11",
        "url": "https://www.youtube.com/watch?v=iYYRH4apXDo",
        "distance": 238900.0,
        "id": 1
    }
]
```

### Create a New Artist
```bash
curl -X POST http://localhost:8000/v1/artists \
  -H "Content-Type: application/json" \
  -d '{"name": "Led Zeppelin"}'
```

**Expected Response:**
```json
{
    "name": "Led Zeppelin",
    "id": 6
}
```

### Create a New Song
```bash
curl -X POST http://localhost:8000/v1/songs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Stairway to Heaven",
    "artist_id": 6,
    "release_date": "1971-11-08",
    "url": "https://www.youtube.com/watch?v=QkF3oxziUI4",
    "distance": 100.0
  }'
```

### Update an Artist
```bash
curl -X PUT http://localhost:8000/v1/artists/6 \
  -H "Content-Type: application/json" \
  -d '{"name": "Led Zeppelin (Updated)"}'
```

### Delete a Song
```bash
curl -X DELETE http://localhost:8000/v1/songs/1
```

## Using Swagger UI

The easiest way to test the API is through the Swagger UI:

1. Open your browser to: http://localhost:8000/swagger-ui.html
2. You'll see all available endpoints with descriptions
3. Click on an endpoint to expand it
4. Click "Try it out" to test the endpoint
5. Fill in parameters and click "Execute"
6. View the response below

## Managing the Environment

### View Logs
```bash
# All services
docker compose logs -f

# Individual services
docker compose logs -f nextui
docker compose logs -f fastDataApi
docker compose logs -f sqlserver
```

### Restart Services
```bash
# Restart everything
docker compose restart

# Restart individual services
docker compose restart nextui
docker compose restart fastDataApi
docker compose restart sqlserver
```

### Stop Services
```bash
docker compose down
```

### Stop and Remove Data
```bash
docker compose down -v
```

## Connecting to SQL Server Directly

### Using Azure Data Studio (Recommended)
1. Download from: https://docs.microsoft.com/en-us/sql/azure-data-studio/download
2. Connect with:
   - Server: localhost,1433
   - Authentication: SQL Login
   - Username: sa
   - Password: YourStrong@Passw0rd

### Using sqlcmd
```bash
docker exec -it sqlserver-dev /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "YourStrong@Passw0rd" -C
```

## Project Structure

```
accessible/
├── fastDataApi/            # Python FastAPI backend
│   ├── app/
│   │   ├── main.py        # FastAPI application
│   │   ├── database.py    # Database connection
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── schemas.py     # Pydantic schemas
│   │   └── routers/       # API endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── nextui/                # Next.js frontend
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/             # API client and utilities
│   ├── types/           # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── sql/                  # Database scripts
│   ├── init_db.sql      # Create database
│   ├── schema.sql       # Create tables
│   └── seed_data.sql    # Sample data
├── compose.yaml         # Docker Compose config
└── init-database.sh     # Database setup script
```

## Troubleshooting

### API won't start
```bash
# Check logs
docker compose logs fastDataApi

# Rebuild
docker compose up -d --build fastDataApi
```

### Can't connect to database
```bash
# Verify SQL Server is running
docker compose ps

# Check SQL Server logs
docker compose logs sqlserver

# Test connection
docker exec sqlserver-dev /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "YourStrong@Passw0rd" -C -Q "SELECT @@VERSION"
```

### Database doesn't exist
```bash
# Reinitialize
./init-database.sh
```

### Port conflicts
If port 8000 or 1433 is already in use, edit `compose.yaml` to change the port mappings.

## Next Steps

- **Add authentication**: Implement JWT or OAuth2 in both API and frontend
- **Add pagination**: Implement pagination for list endpoints
- **Add filtering**: Add query parameters and search functionality
- **Write tests**: Add pytest tests for the API and Vitest tests for frontend
- **Deploy**: Deploy to a cloud provider (AWS, Azure, or Vercel)

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **SQL Server Documentation**: https://docs.microsoft.com/en-us/sql/
