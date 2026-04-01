"""Post-processor: add credit image(s) to episode output folders."""

import shutil
from pathlib import Path
from typing import Callable

# prefix ชื่อไฟล์เครดิตใน output (ใช้ใน split เพื่อไม่หั่น)
# ถ้าเลือกหลายไฟล์ จะตั้งชื่อ 9999credit_01.png, 9999credit_02.png, ...
CREDIT_OUTPUT_NAME = "9999credit.png"           # fallback เมื่อมีไฟล์เดียว
CREDIT_OUTPUT_PREFIX = "9999credit"             # prefix สำหรับหลายไฟล์


def default_credit_path() -> str:
    """Default credit path: [parent of Rabbit Hole]/logo/9999credit.png"""
    project_root = Path(__file__).resolve().parent.parent.parent
    parent_folder = project_root.parent
    return str(parent_folder / "logo" / "9999credit.png")


def apply_credit(
    base_path: str,
    output_folder: str,
    credit_paths: list[str] | str,  # รับได้ทั้ง list หรือ string เดียว (backward-compat)
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str]]:
    """
    Copy credit image(s) into every episode subfolder of
    base_path/<output_folder>/<episode_name>/.

    - ถ้ามีไฟล์เดียว: ใช้ชื่อ  9999credit.png
    - ถ้ามีหลายไฟล์: ใช้ชื่อ  9999credit_01.png, 9999credit_02.png, ...

    Returns (success, log_lines).
    """
    # รองรับ backward-compat: ถ้าส่ง string เดียวมา ให้ห่อเป็น list
    if isinstance(credit_paths, str):
        credit_paths = [credit_paths] if credit_paths.strip() else []

    # กรองเฉพาะไฟล์ที่มีอยู่จริง
    valid_srcs = [Path(p) for p in credit_paths if p.strip() and Path(p).is_file()]

    base = Path(base_path)
    out_dir = base / output_folder
    log: list[str] = []

    def _log(msg: str) -> None:
        log.append(msg)
        if log_callback:
            log_callback(msg)

    if not out_dir.exists():
        return False, [f"Output folder ไม่พบ: {out_dir}"]

    if not valid_srcs:
        return False, ["ไม่มีไฟล์เครดิตที่ถูกต้อง"]

    # กำหนดชื่อไฟล์ปลายทางสำหรับแต่ละ source
    if len(valid_srcs) == 1:
        # ไฟล์เดียว → ใช้ชื่อ 9999credit.png เหมือนเดิม
        output_names = [CREDIT_OUTPUT_NAME]
    else:
        # หลายไฟล์ → 9999credit_01.png, 9999credit_02.png, ...
        output_names = [
            f"{CREDIT_OUTPUT_PREFIX}_{i+1:02d}{Path(src).suffix}"
            for i, src in enumerate(valid_srcs)
        ]

    count = 0
    try:
        for ep_dir in sorted(out_dir.iterdir()):
            if ep_dir.is_dir():
                for src, out_name in zip(valid_srcs, output_names):
                    shutil.copy2(src, ep_dir / out_name)
                count += 1
        _log(f"เพิ่มเครดิต {len(valid_srcs)} ไฟล์ × {count} ตอน")
        return True, log
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        return False, log
