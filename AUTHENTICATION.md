# Authentication System Documentation

## Overview

This document describes the authentication and authorization system implemented for the Accessible project. The system provides:

- **User registration and login** with username/password
- **Role-based access control (RBAC)** with `user` and `admin` roles
- **JWT-based authentication** with access and refresh tokens
- **Stateless Kubernetes-ready design** - no pod-level persistence required
- **Shared authentication library** usable by both FastAPI and Flask
- **Admin user management** endpoints for CRUD operations on users
- **PostgreSQL database** for user data (separate from application SQL Server)

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │   Next.js     │  │   Next.js     │  │   Next.js     │   │
│  │   Pods        │  │   Pods        │  │   Pods        │   │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘   │
│          │                   │                   │            │
│          └───────────────────┴───────────────────┘            │
│                              │                                │
│   ┌──────────────────────────┼──────────────────────┐        │
│   │                          │                       │        │
│   │  ┌───────────────┐  ┌───┴───────────┐  ┌──────▼─────┐  │
│   │  │   FastAPI     │  │   FastAPI     │  │   Flask    │  │
│   │  │   Pods        │  │   Pods        │  │   Pods     │  │
│   │  └───────┬───────┘  └───────┬───────┘  └──────┬─────┘  │
│   │          │                   │                 │         │
└───┼──────────┼───────────────────┼─────────────────┼─────────┘
    │          │                   │                 │
    │  ┌───────▼───────────────────▼─────────────────▼────┐
    │  │         PostgreSQL (Auth Database)              │
    └─►│         - Users table with roles                │
       │         - Refresh tokens table                  │
       │         - External managed service or StatefulSet│
       └──────────────────────────────────────────────────┘

       ┌─────────────────────────────────────────────────┐
       │   SQL Server (Application Data - Fixed Schema)  │
       │   - Artists, Songs tables                       │
       │   - Not used for authentication                 │
       └─────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Stateless Services**: All Kubernetes pods are stateless. JWT tokens contain user information, eliminating the need for session storage.

2. **External User Database**: PostgreSQL stores user data separately from application data, allowing independent scaling and management.

3. **Shared Authentication Library**: The `auth_lib/` Python package provides common authentication logic used by both FastAPI and Flask APIs.

4. **Role-Based Access Control**: Extensible role system starts with `user` and `admin`, easily expanded for future roles.

5. **Token-Based Authentication**: JWT access tokens (15 min) and refresh tokens (7 days) with rotation for security.

---

## Database Schema

### PostgreSQL Auth Database

Location: `sql/auth_schema.sql`

#### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### Refresh Tokens Table

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN NOT NULL DEFAULT FALSE
);
```

#### User Roles Enum

```sql
CREATE TYPE user_role AS ENUM ('user', 'admin');
```

**To add new roles**: Simply add to the enum:
```sql
ALTER TYPE user_role ADD VALUE 'moderator';
```

---

## Shared Authentication Library

Location: `auth_lib/`

### Structure

```
auth_lib/
├── __init__.py         # Package exports
├── config.py           # Configuration settings
├── models.py           # SQLAlchemy User and RefreshToken models
├── database.py         # Database connection management
├── security.py         # Password hashing with bcrypt
├── jwt_utils.py        # JWT token creation and validation
└── schemas.py          # Pydantic request/response schemas
```

### Key Components

#### User Model (`models.py`)

```python
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    # Add future roles here

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, nullable=False, default=True)
    # ... timestamps
```

#### JWT Utilities (`jwt_utils.py`)

- `create_access_token()` - Generate short-lived access tokens (15 min)
- `create_refresh_token()` - Generate long-lived refresh tokens (7 days)
- `verify_token()` - Validate and decode JWT tokens
- `extract_user_from_token()` - Extract user info from access token

#### Security (`security.py`)

- `hash_password()` - Bcrypt password hashing
- `verify_password()` - Password verification

---

## FastAPI Implementation

### Authentication Endpoints

**Location**: `fastDataApi/app/routers/auth.py`

- `POST /auth/register` - Register new user (role: `user`)
- `POST /auth/login` - Login with username/password
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Revoke refresh token
- `GET /auth/me` - Get current user info (requires authentication)

### Admin Endpoints

**Location**: `fastDataApi/app/routers/admin.py`

- `GET /admin/users` - List all users (paginated, filterable)
- `GET /admin/users/{user_id}` - Get user by ID
- `POST /admin/users` - Create new user (any role)
- `PUT /admin/users/{user_id}` - Update user (email, role, is_active)
- `DELETE /admin/users/{user_id}` - Delete user
- `GET /admin/users/search/username/{username}` - Search by username

**All admin endpoints require admin role**.

### Authentication Dependencies

**Location**: `fastDataApi/app/dependencies.py`

```python
# Use in routes to require authentication
@router.get("/protected")
async def protected_route(user: User = Depends(require_user)):
    return {"message": f"Hello {user.username}"}

# Use in routes to require admin role
@router.get("/admin-only")
async def admin_route(admin: User = Depends(require_admin)):
    return {"message": "Admin access"}

# Use for custom role requirements
@router.get("/custom")
async def custom_route(user: User = Depends(require_role(UserRole.ADMIN, UserRole.MODERATOR))):
    return {"message": "Admin or Moderator"}
```

### Protecting Existing Endpoints

To add authentication to existing endpoints:

```python
from fastDataApi.app.dependencies import require_user

# Before
@router.get("/v1/songs")
async def get_songs(db: Session = Depends(get_db)):
    ...

# After - require authentication
@router.get("/v1/songs")
async def get_songs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user)
):
    ...
```

---

## Flask Implementation

### Authentication Routes

**Location**: `flaskDataApi/app/routes/auth.py`

Same endpoints as FastAPI:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

### Authentication Decorators

**Location**: `flaskDataApi/app/decorators.py`

```python
from flaskDataApi.app.decorators import require_auth, require_admin

# Require authentication
@app.route('/protected')
@require_auth
def protected_route():
    user_id = request.user_id  # Set by decorator
    username = request.username
    role = request.role
    return jsonify({"message": f"Hello {username}"})

# Require admin role
@app.route('/admin-only')
@require_admin
def admin_route():
    return jsonify({"message": "Admin access"})
```

---

## Next.js UI Implementation

### Authentication Types

**Location**: `nextui/types/index.ts`

```typescript
export type UserRole = 'user' | 'admin';

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
```

### Implementation Tasks Remaining

The following Next.js components still need to be implemented:

1. **Auth Context Provider** (`nextui/contexts/AuthContext.tsx`)
   - State management for authentication
   - Token storage (HTTPOnly cookies or localStorage)
   - Auto-refresh tokens before expiry

2. **Auth API Client** (`nextui/lib/auth-api.ts`)
   - Login/register/logout functions
   - Token refresh logic
   - Authenticated fetch wrapper

3. **Login Page** (`nextui/app/login/page.tsx`)
   - Username/password form
   - Error handling
   - Redirect after login

4. **Registration Page** (`nextui/app/register/page.tsx`)
   - Username/email/password form
   - Password strength validation
   - Auto-login after registration

5. **Admin Dashboard** (`nextui/app/admin/users/page.tsx`)
   - User list with pagination
   - Create/update/delete users
   - Role management
   - Search functionality

6. **Middleware** (`nextui/middleware.ts`)
   - Protect routes requiring authentication
   - Role-based route protection
   - Redirect unauthenticated users to login

7. **Updated API Client** (`nextui/lib/api.ts`)
   - Add Authorization header to requests
   - Handle 401 errors (token expired)
   - Trigger token refresh

---

## Configuration

### Environment Variables

**File**: `.env` (copy from `.env.example`)

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production  # Generate with: openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# PostgreSQL Auth Database
POSTGRES_AUTH_DB_URL=postgresql://postgres:authdbpassword@localhost:5432/auth_db

# Password Hashing
BCRYPT_ROUNDS=12

# API Service Selection (Docker Compose)
API_SERVICE_URL=http://fastDataApi:8000
```

### Makefile Database Management

Both databases (SQL Server for data, PostgreSQL for auth) are managed via Makefile targets, not docker-compose.

**PostgreSQL Auth Database Targets:**

- `make authdb-start` - Start PostgreSQL container (auto-initializes on first run)
- `make authdb-stop` - Stop PostgreSQL container
- `make authdb-status` - Check if PostgreSQL is running and ready
- `make authdb-init` - Verify database initialization (tables exist, show user count)
- `make authdb-clean` - Stop and remove container and volume (requires FORCE=yes)
- `make authdb-logs` - Stream container logs
- `make authdb-shell` - Open psql shell to auth database

**Configuration Variables** (in Makefile):
```makefile
AUTHDB_CONTAINER := postgres-auth-dev
AUTHDB_IMAGE := postgres:16-alpine
AUTHDB_USER := postgres
AUTHDB_PASSWORD := authdbpassword
AUTHDB_NAME := auth_db
AUTHDB_PORT := 5432
AUTHDB_VOLUME := postgres-auth-data
```

**Docker Compose** now only contains application services (FastAPI, Flask, Next.js). Databases run independently via Makefile for better control during development

---

## Setup Instructions

### 1. Generate JWT Secret

```bash
openssl rand -hex 32
```

Copy the output to `.env` as `JWT_SECRET_KEY`.

### 2. Start PostgreSQL

```bash
make authdb-start
```

The database will automatically initialize with schema and seed data on first startup.

### 3. Verify Database

```bash
make authdb-status
```

This will check that PostgreSQL is running and ready. You can also verify the database contents:

```bash
make authdb-init
```

You should see the default admin user exists (username: `admin`, password: `Admin123!`).

### 4. Install Auth Library Dependencies

**FastAPI**:
```bash
cd fastDataApi
pip install -r requirements.txt
```

**Flask**:
```bash
cd flaskDataApi
pip install -r requirements.txt
```

### 5. Start API Services

```bash
# FastAPI
docker compose --profile fastapi up -d

# Or Flask
docker compose --profile flask up -d

# Or both
docker compose --profile both up -d
```

### 6. Test Authentication

**Register a new user**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}'
```

**Login**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}'
```

**Access protected endpoint**:
```bash
TOKEN="<access_token from login response>"
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Admin: List users**:
```bash
# Login as admin first (username: admin, password: Admin123!)
ADMIN_TOKEN="<access_token from admin login>"
curl -X GET http://localhost:8000/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Security Best Practices

### Production Checklist

- [ ] Change JWT_SECRET_KEY to a secure random value
- [ ] Change PostgreSQL password from default
- [ ] Enable HTTPS/TLS for all services
- [ ] Configure CORS to specific origins (remove `allow_origins=["*"]`)
- [ ] Use managed PostgreSQL service (Azure Database, AWS RDS)
- [ ] Implement rate limiting on auth endpoints
- [ ] Add CSRF protection for cookie-based auth
- [ ] Enable PostgreSQL SSL connections
- [ ] Rotate JWT secret periodically
- [ ] Implement account lockout after failed login attempts
- [ ] Add email verification for registration
- [ ] Implement password reset functionality
- [ ] Enable audit logging for admin actions
- [ ] Use Kubernetes secrets for sensitive configuration

### Password Requirements

Current validation in `auth_lib/schemas.py`:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**To strengthen**: Add special character requirement, increase minimum length.

### Token Security

- Access tokens expire in 15 minutes (short-lived)
- Refresh tokens expire in 7 days but are stored in database for revocation
- Refresh token rotation on every refresh (old token revoked, new token issued)
- Logout revokes refresh token immediately

---

## Extending the System

### Adding New Roles

1. Add to enum in `auth_lib/models.py`:
```python
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"  # New role
```

2. Update PostgreSQL enum:
```sql
ALTER TYPE user_role ADD VALUE 'moderator';
```

3. Create role-specific dependencies/decorators as needed.

### Adding Custom Claims to JWT

Edit `auth_lib/jwt_utils.py` in `create_access_token()`:

```python
payload = {
    "sub": user_id,
    "username": username,
    "role": role,
    "custom_claim": "custom_value",  # Add here
    "type": TOKEN_TYPE_ACCESS,
    "exp": expire,
    "iat": datetime.utcnow(),
}
```

### Adding OAuth2 Providers

For future Google/GitHub login:

1. Install `authlib` in requirements.txt
2. Create OAuth2 routes in `auth.py`
3. Link OAuth user ID to local user account
4. Issue same JWT tokens after OAuth authentication

---

## Troubleshooting

### "Token has expired" errors

- Access tokens expire after 15 minutes by design
- Use refresh token to get new access token: `POST /auth/refresh`
- Implement auto-refresh in Next.js client

### "User not found" errors

- Verify PostgreSQL is running: `docker ps | grep postgres`
- Check database connection: `docker logs accessible-postgres-auth`
- Verify environment variable `POSTGRES_AUTH_DB_URL` is correct

### Admin user can't login

- Default credentials: username `admin`, password `Admin123!`
- Verify seed data loaded: `docker exec -it accessible-postgres-auth psql -U postgres -d auth_db -c "SELECT * FROM users;"`
- Re-run seed script if needed

### CORS errors in browser

- Update `fastDataApi/app/main.py` CORS configuration
- Change `allow_origins=["*"]` to specific origin: `allow_origins=["http://localhost:3000"]`
- Ensure `allow_credentials=True` is set

---

## API Reference

### Authentication Endpoints

#### POST /auth/register
Register a new user (role: `user`).

**Request**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### POST /auth/login
Login with username and password.

**Request**:
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### GET /auth/me
Get current user information (requires authentication).

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true
}
```

### Admin Endpoints

#### GET /admin/users
List all users (admin only, paginated).

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters**:
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Max records to return (default: 100)
- `role` (string): Filter by role (`user`, `admin`)
- `is_active` (bool): Filter by active status

**Response** (200 OK):
```json
{
  "users": [
    {
      "id": "...",
      "username": "johndoe",
      "email": "john@example.com",
      "role": "user",
      "is_active": true,
      "created_at": "2025-01-15T10:30:00",
      "updated_at": "2025-01-15T10:30:00"
    }
  ],
  "total": 42
}
```

#### POST /admin/users
Create new user with specified role (admin only).

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters**:
- `role` (string): User role (`user` or `admin`, default: `user`)

**Request**:
```json
{
  "username": "newadmin",
  "email": "admin@example.com",
  "password": "AdminPass123!"
}
```

**Response** (201 Created):
```json
{
  "id": "...",
  "username": "newadmin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "...",
  "updated_at": "..."
}
```

---

## Next Steps

To complete the authentication system, implement the Next.js UI components listed in the "Implementation Tasks Remaining" section. This includes:

1. Auth context for state management
2. Login and registration pages
3. Admin dashboard for user management
4. Route protection middleware
5. Authenticated API client

All backend infrastructure is complete and ready for frontend integration.
