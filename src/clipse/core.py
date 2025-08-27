
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, IO, Union

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


def load_config(source: Union[str, Path, IO[str]]) -> dict[str, Any]:
    """
    Load a Clipse config from a file path or file-like handle.
    Supports JSON; YAML if PyYAML is installed.
    """
    if hasattr(source, "read"):
        text = source.read()  # type: ignore[assignment]
        return _loads_guess(text)
    p = Path(source)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("YAML support requires PyYAML; install it or use JSON.")
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _loads_guess(text: str) -> dict[str, Any]:
    s = text.lstrip()
    if s.startswith("{") or s.startswith("["):
        return json.loads(text)
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return json.loads(text)
