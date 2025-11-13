"""
Application entry point for flaskDataApi
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Run with Flask development server
    # In production, use gunicorn instead
    app.run(host="0.0.0.0", port=8001, debug=True)
