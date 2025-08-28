# Dclipse JSON Schemas

Authoritative schemas are maintained under `src/dclipse/schema/` and mirrored here for documentation and GitHub Pages.

- Core schema: [`dclipse.schema.1.0.0.json`](./dclipse.schema.1.0.0.json)
- Style schema: [`dclipse_style.schema.1.0.0.json`](./dclipse_style.schema.1.0.0.json)

Usage examples and references:

- Programmatic validation uses the packaged schemas via `importlib.resources` in `src/dclipse/schema.py`.
- Repo-level copies are also in `/schema/` for easy linking from the README and Wiki.

To update these copies, run:

```bash
make schema-sync
```

CI and pre-commit will fail if these files are out of date relative to `src/dclipse/schema/`.
