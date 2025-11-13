"""
Error handlers for Flask application
"""
from flask import jsonify
from marshmallow import ValidationError


def register_error_handlers(app):
    """
    Register error handlers with the Flask app
    """

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        return jsonify({"detail": str(error.description)}), 404

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors"""
        return jsonify({"detail": str(error.description)}), 400

    @app.errorhandler(ValidationError)
    def validation_error(error):
        """Handle Marshmallow validation errors"""
        return jsonify({"detail": "Validation error", "errors": error.messages}), 400

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        return jsonify({"detail": "Internal server error"}), 500
