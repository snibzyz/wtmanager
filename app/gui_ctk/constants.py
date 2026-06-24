"""Constants for the CustomTkinter UI (no Flet dependency).

build_folder_name มี logic เดียวกับ app/gui/constants.py เป๊ะ เพื่อให้ชื่อ
โฟลเดอร์ output เหมือนเวอร์ชันเดิมทุกประการ.
"""

from __future__ import annotations

# ลำดับคงที่สำหรับสร้างชื่อโฟลเดอร์ output (ตรงกับเวอร์ชันเดิม)
FUNC_ORDER = ["raw", "inp", "res", "split", "trans", "text", "ep", "cred", "com"]

FUNC_LABELS = {
    "raw": "ดึงไฟล์ดิบ (raw)",
    "inp": "ดึงไฟล์คลีน (inpaint)",
    "res": "ดึงไฟล์ลงคำ (result)",
    "split": "หั่นภาพใหม่ (split)",
    "trans": "ดึงไฟล์แปล (translate)",
    "text": "ดึงไฟล์ถอดคำ (text)",
    "ep": "เข้าไฟล์ตอน (episode)",
    "cred": "เพิ่มเครดิต (credit)",
    "com": "ย่อไฟล์ (compress)",
}

# กลุ่มแสดงผลใน UI
# กลุ่มหลัก = ดึงไฟล์ภาพ 3 แบบ เลือกอิสระแยกกันได้ (raw/inp/res)
SOURCE_FUNCS = ["raw", "inp", "res"]
# กลุ่มรอง = ดึงไฟล์ข้อความ + post-process
EXTRA_FUNCS = ["trans", "text", "split", "ep", "cred", "com"]

# ไอคอนของแต่ละฟังก์ชัน (ชื่อใน app.gui_ctk.icons.GLYPH)
FUNC_ICON = {
    "raw": "image",
    "inp": "edit",
    "res": "picture",
    "split": "cut",
    "trans": "globe",
    "text": "page",
    "ep": "newfolder",
    "cred": "star",
    "com": "compress",
}


def build_folder_name(funcs: set[str]) -> str:
    """Build output folder name from selected functions in fixed order."""
    parts = [f for f in FUNC_ORDER if f in funcs]
    return "_".join(parts) if parts else ""


__all__ = [
    "FUNC_ORDER", "FUNC_LABELS", "SOURCE_FUNCS", "EXTRA_FUNCS",
    "build_folder_name",
]
