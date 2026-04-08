"""Normalize paths to absolute form so collectors work the same on every machine."""

from __future__ import annotations

from pathlib import Path


def canonical_dir(path: str | None) -> str:
    """Return resolved absolute path if it exists as a directory, else ''."""
    if not path or not str(path).strip():
        return ""
    p = Path(path).expanduser()
    if not p.is_dir():
        return ""
    try:
        return str(p.resolve())
    except (OSError, RuntimeError):
        return str(p.absolute())


def canonical_file(path: str | None) -> str:
    """Return resolved absolute path if it exists as a file, else ''."""
    if not path or not str(path).strip():
        return ""
    p = Path(path).expanduser()
    if not p.is_file():
        return ""
    try:
        return str(p.resolve())
    except (OSError, RuntimeError):
        return str(p.absolute())
