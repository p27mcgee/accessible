"""
flaskDataApi - Flask microservice for CRUD access to SQL Server

This microservice provides REST API endpoints:
- /v1/artists - Artist CRUD operations
- /v1/songs   - Song CRUD operations
"""
import os
import warnings
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from app.logging_config import configure_logging, get_logger
from app.middleware.logging import setup_request_logging
from app.middleware.cors_logging import setup_cors_logging

# Configure logging before anything else
configure_logging()
logger = get_logger(__name__)


def create_app():
    """
    Flask application factory
    """
    app = Flask(__name__)

    # Set up request/response logging
    setup_request_logging(app)

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
        warnings.warn(
            "CORS wildcard (*) detected! This is insecure and should never be used in production.",
            category=UserWarning
        )
        logger.warning(
            "CORS wildcard detected in configuration",
            allowed_origins=allowed_origins,
            security_risk=True
        )

    logger.info(
        "CORS configured",
        allowed_origins=allowed_origins,
        supports_credentials=True
    )

    CORS(
        app,
        resources={r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }}
    )

    # Set up CORS logging (after CORS is configured)
    setup_cors_logging(app, allowed_origins)

    # Configure Swagger/OpenAPI documentation
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs"
    }

    swagger_template = {
        "info": {
            "title": "flaskDataApi",
            "description": "Flask microservice for CRUD access to SQL Server",
            "version": "1.0.0"
        },
        "basePath": "/",
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Initialize database
    from app.database import init_db
    init_db(app)

    # Import models (needed for Flask-SQLAlchemy to work properly)
    from app import models

    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Register blueprints
    from app.routes.artists import artists_bp
    from app.routes.songs import songs_bp

    app.register_blueprint(artists_bp)
    app.register_blueprint(songs_bp)

    logger.info("Blueprints registered", blueprints=["artists", "songs"])

    # Root endpoint
    @app.route('/')
    def root():
        """Root endpoint - API info"""
        return jsonify({
            "name": "flaskDataApi",
            "version": "1.0.0",
            "description": "Flask data microservice",
            "endpoints": {
                "artists": "/v1/artists",
                "songs": "/v1/songs",
                "docs": "/apidocs",
            }
        })

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})

    # Log application startup
    logger.info(
        "flaskDataApi initialized",
        version="1.0.0",
        endpoints=["/", "/health", "/v1/artists", "/v1/songs"]
    )

    return app
