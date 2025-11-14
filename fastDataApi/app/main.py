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
from app.logging_config import configure_logging, get_logger
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.cors_logging import CORSLoggingMiddleware

# Configure logging before anything else
configure_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="fastDataApi",
    description="Python microservice for CRUD access to SQL Server",
    version="1.0.0",
    docs_url="/swagger-ui.html",
    redoc_url="/api-docs"
)

# Add request logging middleware (must be added first)
app.add_middleware(RequestLoggingMiddleware)

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
    logger.warning(
        "CORS wildcard detected in configuration",
        allowed_origins=allowed_origins,
        security_risk=True
    )

logger.info(
    "CORS configured",
    allowed_origins=allowed_origins,
    allow_credentials=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Add CORS logging middleware (after CORS middleware)
app.add_middleware(CORSLoggingMiddleware, allowed_origins=allowed_origins)

# Include routers
app.include_router(artists.router)
app.include_router(songs.router)
app.include_router(health.router)

logger.info("Routers registered", routers=["artists", "songs", "health"])


@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info(
        "fastDataApi starting up",
        version="1.0.0",
        endpoints=["GET /", "GET /health", "/v1/artists", "/v1/songs"]
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("fastDataApi shutting down")


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
