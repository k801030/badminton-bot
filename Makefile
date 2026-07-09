VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
BLACK = $(VENV)/bin/black

.PHONY: setup run test clean format lint

setup: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --index-url https://pypi.org/simple -r requirements.txt
	touch $(VENV)/bin/activate

run: setup
	$(PYTHON) app/main.py

run-dev: setup
	ENV=dev $(PYTHON) app/main.py

test: setup
	PYTHONPATH=app $(PYTHON) -m pytest tests

format: setup
	$(BLACK) app tests

lint: setup
	$(BLACK) --check app tests

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
