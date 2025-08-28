#!/usr/bin/env python3
"""Sync packaged schemas from src/clipse/schema/ to repo-level locations.

- Source of truth: src/clipse/schema/*.json
- Destinations:    schema/*.json and docs/schema/*.json

Usage:
  python tools/sync_schemas.py [--check]

When --check is provided, the script exits with non-zero status if any destination
would change (no files are written). This is suitable for CI or pre-commit.
"""
from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src" / "clipse" / "schema"
DEST_REPO = ROOT / "schema"
DEST_DOCS = ROOT / "docs" / "schema"


def copy_if_different(src: Path, dest: Path, *, check: bool) -> bool:
    """Copy file if contents differ.

    Args:
        src: Source file path.
        dest: Destination file path.
        check: If True, do not write; only report whether a change would occur.

    Returns:
        True if a change occurred (or would occur in check mode); False otherwise.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and filecmp.cmp(src, dest, shallow=False):
        return False  # no change
    if check:
        return True  # would change
    shutil.copy2(src, dest)
    return True


def main(argv: list[str]) -> int:
    """Entry point for schema sync utility.

    Supports a "--check" flag to verify that destination copies are up to date
    without modifying files, returning non-zero when they are not.
    """
    check = "--check" in argv
    changed = False

    for src in SRC_DIR.glob("*.json"):
        for dest_dir in (DEST_REPO, DEST_DOCS):
            dest = dest_dir / src.name
            if copy_if_different(src, dest, check=check):
                changed = True

    if check and changed:
        print("Schema sync check failed: destinations are out of date.")
        print(f"Run: python {Path(__file__).name} to update copies.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
