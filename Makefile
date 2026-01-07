.PHONY: help install install-dev test lint format type-check clean build docs

help:
	@echo "DS-pyVDC-API Development Commands"
	@echo "=================================="
	@echo "install       - Install package in production mode"
	@echo "install-dev   - Install package with development dependencies"
	@echo "test          - Run tests with pytest"
	@echo "test-cov      - Run tests with coverage report"
	@echo "lint          - Run flake8 linter"
	@echo "format        - Format code with black"
	@echo "format-check  - Check code formatting without modifying"
	@echo "type-check    - Run mypy type checker"
	@echo "clean         - Remove build artifacts and cache files"
	@echo "build         - Build distribution packages"
	@echo "docs          - Build documentation"
	@echo "all           - Run format, lint, type-check, and test"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=ds_pyvdc_api --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/

format:
	black src/ tests/ examples/

format-check:
	black --check src/ tests/ examples/

type-check:
	mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docs:
	cd docs && make html

all: format lint type-check test
