.PHONY: clean venv test install docs

clean:
	find . -name '*.py[co]' -delete

venv:
	python -m venv env
	env/bin/pip install -r requirements.txt

test:
	isort --check --diff tastytrade/
	flake8 --count --show-source --statistics tastytrade/
	mypy -p tastytrade

install:
	env/bin/pip install -e .

docs:
	cd docs; make html
