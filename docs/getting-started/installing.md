# Installing

Dclipse will be published to PyPI once stable. Until then, install from source.

## Option A: PyPI (planned)

```bash
pip install dclipse
```

## Option B: From source (editable)

```bash
git clone https://github.com/msat1971/dclipse.git
cd dclipse
python -m venv .venv && . .venv/bin/activate
pip install -U pip
pip install -e '.[dev]'
```

## Verify installation

```bash
dclipse --help
```

If the command is not found, ensure your virtualenv is activated or your PATH includes the environment's bin directory.
