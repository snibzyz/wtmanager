"""Hub GUI - Single-page horizontal layout. Assembles components."""

import flet as ft

from app.config import load_config
from app.gui.header import build_header
from app.gui.left_panel import build_left_panel
from app.gui.right_panel import build_right_panel
from app.theme import BLACK
from app.workspace import get_last_workspace


def main(page: ft.Page) -> None:
    page.title = "WTManager"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1100
    page.window.height = 720
    page.window.min_width = 900
    page.window.min_height = 600
    page.window.maximized = True
    page.padding = 16
    page.bgcolor = BLACK

    cfg = load_config()

    # Shared state
    parent_path_ref: dict[str, str] = {"value": get_last_workspace()}
    selected_paths_ref: dict[str, set] = {"value": set()}
    story_buttons: dict[str, ft.FilledTonalButton] = {}
    selected_funcs: set[str] = set(cfg.get("selected_functions", []))

    # Pickers + clipboard (Flet 0.80+ ไม่รองรับ page.clipboard = ...)
    dir_picker = ft.FilePicker()
    file_picker = ft.FilePicker()
    clipboard_svc = ft.Clipboard()
    page.services.extend([dir_picker, file_picker, clipboard_svc])

    # Build components
    header = build_header()
    left_panel = build_left_panel(
        page, dir_picker, parent_path_ref, selected_paths_ref, story_buttons
    )
    right_panel = build_right_panel(
        page,
        file_picker,
        selected_funcs,
        parent_path_ref,
        selected_paths_ref,
        clipboard_svc=clipboard_svc,
    )

    # Assemble
    page.add(
        ft.Column(
            [
                header,
                ft.Row(
                    [left_panel, right_panel],
                    spacing=14,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=0,
            expand=True,
        )
    )
