# Makefile for Simple Apps v2

.PHONY: help install install-dev install-test clean lint format test test-unit test-integration test-e2e serve build docs pre-commit

# Default target
help:
	@echo "Available commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  install-test     Install test dependencies"
	@echo "  clean            Clean up build artifacts and caches"
	@echo "  lint             Run linting (ruff check)"
	@echo "  format           Format code (ruff format)"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e         Run end-to-end tests only"
	@echo "  serve            Start the API server"
	@echo "  build            Build the package"
	@echo "  docs             Generate documentation"
	@echo "  pre-commit       Install pre-commit hooks"

# Installation targets
install:
	pip install -e .

install-dev: install
	pip install -e ".[dev]"

install-test: install
	pip install -e ".[test]"

install-all: install
	pip install -e ".[all]"

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf test_output/
	rm -rf screenshots/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Code quality
lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

mypy:
	mypy src/

# Testing
test: test-unit

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v -m integration

test-e2e:
	pytest tests/e2e/ -v -m e2e

test-browser:
	pytest -v -m browser

test-llm:
	pytest -v -m llm

test-coverage:
	pytest --cov=simple_apps_v2 --cov-report=html --cov-report=term-missing

# Development
serve:
	python -m simple_apps_v2.cli serve

serve-dev:
	python -m simple_apps_v2.cli serve --reload --log-level debug

# Building
build:
	python -m build

build-wheel:
	python -m build --wheel

# Documentation
docs:
	mkdocs build

docs-serve:
	mkdocs serve

# Pre-commit
pre-commit:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

# Health check
health:
	python -m simple_apps_v2.cli health

# Extract elements (example)
extract-example:
	python -m simple_apps_v2.cli extract https://example.com --output example_elements.json

# Playwright setup
playwright-install:
	playwright install chromium

# Docker (if needed in future)
docker-build:
	docker build -t simple-apps-v2 .

docker-run:
	docker run -p 5175:5175 simple-apps-v2

# Environment setup
setup-env:
	cp .env.example .env
	@echo "Please edit .env file with your API keys"

# All setup
setup: install-all playwright-install pre-commit setup-env
	@echo "Setup complete! Edit .env file with your API keys, then run 'make serve'"