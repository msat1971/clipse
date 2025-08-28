from __future__ import annotations

from typing import TYPE_CHECKING

from clipse.instructions import detect_project_style

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


def test_detect_project_style_defaults_to_pip_when_no_markers(tmp_path: Path) -> None:
    # No pyproject.toml or requirements.txt here
    style = detect_project_style(root=tmp_path)
    assert style == "pip"
