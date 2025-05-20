.PHONY: install dev test lint format clean build docker docker-compose docs

# Default Python executable
PYTHON ?= python3

# Poetry command
POETRY ?= poetry

# Docker compose command
DOCKER_COMPOSE ?= docker-compose

# Default image name for Docker
IMAGE_NAME ?= ollama-client

# Default tag for Docker image
IMAGE_TAG ?= latest

# Install dependencies
install:
	$(POETRY) install

# Install development dependencies
dev:
	$(POETRY) install --with dev

# Run tests
test:
	$(POETRY) run pytest

# Run tests with coverage
coverage:
	$(POETRY) run pytest --cov=ollama_client tests/ --cov-report=term --cov-report=html

# Run linters
lint:
	$(POETRY) run ruff ollama_client
	$(POETRY) run mypy ollama_client

# Format code
format:
	$(POETRY) run black ollama_client
	$(POETRY) run isort ollama_client

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build:
	$(POETRY) build

# Build Docker image
docker:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Run with Docker Compose
docker-compose:
	$(DOCKER_COMPOSE) up -d

# Stop Docker Compose services
docker-compose-down:
	$(DOCKER_COMPOSE) down

# Generate OpenAPI documentation
docs:
	mkdir -p docs
	$(POETRY) run python -m ollama_client.interfaces.rest.openapi docs/openapi.json

# Run shell interface
shell:
	$(POETRY) run python -m ollama_client.interfaces.shell.interactive

# Run REST API server
api:
	$(POETRY) run python -m ollama_client.interfaces.rest.app

# Run MCP adapter
mcp:
	$(POETRY) run python -m ollama_client.interfaces.mcp.adapter

# Run all services locally (not in Docker)
run-all:
	$(POETRY) run python -m ollama_client.interfaces.rest.app & \
	$(POETRY) run python -m ollama_client.interfaces.mcp.adapter & \
	wait

# Generate requirements.txt from poetry
requirements:
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

# Install pre-commit hooks
pre-commit:
	$(POETRY) run pre-commit install

# Help target
help:
	@echo "Available targets:"
	@echo "  install             Install dependencies"
	@echo "  dev                 Install development dependencies"
	@echo "  test                Run tests"
	@echo "  coverage            Run tests with coverage"
	@echo "  lint                Run linters"
	@echo "  format              Format code"
	@echo "  clean               Clean build artifacts"
	@echo "  build               Build package"
	@echo "  docker              Build Docker image"
	@echo "  docker-compose      Run with Docker Compose"
	@echo "  docker-compose-down Stop Docker Compose services"
	@echo "  docs                Generate OpenAPI documentation"
	@echo "  shell               Run shell interface"
	@echo "  api                 Run REST API server"
	@echo "  mcp                 Run MCP adapter"
	@echo "  run-all             Run all services locally"
	@echo "  requirements        Generate requirements.txt from poetry"
	@echo "  pre-commit          Install pre-commit hooks"