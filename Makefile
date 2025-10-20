.PHONY: install test lint format ci

install:
	python -m pip install -U pip
	pip install -r requirements.txt

test:
	pytest -q

lint:
	ruff check .

format:
	black .

ci: install test
