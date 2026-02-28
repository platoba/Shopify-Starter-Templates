.PHONY: help test lint validate preview-minimal preview-dropship preview-landing docker-up docker-down clean

help:  ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

test:  ## Run all tests
	python -m pytest tests/ -v --tb=short

test-cov:  ## Run tests with coverage
	python -m pytest tests/ --cov=tools --cov-report=term-missing --cov-report=html

lint:  ## Lint Python code
	ruff check tools/ tests/

lint-fix:  ## Auto-fix lint issues
	ruff check --fix tools/ tests/

validate:  ## Validate all HTML templates
	python tools/cli.py validate

list:  ## List available templates
	python tools/cli.py list

preview-minimal:  ## Preview minimal-store (port 8081)
	python tools/cli.py preview minimal-store --port 8081

preview-dropship:  ## Preview dropship-starter (port 8082)
	python tools/cli.py preview dropship-starter --port 8082

preview-landing:  ## Preview landing-product (port 8083)
	python tools/cli.py preview landing-product --port 8083

docker-up:  ## Start all preview servers via Docker
	docker compose up -d

docker-down:  ## Stop Docker services
	docker compose down

docker-test:  ## Run tests in Docker
	docker compose run --rm test

clean:  ## Remove generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
