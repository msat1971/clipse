from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing-only import
    from pathlib import Path

from dclipse.core import load_config


def test_load_config_json_and_yaml(tmp_path: Path) -> None:
    # JSON
    jpath = tmp_path / "conf.json"
    jpath.write_text('{"name": "demo", "version": "1.0"}', encoding="utf-8")
    cfg = load_config(jpath)
    assert isinstance(cfg, dict)
    assert cfg["name"] == "demo"

    # YAML
    ypath = tmp_path / "conf.yaml"
    ypath.write_text(
        """
name: demo
version: "1.0"
""".lstrip(),
        encoding="utf-8",
    )
    cfg2 = load_config(ypath)
    assert isinstance(cfg2, dict)
    assert cfg2["version"] == "1.0"
