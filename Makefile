
.PHONY: help install-dev lint type test format build clean

help:
	@echo "Targets: install-dev lint type test format build clean"

install-dev:
	python -m pip install -U pip
	pip install -e .[dev]

format-check:
	poetry run ruff format aws_lambda_powertools tests examples --check

format:
	poetry run ruff format aws_lambda_powertools tests examples

lint: format
	poetry run ruff check aws_lambda_powertools tests examples

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
