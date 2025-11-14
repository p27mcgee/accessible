"""
Error handlers for Flask application with structured logging
"""
from flask import jsonify, request
from marshmallow import ValidationError
import structlog

from app.utils.logger import get_request_id

# Get logger
logger = structlog.get_logger(__name__)


def register_error_handlers(app):
    """
    Register error handlers with the Flask app
    """

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        request_id = get_request_id()
        error_logger = logger.bind(request_id=request_id) if request_id else logger

        error_logger.warning(
            "Resource not found",
            method=request.method,
            path=request.path,
            error_detail=str(error.description),
            status_code=404
        )

        return jsonify({"detail": str(error.description)}), 404

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors"""
        request_id = get_request_id()
        error_logger = logger.bind(request_id=request_id) if request_id else logger

        error_logger.warning(
            "Bad request",
            method=request.method,
            path=request.path,
            error_detail=str(error.description),
            status_code=400
        )

        return jsonify({"detail": str(error.description)}), 400

    @app.errorhandler(ValidationError)
    def validation_error(error):
        """Handle Marshmallow validation errors"""
        request_id = get_request_id()
        error_logger = logger.bind(request_id=request_id) if request_id else logger

        error_logger.warning(
            "Validation error",
            method=request.method,
            path=request.path,
            validation_errors=error.messages,
            status_code=400
        )

        return jsonify({"detail": "Validation error", "errors": error.messages}), 400

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        request_id = get_request_id()
        error_logger = logger.bind(request_id=request_id) if request_id else logger

        error_logger.error(
            "Internal server error",
            method=request.method,
            path=request.path,
            error_type=type(error).__name__,
            error_message=str(error),
            status_code=500,
            exc_info=True
        )

        return jsonify({"detail": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        request_id = get_request_id()
        error_logger = logger.bind(request_id=request_id) if request_id else logger

        error_logger.error(
            "Unhandled exception",
            method=request.method,
            path=request.path,
            error_type=type(error).__name__,
            error_message=str(error),
            exc_info=True
        )

        # Return 500 for unhandled exceptions
        return jsonify({"detail": "Internal server error"}), 500
