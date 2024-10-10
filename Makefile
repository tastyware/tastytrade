.PHONY: install lint test docs

install:
	uv sync

lint:
	uv run ruff format tastytrade/ tests/
	uv run ruff check tastytrade/ tests/
	uv run pyright tastytrade/ tests/

test:
	uv run pytest --cov=tastytrade --cov-report=term-missing tests/ --cov-fail-under=95

docs:
	cd docs; uv pip install -r requirements.txt; make html
