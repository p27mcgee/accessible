"""
fastDataApi - FastAPI microservice for CRUD access to SQL Server

This microservice provides REST API endpoints:
- /v1/artists - Artist CRUD operations
- /v1/songs   - Song CRUD operations
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import artists, songs, health

# Create FastAPI application
app = FastAPI(
    title="fastDataApi",
    description="Python microservice for CRUD access to SQL Server",
    version="1.0.0",
    docs_url="/swagger-ui.html",
    redoc_url="/api-docs"
)

# Configure CORS - Load allowed origins from environment variable
# SECURITY: Never use "*" in production!
cors_origins_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost,http://localhost:80,http://localhost:3000"  # Development default
)
# Parse comma-separated origins into list
allowed_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Validate that wildcard is not used in production
if "*" in allowed_origins:
    import warnings
    warnings.warn(
        "CORS wildcard (*) detected! This is insecure and should never be used in production.",
        SecurityWarning
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(artists.router)
app.include_router(songs.router)
app.include_router(health.router)


@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "name": "fastDataApi",
        "version": "1.0.0",
        "description": "Python data microservice",
        "endpoints": {
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
