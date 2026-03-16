.PHONY: app app-build app-down app-restart test clean typecheck

app:
	docker compose up -d

app-build:
	docker compose build

app-restart:
	docker compose down && docker compose up -d

app-down:
	docker compose down

test:
	poetry run pytest -v

clean:
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf pytest-results.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

typecheck:
	poetry run mypy src
