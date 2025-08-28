from __future__ import annotations

import json
from io import StringIO
from typing import TYPE_CHECKING

import pytest

from clipse import core

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


def test_load_config_from_filelike_json() -> None:
    sio = StringIO(json.dumps({"k": 1}))
    cfg = core.load_config(sio)
    assert cfg == {"k": 1}


def test_load_config_yaml_ext_without_yaml(tmp_path: Path, monkeypatch) -> None:
    yml = tmp_path / "c.yaml"
    yml.write_text("a: 1\n", encoding="utf-8")
    monkeypatch.setattr(core, "yaml", None)
    with pytest.raises(RuntimeError):
        core.load_config(yml)


def test_load_config_yaml_ext_with_yaml(tmp_path: Path, monkeypatch) -> None:
    yml = tmp_path / "c.yaml"
    yml.write_text("a: 1\n", encoding="utf-8")

    class DummyYaml:
        @staticmethod
        def safe_load(text: str):
            return {"a": 1}

    monkeypatch.setattr(core, "yaml", DummyYaml)
    cfg = core.load_config(yml)
    assert cfg == {"a": 1}


def test_loads_guess_yaml_branch_with_yaml(monkeypatch) -> None:
    class DummyYaml:
        @staticmethod
        def safe_load(text: str):
            return {"a": 1}

    monkeypatch.setattr(core, "yaml", DummyYaml)
    cfg = core._loads_guess("a: 1\n")
    assert cfg == {"a": 1}


def test_loads_guess_when_yaml_unavailable_raises(monkeypatch) -> None:
    # When yaml is None and input doesn't look like JSON, raise a clear error
    monkeypatch.setattr(core, "yaml", None)
    with pytest.raises(RuntimeError):
        core._loads_guess("a: 1\n")
