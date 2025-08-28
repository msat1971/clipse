"""Core utilities for loading Clipse configuration files (JSON/YAML).

Examples:
    Load from a file path:

    >>> from clipse.core import load_config
    >>> cfg = load_config("./clipse")
    >>> isinstance(cfg, dict)
    True
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import IO, Any, Union

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


def load_config(source: Union[str, Path, IO[str]]) -> dict[str, Any]:
    """Load a Clipse config from a file path or file-like handle.

    Supports JSON; YAML if PyYAML is installed.

    Examples:
        From a file path:

        >>> from clipse.core import load_config
        >>> cfg = load_config("./examples/example_config.json")  # doctest: +SKIP
        >>> isinstance(cfg, dict)
        True
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
    """Decode ``text`` as JSON if it looks like JSON; otherwise YAML if available.

    Raises a clear error if YAML is not available and the input does not look like JSON.
    """
    s = text.lstrip()
    if s.startswith("{") or s.startswith("["):
        return json.loads(text)
    if yaml is None:
        raise RuntimeError(
            "YAML support requires PyYAML; install it or provide JSON input.",
        )
    return yaml.safe_load(text) or {}
