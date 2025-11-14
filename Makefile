.PHONY: help build build-fast-data-api build-flask-data-api build-ui tag push clean version \
	db-start db-stop db-status db-init db-clean db-logs db-shell \
	authdb-start authdb-stop authdb-status authdb-init authdb-clean authdb-logs authdb-shell

# Extract version from pyproject.toml
# Try Python 3.11+ tomllib first, fallback to grep
VERSION := $(shell python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || grep '^version =' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

# Docker configuration
REGISTRY := pmcgee
PLATFORM := linux/amd64

# Image names (local build)
FAST_DATA_API_LOCAL := accessible-fast-data-api
FLASK_DATA_API_LOCAL := accessible-flask-data-api
NEXTUI_LOCAL := accessible-nextui

# Image names (registry)
FAST_DATA_API_IMAGE := $(REGISTRY)/$(FAST_DATA_API_LOCAL)
FLASK_DATA_API_IMAGE := $(REGISTRY)/$(FLASK_DATA_API_LOCAL)
NEXTUI_IMAGE := $(REGISTRY)/$(NEXTUI_LOCAL)

# Build contexts
FAST_DATA_API_CONTEXT := ./fastDataApi
FLASK_DATA_API_CONTEXT := ./flaskDataApi
NEXTUI_CONTEXT := ./nextui

# Database configuration (for dev/test)
DB_CONTAINER := sqlserver-dev
DB_IMAGE := mcr.microsoft.com/mssql/server:2022-latest
DB_PASSWORD := YourStrong@Passw0rd
DB_VOLUME := sqlserver-data

# PostgreSQL Auth Database configuration (for dev/test)
AUTHDB_CONTAINER := postgres-auth-dev
AUTHDB_IMAGE := postgres:16-alpine
AUTHDB_USER := postgres
AUTHDB_PASSWORD := authdbpassword
AUTHDB_NAME := auth_db
AUTHDB_PORT := 5432
AUTHDB_VOLUME := postgres-auth-data

help:
	@echo "Accessible Build System"
	@echo "======================="
	@echo ""
	@echo "Version: $(VERSION)"
	@echo "Registry: $(REGISTRY)"
	@echo ""
	@echo "Build targets:"
	@echo "  make build                 - Build all services"
	@echo "  make build-fast-data-api   - Build FastAPI data service"
	@echo "  make build-flask-data-api  - Build Flask data service"
	@echo "  make build-ui              - Build Next.js UI"
	@echo "  make tag                   - Tag images for registry (adds $(REGISTRY)/* prefix)"
	@echo "  make push                  - Push all images to Docker Hub"
	@echo "  make version               - Display current version"
	@echo "  make clean                 - Remove local Docker images"
	@echo ""
	@echo "Database targets (dev/test only):"
	@echo "  make db-start              - Start database container"
	@echo "  make db-stop               - Stop database container"
	@echo "  make db-status             - Check database state (absent/empty/ready)"
	@echo "  make db-init               - Initialize database (create DB, schema, seed data)"
	@echo "  make db-clean              - Stop and remove database container + volume"
	@echo "                             (use FORCE=yes to skip confirmation)"
	@echo "  make db-logs               - View database logs"
	@echo "  make db-shell              - Open sqlcmd shell to database"
	@echo ""
	@echo "Typical workflow:"
	@echo "  1. make db-start && make db-init    (start and initialize database)"
	@echo "  2. docker compose --profile fastapi up -d  (start application services)"
	@echo "  3. make db-status                   (verify database is ready)"
	@echo ""

version:
	@echo "Current version: $(VERSION)"
	@echo "Source: pyproject.toml"

build: build-fast-data-api build-flask-data-api build-ui
	@echo ""
	@echo "✓ All services built successfully"
	@echo ""
	@echo "Images created:"
	@docker images | grep -E "accessible-(fast-data-api|flask-data-api|nextui)" | head -10

build-fast-data-api:
	@echo "Building FastAPI data service..."
	docker build \
		--platform $(PLATFORM) \
		--tag $(FAST_DATA_API_LOCAL):$(VERSION) \
		--tag $(FAST_DATA_API_LOCAL):latest \
		--file $(FAST_DATA_API_CONTEXT)/Dockerfile \
		$(FAST_DATA_API_CONTEXT)
	@echo "✓ Built $(FAST_DATA_API_LOCAL):$(VERSION)"

build-flask-data-api:
	@echo "Building Flask data service..."
	docker build \
		--platform $(PLATFORM) \
		--tag $(FLASK_DATA_API_LOCAL):$(VERSION) \
		--tag $(FLASK_DATA_API_LOCAL):latest \
		--file $(FLASK_DATA_API_CONTEXT)/Dockerfile \
		$(FLASK_DATA_API_CONTEXT)
	@echo "✓ Built $(FLASK_DATA_API_LOCAL):$(VERSION)"

build-ui:
	@echo "Building Next.js UI..."
	docker build \
		--platform $(PLATFORM) \
		--tag $(NEXTUI_LOCAL):$(VERSION) \
		--tag $(NEXTUI_LOCAL):latest \
		--file $(NEXTUI_CONTEXT)/Dockerfile \
		$(NEXTUI_CONTEXT)
	@echo "✓ Built $(NEXTUI_LOCAL):$(VERSION)"

tag:
	@echo "Tagging images for registry..."
	docker tag $(FAST_DATA_API_LOCAL):$(VERSION) $(FAST_DATA_API_IMAGE):$(VERSION)
	docker tag $(FAST_DATA_API_LOCAL):$(VERSION) $(FAST_DATA_API_IMAGE):latest
	docker tag $(FLASK_DATA_API_LOCAL):$(VERSION) $(FLASK_DATA_API_IMAGE):$(VERSION)
	docker tag $(FLASK_DATA_API_LOCAL):$(VERSION) $(FLASK_DATA_API_IMAGE):latest
	docker tag $(NEXTUI_LOCAL):$(VERSION) $(NEXTUI_IMAGE):$(VERSION)
	docker tag $(NEXTUI_LOCAL):$(VERSION) $(NEXTUI_IMAGE):latest
	@echo ""
	@echo "✓ Tagged images:"
	@echo "  $(FAST_DATA_API_IMAGE):$(VERSION)"
	@echo "  $(FAST_DATA_API_IMAGE):latest"
	@echo "  $(FLASK_DATA_API_IMAGE):$(VERSION)"
	@echo "  $(FLASK_DATA_API_IMAGE):latest"
	@echo "  $(NEXTUI_IMAGE):$(VERSION)"
	@echo "  $(NEXTUI_IMAGE):latest"

push:
	@echo "Pushing images to Docker Hub..."
	@echo ""
	@echo "Pushing FastAPI data service..."
	docker push $(FAST_DATA_API_IMAGE):$(VERSION)
	docker push $(FAST_DATA_API_IMAGE):latest
	@echo ""
	@echo "Pushing Flask data service..."
	docker push $(FLASK_DATA_API_IMAGE):$(VERSION)
	docker push $(FLASK_DATA_API_IMAGE):latest
	@echo ""
	@echo "Pushing Next.js UI..."
	docker push $(NEXTUI_IMAGE):$(VERSION)
	docker push $(NEXTUI_IMAGE):latest
	@echo ""
	@echo "✓ All images pushed to Docker Hub"
	@echo ""
	@echo "Published images:"
	@echo "  $(FAST_DATA_API_IMAGE):$(VERSION)"
	@echo "  $(FAST_DATA_API_IMAGE):latest"
	@echo "  $(FLASK_DATA_API_IMAGE):$(VERSION)"
	@echo "  $(FLASK_DATA_API_IMAGE):latest"
	@echo "  $(NEXTUI_IMAGE):$(VERSION)"
	@echo "  $(NEXTUI_IMAGE):latest"

clean:
	@echo "Removing local Docker images..."
	-docker rmi $(FAST_DATA_API_LOCAL):$(VERSION) $(FAST_DATA_API_LOCAL):latest 2>/dev/null || true
	-docker rmi $(FLASK_DATA_API_LOCAL):$(VERSION) $(FLASK_DATA_API_LOCAL):latest 2>/dev/null || true
	-docker rmi $(NEXTUI_LOCAL):$(VERSION) $(NEXTUI_LOCAL):latest 2>/dev/null || true
	-docker rmi $(FAST_DATA_API_IMAGE):$(VERSION) $(FAST_DATA_API_IMAGE):latest 2>/dev/null || true
	-docker rmi $(FLASK_DATA_API_IMAGE):$(VERSION) $(FLASK_DATA_API_IMAGE):latest 2>/dev/null || true
	-docker rmi $(NEXTUI_IMAGE):$(VERSION) $(NEXTUI_IMAGE):latest 2>/dev/null || true
	@echo "✓ Cleanup complete"

# Database Management (Development/Test)
# =======================================

db-start:
	@echo "Starting SQL Server database container..."
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(DB_CONTAINER)$$"; then \
		if docker ps --format '{{.Names}}' | grep -q "^$(DB_CONTAINER)$$"; then \
			echo "✓ Database container '$(DB_CONTAINER)' is already running"; \
		else \
			echo "Starting existing container '$(DB_CONTAINER)'..."; \
			docker start $(DB_CONTAINER); \
			echo "✓ Database container started"; \
		fi \
	else \
		echo "Creating new database container '$(DB_CONTAINER)'..."; \
		docker run -d \
			--name $(DB_CONTAINER) \
			-p 1433:1433 \
			-e ACCEPT_EULA=Y \
			-e MSSQL_SA_PASSWORD=$(DB_PASSWORD) \
			-e MSSQL_PID=Developer \
			-v $(DB_VOLUME):/var/opt/mssql \
			-v $$(pwd)/sql:/docker-entrypoint-initdb.d \
			$(DB_IMAGE); \
		echo "✓ Database container created and started"; \
		echo "  Waiting for SQL Server to be ready..."; \
		sleep 10; \
	fi
	@echo ""
	@echo "Database is starting up. Run 'make db-status' to check when ready."

db-stop:
	@echo "Stopping database container..."
	@if docker ps --format '{{.Names}}' | grep -q "^$(DB_CONTAINER)$$"; then \
		docker stop $(DB_CONTAINER); \
		echo "✓ Database container stopped"; \
	else \
		echo "✓ Database container is not running"; \
	fi

db-status:
	@./db-ready.sh

db-init:
	@echo "Initializing database..."
	@echo ""
	@echo "Step 1: Creating starsongs database..."
	@docker exec $(DB_CONTAINER) /opt/mssql-tools18/bin/sqlcmd \
		-S localhost -U sa -P "$(DB_PASSWORD)" -C \
		-i /docker-entrypoint-initdb.d/init_db.sql
	@echo "✓ Database created"
	@echo ""
	@echo "Step 2: Creating schema (tables, indexes)..."
	@docker exec $(DB_CONTAINER) /opt/mssql-tools18/bin/sqlcmd \
		-S localhost -U sa -P "$(DB_PASSWORD)" -C -d starsongs \
		-i /docker-entrypoint-initdb.d/schema.sql
	@echo "✓ Schema created"
	@echo ""
	@echo "Step 3: Loading seed data..."
	@docker exec $(DB_CONTAINER) /opt/mssql-tools18/bin/sqlcmd \
		-S localhost -U sa -P "$(DB_PASSWORD)" -C -d starsongs \
		-i /docker-entrypoint-initdb.d/seed_data.sql
	@echo "✓ Seed data loaded"
	@echo ""
	@echo "✅ Database initialization complete!"
	@echo ""
	@./db-ready.sh

db-clean:
	@if [ "$(FORCE)" != "yes" ] && [ "$(FORCE)" != "y" ] && [ "$(FORCE)" != "1" ]; then \
		echo "⚠️  This will DESTROY the database container and all data!"; \
		echo "Press Ctrl+C to cancel, or Enter to continue..."; \
		read confirm; \
	fi
	@echo "Stopping and removing database container..."
	-docker stop $(DB_CONTAINER) 2>/dev/null || true
	-docker rm $(DB_CONTAINER) 2>/dev/null || true
	@echo "Waiting for container to be removed..."
	@while docker ps -a --format '{{.Names}}' | grep -q "^$(DB_CONTAINER)$$"; do \
		sleep 0.5; \
	done
	@echo "Removing database volume..."
	-docker volume rm $(DB_VOLUME) 2>/dev/null || true
	@echo "✓ Database container and volume removed"

db-logs:
	@docker logs -f $(DB_CONTAINER)

db-shell:
	@echo "Opening sqlcmd shell to database..."
	@echo "Tip: Run 'SELECT name FROM sys.databases;' to list databases"
	@echo ""
	@docker exec -it $(DB_CONTAINER) /opt/mssql-tools18/bin/sqlcmd \
		-S localhost -U sa -P "$(DB_PASSWORD)" -C

#===============================================================================
# PostgreSQL Auth Database Targets
#===============================================================================

authdb-start:
	@echo "Starting PostgreSQL auth database container..."
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(AUTHDB_CONTAINER)$$"; then \
		if docker ps --format '{{.Names}}' | grep -q "^$(AUTHDB_CONTAINER)$$"; then \
			echo "✓ PostgreSQL container already running"; \
		else \
			echo "Starting existing PostgreSQL container..."; \
			docker start $(AUTHDB_CONTAINER); \
			echo "Waiting for PostgreSQL to be ready..."; \
			sleep 5; \
			echo "✓ PostgreSQL container started"; \
		fi \
	else \
		echo "Creating new PostgreSQL container..."; \
		docker run -d \
			--name $(AUTHDB_CONTAINER) \
			-p $(AUTHDB_PORT):5432 \
			-e POSTGRES_DB=$(AUTHDB_NAME) \
			-e POSTGRES_USER=$(AUTHDB_USER) \
			-e POSTGRES_PASSWORD=$(AUTHDB_PASSWORD) \
			-v $(AUTHDB_VOLUME):/var/lib/postgresql/data \
			-v $$(pwd)/sql/auth_schema.sql:/docker-entrypoint-initdb.d/01-schema.sql \
			-v $$(pwd)/sql/auth_seed.sql:/docker-entrypoint-initdb.d/02-seed.sql \
			$(AUTHDB_IMAGE); \
		echo "Waiting for PostgreSQL to initialize..."; \
		sleep 5; \
		echo "✓ PostgreSQL container created and running"; \
	fi

authdb-stop:
	@echo "Stopping PostgreSQL auth database container..."
	@if docker ps --format '{{.Names}}' | grep -q "^$(AUTHDB_CONTAINER)$$"; then \
		docker stop $(AUTHDB_CONTAINER); \
		echo "✓ PostgreSQL container stopped"; \
	else \
		echo "PostgreSQL container is not running"; \
	fi

authdb-status:
	@echo "Checking PostgreSQL auth database status..."
	@if ! docker ps -a --format '{{.Names}}' | grep -q "^$(AUTHDB_CONTAINER)$$"; then \
		echo "❌ PostgreSQL container does not exist"; \
		echo "Run 'make authdb-start' to create it"; \
		exit 2; \
	elif ! docker ps --format '{{.Names}}' | grep -q "^$(AUTHDB_CONTAINER)$$"; then \
		echo "❌ PostgreSQL container exists but is not running"; \
		echo "Run 'make authdb-start' to start it"; \
		exit 1; \
	else \
		echo "Checking PostgreSQL readiness..."; \
		if docker exec $(AUTHDB_CONTAINER) pg_isready -U $(AUTHDB_USER) > /dev/null 2>&1; then \
			echo "✓ PostgreSQL is ready and accepting connections"; \
			echo ""; \
			echo "Connection info:"; \
			echo "  Host: localhost"; \
			echo "  Port: $(AUTHDB_PORT)"; \
			echo "  Database: $(AUTHDB_NAME)"; \
			echo "  User: $(AUTHDB_USER)"; \
		else \
			echo "⚠ PostgreSQL container is running but not ready yet"; \
			echo "Wait a few seconds and try again"; \
			exit 1; \
		fi \
	fi

authdb-init:
	@echo "Checking PostgreSQL auth database initialization..."
	@if ! docker ps --format '{{.Names}}' | grep -q "^$(AUTHDB_CONTAINER)$$"; then \
		echo "❌ PostgreSQL container is not running"; \
		echo "Run 'make authdb-start' first"; \
		exit 1; \
	fi
	@echo "Verifying database and tables..."
	@docker exec $(AUTHDB_CONTAINER) psql -U $(AUTHDB_USER) -d $(AUTHDB_NAME) -c "\dt" | grep users > /dev/null 2>&1 && \
		echo "✓ users table exists" || echo "❌ users table not found"
	@docker exec $(AUTHDB_CONTAINER) psql -U $(AUTHDB_USER) -d $(AUTHDB_NAME) -c "\dt" | grep refresh_tokens > /dev/null 2>&1 && \
		echo "✓ refresh_tokens table exists" || echo "❌ refresh_tokens table not found"
	@echo ""
	@echo "User count:"
	@docker exec $(AUTHDB_CONTAINER) psql -U $(AUTHDB_USER) -d $(AUTHDB_NAME) -t -c "SELECT COUNT(*) || ' users' FROM users;"
	@echo ""
	@echo "✓ PostgreSQL auth database is initialized"

authdb-clean:
	@echo "⚠️  WARNING: This will DELETE the PostgreSQL auth database container and ALL DATA"
	@echo "This includes all user accounts and authentication data"
	@echo ""
ifndef FORCE
	@echo "To confirm, run: make authdb-clean FORCE=yes"
	@exit 1
endif
	@echo "Stopping PostgreSQL container..."
	-docker stop $(AUTHDB_CONTAINER) 2>/dev/null || true
	@echo "Removing PostgreSQL container..."
	-docker rm $(AUTHDB_CONTAINER) 2>/dev/null || true
	@echo "Waiting for container removal..."
	@while docker ps -a --format '{{.Names}}' | grep -q "^$(AUTHDB_CONTAINER)$$"; do \
		sleep 0.5; \
	done
	@echo "Removing PostgreSQL volume..."
	-docker volume rm $(AUTHDB_VOLUME) 2>/dev/null || true
	@echo "✓ PostgreSQL container and volume removed"

authdb-logs:
	@docker logs -f $(AUTHDB_CONTAINER)

authdb-shell:
	@echo "Opening psql shell to auth database..."
	@echo "Tip: Run '\dt' to list tables, '\du' to list users"
	@echo ""
	@docker exec -it $(AUTHDB_CONTAINER) psql -U $(AUTHDB_USER) -d $(AUTHDB_NAME)
