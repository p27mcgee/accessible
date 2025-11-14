# Configuration Guide

Complete reference for configuring the Accessible project for development, staging, and production environments.

## Environment Variables

All configuration is managed through environment variables. Set these in a `.env` file or your deployment platform.

### Quick Setup

```bash
# Copy template
cp .env.example .env

# Edit configuration
vim .env

# Restart services
docker compose down
docker compose --profile fastapi up -d
```

---

## CORS Configuration

### Overview

CORS (Cross-Origin Resource Sharing) controls which origins can access your API. Proper configuration prevents unauthorized access and CSRF attacks.

### Environment Variable

**CORS_ORIGINS** - Comma-separated list of allowed origins

```bash
# Development
CORS_ORIGINS=http://localhost,http://localhost:80,http://localhost:3000

# Production
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

### Examples by Environment

**Local Development:**
```bash
CORS_ORIGINS=http://localhost,http://localhost:80,http://localhost:3000,http://127.0.0.1
```

**Staging:**
```bash
CORS_ORIGINS=https://staging.example.com,https://staging-admin.example.com
```

**Production (HTTPS only):**
```bash
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

### Implementation

Both FastAPI and Flask parse the environment variable:

```python
cors_origins_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost,http://localhost:80,http://localhost:3000"
)
allowed_origins = [origin.strip() for origin in cors_origins_str.split(",")]
```

### Testing CORS

**Test allowed origin:**
```bash
curl -H "Origin: http://localhost" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/v1/artists

# Should return: Access-Control-Allow-Origin: http://localhost
```

**Test blocked origin:**
```bash
curl -H "Origin: https://evil.com" \
     -X OPTIONS \
     http://localhost:8000/v1/artists

# Should NOT return Access-Control-Allow-Origin header
```

### Security Best Practices

**DO:**
- ✅ Use specific origins (e.g., `https://app.example.com`)
- ✅ Use HTTPS in production (`https://`, not `http://`)
- ✅ Set different origins per environment
- ✅ Include protocol and port (e.g., `http://localhost:3000`)

**DON'T:**
- ❌ Never use `*` wildcard in production
- ❌ Don't allow `http://` origins in production
- ❌ Don't include trailing slashes
- ❌ Don't use IP addresses in production

### Troubleshooting

**CORS errors in browser:**
```
Access to fetch at 'http://localhost:8000/v1/artists' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solution:**
1. Verify origin is in `CORS_ORIGINS`
2. Restart API service: `docker compose restart fastDataApi`
3. Check logs: `docker compose logs fastDataApi | grep CORS`

---

## Database Connection Pooling

### Overview

Connection pooling maintains a pool of reusable database connections, improving performance and resource utilization.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| **DB_POOL_SIZE** | 20 | Persistent connections in pool |
| **DB_POOL_MAX_OVERFLOW** | 10 | Additional on-demand connections |
| **DB_POOL_TIMEOUT** | 30 | Seconds to wait for connection |
| **DB_POOL_RECYCLE** | 3600 | Recycle connections after N seconds |
| **DB_POOL_PRE_PING** | true | Test connections before use |
| **DB_SQL_ECHO** | false | Log all SQL statements |

### Configuration by Environment

**Development:**
```bash
DB_POOL_SIZE=5
DB_POOL_MAX_OVERFLOW=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_SQL_ECHO=true  # Enable for debugging
```

**Staging:**
```bash
DB_POOL_SIZE=15
DB_POOL_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=20
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_SQL_ECHO=false
```

**Production:**
```bash
DB_POOL_SIZE=30
DB_POOL_MAX_OVERFLOW=15
DB_POOL_TIMEOUT=15
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_SQL_ECHO=false
```

### Parameter Details

#### DB_POOL_SIZE
Number of persistent connections maintained in the pool.

**Recommendations:**
- Development: 5-10
- Staging: 10-20
- Production: 20-50
- Formula: `(num_workers * 2) + spare_connections`

**Example calculation:**
```
4 Uvicorn workers × 2 = 8 connections
8 + 5 spare = 13 minimum
Recommended: 20 (for headroom)
```

#### DB_POOL_MAX_OVERFLOW
Additional connections created on-demand when pool is exhausted.

**Recommendations:**
- Development: 5-10
- Production: 10-20
- Formula: `pool_size * 0.5`

**How it works:**
- Total max connections = `pool_size + max_overflow`
- Overflow connections are closed after use
- Example: pool_size=20, overflow=10 → max 30 concurrent connections

#### DB_POOL_TIMEOUT
Seconds to wait for an available connection before raising an error.

**Recommendations:**
- Development: 30 seconds
- Production: 10-30 seconds
- High-traffic: 5-10 seconds (fail fast)

If timeout errors occur frequently, increase `pool_size` or optimize slow queries.

#### DB_POOL_RECYCLE
Recycle connections after N seconds to prevent stale connections.

**Recommendations:**
- SQL Server: 3600 seconds (1 hour)
- PostgreSQL: 3600-7200 seconds
- MySQL: 28800 seconds (8 hours)

**Why it matters:**
- Prevents using broken connections
- Handles database restarts gracefully
- Works around network issues

#### DB_POOL_PRE_PING
Test connections before using them (executes `SELECT 1`).

**Recommendation:** Always keep `true`

**Benefits:**
- Prevents using broken connections
- Automatic recovery from database restarts
- Minimal overhead (~1ms per checkout)

#### DB_SQL_ECHO
Log all SQL statements to console.

**Recommendations:**
- Development: `true` (helpful for debugging)
- Production: `false` (significant overhead)

**Impact:** ~5-10% performance overhead when enabled.

### Monitoring

#### Pool Status Endpoint

```bash
curl http://localhost:8000/health/pool
```

**Response:**
```json
{
  "pool_size": 20,
  "checked_out": 3,
  "overflow": 0,
  "total_connections": 3,
  "status": "healthy"
}
```

**Status values:**
- `healthy`: Connections available
- `degraded`: Pool exhausted

#### Database Health Check

```bash
curl http://localhost:8000/health/db
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "Database is responsive"
}
```

#### View Logs

```bash
# Startup log shows pool configuration
docker compose logs fastDataApi | grep "Database pool configured"

# Output:
# INFO: Database pool configured: size=20, max_overflow=10, timeout=30s, recycle=3600s, pre_ping=True
```

### Performance Tuning

#### Calculate Optimal Pool Size

**Formula:**
```
pool_size = (num_workers × concurrent_requests_per_worker) + spare_connections
```

**FastAPI with Uvicorn:**
```
Workers: 4
Concurrent requests per worker: 2
Spare: 5

pool_size = (4 × 2) + 5 = 13
Recommended: 20
```

**Flask with Gunicorn:**
```
Workers: 4
Concurrent requests per worker: 1 (WSGI is synchronous)
Spare: 5

pool_size = (4 × 1) + 5 = 9
Recommended: 15
```

#### Load Testing

Monitor pool status during load tests:

```bash
# Watch pool in real-time
watch -n 1 'curl -s http://localhost:8000/health/pool | jq'
```

**Look for:**
- ✅ `checked_out` stays below `pool_size` (healthy)
- ⚠️ `overflow` > 0 consistently (increase pool_size)
- ❌ `status: "degraded"` (pool exhausted, increase urgently)

### Troubleshooting

#### TimeoutError: QueuePool limit exceeded

**Error:**
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 20 overflow 10 reached,
connection timed out, timeout 30
```

**Solutions:**
1. Increase pool size: `DB_POOL_SIZE=30`
2. Increase overflow: `DB_POOL_MAX_OVERFLOW=15`
3. Optimize slow queries
4. Increase timeout temporarily: `DB_POOL_TIMEOUT=60`

#### Stale connection errors

**Error:**
```
OperationalError: (pyodbc.OperationalError) ('08S01',
'[08S01] [Microsoft][ODBC Driver 18 for SQL Server]Communication link failure')
```

**Solutions:**
1. Ensure pre_ping enabled: `DB_POOL_PRE_PING=true`
2. Reduce recycle time: `DB_POOL_RECYCLE=1800`
3. Check network connectivity

#### Too many connections on database

**Error:**
```
Error: Login failed for user 'sa'. Reason:
Maximum number of user connections already reached.
```

**Solutions:**
1. Reduce pool size per instance: `DB_POOL_SIZE=10`
2. Calculate total: `num_instances × (pool_size + max_overflow)`
3. Scale down unnecessary instances
4. Check database max connections:
   ```sql
   SELECT @@MAX_CONNECTIONS;
   ```

### Best Practices

**DO:**
- ✅ Always enable `pool_pre_ping=true`
- ✅ Monitor pool status in production
- ✅ Calculate pool size based on workers
- ✅ Disable `DB_SQL_ECHO` in production
- ✅ Load test before deployment
- ✅ Set `pool_recycle` to prevent stale connections

**DON'T:**
- ❌ Don't use SQLAlchemy defaults in production
- ❌ Don't set pool_size too high (wastes resources)
- ❌ Don't disable `pool_pre_ping`
- ❌ Don't enable `DB_SQL_ECHO` in production
- ❌ Don't ignore pool exhaustion warnings

---

## Complete Environment Reference

### .env Template

```bash
# CORS Configuration
CORS_ORIGINS=http://localhost,http://localhost:80,http://localhost:3000

# Database Connection Pool
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
DB_SQL_ECHO=false

# Database Connection
DB_HOST=sqlserver
DB_PORT=1433
DB_NAME=starsongs
DB_USER=sa
DB_PASSWORD=YourStrong@Passw0rd
```

### Kubernetes/Helm Configuration

**ConfigMap example:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: accessible-config
data:
  CORS_ORIGINS: "https://app.example.com,https://www.example.com"
  DB_POOL_SIZE: "30"
  DB_POOL_MAX_OVERFLOW: "15"
  DB_POOL_TIMEOUT: "15"
  DB_POOL_RECYCLE: "3600"
  DB_POOL_PRE_PING: "true"
  DB_SQL_ECHO: "false"
```

**Helm values.yaml:**
```yaml
env:
  corsOrigins: "https://app.example.com"
  dbPoolSize: "30"
  dbPoolMaxOverflow: "15"
  dbPoolTimeout: "15"
  dbPoolRecycle: "3600"
  dbPoolPrePing: "true"
  dbSqlEcho: "false"
```

---

## Related Documentation

- [DATABASE.md](DATABASE.md) - Database management
- [TODO.md](TODO.md) - Production readiness checklist
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Architecture overview

---

**Last Updated:** November 14, 2025
