
.PHONY: help install-dev lint type test format format-check build clean

.PHONY: help install-dev lint type test format format-check build clean

help:
	@echo "Targets: install-dev lint type test format build clean"

install-dev:
	python -m pip install -U pip
	pip install -e .[dev]

format-check:
	ruff format src tests examples --check

format:
	ruff format src tests examples

lint: format
	ruff check src tests examples

type:
	mypy src/clipse

test:
	pytest

format:
	ruff check --fix .

build:
	python -m build

clean:
	rm -rf dist build .pytest_cache .mypy_cache
