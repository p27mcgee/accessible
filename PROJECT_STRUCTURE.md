# Project Structure

This document provides an overview of the Accessible project structure, including the Python FastAPI backend and Next.js frontend.

## Directory Structure

```
accessible/
├── fastDataApi/                  # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database connection management
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic schemas (DTOs)
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── artists.py       # Artist CRUD endpoints
│   │       └── songs.py         # Song CRUD endpoints
│   ├── Dockerfile               # Container build instructions
│   ├── requirements.txt         # Python dependencies
│   └── README.md               # API documentation
│
├── nextui/                      # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── SongList.tsx        # Server Component for data fetching
│   │   ├── SongTable.tsx       # Client Component for table rendering
│   │   └── LoadingSpinner.tsx  # Loading state component
│   ├── lib/
│   │   └── api.ts              # API client
│   ├── types/
│   │   └── index.ts            # TypeScript type definitions
│   ├── __tests__/              # Vitest test files
│   ├── Dockerfile              # Multi-stage container build
│   ├── next.config.ts          # Next.js configuration
│   ├── package.json            # Node dependencies
│   └── .env.local              # Local environment variables
│
├── sql/                         # Database scripts
│   ├── init_db.sql             # Database creation
│   ├── schema.sql              # Table definitions
│   └── seed_data.sql           # Sample data
│
├── compose.yaml                # Docker Compose configuration
├── version.json                # Semantic version configuration
├── init-database.sh           # Database initialization script
├── set-version.sh             # Script to apply version from version.json
├── bump-version.sh            # Script to bump semantic version
├── build-versioned.sh         # Script to build with version tags
├── publish-images.sh          # Script to publish versioned images
├── setup-env.sh               # Environment setup helper
├── .env                       # Environment variables (gitignored)
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
├── README.md                  # Main documentation
├── GETTING_STARTED.md         # Quick start guide
└── PROJECT_STRUCTURE.md       # This file
```

## Mapping to Java JPA Project

### Source: `/Users/pmcgee/_dev/star-songs/songdata/src/main/java/com/mcgeecahill/starsongs/songdata`

| Java Component | Python Equivalent | Purpose |
|---------------|------------------|---------|
| `domain/Artist.java` | `app/models.py::Artist` | Artist entity/ORM model |
| `domain/Song.java` | `app/models.py::Song` | Song entity/ORM model |
| `dto/ArtistDto.java` | `app/schemas.py::ArtistDto` | Artist data transfer object |
| `dto/SongDto.java` | `app/schemas.py::SongDto` | Song data transfer object |
| `controllers/ArtistRestControllerV1.java` | `app/routers/artists.py` | Artist REST endpoints |
| `controllers/SongRestControllerV1.java` | `app/routers/songs.py` | Song REST endpoints |
| `jpa/ArtistRepository.java` | SQLAlchemy Session (via `get_db()`) | Data access |
| `jpa/SongRepository.java` | SQLAlchemy Session (via `get_db()`) | Data access |

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend Framework** | Next.js 16 | React-based web framework with App Router |
| **UI Library** | React 19 | Server and Client Components |
| **Styling** | TailwindCSS 4 | Utility-first CSS framework |
| **Type Safety** | TypeScript 5 | Static type checking |
| **Backend Framework** | FastAPI | Modern Python web framework |
| **ORM** | SQLAlchemy 2.0 | Python database toolkit |
| **Validation** | Pydantic | Data validation and serialization |
| **API Docs** | OpenAPI/Swagger | Built-in API documentation |
| **Backend Server** | Uvicorn | ASGI server |
| **Database** | SQL Server 2022 | Relational database |
| **Database Driver** | pyodbc | ODBC driver for SQL Server |
| **Containerization** | Docker Compose | Multi-container orchestration |

## API Endpoints

The FastAPI backend provides the following REST endpoints:

### Artists API (`/v1/artists`)
- `GET /v1/artists` - List all artists
- `GET /v1/artists/{id}` - Get artist by ID
- `POST /v1/artists` - Create new artist
- `PUT /v1/artists/{id}` - Update artist
- `DELETE /v1/artists/{id}` - Delete artist

### Songs API (`/v1/songs`)
- `GET /v1/songs` - List all songs
- `GET /v1/songs/{id}` - Get song by ID
- `POST /v1/songs` - Create new song
- `PUT /v1/songs/{id}` - Update song
- `DELETE /v1/songs/{id}` - Delete song

## Database Schema

The schema is defined in `sql/schema.sql` and matches the JPA entity definitions:

### Artist Table
```sql
CREATE TABLE dbo.Artist (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(64) NOT NULL
);
```

### Song Table
```sql
CREATE TABLE dbo.Song (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(64) NOT NULL,
    artistID INT NULL,
    released DATE NULL,
    URL NVARCHAR(1024) NULL,
    distance FLOAT(53) NULL,
    CONSTRAINT FK_Song_Artist FOREIGN KEY (artistID) REFERENCES dbo.Artist(id)
);
```

## Environment Variables

The application uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_SERVER` | localhost | SQL Server host |
| `DB_PORT` | 1433 | SQL Server port |
| `DB_NAME` | starsongs | Database name |
| `DB_USER` | sa | Database username |
| `DB_PASSWORD` | YourStrong@Passw0rd | Database password |

## Docker Services

### SQL Server (`sqlserver`)
- **Image**: mcr.microsoft.com/mssql/server:2022-latest
- **Container**: sqlserver-dev
- **Port**: 1433
- **Platform**: linux/amd64 (uses Rosetta 2 on Apple Silicon)
- **Health Check**: SQL query verification every 10s
- **Volume**: sqlserver-data (persistent storage)

### API Service (`fastDataApi`)
- **Build**: Local Dockerfile in `./fastDataApi`
- **Container**: accessible-fast-data-api
- **Port**: 8000
- **Depends On**: sqlserver (with health check)
- **Auto-restart**: unless-stopped
- **Environment**: Database connection details

### Frontend Service (`nextui`)
- **Build**: Multi-stage Dockerfile in `./nextui`
- **Container**: accessible-nextui
- **Port**: 80 (maps to container port 3000)
- **Depends On**: fastDataApi
- **Auto-restart**: unless-stopped
- **Environment**: API URL configuration

## Key Differences from Java Implementation

1. **Field Naming**:
   - Database uses SQL Server conventions: `artistID`, `released`, `URL`
   - DTOs use camelCase: `artistId`, `releaseDate`, `url`
   - Python code handles the mapping transparently

2. **Repository Pattern**:
   - Java uses Spring Data JPA repositories
   - Python uses SQLAlchemy Session directly via dependency injection

3. **Error Handling**:
   - Java uses custom exception classes with `@ControllerAdvice`
   - Python uses FastAPI `HTTPException`

4. **Documentation**:
   - Java requires SpringDoc annotations
   - Python generates OpenAPI docs automatically from Pydantic models

## Development Workflow

1. **Start services**: `docker compose up -d`
2. **Initialize database**: `./init-database.sh`
3. **Access services**:
   - Frontend: http://localhost
   - API docs: http://localhost:8000/swagger-ui.html
4. **Make changes**: Edit files in `fastDataApi/app/` or `nextui/`
5. **Rebuild**:
   - Backend: `docker compose up -d --build fastDataApi`
   - Frontend: `docker compose up -d --build nextui`
6. **View logs**:
   - All: `docker compose logs -f`
   - Backend: `docker compose logs -f fastDataApi`
   - Frontend: `docker compose logs -f nextui`

## Testing

### Manual Testing
Use the Swagger UI at http://localhost:8000/swagger-ui.html

### Command Line Testing
```bash
# Create artist
curl -X POST http://localhost:8000/v1/artists \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Artist"}'

# Get all artists
curl http://localhost:8000/v1/artists

# Create song
curl -X POST http://localhost:8000/v1/songs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Song",
    "artistId": 1,
    "releaseDate": "2024-01-01",
    "url": "https://example.com",
    "distance": 100.0
  }'

# Get all songs
curl http://localhost:8000/v1/songs
```

## Deployment Considerations

### Security
- Change default SQL Server password
- Configure CORS properly for production
- Use environment variables for sensitive data
- Enable HTTPS/TLS for both frontend and API
- Implement authentication and authorization
- Use secrets management (e.g., Azure Key Vault, AWS Secrets Manager)

### Performance
- Configure connection pooling in SQLAlchemy
- Add database indexes for frequently queried fields
- Use async endpoints for high concurrency
- Enable Next.js caching and optimization features
- Consider CDN for static assets

### Monitoring
- Add structured logging for both frontend and backend
- Implement health check endpoints
- Set up application metrics and monitoring
- Configure error tracking (e.g., Sentry)

## Future Enhancements

### Backend
- [ ] Add authentication/authorization (JWT tokens)
- [ ] Implement pagination for list endpoints
- [ ] Add filtering and sorting parameters
- [ ] Create automated pytest tests
- [ ] Add database migrations (Alembic)
- [ ] Implement Redis caching
- [ ] Add rate limiting

### Frontend
- [ ] Add authentication UI (login/logout)
- [ ] Implement CRUD forms for artists and songs
- [ ] Add search and filter functionality
- [ ] Create responsive mobile design
- [ ] Add data visualization (charts/graphs)
- [ ] Implement client-side caching
- [ ] Add Vitest component tests

### DevOps
- [ ] Create CI/CD pipeline
- [ ] Add Docker health checks
- [ ] Set up staging environment
- [ ] Implement database backups
- [ ] Add monitoring and alerting
