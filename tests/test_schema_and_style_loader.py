from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from clipse import schema, style_loader

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


def test_load_json_or_yaml_unsupported_extension(tmp_path: Path) -> None:
    p = tmp_path / "style.txt"
    p.write_text("whatever", encoding="utf-8")
    with pytest.raises(ValueError):
        schema._load_json_or_yaml(p)  # type: ignore[attr-defined]


def test_load_and_validate_style_file_validation_error_message(tmp_path: Path) -> None:
    # Missing required fields per style schema should trigger a validation error
    bad = tmp_path / ".clipse_style.json"
    bad.write_text(json.dumps({"version": "1.0.0"}), encoding="utf-8")
    with pytest.raises(Exception) as ei:
        schema.load_and_validate_style_file(bad)
    assert "Style schema validation failed" in str(ei.value)


def test_discover_style_path_with_env_and_project_root(tmp_path: Path, monkeypatch) -> None:
    # 1) explicit path has priority
    s1 = tmp_path / "a.json"
    s1.write_text("{}", encoding="utf-8")
    assert style_loader.discover_style_path(explicit_path=s1) == s1.resolve()

    # 2) env var is used when set and exists
    s2 = tmp_path / "b.json"
    s2.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("CLIPSE_STYLE_FILE", str(s2))
    assert style_loader.discover_style_path(explicit_path=None) == s2.resolve()

    # 3) project root discovery via .git and .clipse_style.json
    root = tmp_path / "proj"
    sub = root / "sub"
    sub.mkdir(parents=True)
    (root / ".git").mkdir()
    s3 = root / ".clipse_style.json"
    s3.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("CLIPSE_STYLE_FILE", "")  # unset effect
    found = style_loader.discover_style_path(explicit_path=None, cwd=sub)
    assert found == s3.resolve()


def test_load_style_errors_for_missing_and_invalid_py(tmp_path: Path, monkeypatch) -> None:
    # No style found
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CLIPSE_STYLE_FILE", raising=False)
    with pytest.raises(FileNotFoundError):
        style_loader.load_style()

    # Invalid python style module missing callable render
    py = tmp_path / ".clipse_style.py"
    py.write_text("STYLE_NAME='x'\n# no render here\n", encoding="utf-8")
    with pytest.raises(TypeError):
        style_loader.load_style(explicit_path=py)
