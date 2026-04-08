"""Workspace path persistence and subfolder scanning."""

from pathlib import Path

from app.config import get_last_workspace_from_config, set_last_workspace_in_config
from app.paths import canonical_dir


def get_last_workspace() -> str:
    """Read the last workspace path from config."""
    return get_last_workspace_from_config()


def set_last_workspace(path: str) -> None:
    """Save workspace path to config."""
    set_last_workspace_in_config(path)


def get_workspace_subfolders(parent_path: str) -> list[tuple[str, str]]:
    """Return all subfolders in workspace as (full_path, name), paths fully resolved."""
    root = canonical_dir(parent_path)
    if not root:
        return []
    parent = Path(root)
    result: list[tuple[str, str]] = []
    for p in parent.iterdir():
        if not p.is_dir():
            continue
        try:
            full = str(p.resolve())
        except (OSError, RuntimeError):
            full = str(p.absolute())
        result.append((full, p.name))
    result.sort(key=lambda x: x[1])
    return result
