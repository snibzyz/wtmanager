"""Theme widgets - opacity helper, gradients, section_card."""

import flet as ft

from app.theme.colors import CARD_BG, CARD_BORDER, PINK, PINK_DARK, PINK_LIGHT, PINK_SOFT, TEXT_WHITE


def opacity(hex_color: str, alpha: float) -> str:
    """Create color with opacity. alpha 0-1."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return hex_color
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = int(255 * alpha)
    return f"#{a:02x}{r:02x}{g:02x}{b:02x}"


def pink_gradient(alpha_start: float = 0.35, alpha_end: float = 0.15) -> list[str]:
    return [opacity(PINK_LIGHT, alpha_start), opacity(PINK_DARK, alpha_end)]


def pink_gradient_three(alpha: float = 0.25) -> list[str]:
    return [
        opacity(PINK_LIGHT, alpha),
        opacity(PINK_SOFT, alpha * 0.9),
        opacity(PINK_DARK, alpha * 0.6),
    ]


def section_card(title: str, icon, content: ft.Control) -> ft.Container:
    """Styled section card (dark + pink gradient)."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=PINK, size=20),
                            bgcolor=opacity(PINK_SOFT, 0.2),
                            border_radius=8,
                            padding=8,
                        ),
                        ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=TEXT_WHITE),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=1, color=CARD_BORDER),
                ft.Container(content=content, padding=ft.padding.only(top=12)),
            ],
            spacing=0,
        ),
        padding=20,
        border_radius=16,
        bgcolor=CARD_BG,
        border=ft.border.all(1, CARD_BORDER),
    )
