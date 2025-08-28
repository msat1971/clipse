# Configuring

Configure Dclipse with two inputs:

- Core configuration (JSON or YAML) that describes objects, actions, parameters, and constraints.
- Optional style file (Python or declarative JSON/YAML) to shape CLI UX conventions.

## Core configuration (JSON/YAML)

- Always supported: JSON
- YAML supported when `PyYAML` is installed
- Validated against the core schema: see [Schemas](../schema/index.md)

Minimal JSON example (excerpt):

```json
{
  "objects": {
    "project": {
      "actions": { "init": {}, "status": {} }
    }
  }
}
```

Programmatic load:

```python
from dclipse import load_config
cfg = load_config("./examples/example_config.json")
```

Validate and explain:

```bash
dclipse validate --config ./examples/example_config.json
dclipse explain --config ./examples/example_config.json --format json
```

## Style file (optional)

You can control naming, option prefixes, help layout, etc., via a style.

- Option A: Python style module `.dclipse_style.py` exporting `render(...)`
- Option B: Declarative `.dclipse_style.json|.yaml|.yml` validated against the style schema

Discovery order (see `src/dclipse/style_loader.py`):

1. `--style-file` flag to `dclipse generate`
2. `DCLIPSE_STYLE_FILE` environment variable
3. `.dclipse_style.py` or `.dclipse_style.(json|yaml|yml)` at repo root (git root preferred)

List available styles:

```bash
dclipse list-styles
```

Use a style during generation:

```bash
dclipse generate --config ./examples/example_config.json \
  --out ./generated_cli --style-file ./.dclipse_style.py
```

See schema details at [Schemas](../schema/index.md).
