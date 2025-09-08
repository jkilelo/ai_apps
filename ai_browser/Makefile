# Makefile for AI-First Smart Browser
# Usage: make [target]

.PHONY: help install dev test clean lint format stealth container-up container-down

# Variables
PYTHON := python3.11
UV := uv
PROJECT := ai-first-smart-browser

# Default target
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Setup
install: ## Install production dependencies
	$(UV) pip install -r requirements.txt
	playwright install chromium

dev: ## Install development dependencies
	$(UV) pip install -e ".[dev]"
	pre-commit install
	playwright install --with-deps

# Container Management
container-up: ## Start all Podman containers
	podman start falkordb meilisearch
	@echo "Waiting for services to be ready..."
	@sleep 5
	@make container-health

container-down: ## Stop all Podman containers
	podman stop falkordb meilisearch

container-health: ## Check container health
	@echo "FalkorDB:" && redis-cli -p 6379 ping
	@echo "Meilisearch:" && curl -s http://localhost:7700/health | grep -o "available"

deploy-qdrant: ## Deploy Qdrant vector database
	podman run -d --name qdrant -p 6333:6333 -p 6334:6334 -v ./data/qdrant:/qdrant/storage docker.io/qdrant/qdrant:latest

# Testing
test: ## Run all tests
	$(UV) run pytest tests/ -v --cov=src --cov-report=term-missing

test-unit: ## Run unit tests only
	$(UV) run pytest tests/unit/ -v

test-integration: ## Run integration tests
	$(UV) run pytest tests/integration/ -v

test-stealth: ## Run stealth validation tests
	$(UV) run pytest tests/stealth/ -v
	$(UV) run python src/commands/test_stealth.py

test-coverage: ## Generate coverage report
	$(UV) run pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Code Quality
lint: ## Run linting checks
	$(UV) run ruff check src/ tests/

format: ## Format code
	$(UV) run ruff check src/ tests/ --fix
	$(UV) run ruff format src/ tests/

typecheck: ## Run type checking
	$(UV) run mypy src/ --strict

quality: lint typecheck ## Run all quality checks

# Stealth Development
stealth-test: ## Test stealth capabilities
	$(UV) run python src/main.py --test-stealth

stealth-sites: ## Test against detection sites
	@for site in bot.sannysoft.com arh.antoinevastel.com nowsecure.nl; do \
		echo "Testing $$site..."; \
		$(UV) run python src/main.py --task "navigate" --url "https://$$site"; \
	done

# Browser Development
browser-dev: ## Launch browser in development mode
	$(UV) run python src/main.py --headless false --devtools true

browser-session: ## Start persistent browser session
	$(UV) run python src/commands/browser_session.py

# Memory Layer
memory-init: ## Initialize memory stores
	$(UV) run python scripts/initialize_memory_stores.py

memory-clean: ## Clean session memory
	rm -f .claude/memory/session.db
	@echo "Session memory cleared"

# Development
run: ## Run the main application
	$(UV) run python src/main.py

shell: ## Start IPython shell with project context
	$(UV) run ipython -i scripts/shell_context.py

profile: ## Profile application performance
	$(UV) run python -m cProfile -o .claude/profiles/latest.prof src/main.py
	@echo "Profile saved to .claude/profiles/latest.prof"

benchmark: ## Run performance benchmarks
	hyperfine "$(UV) run python src/main.py --benchmark"

# Documentation
docs-serve: ## Serve documentation locally
	mkdocs serve -a localhost:8888

docs-build: ## Build documentation
	mkdocs build

# Cleanup
clean: ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	rm -rf build dist *.egg-info

clean-all: clean ## Clean everything including virtual environment
	rm -rf .venv
	rm -rf data/qdrant data/meilisearch

# Git
commit: quality test ## Run checks before commit
	@echo "All checks passed! Ready to commit."

# Installation shortcuts
uv-install: ## Install UV package manager
	curl -LsSf https://astral.sh/uv/install.sh | sh

podman-install: ## Install Podman (Windows)
	@echo "Download Podman Desktop from: https://podman-desktop.io/"

# Project info
info: ## Show project information
	@echo "Project: $(PROJECT)"
	@echo "Python: $(PYTHON)"
	@echo "Location: $(shell pwd)"
	@echo "Containers: $(shell podman ps --format 'table {{.Names}}' | tail -n +2 | tr '\n' ' ')"

.DEFAULT_GOAL := help