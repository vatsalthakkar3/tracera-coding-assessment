# Use .PHONY to ensure these targets run even if files with the same name exist.
.PHONY: all test coverage clean

# Default command to run when you just type "make"
all: test

format:
	@echo "----------- Running code formatter -----------"
	uv run ruff format src tests --check
	@echo "----------- Code Formatting Complete -----------"

lint:
	@echo "----------- Running linter -----------"
	uv run ruff check src tests
	@echo "----------- Linting Complete -----------"

test:
	@echo "----------- Running tests -----------"
	uv run pytest tests
	@echo "----------- Unit Test Complete -----------"

coverage:
	@echo "----------- Running tests with coverage -----------"
	uv run pytest --cov=src --cov-report=term --cov-report=html tests
	@echo "----------- Coverage Complete -----------"

clean:
	@echo "----------- Cleaning up -----------"
	rm -rf htmlcov .pytest_cache .mypy_cache __pycache__ */__pycache__
	rm -f .coverage
	@echo "----------- Cleanup Complete -----------"