"""
flaskDataApi - Flask microservice for CRUD access to SQL Server

This microservice provides REST API endpoints:
- /v1/artists - Artist CRUD operations
- /v1/songs   - Song CRUD operations
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger


def create_app():
    """
    Flask application factory
    """
    app = Flask(__name__)

    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

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

    return app
