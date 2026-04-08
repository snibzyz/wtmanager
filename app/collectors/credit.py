"""Post-processor: add credit image(s) to episode output folders."""

import shutil
from pathlib import Path
from typing import Any, Callable

from app.paths import canonical_file

# prefix ชื่อไฟล์เครดิตใน output (ใช้ใน split เพื่อไม่หั่น)
# ถ้าเลือกหลายไฟล์ จะตั้งชื่อ 9999credit_01.png, 9999credit_02.png, ...
CREDIT_OUTPUT_NAME = "9999credit.png"           # fallback เมื่อมีไฟล์เดียว
CREDIT_OUTPUT_PREFIX = "9999credit"             # prefix สำหรับหลายไฟล์


def default_credit_path() -> str:
    """Default credit path: [parent of Rabbit Hole]/logo/9999credit.png (resolved if exists)."""
    project_root = Path(__file__).resolve().parent.parent.parent
    parent_folder = project_root.parent
    cand = parent_folder / "logo" / "9999credit.png"
    if cand.is_file():
        return canonical_file(str(cand)) or str(cand)
    return str(cand)


def apply_credit(
    base_path: str,
    output_folder: str,
    credit_paths: list[str] | str,  # รับได้ทั้ง list หรือ string เดียว (backward-compat)
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str], dict[str, Any]]:
    """
    Copy credit image(s) into every episode subfolder of
    base_path/<output_folder>/<episode_name>/.

    - ถ้ามีไฟล์เดียว: ใช้ชื่อ  9999credit.png
    - ถ้ามีหลายไฟล์: ใช้ชื่อ  9999credit_01.png, 9999credit_02.png, ...

    Returns (success, log_lines, stats).
    """
    # รองรับ backward-compat: ถ้าส่ง string เดียวมา ให้ห่อเป็น list
    if isinstance(credit_paths, str):
        credit_paths = [credit_paths] if credit_paths.strip() else []

    # กรองเฉพาะไฟล์ที่มีอยู่จริง (ใช้ canonical path)
    valid_srcs: list[Path] = []
    for p in credit_paths:
        if not isinstance(p, str) or not p.strip():
            continue
        c = canonical_file(p)
        if c:
            valid_srcs.append(Path(c))

    base = Path(base_path)
    out_dir = base / output_folder
    log: list[str] = []
    stats: dict[str, Any] = {
        "templates": 0,
        "episodes": 0,
        "files_copied_total": 0,
    }

    def _log(msg: str) -> None:
        log.append(msg)
        if log_callback:
            log_callback(msg)

    if not out_dir.exists():
        return False, [f"Output folder ไม่พบ: {out_dir}"], stats

    if not valid_srcs:
        return False, ["ไม่มีไฟล์เครดิตที่ถูกต้อง"], stats

    stats["templates"] = len(valid_srcs)

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

    preview = ", ".join(p.name for p in valid_srcs[:4])
    if len(valid_srcs) > 4:
        preview += " …"
    _log(f"เครดิต — แม่แบบ {len(valid_srcs)} ไฟล์: {preview}")

    count = 0
    try:
        for ep_dir in sorted(out_dir.iterdir()):
            if ep_dir.is_dir():
                _log(
                    f"  • ตอน [{ep_dir.name}]: กำลังใส่ {len(output_names)} ไฟล์ "
                    f"({', '.join(output_names[:3])}{'…' if len(output_names) > 3 else ''})"
                )
                for src, out_name in zip(valid_srcs, output_names):
                    shutil.copy2(src, ep_dir / out_name)
                count += 1
        stats["episodes"] = count
        stats["files_copied_total"] = count * len(valid_srcs)
        _log(
            f"เครดิตเสร็จ — แบบละ {len(valid_srcs)} ไฟล์ × {count} ตอน "
            f"(รวมคัดลอก {stats['files_copied_total']} ไฟล์)"
        )
        return True, log, stats
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        stats["episodes"] = count
        stats["files_copied_total"] = count * len(valid_srcs)
        return False, log, stats
