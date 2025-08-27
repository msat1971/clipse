from __future__ import annotations

from pathlib import Path
import textwrap
import pytest

from clipse.style_loader import load_style, discover_style_path


_MINIMAL_STYLE_PY = textwrap.dedent(
    """
    STYLE_NAME = "custom-minimal"

    def render(resolved_model, *, package_name: str, engine: str | None = None) -> dict[str, str]:
        # Return bare minimum generated files
        return {
            "generated_cli/adapter.py": "def register(h):\n    pass\n\n"
                                        "def invoke(object_id, action_id, **kwargs):\n    return None\n",
            "generated_cli/app.py": "def main():\n    return 0\n\nif __name__ == '__main__':\n    main()\n",
            "generated_cli/__init__.py": "__all__ = []\n"
        }
    """
)


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
