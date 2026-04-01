"""Header component."""

import flet as ft

from app.theme import PINK_LIGHT, TEXT_MUTED, TEXT_WHITE, pink_gradient_three


def build_header() -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.EMOJI_NATURE, size=28, color=PINK_LIGHT),
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=pink_gradient_three(0.28),
                    ),
                    border_radius=12,
                    padding=10,
                ),
                ft.Text("WTManager", size=22, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                ft.Container(expand=True),
                ft.Text("workspace collector", size=11, color=TEXT_MUTED, italic=True),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(bottom=8),
    )
