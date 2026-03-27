.PHONY: help install test run clean lint format check

help:
	@echo "Available targets:"
	@echo "  install  - Install dependencies"
	@echo "  test     - Run unit tests"
	@echo "  run      - Run the currency converter"
	@echo "  lint     - Check code style with flake8"
	@echo "  format   - Format code with black"
	@echo "  check    - Run lint and tests"
	@echo "  clean    - Remove __pycache__ and .pyc files"

install:
	pip install -r ../requirements.txt

test:
	PYTHONPATH=/workspaces/fumiklea python -m unittest discover -s tests

run:
	PYTHONPATH=/workspaces/fumiklea python -m currency_converter.src.main

lint:
	flake8 . tests

format:
	black . tests

check: lint test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete