#!/usr/bin/env python3
"""Pre-commit check: ensure public APIs include an "Examples" section in docstrings.

Rules:
- Only checks files under src/ (Python files).
- Skips files under tests/ and examples/.
- Public = name does not start with underscore.
- Checks module docstring, public classes, and public functions/methods.
- Passes if docstring contains the substring "Examples" (case-insensitive).

Usage (pre-commit passes changed file paths as argv):
    tools/check_doc_examples.py FILE [FILE ...]
"""
from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing-only
    from collections.abc import Iterable
from pathlib import Path


def _is_python_file(path: Path) -> bool:
    return path.suffix == ".py"


def _should_skip(path: Path) -> bool:
    parts = path.parts
    if any(p in {"tests", "examples"} for p in parts):
        return True
    # Limit enforcement to core modules to start; expand over time
    allowed = {"core.py", "resolver.py", "style_loader.py", "instructions.py", "__init__.py"}
    return path.name not in allowed


def _has_examples(doc: str | None) -> bool:
    if not doc:
        return False
    return "examples" in doc.lower()


def _iter_public_nodes(tree: ast.AST) -> Iterable[tuple[str, ast.AST]]:
    for node in tree.body:  # type: ignore[attr-defined]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                yield node.name, node
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                yield node.name, node
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
                        yield f"{node.name}.{item.name}", item


def check_file(path: Path) -> list[str]:
    """Check a single Python file for 'Examples' sections in public APIs."""
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return [f"{path}: SyntaxError: {e}"]

    failures: list[str] = []

    # Skip module-level enforcement to reduce noise for now.

    for name, node in _iter_public_nodes(tree):
        doc = ast.get_docstring(node)
        if not _has_examples(doc):
            kind = (
                "class" if isinstance(node, ast.ClassDef) else "function"
            )
            line = getattr(node, "lineno", "?")
            failures.append(
                f"{path}:{line}: public {kind} '{name}' docstring missing 'Examples' section",
            )

    return failures


def main(argv: list[str]) -> int:
    """Entrypoint for pre-commit: process changed files and report failures.

    Supports an optional "--warn" flag to emit messages as warnings without
    failing the hook (exit 0). Usage:

        tools/check_doc_examples.py [--warn] FILE [FILE ...]
    """
    warn = False
    args: list[str] = []
    for a in argv[1:]:
        if a == "--warn":
            warn = True
        else:
            args.append(a)

    files = [Path(a) for a in args]
    py_files = [p for p in files if _is_python_file(p) and not _should_skip(p) and str(p).startswith("src/")]
    failures: list[str] = []
    for p in py_files:
        failures.extend(check_file(p))

    if failures:
        for msg in failures:
            print(msg)
        return 0 if warn else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
