from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from clipse import cli

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


def test_discover_config_path_env_var(monkeypatch, tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.json"
    cfg.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("CLIPSE_APP_CONFIG", str(cfg))
    p = cli._discover_config_path(None)
    assert p == cfg


def test_discover_config_path_explicit(tmp_path: Path) -> None:
    cfg = tmp_path / "clipse"
    cfg.write_text("{}", encoding="utf-8")
    p = cli._discover_config_path(cfg)
    assert p == cfg


def test_discover_config_path_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("CLIPSE_APP_CONFIG", raising=False)
    cwd = tmp_path / "work"
    cwd.mkdir()
    # ensure no .clipse/clipse exist
    with pytest.raises(FileNotFoundError):
        # change cwd via monkeypatch.chdir
        monkeypatch.chdir(cwd)
        cli._discover_config_path(None)


def test_cmd_explain_text_prints_issues(monkeypatch, tmp_path: Path, capsys) -> None:
    # Build a minimal schema-valid config that will generate constraint issues.
    # Use an object with constraints but no selected keys so at_least_one_of triggers.
    cfg = {
        "global": {"options": {}},
        "behavior": {},
        "objects": {
            "obj": {
                "names": ["obj"],
                "description_short": "d",
                "constraints": {"at_least_one_of": [["x", "y"]]},
                "options": {},
                "positionals": {},
            },
        },
        "actions": {},
    }
    config_path = tmp_path / "example.json"
    config_path.write_text(json.dumps(cfg), encoding="utf-8")

    rc = cli.cmd_explain(str(config_path), fmt="text")
    assert rc == 0
    out = capsys.readouterr().out
    # Should include config path and a 'Constraint issues' section
    assert "Config:" in out
    assert "Constraint issues:" in out


def test_cmd_generate_writes_files_and_uses_style_discovery(tmp_path: Path, monkeypatch, capsys) -> None:
    # Minimal schema-valid config
    cfg = {
        "global": {"options": {}},
        "behavior": {},
        "objects": {},
        "actions": {},
    }
    config_path = tmp_path / "example.json"
    config_path.write_text(json.dumps(cfg), encoding="utf-8")

    # Create a declarative style file in project root for discovery
    style = tmp_path / ".clipse_style.json"
    style_obj = {
        "name": "custom-minimal",
        "version": "1.0.0",
        "command_structure": {"pattern": "unix"},
        "options": {"long_prefix": "--"},
        "positionals": {},
    }
    style.write_text(json.dumps(style_obj), encoding="utf-8")

    out_dir = tmp_path / "generated"

    # Ensure cwd is tmp_path so discover_style_path finds the style file
    monkeypatch.chdir(tmp_path)

    rc = cli.cmd_generate(str(config_path), str(out_dir), None)
    assert rc == 0
    # Files should be created
    assert (out_dir / "__init__.py").exists()
    assert (out_dir / "py.typed").exists()
    assert (out_dir / "adapter.py").exists()
    assert (out_dir / "app.py").exists()

    printed = capsys.readouterr().out
    assert "Generated package at" in printed
    assert "Using style file:" in printed


def test_cmd_list_styles(tmp_path: Path, monkeypatch, capsys) -> None:
    # With no style file present, it should still print built-ins and succeed
    monkeypatch.chdir(tmp_path)
    rc = cli.cmd_list_styles()
    assert rc == 0
    out = capsys.readouterr().out
    for s in cli.BUILTIN_STYLES:
        assert f"- {s}" in out
