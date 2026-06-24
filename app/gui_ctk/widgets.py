"""Reusable CustomTkinter widgets: styled card + section header."""

from __future__ import annotations

import customtkinter as ctk

from app.gui_ctk import icons
from app.gui_ctk.theme import (
    BADGE_BG, CARD_BORDER, CARD_FG, PINK, TEXT_WHITE, font,
)


def make_card(parent, **kwargs) -> ctk.CTkFrame:
    """การ์ดสไตล์เดียวกับเวอร์ชันเดิม: พื้นเข้ม ขอบบาง มุมมน."""
    opts = dict(
        fg_color=CARD_FG,
        border_width=1,
        border_color=CARD_BORDER,
        corner_radius=14,
    )
    opts.update(kwargs)
    return ctk.CTkFrame(parent, **opts)


def section_header(parent, title: str, icon: str | None = None) -> ctk.CTkFrame:
    """หัวข้อ section: badge ไอคอน + ชื่อ + เส้นคั่นด้านล่าง.

    pack ลงใน parent (ที่จัดเรียงแนวตั้ง) แล้วคืน frame หัวข้อ.
    """
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=14, pady=(12, 0))

    badge = ctk.CTkLabel(
        row, text="", fg_color=BADGE_BG,
        corner_radius=6, width=30, height=30,
    )
    icon_img = icons.glyph(icon, 16, PINK) if icon else None
    if icon_img is not None:
        badge.configure(image=icon_img)
    else:
        badge.configure(text="●", text_color=PINK, font=font(13, bold=True))
    badge.pack(side="left")

    ctk.CTkLabel(
        row, text=title, text_color=TEXT_WHITE, font=font(14, bold=True),
    ).pack(side="left", padx=(10, 0))

    divider = ctk.CTkFrame(parent, height=1, fg_color=CARD_BORDER)
    divider.pack(fill="x", padx=14, pady=(8, 4))
    return row
