"""
Configuration settings for authentication library
"""
import os
from datetime import timedelta

# PostgreSQL connection string for auth database
POSTGRES_AUTH_DB_URL = os.getenv(
    "POSTGRES_AUTH_DB_URL",
    "postgresql://postgres:postgres@localhost:5432/auth_db"
)

# JWT Settings
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
)

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

# Password hashing
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
