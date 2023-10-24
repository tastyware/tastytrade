.PHONY: clean venv test install docs

clean:
	find . -name '*.py[co]' -delete

venv:
	python -m venv env
	env/bin/pip install -r requirements.txt

lint:
	isort --check --diff tastytrade/ tests/
	flake8 --count --show-source --statistics tastytrade/ tests/
	mypy -p tastytrade

test:
	python -m pytest --cov=tastytrade --cov-report=term-missing tests/

install:
	env/bin/pip install -e .

docs:
	cd docs; make html
