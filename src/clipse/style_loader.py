"""Style discovery and loading for clipse.

Supports Python style modules that implement a ``render`` function and
declarative JSON/YAML style files validated against the style schema.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Protocol

if TYPE_CHECKING:  # pragma: no cover - typing-only import
    from types import ModuleType

from .schema import load_and_validate_style_file


class RenderFn(Protocol):
    """Protocol for style render functions."""

    def __call__(
        self,
        resolved_model: Any,
        *,
        package_name: str,
        engine: Optional[str] = None,
    ) -> dict[str, str]:
        """Render files for the resolved model into a mapping of paths->contents."""


@dataclass(frozen=True)
class LoadedStyle:
    """Represents a resolved style, backed by either a Python module or a declarative config."""

    name: str
    source: Path
    is_python_module: bool
    module: Optional[ModuleType]
    config: Optional[dict[str, Any]]

    def render(self) -> RenderFn:
        """Return the ``render`` callable from the loaded Python module.

        Raises:
            RuntimeError: If this style is declarative and not a Python module.
            TypeError: If the module lacks a callable ``render`` symbol.
        """
        if not self.is_python_module:
            raise RuntimeError(
                "Declarative style files declare rules but do not implement 'render'. "
                "The generator must select an engine-appropriate renderer.",
            )
        assert self.module is not None
        fn = getattr(self.module, "render", None)
        if not callable(fn):
            raise TypeError(
                "InvalidStyleModule: "
                f"{self.source} does not export a callable "
                "'render(resolved_model, *, package_name, engine)'.",
            )
        return fn  # type: ignore[return-value]


def _import_py_module(path: Path) -> ModuleType:
    """Import a Python module by file path without adding to sys.path."""
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import style module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _discover_project_root(start: Path) -> Path:
    """Heuristic: git repo root ('.git' folder) or fallback to start."""
    cur = start.resolve()
    for parent in [cur, *cur.parents]:
        if (parent / ".git").exists():
            return parent
    return cur


def discover_style_path(
    *,
    explicit_path: Optional[Path],
    env_var: str = "CLIPSE_STYLE_FILE",
    cwd: Optional[Path] = None,
) -> Optional[Path]:
    """Discover the style file path to use.

    Discovery order:
      1) --style-file (explicit_path)
      2) $CLIPSE_STYLE_FILE
      3) ./.clipse_style{.py,.json,.yaml,.yml} in project root.
    """
    if explicit_path:
        return explicit_path.resolve()

    env_val = os.getenv(env_var)
    if env_val:
        p = Path(env_val).expanduser()
        if p.exists():
            return p.resolve()

    root = _discover_project_root(cwd or Path.cwd())
    for cand in (
        root / ".clipse_style.py",
        root / ".clipse_style.json",
        root / ".clipse_style.yaml",
        root / ".clipse_style.yml",
    ):
        if cand.exists():
            return cand.resolve()

    return None


def load_style(explicit_path: Optional[Path] = None) -> LoadedStyle:
    """Load a style definition from the discovered path.

    Supports:
      - Python module at .py with a callable `render(...)`.
      - JSON/YAML file validated against the style schema.

    Examples:
        >>> from clipse.style_loader import load_style  # doctest: +SKIP
        >>> style = load_style()  # doctest: +SKIP
        >>> style.name  # doctest: +SKIP
        'custom-minimal'
    """
    path = discover_style_path(explicit_path=explicit_path)
    if path is None:
        raise FileNotFoundError(
            "StyleNotFound: no style file found. Provide --style-file, set CLIPSE_STYLE_FILE, "
            "or create ./.clipse_style.(py|json|yaml|yml) in the project root.",
        )

    if path.suffix.lower() == ".py":
        mod = _import_py_module(path)
        # Validate that the module exports a callable render at load time
        fn = getattr(mod, "render", None)
        if not callable(fn):
            raise TypeError(
                "InvalidStyleModule: "
                f"{path} does not export a callable "
                "'render(resolved_model, *, package_name, engine)'.",
            )
        name = getattr(mod, "STYLE_NAME", path.stem)
        return LoadedStyle(name=name, source=path, is_python_module=True, module=mod, config=None)

    # JSON/YAML declarative file
    cfg = load_and_validate_style_file(path)
    name = str(cfg.get("name", path.stem))
    return LoadedStyle(name=name, source=path, is_python_module=False, module=None, config=cfg)
