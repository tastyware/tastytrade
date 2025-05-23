.PHONY: install lint test docs

install:
	uv sync

lint:
	uv run ruff check --select I --fix
	uv run ruff format tastytrade/ tests/
	uv run ruff check tastytrade/ tests/
	uv run pyright tastytrade/ tests/
	uv run mypy tastytrade/

test:
	uv run pytest --cov=tastytrade --cov-report=term-missing tests/ --cov-fail-under=95

docs:
	uv run -m sphinx -T -b html -d docs/_build/doctrees -D language=en docs/ docs/_build/
