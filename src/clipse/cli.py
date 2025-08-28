"""Command-line interface for clipse.

Provides commands to:
- validate a config against the core schema
- explain the resolved config (JSON or text)
- generate a minimal runnable CLI package scaffold
- list built-in and discovered styles
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from .core import load_config
from .instructions import generate_instructions
from .resolver import resolve_config
from .schema import validate_core_config
from .style_loader import discover_style_path

BUILTIN_STYLES = ["noun-verb", "verb-noun", "unix", "shell"]


def _discover_config_path(explicit: Optional[Path]) -> Path:
    """Resolve the config path using discovery rules.

    Discovery order:
      1) env var `CLIPSE_APP_CONFIG`
      2) explicit `--config`
      3) local file `./.clipse`
      4) local file `./clipse`

    Raises FileNotFoundError if none are found.
    """
    # Discovery order: 1) env CLIPSE_APP_CONFIG 2) --config 3) ./.clipse 4) ./clipse
    env_val = os.getenv("CLIPSE_APP_CONFIG")
    if env_val:
        p = Path(env_val).expanduser()
        if p.exists():
            return p
    if explicit:
        return explicit
    for cand in (Path(".clipse"), Path("clipse")):
        if cand.exists():
            return cand
    raise FileNotFoundError("No config found. Use --config or set CLIPSE_APP_CONFIG or place ./.clipse")


def cmd_validate(config_path: Optional[str]) -> int:
    """Validate the config file against the core schema.

    Prints a success message on validation. Returns 0 on success.
    """
    path = _discover_config_path(Path(config_path) if config_path else None)
    cfg = load_config(path)
    validate_core_config(cfg)
    res = resolve_config(cfg)
    print(f"OK: {path} validates against core schema")
    return 0


def cmd_explain(config_path: Optional[str], fmt: str) -> int:
    """Resolve and print the effective config.

    fmt: "json" or "text". Returns 0 on success.
    """
    path = _discover_config_path(Path(config_path) if config_path else None)
    cfg = load_config(path)
    res = resolve_config(cfg)
    if fmt == "json":
        print(json.dumps(res.resolved, indent=2, sort_keys=True))
    else:
        print(f"Config: {path}\n")
        print(json.dumps(res.resolved, indent=2))
        if res.issues:
            print("\nConstraint issues:")
            for issue in res.issues:
                print(f" - {issue}")
    return 0


def _write_file(p: Path, content: str) -> None:
    """Write text to a file, creating parent directories as needed."""
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def cmd_generate(config_path: Optional[str], out_dir: str, style_file: Optional[str]) -> int:
    """Generate a minimal runnable CLI package scaffold.

    Validates the provided config, creates the output package directory,
    writes `adapter.py`, `app.py`, `__init__.py`, and `py.typed`, and prints
    integration instructions.
    """
    # Load to ensure config is valid; error early if invalid.
    path = _discover_config_path(Path(config_path) if config_path else None)
    cfg = load_config(path)
    validate_core_config(cfg)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Write a minimal runnable package scaffold
    _write_file(
        out / "__init__.py",
        '"""Generated CLI package scaffold.\n\nThis package is produced by clipse\'s \'generate\' command.\n"""\n__all__ = []\n',
    )
    _write_file(out / "py.typed", "")
    _write_file(
        out / "adapter.py",
        '''
from __future__ import annotations
from typing import Any, Callable

"""Adapter layer that forwards object/action invocations to a registered handler.

The generated application calls `invoke(object_id, action_id, **kwargs)` which
delegates to a handler function registered via `register(handler)`.
"""

_HANDLER: Callable[[str, str, dict], Any] | None = None

def register(handler: Callable[[str, str, dict], Any]) -> None:
    """Register a handler callable to process invocations.

    The handler receives `(object_id, action_id, kwargs)` and returns any value
    to be printed by the app (or None).
    """
    global _HANDLER
    _HANDLER = handler


def invoke(object_id: str, action_id: str, **kwargs: Any) -> Any:
    """Invoke the registered handler or raise if none is registered."""
    if _HANDLER is None:
        raise RuntimeError("No handler registered. Call register(handler) first.")
    return _HANDLER(object_id, action_id, kwargs)
'''.lstrip(),
    )
    _write_file(
        out / "app.py",
        '''
from __future__ import annotations
import argparse
from .adapter import invoke

"""Command-line entrypoint for the generated CLI scaffold."""


def main() -> int:
    """Parse arguments and forward to the adapter handler."""
    parser = argparse.ArgumentParser(prog="generated-cli", description="Generated CLI scaffold")
    parser.add_argument("object", help="Object id")
    parser.add_argument("action", help="Action id")
    args = parser.parse_args()

    res = invoke(args.object, args.action)
    if res is not None:
        print(res)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
'''.lstrip(),
    )

    # Emit simple instructions
    style_path = discover_style_path(explicit_path=Path(style_file) if style_file else None)
    print(f"Generated package at {out.resolve()}")
    if style_path:
        print(f"Using style file: {style_path}")
    instr = generate_instructions()
    print("\nIntegration Instructions:")
    print(instr.install_snippet)
    print(instr.entrypoint_snippet)
    print(instr.ci_snippet)
    return 0


def cmd_list_styles() -> int:
    """List built-in styles and any discovered style file path."""
    # Built-ins plus discovered style file path
    print("Built-in styles:")
    for s in BUILTIN_STYLES:
        print(f"  - {s}")
    found = discover_style_path(explicit_path=None)
    if found:
        print(f"Discovered style file: {found}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argparse parser for clipse."""
    p = argparse.ArgumentParser(prog="clipse", description="Clipse generator")
    p.add_argument("--list-styles", action="store_true", dest="list_styles", help="List built-in and discovered styles")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate a config against the core schema")
    v.add_argument("--config", dest="config")

    e = sub.add_parser("explain", help="Explain resolved config (json|text)")
    e.add_argument("--config", dest="config")
    e.add_argument("--format", choices=["json", "text"], default="text")

    g = sub.add_parser("generate", help="Generate a runnable CLI package")
    g.add_argument("--config", dest="config")
    g.add_argument("--out", default="./generated_cli")
    g.add_argument("--style-file", dest="style_file")

    sub.add_parser("list-styles", help="List built-in and discovered styles")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint. Parses args and dispatches to subcommands."""
    parser = build_parser()
    ns = parser.parse_args(argv)

    if getattr(ns, "list_styles", False):
        return cmd_list_styles()

    if ns.cmd == "validate":
        return cmd_validate(ns.config)
    if ns.cmd == "explain":
        return cmd_explain(ns.config, ns.format)
    if ns.cmd == "generate":
        return cmd_generate(ns.config, ns.out, ns.style_file)
    if ns.cmd == "list-styles":
        return cmd_list_styles()
    parser.error("unknown command")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
