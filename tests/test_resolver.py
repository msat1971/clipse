from __future__ import annotations

from pathlib import Path

from dclipse.core import load_config
from dclipse.resolver import resolve_config


def test_resolve_example_config() -> None:
    path = Path(__file__).parent.parent / "examples" / "example_config.json"
    cfg = load_config(path)
    res = resolve_config(cfg)
    assert isinstance(res.resolved, dict)
    # ensure refs and vars (if present) render without raising
    assert isinstance(res.issues, list)
