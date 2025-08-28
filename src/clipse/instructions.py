from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class IntegrationInstructions:
    package_manager: str
    install_snippet: str
    entrypoint_snippet: str
    ci_snippet: str


def detect_project_style(root: Optional[Path] = None) -> str:
    root = root or Path.cwd()
    if (root / "pyproject.toml").exists():
        # Could refine to detect poetry/pdm/hatch by reading tool tables, but keep simple
        return "hatch"
    if (root / "requirements.txt").exists():
        return "pip"
    return "pip"


def generate_instructions(
    project_style: Optional[str] = None, package: str = "generated_cli",
) -> IntegrationInstructions:
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
