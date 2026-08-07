.PHONY: all setup run test lint format clean test-coverage

# Setup environment using uv
setup:
	uv venv
	uv pip install -r requirements.txt
	uv pip install pytest pytest-cov mock autopep8 flake8

# Run the application
run:
	PYTHONPATH=src uv run python3 -m dica.core.app

# Run all tests
test:
	uv run pytest tests/ -v

# Run tests with coverage report
test-coverage:
	uv run pytest tests/ --cov=src/dica --cov-report=term-missing

# Lint the codebase
lint:
	uv run flake8 src/ tests/

# Format the codebase
format:
	uv run autopep8 --in-place --recursive src/ tests/

# Clean temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage
