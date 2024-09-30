.PHONY: install lint test docs

install:
	uv sync
	uv pip install -e .

lint:
	uv run ruff check .
	uv run ruff format .
	uv run mypy -p tastytrade
	uv run mypy -p tests

test:
	uv run pytest --cov=tastytrade --cov-report=term-missing tests/ --cov-fail-under=95

docs:
	cd docs; make html
