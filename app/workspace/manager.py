"""Workspace path persistence and subfolder scanning."""

from pathlib import Path

from app.config import get_last_workspace_from_config, set_last_workspace_in_config


def get_last_workspace() -> str:
    """Read the last workspace path from config."""
    return get_last_workspace_from_config()


def set_last_workspace(path: str) -> None:
    """Save workspace path to config."""
    set_last_workspace_in_config(path)


def get_workspace_subfolders(parent_path: str) -> list[tuple[str, str]]:
    """Return all subfolders in workspace as (full_path, name)."""
    parent = Path(parent_path)
    if not parent.exists() or not parent.is_dir():
        return []
    result = [(str(p), p.name) for p in parent.iterdir() if p.is_dir()]
    result.sort(key=lambda x: x[1])
    return result
