"""Button styles for GUI components."""

import flet as ft

from app.theme import CARD_BORDER, PINK, PINK_LIGHT, TEXT_MUTED, TEXT_WHITE, opacity


def chip_on() -> ft.ButtonStyle:
    return ft.ButtonStyle(
        color=TEXT_WHITE, bgcolor=PINK,
        overlay_color=opacity(PINK_LIGHT, 0.3),
        side=ft.BorderSide(1, PINK),
    )


def chip_off() -> ft.ButtonStyle:
    return ft.ButtonStyle(
        color=TEXT_MUTED, bgcolor=opacity(PINK, 0.10),
        overlay_color=opacity(PINK, 0.2),
        side=ft.BorderSide(1, CARD_BORDER),
    )


def chip_disabled() -> ft.ButtonStyle:
    return ft.ButtonStyle(
        color=opacity(TEXT_MUTED, 0.4), bgcolor=opacity(PINK, 0.04),
        overlay_color=ft.Colors.TRANSPARENT,
        side=ft.BorderSide(1, opacity(CARD_BORDER, 0.4)),
    )


STORY_SELECTED = ft.ButtonStyle(
    color=TEXT_WHITE, bgcolor=PINK,
    overlay_color=opacity(PINK_LIGHT, 0.3),
)

STORY_UNSELECTED = ft.ButtonStyle(
    color=TEXT_MUTED, bgcolor=opacity(PINK, 0.12),
    overlay_color=opacity(PINK, 0.2),
)


def fmt_style(selected: bool) -> ft.ButtonStyle:
    return (
        ft.ButtonStyle(color=TEXT_WHITE, bgcolor=PINK, overlay_color=opacity(PINK_LIGHT, 0.3))
        if selected
        else ft.ButtonStyle(color=TEXT_MUTED, bgcolor=opacity(PINK, 0.15), overlay_color=opacity(PINK, 0.25))
    )
