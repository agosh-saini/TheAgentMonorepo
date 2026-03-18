.PHONY: test lint format check

test:
	pytest .

lint:
	ruff check .

format:
	ruff format .

check: format lint test
