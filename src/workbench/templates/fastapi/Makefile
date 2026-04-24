.PHONY: test install clean run

test:
	uv run pytest tests/ -v

install:
	uv pip install -e ".[dev]"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache

run:
	uv run uvicorn {{project_name}}.main:app --reload
