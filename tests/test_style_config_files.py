from __future__ import annotations

import json
from pathlib import Path

import pytest

from clipse.schema import load_and_validate_style_file
from clipse.style_loader import discover_style_path, load_style


_MINIMAL_JSON = {
    "name": "posix-unix",
    "version": "1.0.0",
    "command_structure": {"pattern": "unix"},
    "options": {"long_prefix": "--"},
    "positionals": {}
}

_MINIMAL_YAML = """
name: aws-cli-like
version: 1.0.0
command_structure:
  pattern: verb-noun
options:
  long_prefix: "--"
positionals: {}
"""


def test_validate_json_style_ok(tmp_path: Path) -> None:
    p = tmp_path / ".clipse_style.json"
    p.write_text(json.dumps(_MINIMAL_JSON), encoding="utf-8")
    obj = load_and_validate_style_file(p)
    assert obj["name"] == "posix-unix"
    assert obj["command_structure"]["pattern"] == "unix"


def test_validate_yaml_style_ok(tmp_path: Path) -> None:
    p = tmp_path / ".clipse_style.yaml"
    p.write_text(_MINIMAL_YAML, encoding="utf-8")
    obj = load_and_validate_style_file(p)
    assert obj["name"] == "aws-cli-like"
    assert obj["command_structure"]["pattern"] == "verb-noun"


def test_style_discovery_precedence_env_over_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    # project-level style
    (project / ".clipse_style.json").write_text(json.dumps(_MINIMAL_JSON), encoding="utf-8")
    # env points elsewhere
    elsewhere = tmp_path / "custom.yaml"
    elsewhere.write_text(_MINIMAL_YAML, encoding="utf-8")
    monkeypatch.setenv("CLIPSE_STYLE_FILE", str(elsewhere))

    # ensure discovery returns env path
    found = discover_style_path(explicit_path=None, cwd=project)
    assert found == elsewhere.resolve()

    # load resolves to YAML config style
    style = load_style(explicit_path=None)
    assert style.is_python_module is False
    assert style.config and style.config["name"] == "aws-cli-like"


def test_style_validation_error(tmp_path: Path) -> None:
    bad = tmp_path / ".clipse_style.json"
    bad.write_text(json.dumps({"name": "oops"}), encoding="utf-8")  # missing required sections
    with pytest.raises(Exception):
        load_and_validate_style_file(bad)
