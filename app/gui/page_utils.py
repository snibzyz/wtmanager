"""Flet Page helpers (session lifecycle-safe)."""

from __future__ import annotations

import flet as ft


def safe_page_update(page: ft.Page) -> None:
    """Call page.update(); swallow error if the Flet session is already gone."""
    try:
        page.update()
    except RuntimeError as e:
        if "destroyed session" in str(e).lower():
            return
        raise
