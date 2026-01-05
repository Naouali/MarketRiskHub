.PHONY: help install test clean run-dashboard run-example lint format

help:
	@echo "Market Risk Hub - Available Commands"
	@echo "===================================="
	@echo "make install        - Install all dependencies"
	@echo "make test          - Run all tests"
	@echo "make test-coverage - Run tests with coverage report"
	@echo "make run-dashboard - Launch Streamlit dashboard"
	@echo "make run-example   - Run simple example script"
	@echo "make clean         - Remove cache and build files"
	@echo "make lint          - Run linting checks"
	@echo "make format        - Format code with black"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=src/market_risk_hub --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

run-dashboard:
	streamlit run dashboard/app.py

run-example:
	python examples/simple_example.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	rm -rf data/cache/*

lint:
	@echo "Running flake8..."
	@pip install flake8 > /dev/null 2>&1 || true
	@flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__ || echo "Install flake8 for linting: pip install flake8"

format:
	@echo "Formatting with black..."
	@pip install black > /dev/null 2>&1 || true
	@black src/ tests/ examples/ --line-length=100 || echo "Install black for formatting: pip install black"
