.PHONY: clean venv test install docs

clean:
	find . -name '*.py[co]' -delete

venv:
	python -m venv env
	env/bin/pip install -r requirements.txt

test:
	isort --check --diff tastytrade/ tests/
	flake8 --count --show-source --statistics --ignore=E501 tastytrade/ tests/
	mypy -p tastytrade
	python -m pytest --cov=tastytrade --cov-report=term-missing tests/

install:
	env/bin/pip install -e .

docs:
	cd docs; make html
