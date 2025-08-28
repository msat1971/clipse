"""Utilities to generate integration instructions for generated CLI packages.

This module detects the host project's packaging style and returns concise
snippets users can paste into their project configuration and CI.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IntegrationInstructions:
    """Container for integration snippets for a generated CLI."""

    package_manager: str
    install_snippet: str
    entrypoint_snippet: str
    ci_snippet: str


def detect_project_style(root: Path | None = None) -> str:
    """Detect the host project's packaging style.

    Args:
        root: Optional path to inspect. Defaults to current working directory.

    Returns:
        A short style identifier, currently "hatch" or "pip".
    """
    root = root or Path.cwd()
    if (root / "pyproject.toml").exists():
        # Could refine to detect poetry/pdm/hatch by reading tool tables, but keep simple
        return "hatch"
    if (root / "requirements.txt").exists():
        return "pip"
    return "pip"


def generate_instructions(
    project_style: str | None = None,
    package: str = "generated_cli",
) -> IntegrationInstructions:
    """Build install, entrypoint, and CI snippets for the given style.

    Args:
        project_style: Optional override for the detected project style.
        package: Name of the generated CLI package.

    Returns:
        An `IntegrationInstructions` instance with the appropriate snippets.

    Examples:
        >>> from clipse.instructions import generate_instructions
        >>> instr = generate_instructions(project_style="hatch", package="my_cli")
        >>> "[project.scripts]" in instr.entrypoint_snippet
        True
    """
    style = project_style or detect_project_style()
    if style == "hatch":
        install = "pip install -e .[dev]"
        entrypoint = f'[project.scripts]\n{package} = "{package}.app:main"'
        ci = "ruff check . && mypy --strict src && pytest -q --cov=src --cov-report=term-missing"
    else:
        install = "pip install -e ."
        entrypoint = f"console_scripts = {package}={package}.app:main"
        ci = "pytest -q"
    return IntegrationInstructions(style, install, entrypoint, ci)
