
.PHONY: help install-dev lint type test format format-check build clean

help:
	@echo "Targets: install-dev lint type test format build clean"

install-dev:
	.venv/bin/python -m pip install -U pip
	.venv/bin/pip install -e '.[dev]'

format-check:
	.venv/bin/python -m ruff format src tests examples --check

format:
	.venv/bin/python -m ruff format src tests examples

lint: format
	.venv/bin/python -m ruff check src tests examples

type:
	.venv/bin/python -m mypy src/clipse

test:
	.venv/bin/python -m pytest -q

build:
	.venv/bin/python -m build

clean:
	rm -rf dist build .pytest_cache .mypy_cache
