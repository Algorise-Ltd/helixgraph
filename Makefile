.PHONY: setup lint format check

setup:
	python -m venv .venv
	.venv\Scripts\activate
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

lint:
	pre-commit run --all-files

format:
	black .

check:
	black --check .
