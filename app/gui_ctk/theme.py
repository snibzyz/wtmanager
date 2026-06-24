"""Theme for the CustomTkinter UI.

หมายเหตุสำคัญ: tkinter รับสีเป็น #RRGGBB เท่านั้น (ไม่รองรับ #AARRGGBB
แบบที่ Flet ใช้ผ่าน opacity()) จึงต้องเตรียมสีที่ "ผสมไว้แล้ว" เป็น hex ทึบ.
"""

from __future__ import annotations

# สีหลัก (ค่าตรงกับ app/theme/colors.py เดิมเป๊ะ — โทนเหมือนเวอร์ชัน Flet).
# จงใจ "ไม่" import จาก app.theme เพราะ app/theme/__init__.py ลาก flet มาด้วย
# ซึ่งจะทำให้เวอร์ชันใหม่พังบนเครื่องที่ flet โหลดไม่ได้ (เหตุผลที่เราย้ายมา CTk).
PINK = "#E37F9D"
PINK_LIGHT = "#F4BECF"
PINK_DARK = "#C75A7A"
PINK_SOFT = "#E8A0B8"
BLACK = "#0F0F0F"
CARD_BG = "#1A1A1A"
CARD_BORDER = "#2D2D2D"
TEXT_MUTED = "#9CA3AF"
TEXT_WHITE = "#FFFFFF"
SUCCESS = "#10B981"

# สถานะเพิ่มเติม (เทียบเท่าที่ Flet ใช้ hardcode ใน log)
ERROR = "#EF4444"
WARN = "#F59E0B"

# ── สีที่ผสมไว้แล้ว (แทน opacity() ของ Flet) ──────────────────────────────
# พื้นหลังหน้าต่าง / การ์ด
WINDOW_BG = BLACK
CARD_FG = CARD_BG

# chip (ปุ่มฟังก์ชัน / ปุ่มเรื่อง)
CHIP_ON_BG = PINK
CHIP_ON_HOVER = PINK_DARK
CHIP_OFF_BG = "#241A1E"      # PINK จาง ๆ บนพื้นดำ
CHIP_OFF_HOVER = "#2E2024"
CHIP_OFF_BORDER = CARD_BORDER
CHIP_DISABLED_BG = "#161214"
CHIP_DISABLED_TEXT = "#5B5560"
CHIP_DISABLED_BORDER = "#241F22"

# badge ไอคอนหัวข้อ (PINK_SOFT จาง)
BADGE_BG = "#2E2226"

# กล่อง log
LOG_BG = "#141414"

# ── ฟอนต์ ────────────────────────────────────────────────────────────────
# Tahoma มีอยู่ทุกเครื่อง Windows และเรนเดอร์ภาษาไทยได้ดี (กัน "□□□")
FONT_FAMILY = "Tahoma"


def font(size: int = 13, bold: bool = False) -> tuple:
    """คืน font tuple ให้ CTk widget (ไม่ต้องมี root ก่อน)."""
    return (FONT_FAMILY, size, "bold") if bold else (FONT_FAMILY, size)


# ── chip helpers ──────────────────────────────────────────────────────────
def chip_style(state: str) -> dict:
    """คืน kwargs สำหรับ btn.configure() ตามสถานะ on/off/disabled."""
    if state == "on":
        return dict(
            fg_color=CHIP_ON_BG, hover_color=CHIP_ON_HOVER,
            text_color=TEXT_WHITE, border_width=1, border_color=CHIP_ON_BG,
        )
    if state == "disabled":
        return dict(
            fg_color=CHIP_DISABLED_BG, hover_color=CHIP_DISABLED_BG,
            text_color=CHIP_DISABLED_TEXT, border_width=1,
            border_color=CHIP_DISABLED_BORDER,
        )
    # off
    return dict(
        fg_color=CHIP_OFF_BG, hover_color=CHIP_OFF_HOVER,
        text_color=TEXT_MUTED, border_width=1, border_color=CHIP_OFF_BORDER,
    )


__all__ = [
    "BLACK", "CARD_BG", "CARD_BORDER", "PINK", "PINK_DARK", "PINK_LIGHT",
    "PINK_SOFT", "SUCCESS", "TEXT_MUTED", "TEXT_WHITE", "ERROR", "WARN",
    "WINDOW_BG", "CARD_FG", "CHIP_ON_BG", "CHIP_ON_HOVER", "CHIP_OFF_BG",
    "CHIP_OFF_HOVER", "CHIP_OFF_BORDER", "CHIP_DISABLED_BG",
    "CHIP_DISABLED_TEXT", "CHIP_DISABLED_BORDER", "BADGE_BG", "LOG_BG",
    "FONT_FAMILY", "font", "chip_style",
]
