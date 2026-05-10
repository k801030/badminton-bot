VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

.PHONY: setup run test clean

setup: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --index-url https://pypi.org/simple -r requirements.txt
	touch $(VENV)/bin/activate

run: setup
	$(PYTHON) app/main.py

test: setup
	$(PYTHON) -m pytest tests

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
