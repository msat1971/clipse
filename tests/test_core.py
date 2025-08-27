
from __future__ import annotations

import json
from pathlib import Path

import clipse
from clipse import core


def test_version_string() -> None:
    assert isinstance(clipse.__version__, str) and len(clipse.__version__) > 0


def test_load_config_json(tmp_path: Path) -> None:
    cfg = {
        "global": {"options": []},
        "behavior": {"io": {"stdout": {"default": "text"}}},
        "objects": [],
        "actions": [],
    }
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    loaded = core.load_config(p)
    assert "objects" in loaded and "actions" in loaded
