from __future__ import annotations

from pathlib import Path

from clipse.core import load_config
from clipse.schema import validate_core_config


def test_example_config_validates() -> None:
    path = Path(__file__).parent.parent / "examples" / "example_config.json"
    assert path.exists(), "example_config.json should exist"
    cfg = load_config(path)
    # Should not raise
    validate_core_config(cfg)

    # sanity on structure
    assert isinstance(cfg, dict)
    assert "objects" in cfg or "actions" in cfg
