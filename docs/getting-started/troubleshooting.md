# Troubleshooting

Common issues and how to resolve them.

## Command not found: `dclipse`

- Ensure your virtual environment is activated.
- On Windows, use `Scripts\\activate`; on Unix/macOS, `. .venv/bin/activate`.
- Verify install: `pip show dclipse` or `pip list | grep dclipse`.

## YAML not supported errors

- Install PyYAML: `pip install PyYAML`
- Or use JSON for configuration and style files.

## Schema validation failures

- Ensure your config conforms to the core schema.
- See schemas at: [Schemas](../schema/index.md)
- Use `dclipse validate --config <path>` and read the error path and message.

## Style file not discovered

- Check discovery order in `src/dclipse/style_loader.py`.
- Pass `--style-file` explicitly or set `DCLIPSE_STYLE_FILE`.
- Place `.dclipse_style.*` at the git repo root.

## Generation produced files but CLI fails to run

- Ensure you added an entry point (`[project.scripts]` or `console_scripts`).
- Confirm Python version compatibility (see README badges).
- Inspect generated `adapter.py` and register your handler correctly.

## Still stuck?

- Open an issue: [https://github.com/msat1971/dclipse/issues](https://github.com/msat1971/dclipse/issues)
- Start a discussion: [https://github.com/msat1971/dclipse/discussions](https://github.com/msat1971/dclipse/discussions)
