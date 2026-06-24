"""Constants shared across GUI components."""

import flet as ft

# Fixed order for building output folder name
FUNC_ORDER = ["raw", "inp", "res", "split", "trans", "text", "ep", "cred", "com"]

FUNC_LABELS = {
    "raw": "ดึงไฟล์ดิบ",
    "inp": "ดึงไฟล์คลีน",
    "res": "ดึงไฟล์ลงคำ",
    "split": "หั่นภาพใหม่",
    "trans": "ดึงไฟล์แปล",
    "text": "ดึงไฟล์ถอดคำ",
    "ep": "เข้าไฟล์ตอน",
    "cred": "เพิ่มเครดิต",
    "com": "ย่อไฟล์",
}

FUNC_ICONS = {
    "raw": ft.Icons.IMAGE,
    "inp": ft.Icons.AUTO_FIX_HIGH,
    "res": ft.Icons.IMAGE_SEARCH,
    "split": ft.Icons.CROP,
    "trans": ft.Icons.TRANSLATE,
    "text": ft.Icons.DESCRIPTION,
    "ep": ft.Icons.CREATE_NEW_FOLDER,
    "cred": ft.Icons.STAR,
    "com": ft.Icons.COMPRESS,
}


def build_folder_name(funcs: set[str]) -> str:
    """Build output folder name from selected functions in fixed order."""
    parts = [f for f in FUNC_ORDER if f in funcs]
    return "_".join(parts) if parts else ""
