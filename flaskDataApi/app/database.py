"""
Database configuration and session management for SQL Server with Flask
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os

# Create base class for models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with custom base
db = SQLAlchemy(model_class=Base)


def init_db(app):
    """
    Initialize database with Flask app
    """
    # SQL Server connection parameters
    db_server = os.getenv("DB_SERVER", "localhost")
    db_port = os.getenv("DB_PORT", "1433")
    db_name = os.getenv("DB_NAME", "starsongs")
    db_user = os.getenv("DB_USER", "sa")
    db_password = os.getenv("DB_PASSWORD", "YourStrong@Passw0rd")

    # SQL Server connection string using pyodbc
    # TrustServerCertificate=yes is needed for self-signed certificates in Docker
    from urllib.parse import quote_plus

    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={db_server},{db_port};"
        f"DATABASE={db_name};"
        f"UID={db_user};"
        f"PWD={db_password};"
        f"TrustServerCertificate=yes"
    )

    sqlalchemy_database_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"

    # Configure Flask-SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Set to False in production
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before using them
    }

    # Initialize db with app
    db.init_app(app)
