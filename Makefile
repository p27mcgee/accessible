.PHONY: help build build-fast-data-api build-flask-data-api build-ui tag push clean version

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

help:
	@echo "Accessible Build System"
	@echo "======================="
	@echo ""
	@echo "Version: $(VERSION)"
	@echo "Registry: $(REGISTRY)"
	@echo ""
	@echo "Available targets:"
	@echo "  make build                 - Build all services"
	@echo "  make build-fast-data-api   - Build FastAPI data service"
	@echo "  make build-flask-data-api  - Build Flask data service"
	@echo "  make build-ui              - Build Next.js UI"
	@echo "  make tag                   - Tag images for registry (adds $(REGISTRY)/* prefix)"
	@echo "  make push                  - Push all images to Docker Hub"
	@echo "  make version               - Display current version"
	@echo "  make clean                 - Remove local Docker images"
	@echo "  make help                  - Show this help message"
	@echo ""
	@echo "Typical workflow:"
	@echo "  1. Edit pyproject.toml to update version"
	@echo "  2. make build              (builds locally as accessible-*)"
	@echo "  3. make tag                (tags as pmcgee/accessible-*)"
	@echo "  4. make push               (pushes to Docker Hub)"
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
