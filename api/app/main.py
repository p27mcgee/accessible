"""
Star Songs API - FastAPI microservice for CRUD access to SQL Server
Based on the Java JPA project from star-songs

This microservice provides REST API endpoints matching the Java Spring Boot application:
- /v1/artists - Artist CRUD operations
- /v1/songs   - Song CRUD operations
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import artists, songs

# Create FastAPI application
app = FastAPI(
    title="Star Songs API",
    description="Python microservice for CRUD access to SQL Server - compatible with star-songs Java API",
    version="1.0.0",
    docs_url="/swagger-ui.html",  # Match Spring Boot default
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
app.include_router(artists.router)
app.include_router(songs.router)


@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "name": "Star Songs API",
        "version": "1.0.0",
        "description": "Python microservice compatible with star-songs Java API",
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
