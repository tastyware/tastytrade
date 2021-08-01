.PHONY: clean venv test

clean:
	find . -name '*.py[co]' -delete

venv:
	python -m venv env
	env/bin/pip install -r requirements.txt

test:
	isort --check --diff tastyworks/ tests/
	flake8 --count --show-source --statistics --ignore=E501 tastyworks/ tests/
	python -m pytest --cov=tastyworks --cov-report=term-missing tests/

install:
	env/bin/pip install -e .
