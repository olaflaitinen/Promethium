# Promethium Makefile
# 
# Common development and automation tasks for the Promethium framework.
# Run `make help` to see available targets.

.PHONY: help install install-dev install-cli test lint format clean docs run-example benchmark

# Default target
help:
	@echo "Promethium Development Tasks"
	@echo "============================"
	@echo ""
	@echo "Installation:"
	@echo "  make install       Install core package"
	@echo "  make install-dev   Install with development dependencies"
	@echo "  make install-cli   Install with CLI dependencies"
	@echo "  make install-all   Install all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test          Run test suite"
	@echo "  make lint          Run linters (ruff, mypy)"
	@echo "  make format        Format code with black"
	@echo "  make clean         Remove build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          Build documentation"
	@echo ""
	@echo "Examples:"
	@echo "  make run-example   Run a basic example"
	@echo "  make benchmark     Run benchmark suite"
	@echo ""
	@echo "Server:"
	@echo "  make serve         Start API server"
	@echo "  make serve-dev     Start in development mode"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-cli:
	pip install -e ".[cli]"

install-server:
	pip install -e ".[server]"

install-all:
	pip install -e ".[all]"

# Testing
test:
	pytest tests/ -v --cov=promethium --cov-report=term-missing

test-fast:
	pytest tests/ -v --ignore=tests/integration

# Linting and formatting
lint:
	ruff check src/
	mypy src/promethium --ignore-missing-imports

format:
	black src/ tests/ examples/ tools/
	ruff check src/ --fix

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	@echo "Documentation available in docs/"
	@echo "View online: https://github.com/olaflaitinen/Promethium"

# Example runners
run-example:
	python examples/recipes/denoise_shot_gather.py testdata/sample.npy results/output.npy --method wiener --verbose

run-cli-example:
	promethium version
	promethium models
	promethium datasets

# Benchmarking
benchmark:
	python -m benchmarks.run_all configs/batch/classical_vs_ml.yaml

benchmark-quick:
	python -m benchmarks.run_all configs/batch/classical_vs_ml.yaml --output benchmarks/results/

# Server
serve:
	uvicorn promethium.api.main:app --host 0.0.0.0 --port 8000

serve-dev:
	uvicorn promethium.api.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-build:
	docker build -t promethium:latest -f docker/Dockerfile.app .

docker-run:
	docker-compose -f docker/docker-compose.yml up

# Package building
build:
	python -m build

publish-test:
	twine upload --repository testpypi dist/*

publish:
	twine upload dist/*

# Development helpers
experiment-list:
	promethium experiments list

datasets-list:
	promethium datasets list
