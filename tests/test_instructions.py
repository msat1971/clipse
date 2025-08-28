from __future__ import annotations

from dclipse.instructions import IntegrationInstructions, detect_project_style, generate_instructions


def test_generate_instructions_defaults() -> None:
    instr = generate_instructions(package="demo_cli")
    assert isinstance(instr, IntegrationInstructions)
    assert "demo_cli" in instr.entrypoint_snippet
    assert instr.install_snippet
    assert instr.ci_snippet


def test_detect_project_style_returns_str() -> None:
    style = detect_project_style()
    assert isinstance(style, str)
