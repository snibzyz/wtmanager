"""Left panel: Workspace selector + Story grid."""

import flet as ft

from app.gui.styles import STORY_SELECTED, STORY_UNSELECTED
from app.theme import CARD_BG, CARD_BORDER, PINK, PINK_SOFT, TEXT_MUTED, TEXT_WHITE, opacity
from app.workspace import get_last_workspace, get_workspace_subfolders, set_last_workspace


def build_left_panel(
    page: ft.Page,
    dir_picker: ft.FilePicker,
    parent_path_ref: dict,
    selected_paths_ref: dict,
    story_buttons: dict,
) -> ft.Container:

    stories_wrap = ft.Row(wrap=True, spacing=8, run_spacing=8)

    parent_label = ft.Text(
        parent_path_ref["value"] or "ยังไม่ได้เลือก",
        size=13,
        color=TEXT_WHITE if parent_path_ref["value"] else TEXT_MUTED,
        overflow=ft.TextOverflow.ELLIPSIS,
        max_lines=1,
        expand=True,
    )

    def _update_story_styles() -> None:
        sel = selected_paths_ref["value"]
        for path, btn in story_buttons.items():
            btn.style = STORY_SELECTED if path in sel else STORY_UNSELECTED

    def _apply_folder(path: str) -> None:
        if not path:
            return
        parent_path_ref["value"] = path
        set_last_workspace(path)
        parent_label.value = path
        parent_label.color = TEXT_WHITE

        stories = get_workspace_subfolders(path)
        story_buttons.clear()
        selected_paths_ref["value"] = set()
        stories_wrap.controls.clear()

        if not stories:
            stories_wrap.controls.append(
                ft.Text("ไม่พบ subfolder", size=12, color=TEXT_MUTED)
            )
        else:
            for full_path, name in stories:
                btn = ft.FilledTonalButton(
                    content=ft.Text(name, size=12, overflow=ft.TextOverflow.ELLIPSIS),
                    style=STORY_UNSELECTED,
                    height=40,
                    width=130,
                )

                def make_click(fp: str):
                    def click(e: ft.ControlEvent) -> None:
                        if fp in selected_paths_ref["value"]:
                            selected_paths_ref["value"].discard(fp)
                        else:
                            selected_paths_ref["value"].add(fp)
                        _update_story_styles()
                        page.update()
                    return click

                btn.on_click = make_click(full_path)
                story_buttons[full_path] = btn
                stories_wrap.controls.append(btn)
        page.update()

    last = get_last_workspace()
    if last:
        _apply_folder(last)
    else:
        stories_wrap.controls.append(
            ft.Text("เลือกโฟลเดอร์ workspace ก่อน", size=12, color=TEXT_MUTED)
        )

    async def on_folder_click(e: ft.ControlEvent) -> None:
        path = await dir_picker.get_directory_path(dialog_title="เลือกโฟลเดอร์ workspace")
        if path:
            _apply_folder(path)

    def select_all(e: ft.ControlEvent) -> None:
        selected_paths_ref["value"] = set(story_buttons.keys())
        _update_story_styles()
        page.update()

    def clear_all(e: ft.ControlEvent) -> None:
        selected_paths_ref["value"] = set()
        _update_story_styles()
        page.update()

    workspace_row = ft.Row(
        [
            ft.Icon(ft.Icons.FOLDER_OPEN, color=TEXT_MUTED, size=18),
            parent_label,
            ft.IconButton(
                ft.Icons.FOLDER_OPEN, icon_color=PINK, icon_size=20,
                tooltip="เลือก workspace",
                style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=6),
                on_click=on_folder_click,
            ),
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    story_actions = ft.Row(
        [
            ft.TextButton(
                "เลือกทั้งหมด", icon=ft.Icons.CHECK_BOX, icon_color=PINK,
                style=ft.ButtonStyle(color=PINK, padding=ft.padding.symmetric(horizontal=8)),
                on_click=select_all,
            ),
            ft.TextButton(
                "ล้าง", icon=ft.Icons.CHECK_BOX_OUTLINE_BLANK, icon_color=TEXT_MUTED,
                style=ft.ButtonStyle(color=TEXT_MUTED, padding=ft.padding.symmetric(horizontal=8)),
                on_click=clear_all,
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=4,
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Container(content=ft.Icon(ft.Icons.FOLDER, color=PINK, size=18),
                                             bgcolor=opacity(PINK_SOFT, 0.2), border_radius=6, padding=6),
                                ft.Text("Workspace", size=14, weight=ft.FontWeight.W_600, color=TEXT_WHITE),
                            ], spacing=10),
                            ft.Divider(height=1, color=CARD_BORDER),
                            workspace_row,
                        ],
                        spacing=8,
                    ),
                    padding=14, border_radius=14, bgcolor=CARD_BG,
                    border=ft.border.all(1, CARD_BORDER),
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Container(content=ft.Icon(ft.Icons.LIBRARY_BOOKS, color=PINK, size=18),
                                             bgcolor=opacity(PINK_SOFT, 0.2), border_radius=6, padding=6),
                                ft.Text("เรื่อง", size=14, weight=ft.FontWeight.W_600, color=TEXT_WHITE),
                            ], spacing=10),
                            ft.Divider(height=1, color=CARD_BORDER),
                            story_actions,
                            ft.Container(
                                content=ft.Column([stories_wrap], scroll=ft.ScrollMode.AUTO),
                                expand=True,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=14, border_radius=14, bgcolor=CARD_BG,
                    border=ft.border.all(1, CARD_BORDER), expand=True,
                ),
            ],
            spacing=0, expand=True,
        ),
        expand=2,
    )
