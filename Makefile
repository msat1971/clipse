
.PHONY: help install-dev lint type test format format-check build clean schema-sync schema-check docs-build docs-serve

help:
	@echo "Targets: install-dev lint type test format build clean schema-sync schema-check docs-build docs-serve"

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

# --- Schema sync ---
schema-sync:
	python3 tools/sync_schemas.py

schema-check:
	python3 tools/sync_schemas.py --check

# --- Documentation (MkDocs) ---
docs-build:
	.venv/bin/python -m pip install -U pip >/dev/null 2>&1 || true
	.venv/bin/pip install -q mkdocs-material || pip install -q mkdocs-material
	mkdocs build --strict --clean

docs-serve:
	.venv/bin/python -m pip install -U pip >/dev/null 2>&1 || true
	.venv/bin/pip install -q mkdocs-material || pip install -q mkdocs-material
	mkdocs serve -a 127.0.0.1:8000
