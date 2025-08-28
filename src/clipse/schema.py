"""Schema utilities: locate packaged JSON Schemas and validate configs/styles."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing-only imports
    from importlib.resources.abc import Traversable
    from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional
    yaml = None  # YAML is optional; tests will skip if missing

from jsonschema import Draft202012Validator, ValidationError  # type: ignore[import-untyped]

_SCHEMA_DIR = "schema"
_CORE_SCHEMA_NAME = "clipse.schema.1.0.0.json"
_STYLE_SCHEMA_NAME = "clipse_style.schema.1.0.0.json"


@dataclass(frozen=True)
class SchemaPaths:
    """Holds Traversable handles for packaged core and style schemas."""

    core: Traversable
    style: Traversable


def _resource_path(package: str, rel: str) -> Traversable:
    """Return a resource handle for a packaged resource.

    Uses importlib.resources' Traversable interface, which supports `.open()` and is
    compatible with resources inside wheels/zip files without requiring a real
    filesystem `Path`.
    """
    return resources.files(package).joinpath(rel)


def get_schema_paths() -> SchemaPaths:
    """Locate packaged schema files."""
    pkg = __package__.split(".")[0]  # "clipse"
    core = _resource_path(pkg, f"{_SCHEMA_DIR}/{_CORE_SCHEMA_NAME}")
    style = _resource_path(pkg, f"{_SCHEMA_DIR}/{_STYLE_SCHEMA_NAME}")
    return SchemaPaths(core=core, style=style)


def _load_json(path: Traversable) -> dict[str, Any]:
    """Load a JSON document from a package resource path."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_json_or_yaml(path: Path) -> dict[str, Any]:
    """Load JSON or YAML from a filesystem path, enforcing a mapping at top level.

    Raises:
        RuntimeError: If YAML is requested but PyYAML is not installed.
        ValueError: For unsupported extensions or non-mapping YAML content.
    """
    suffix = path.suffix.lower()
    if suffix in (".json",):
        return _load_json(path)
    if suffix in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("PyYAML is required to load YAML style files. Install 'pyyaml'.")
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise ValueError("YAML style file must decode to a mapping.")
            return data
    raise ValueError(f"Unsupported style file extension: {suffix!r}. Use .json, .yaml, or .yml.")


def _validator(schema_path: Traversable) -> Draft202012Validator:
    """Build a JSON Schema validator for the given packaged schema."""
    schema = _load_json(schema_path)
    return Draft202012Validator(schema)


def validate_core_config(config: dict[str, Any]) -> None:
    """Validate a resolved clipse config against the authoritative core schema."""
    v = _validator(get_schema_paths().core)
    v.validate(config)


def validate_style_config(style_obj: dict[str, Any]) -> None:
    """Validate a declarative style object (JSON/YAML) against the style schema."""
    v = _validator(get_schema_paths().style)
    v.validate(style_obj)


def load_and_validate_style_file(path: Path) -> dict[str, Any]:
    """Load a JSON/YAML style file and validate it.

    Returns the parsed style object if valid, raises jsonschema.ValidationError otherwise.
    """
    obj = _load_json_or_yaml(path)
    try:
        validate_style_config(obj)
    except ValidationError as e:  # reframe with file context
        loc = "/".join(str(p) for p in e.path) or "<root>"
        msg = f"Style schema validation failed at {loc}: {e.message}"
        raise ValidationError(msg) from e
    return obj
