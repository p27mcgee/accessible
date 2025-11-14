"""
fastDataApi - FastAPI microservice for CRUD access to SQL Server

This microservice provides REST API endpoints:
- /v1/artists - Artist CRUD operations
- /v1/songs   - Song CRUD operations
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import artists, songs, auth, admin
from auth_lib.database import create_tables

# Create FastAPI application
app = FastAPI(
    title="fastDataApi",
    description="Python microservice for CRUD access to SQL Server",
    version="1.0.0",
    docs_url="/swagger-ui.html",
    redoc_url="/api-docs"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(artists.router)
app.include_router(songs.router)


# Startup event to create auth database tables
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup if they don't exist"""
    create_tables()


@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "name": "fastDataApi",
        "version": "1.0.0",
        "description": "Python data microservice with authentication",
        "endpoints": {
            "auth": "/auth",
            "admin": "/admin/users",
            "artists": "/v1/artists",
            "songs": "/v1/songs",
            "docs": "/swagger-ui.html",
            "openapi": "/openapi.json"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
