"""
Health check and monitoring endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, engine

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get("/pool")
def pool_status():
    """
    Get database connection pool status

    Returns information about the connection pool including:
    - Size: Number of connections in the pool
    - Checked out: Number of connections currently in use
    - Overflow: Number of overflow connections
    - Total checked out: Checked out + overflow connections
    """
    pool = engine.pool

    return {
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.checkedout() + pool.overflow(),
        "configured_pool_size": engine.pool._pool.maxsize if hasattr(engine.pool._pool, 'maxsize') else None,
        "status": "healthy" if pool.checkedout() < pool.size() else "degraded"
    }


@router.get("/db")
def database_health(db: Session = Depends(get_db)):
    """
    Check database connectivity and health

    Performs a simple query to verify database is responsive
    """
    try:
        # Execute a simple query to check connectivity
        result = db.execute(text("SELECT 1 AS health_check"))
        row = result.fetchone()

        if row and row[0] == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "message": "Database is responsive"
            }
        else:
            return {
                "status": "unhealthy",
                "database": "error",
                "message": "Unexpected query result"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
