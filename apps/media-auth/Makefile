.PHONY: setup test lint format check install clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .

test:
	.venv/bin/pytest .

lint:
	.venv/bin/ruff check .

format:
	.venv/bin/ruff format .

check: format lint test

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf *.egg-info
