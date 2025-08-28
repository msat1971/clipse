from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clipse.style_loader import discover_style_path, load_style

if TYPE_CHECKING:  # pragma: no cover - typing-only import
    from pathlib import Path

_MINIMAL_STYLE_PY = """\
STYLE_NAME = "custom-minimal"

def render(resolved_model, *, package_name: str, engine: str | None = None) -> dict[str, str]:
    # Return bare minimum generated files
    return {
        "generated_cli/adapter.py": '''def register(h):
    pass

def invoke(object_id, action_id, **kwargs):
    return None
''',
        "generated_cli/app.py": '''def main():
    return 0

if __name__ == '__main__':
    main()
''',
        "generated_cli/__init__.py": '''__all__ = []
'''
    }
"""


def test_python_style_module_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = tmp_path / ".clipse_style.py"
    mod.write_text(_MINIMAL_STYLE_PY, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    path = discover_style_path(explicit_path=None, cwd=tmp_path)
    assert path == mod.resolve()

    style = load_style()  # should import python module
    assert style.is_python_module is True
    fn = style.render()
    files = fn(resolved_model={}, package_name="generated_cli", engine=None)
    assert "generated_cli/app.py" in files
    assert "generated_cli/adapter.py" in files


def test_python_style_missing_render(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad = tmp_path / ".clipse_style.py"
    bad.write_text("STYLE_NAME='bad'\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    with pytest.raises(TypeError) as ei:
        _ = load_style()  # importing module without render()
    assert "render" in str(ei.value)
