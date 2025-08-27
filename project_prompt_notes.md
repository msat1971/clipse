# Clipse Generator — Project Prompt (Full Mode)

```yaml
# --- meta ---
project: clipse
language: python
python: "3.13"
mode: full                 # full = (re)generate everything
strict: true               # fail if any gate fails
quality_gates:
  coverage_min: 90         # enforce minimum coverage
  mypy: true               # enforce strict type-checking
  ruff: true               # enforce lint rules
  build_wheel: true        # enforce build step works
output_contract:
  tree: true               # print repo tree
  files: true              # print per-file content
  diff: true               # include unified diff
  commands: true           # include local run commands
assumptions_policy: write_after_execution
persona: senior_python_engineer
```

---

## Section 1 — Generation Instructions (for ChatGPT)

These rules govern **how the assistant generates or updates the repository**.

### Meta Rules
- The project already exists → some code is new, some will be refactored.  
- All tests must pass with `pytest`.  
- Coverage ≥ 90% enforced with `--cov-fail-under=90`.  
- Internal consistency: modules, imports, tests, and docs align exactly.  
- Runnable code only — no placeholders.  
- Reuse repo tooling (`ruff`, `mypy`, `pytest`, `hatch`, `pre-commit`).  
- Package schemas inside the wheel (`clipse.schema.1.0.0.json`, `clipse_style.schema.1.0.0.json`).  

### Output Contract
Always output results in this order:  
1. Concise repo tree of new/changed files.  
2. Full per-file content in fenced code blocks (no placeholders).  
3. Unified diff for changed files.  
4. Commands to run locally (`pip install -e .[dev]`, `pytest`, etc.).  

### Quality Gates
- No failing tests.  
- Coverage ≥ 90%.  
- Linting clean with Ruff.  
- Type-check clean with Mypy.  
- Wheel builds with Hatchling + passes `twine check`.  

### Self-Check Before Returning
- Confirm imports resolve.  
- Confirm CLI help runs.  
- Confirm pre-commit hooks succeed on clean repo.  
- Confirm schemas included in wheel (via `importlib.resources`).  

### Assumptions Log
If forced to decide (e.g. ambiguous env precedence), log the assumption + rationale at the end of output.

### Repository Layout (with comments for generation)

```text
├── .chglog                          # Configuration for changelog generation
│   ├── CHANGELOG.tpl.md             # Template for formatting changelog entries
│   └── config.yml                   # Rules for git-chglog (commit parsing, sections)
├── .flake8                          # Config for flake8 linter (legacy, ruff may replace)
├── .gitattributes                   # Git attributes (line endings, linguist settings, etc.)
├── .github                          # GitHub-specific configuration
│   ├── ISSUE_TEMPLATE               # Issue templates for bug reports and feature requests
│   │   ├── bug_report.md            # Template for reporting bugs
│   │   └── feature_request.md       # Template for requesting features
│   └── workflows
│       └── ci.yml                   # GitHub Actions CI workflow (lint, test, coverage, build)
├── .gitignore                       # Ignore patterns for git
├── .pre-commit-config.yaml          # Pre-commit hooks configuration (linting, formatting, etc.)
├── .pylintrc                        # Config for pylint (style/lint rules)
├── 404.html                         # Custom 404 page (for docs hosting, e.g., GitHub Pages)
├── CHANGELOG.md                     # Project changelog (generated/reviewed with .chglog)
├── CODE_OF_CONDUCT.md               # Contributor code of conduct
├── CONTRIBUTING.md                  # Contribution guidelines for developers
├── docs                             # Project documentation
│   ├── api.md                       # API-level documentation for clipse
│   ├── clipse_config_file_guide.md  # Guide for writing/using `.clipse` config files
│   └── index.md                     # Docs index/landing page
├── examples                         # Example configurations and notebooks
│   ├── example_config.json          # Example `.clipse` configuration (used in tests/demos)
│   └── quickstart.ipynb             # Jupyter notebook demonstrating usage
├── LICENSE                          # License for the project (e.g., MIT/Apache)
├── Makefile                         # Common build/test tasks (setup, lint, test, clean, etc.)
├── mypy.ini                         # mypy type-checker configuration
├── project_prompt_notes.md          # Notes/draft prompt(s) for GPT-5 build instructions
├── pyproject.toml                   # Main build config (dependencies, build system, tools)
├── README.md                        # Project overview, installation, usage instructions
├── resources                        # Auxiliary resources for generation/validation
│   └── standard_types.yaml          # Shared standard type definitions for schema mapping
├── ruff.toml                        # Ruff linter configuration
├── schema                           # JSON Schemas for clipse configs and styles
│   ├── clipse_style.schema.1.0.0.json # Schema for declarative `.clipse_style` files
│   └── clipse.schema.1.0.0.json     # Core schema for `.clipse` config files
├── src                              # Source code
│   └── clipse
│       ├── __init__.py              # Marks `clipse` as a package
│       ├── _version.py              # Version definition for the package
│       ├── core.py                  # Core logic (config resolution, generation entrypoints)
│       ├── py.typed                 # Marker for PEP 561 (package provides type hints)
│       ├── schema.py                # Schema loading/validation for core and style configs
│       └── style_loader.py          # Style discovery and loading (Python module or JSON/YAML)
└── tests                            # Unit and integration tests
    ├── test_style_config_files.py   # Tests for JSON/YAML `.clipse_style` validation and discovery
    ├── test_style_python_module.py  # Tests for Python-module `.clipse_style` (with `render()` fn)
    ├── test_schema.py               # Tests core + style schemas validation (happy/sad paths)
    ├── test_loader.py               # Tests refs, overrides, var/env resolution, constraints
    ├── test_instructions.py         # Tests generation of integration instructions for project styles
    └── test_integration.py          # End-to-end tests: config → generated CLI → run demo action
```

---

## Section 2 — Product Specification (for clipse)

This section defines what the `clipse` CLI must do and how it must behave.

### Mission
Implement the **clipse** generator CLI — a developer-facing tool that:  
- Reads a `.clipse` config file (JSON/YAML).  
- Validates + resolves refs, vars, env, constraints.  
- Generates a runnable CLI package (`generated_cli/`).  
- Supports multiple command styles (noun–verb, verb–noun, unix, shell, custom).  
- Emits integration instructions (deps, entrypoints, CI snippets).  
- Ships with ≥90% tested coverage and schemas packaged.

### Coding Principles
- **Clarity & Reuse** → composable modules.  
- **Consistency** → unified style for logging, errors, typing.  
- **Simplicity** → straightforward logic, avoid clever hacks.  
- **Demo-Oriented** → examples and demo action runnable.  
- **Visual Quality** → clean docs + CLI help.

### Config Discovery
1. `CLIPSE_APP_CONFIG` (env var)  
2. `--config` CLI flag  
3. `./.clipse` at repo root  
4. `./clipse` in cwd  

### Styles
- Built-in: noun-verb, verb-noun, unix, shell.  
- Custom style discovery:  
  1. `--style-file PATH`  
  2. `CLIPSE_STYLE_FILE` env var  
  3. `./.clipse_style.{py,json,yaml,yml}`  

### CLI Commands
- `clipse validate --config <path>`  
- `clipse explain --config <path> [--format json|text]`  
- `clipse generate --config <path> --out ./generated_cli --style ...`  
- `clipse --list-styles`  

### Semantic Rules
- Configs are **maps keyed by id**.  
- `$ref` allowed from `shared_defs`.  
- Vars resolve: local → shared. Cycles reported with chain.  
- Env precedence: CLI > env > default (unless overridden).  
- Constraints: requires, conflicts, exactly_one_of, at_least_one_of.  
- JSON Schema is authoritative.

### Generated Package Layout
- `generated_cli/` must include `__init__.py`, `py.typed`, `app.py`, `adapter.py`, `commands/*.py` (if style requires).  

Adapter API:
```python
def register(handler: Callable[[str, str, dict], Any]) -> None: ...
def invoke(object_id: str, action_id: str, **kwargs) -> Any: ...
```

### Integration Instructions
- Auto-detect project style (pip/Poetry/uv/Hatch/PDM).  
- Emit copy/paste snippets for deps, entrypoints, CI glue.  
- Output to stdout, `README.md` anchor, or `docs/INTEGRATION.md`.

### Error Handling
- Categories: Load, Schema, Merge, Vars, Env, Constraint, Style, Backend, Instructions.  
- Errors print breadcrumb paths.  
- Cycles show full chain.

### Tests
- Loader, schema, style, instructions, integration.  
- Coverage ≥ 90%.  
```bash
pytest -q --cov=src/clipse --cov-report=term-missing --cov-fail-under=90
```

### CI/CD
- Pipeline: Ruff → Mypy → Pytest → Hatch build + `twine check` → Codecov.

### Acceptance Criteria
1. `clipse validate` works on `examples/example_config.json`.  
2. `clipse explain` shows resolved defaults/unions.  
3. `clipse generate` produces runnable package for all built-in styles.  
4. Custom style works.  
5. `--list-styles` shows built-ins + discovered.  
6. Integration instructions emitted correctly.  
7. CI enforces ≥90% coverage.  
8. Wheel includes schemas.  
