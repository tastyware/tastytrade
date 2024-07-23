.PHONY: venv lint test docs

venv:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .
	.venv/bin/pip install -r docs/requirements.txt

lint:
	.venv/bin/isort --check --diff tastytrade/ tests/
	.venv/bin/flake8 --count --show-source --statistics tastytrade/ tests/
	.venv/bin/mypy -p tastytrade
	.venv/bin/mypy -p tests

test:
	.venv/bin/pytest --cov=tastytrade --cov-report=term-missing tests/ --cov-fail-under=95

docs:
	cd docs; make html
