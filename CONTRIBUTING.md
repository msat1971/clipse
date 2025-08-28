# Contributing

Thank you for contributing to clipse!

## Docstrings & Examples (Policy)

- All public modules, classes, functions, and methods must have docstrings using the Google style.
- Docstrings must include an "Examples" section demonstrating typical usage.
- Tests and examples folders are exempt from docstring requirements.

This policy is enforced via pre-commit (see below) and Ruff pydocstyle.

## Development Workflow

1. Create a virtualenv and install dev deps:
   ```bash
   pip install -e .[dev]
   ```

2. Install pre-commit hooks (runs on each commit):
   ```bash
   pre-commit install
   ```

3. Run formatters, linters, and tests locally:
   ```bash
   ruff check .
   mypy src
   pytest -q
   ```

4. When adding or changing public APIs:
   - Add/update docstrings with Args/Returns/Raises and an Examples section.
   - Update user docs in `docs/` as needed.
   - Add or update unit tests.

## Makefile & CI

See Makefile targets and CI workflow for automation details.
