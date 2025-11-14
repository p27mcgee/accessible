# Database Management Guide

This guide covers database management for the Accessible project in both development/test and production environments.

## Overview

The database architecture differs between environments:

**Development/Test:**
- SQL Server 2022 running in Docker container
- Managed independently via Makefile
- Runs on host network (accessible at localhost:1433)
- Data persists in Docker volume

**Production:**
- External managed database (Azure SQL, AWS RDS, etc.)
- Connection info provided via Helm chart configuration
- Not deployed in Kubernetes cluster

## Database States

The database can be in one of three states:

| State | Description | How to Reach | Next Step |
|-------|-------------|--------------|-----------|
| **ABSENT** | Container doesn't exist | Fresh install | `make db-start` |
| **EMPTY** | Container running but starsongs database not initialized | After `make db-start` | `make db-init` |
| **READY** | Database initialized with tables and data | After `make db-init` | Start application services |

Check the current state with:
```bash
make db-status
```

## Quick Start (Development)

```bash
# 1. Start database container
make db-start

# 2. Initialize database (create DB, schema, seed data)
make db-init

# 3. Verify it's ready
make db-status

# 4. Start application services
docker compose --profile fastapi up -d
```

## Makefile Commands

### db-start
Start the SQL Server database container.

```bash
make db-start
```

**What it does:**
- Creates new container if it doesn't exist
- Starts existing container if it's stopped
- Uses host network (database accessible at localhost:1433)
- Creates persistent volume for data storage
- Waits 10 seconds for SQL Server to start

**Container Details:**
- Name: `sqlserver-dev`
- Image: `mcr.microsoft.com/mssql/server:2022-latest`
- Network: host (accessible at localhost:1433)
- Volume: `sqlserver-data` → `/var/opt/mssql`
- SQL scripts mounted: `./sql` → `/docker-entrypoint-initdb.d`

### db-stop
Stop the database container (data preserved).

```bash
make db-stop
```

**What it does:**
- Stops the running container
- Data remains in volume (safe operation)

### db-status
Check the database state (absent/empty/ready).

```bash
make db-status
```

**Output examples:**
```
❌ Database state: ABSENT
   Container 'sqlserver-dev' does not exist.
   Run: make db-start

⚠️  Database state: EMPTY
   SQL Server is running but 'starsongs' database does not exist.
   Run: make db-init

✅ Database state: READY
   Database 'starsongs' is initialized and ready for use.
   Tables: Artist, Song
   Data: 5 artists, 6 songs
```

**Exit codes:**
- 0 = READY (database fully initialized)
- 1 = EMPTY (container running, needs initialization)
- 2 = ABSENT (container doesn't exist)

### db-init
Initialize the database (create database, schema, seed data).

```bash
make db-init
```

**What it does:**
1. Creates `starsongs` database
2. Creates tables: `Artist` and `Song`
3. Creates indexes for performance
4. Loads sample data (5 artists, 6 songs)
5. Verifies initialization with `db-ready.sh`

**Requirements:**
- Database container must be running (`make db-start` first)
- Idempotent: Safe to run multiple times

**SQL Scripts Executed:**
1. `sql/init_db.sql` - Create database
2. `sql/schema.sql` - Create tables and indexes
3. `sql/seed_data.sql` - Load sample data

### db-clean
**DESTRUCTIVE:** Stop and remove database container and volume.

```bash
make db-clean
```

**Warning:** This deletes all data! You'll be prompted to confirm.

**What it does:**
1. Prompts for confirmation
2. Stops the container
3. Removes the container
4. Removes the volume (deletes all data)

**Use cases:**
- Start fresh with clean database
- Free disk space
- Troubleshoot persistent database issues

### db-logs
View database container logs (follows in real-time).

```bash
make db-logs
```

**Use cases:**
- Troubleshoot startup issues
- Monitor database activity
- Check for errors

Press Ctrl+C to stop following logs.

### db-shell
Open an interactive sqlcmd shell to the database.

```bash
make db-shell
```

**Useful commands:**
```sql
-- List databases
SELECT name FROM sys.databases;

-- Use starsongs database
USE starsongs;
GO

-- List tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES;
GO

-- Query data
SELECT * FROM dbo.Artist;
GO

SELECT * FROM dbo.Song;
GO

-- Exit
quit
```

## Database Schema

### Artist Table
```sql
CREATE TABLE dbo.Artist (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(64) NOT NULL
);

CREATE INDEX IX_Artist_Name ON dbo.Artist(name);
```

### Song Table
```sql
CREATE TABLE dbo.Song (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(64) NOT NULL,
    artistID INT NULL,
    released DATE NULL,
    URL NVARCHAR(1024) NULL,
    distance FLOAT NULL,
    CONSTRAINT FK_Song_Artist FOREIGN KEY (artistID)
        REFERENCES dbo.Artist(id)
);

CREATE INDEX IX_Song_ArtistID ON dbo.Song(artistID);
CREATE INDEX IX_Song_Title ON dbo.Song(title);
```

**Field Mappings (Database → API):**
- Database: `artistID` → API: `artist_id`
- Database: `released` → API: `release_date`
- Database: `URL` → API: `url`

## Connection Configuration

### Development/Test

APIs connect to the database via `host.docker.internal`:

```yaml
# compose.yaml
environment:
  - DB_SERVER=host.docker.internal
  - DB_PORT=1433
  - DB_NAME=starsongs
  - DB_USER=sa
  - DB_PASSWORD=YourStrong@Passw0rd
```

**Why host.docker.internal?**
- Database runs on host network
- APIs run in Docker containers
- `host.docker.internal` resolves to host machine from within containers
- Alternative: Use `localhost` with `network_mode: host` for API containers

### Direct Connection (Outside Docker)

To connect from your host machine (Azure Data Studio, sqlcmd, etc.):

```
Server: localhost,1433
Username: sa
Password: YourStrong@Passw0rd
Database: starsongs
```

### Production

In production, database connection comes from Helm chart values:

```yaml
# values.yaml (example)
database:
  server: my-database.database.azure.com
  port: 1433
  name: starsongs
  user: appuser
  passwordSecret: database-password  # k8s secret
```

Helm chart injects these as environment variables in API deployments.

## Typical Workflows

### First Time Setup

```bash
# Start and initialize database
make db-start
make db-init

# Verify ready
make db-status

# Start application services
docker compose --profile fastapi up -d

# Check API connectivity
curl http://localhost:8000/v1/artists
```

### Daily Development

```bash
# Start database (if stopped)
make db-start

# Check status
make db-status

# Start services
docker compose --profile fastapi up -d

# ... do development work ...

# Stop services
docker compose down

# Optionally stop database
make db-stop
```

### Reset Database

```bash
# Stop services
docker compose down

# Clean database (destroys data)
make db-clean

# Start fresh
make db-start
make db-init

# Restart services
docker compose --profile fastapi up -d
```

### Modify Schema

```bash
# Option 1: Edit sql/schema.sql and reinitialize
make db-clean
make db-start
make db-init

# Option 2: Manual migration via db-shell
make db-shell
# ... run ALTER TABLE commands ...
```

### Backup and Restore

**Backup:**
```bash
# Stop database
make db-stop

# Backup volume
docker run --rm \
  -v sqlserver-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db-backup-$(date +%Y%m%d).tar.gz /data

# Restart database
make db-start
```

**Restore:**
```bash
# Stop and remove database
make db-clean

# Restore volume
docker volume create sqlserver-data
docker run --rm \
  -v sqlserver-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/db-backup-20250113.tar.gz -C /

# Start database
make db-start
make db-status
```

## Troubleshooting

### Container won't start

**Symptoms:** `make db-start` fails or exits immediately

**Solutions:**
```bash
# Check Docker is running
docker ps

# Check logs
make db-logs

# Remove corrupt container
make db-clean
make db-start
```

### Database initialization fails

**Symptoms:** `make db-init` errors or `make db-status` shows EMPTY

**Solutions:**
```bash
# Check SQL Server is accepting connections
make db-logs

# Wait longer (SQL Server can take 30+ seconds to start)
sleep 30
make db-status

# Check SQL scripts for errors
make db-shell
# Manually run commands from sql/schema.sql
```

### APIs can't connect to database

**Symptoms:** API logs show connection errors

**Solutions:**
```bash
# Verify database is ready
make db-status

# Check connection from API container
docker compose exec fastDataApi ping host.docker.internal

# Test direct sqlcmd connection
docker compose exec fastDataApi \
  apt-get update && apt-get install -y curl && \
  curl telnet://host.docker.internal:1433

# Verify environment variables
docker compose exec fastDataApi env | grep DB_
```

### Port 1433 already in use

**Symptoms:** `make db-start` fails with port conflict

**Solutions:**
```bash
# Check what's using port 1433
lsof -i :1433

# Stop conflicting service
# OR
# Change database port in Makefile (DB_PORT variable)
# And update .env (DB_PORT=1434)
```

### Permission denied errors

**Symptoms:** Volume mount errors or sqlcmd permission denied

**Solutions:**
```bash
# Ensure Docker has access to ./sql directory
ls -la sql/

# On macOS: Ensure Docker Desktop has access to project directory
# Docker Desktop → Settings → Resources → File Sharing

# Recreate volume
make db-clean
make db-start
```

## Production Deployment

### Database Requirements

For production deployment, you need:

1. **Managed Database:** Azure SQL Database, AWS RDS SQL Server, or similar
2. **Network Access:** Kubernetes cluster can reach database
3. **Credentials:** Username, password, server address
4. **Database Created:** `starsongs` database must exist
5. **Schema Applied:** Run sql/schema.sql on production database

### Helm Chart Integration

Your Helm chart should:

1. **Accept database config as values:**
```yaml
# values.yaml
database:
  server: ""
  port: 1433
  name: starsongs
  user: ""
  existingSecret: ""  # k8s secret with password
```

2. **Inject as environment variables:**
```yaml
# deployment.yaml
env:
  - name: DB_SERVER
    value: {{ .Values.database.server }}
  - name: DB_PORT
    value: {{ .Values.database.port | quote }}
  - name: DB_NAME
    value: {{ .Values.database.name }}
  - name: DB_USER
    value: {{ .Values.database.user }}
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ .Values.database.existingSecret }}
        key: password
```

3. **Optional: Init container to verify database:**
```yaml
# deployment.yaml
initContainers:
  - name: wait-for-db
    image: alpine
    command: ['sh', '-c']
    args:
      - |
        # Copy db-ready.sh to init container
        # Run db-ready.sh to verify database is accessible
        # Exit non-zero if database not ready (pod won't start)
```

### Schema Migration

For production schema changes:

1. **Version control:** Store schema changes in git
2. **Migration tool:** Use Flyway, Liquibase, or similar
3. **CI/CD:** Run migrations before deploying new app version
4. **Rollback plan:** Keep rollback scripts for each migration

## Security Considerations

### Development
- Default password (`YourStrong@Passw0rd`) is hardcoded
- Acceptable for local development only
- Never commit production credentials

### Production
- Use strong, randomly generated passwords
- Store credentials in Kubernetes Secrets
- Rotate passwords regularly
- Use managed identity if available (Azure AD, IAM)
- Restrict network access (firewall rules, security groups)
- Enable SSL/TLS for connections
- Enable database encryption at rest

## Additional Resources

- [SQL Server 2022 Documentation](https://docs.microsoft.com/en-us/sql/sql-server/)
- [Azure Data Studio](https://docs.microsoft.com/en-us/sql/azure-data-studio/)
- [Docker SQL Server Best Practices](https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-docker-container-deployment)
- [Helm Chart Development](https://helm.sh/docs/chart_template_guide/)
