<!-- markdownlint-disable MD013 MD041 MD043  -->
# clipse (Command Line Interface Specification Engine)

[![Build](https://github.com/msat1971/clipse/actions/workflows/ci.yml/badge.svg)](https://github.com/msat1971/clipse/actions/workflows/ci.yml) [![codecov.io](https://codecov.io/github/msat1971/clipse/actions/branch/develop/graphs/badge.svg)](https://app.codecov.io/gh/msat1971/clipse) ![PythonSupport](https://img.shields.io/static/v1?label=python&message=%203.9|%203.10|%203.11|%203.12|%203.13&color=blue?style=flat-square&logo=python)

Clipse is a spec‑first toolkit to design, validate, and generate command‑line interfaces from a single configuration file (JSON or YAML). Describe your CLI once; let clipse validate the spec, resolve constraints, and scaffold a runnable package you can integrate into any project.

• Purpose: define once, generate and integrate anywhere.
• Inputs: a config file conforming to clipse’s core schema.
• Outputs: validated, resolved configuration; optional generated CLI package scaffold; integration snippets.

---

## Helpful links

- Documentation site: [https://msat1971.github.io/clipse/](https://msat1971.github.io/clipse/) (built with MkDocs)
- In-repo docs: [`docs/`](docs/)
- Schemas index: [`docs/schema/index.md`](docs/schema/index.md) and repo copies in [`schema/`](schema/)
- Report an issue: [GitHub Issues](https://github.com/msat1971/clipse/issues)
- Discussions: [GitHub Discussions](https://github.com/msat1971/clipse/discussions)
- Contributing guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Table of contents

- What is clipse and why it’s useful
- Installation
- Quickstart (with example output)
- More documentation

---

## What is clipse and why it’s useful

- Faster iteration: change your CLI by editing a spec; avoid re‑wiring argparse/Click code.
- Consistency: schema‑validated configs catch errors early and promote uniform UX.
- Portability: generate a minimal package scaffold you can plug into any project.
- Clarity: an explicit, versioned spec doubles as documentation for your CLI.

## Installation

Clipse will be published to PyPI once stable. For now you can install from source.

- From PyPI (planned):

  ```bash
  pip install clipse
  ```

- From source (editable):

  ```bash
  git clone https://github.com/msat1971/clipse.git
  cd clipse
  python -m venv .venv && . .venv/bin/activate
  pip install -U pip
  pip install -e '.[dev]'
  ```

## Quickstart (with example output)

1. Create a config describing objects, actions, parameters, and constraints (see `examples/example_config.json`).
2. Validate the config.
3. Explain the resolved config.
4. Generate a runnable CLI package scaffold.

```bash
# Validate (auto-discovers ./.clipse or ./clipse when --config is omitted)
clipse validate --config ./examples/example_config.json

# Explain the resolved configuration (JSON)
clipse explain --config ./examples/example_config.json --format json

# Generate a runnable package scaffold (adapter + app + py.typed)
clipse generate --config ./examples/example_config.json --out ./generated_cli
```

Example (abbreviated) output:

```text
✔ Validated config against core schema
ℹ Resolved configuration written to stdout (format=json)
✔ Generated package at ./generated_cli
  - __init__.py
  - adapter.py
  - app.py
  - py.typed
ℹ Integration hints printed (project scripts / console_scripts, CI examples)
```

The generator writes `__init__.py`, `adapter.py`, `app.py`, and `py.typed`, then prints integration snippets (install, entrypoints, CI examples).

## More documentation

- User Guide (install, configure, troubleshoot, full CLI options): `docs/index.md` and `docs/` site
- Integration (use generated code, exceptions, logging): `docs/integration/index.md`
- Project (codebase structure, generated code docs): `docs/project/index.md`
- Schemas (core + style): `docs/schema/index.md`
