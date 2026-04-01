"""Collector: copy inpainted/ images from episode subfolders."""

import shutil
from pathlib import Path
from typing import Callable


def collect_inpainted(
    base_path: str,
    output_folder: str,
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str]]:
    """
    Copy inpainted/ folder contents from each episode subfolder
    into base_path/<output_folder>/<episode_name>/inpainted/.

    Returns (success, log_lines).
    """
    base = Path(base_path)
    if not base.exists() or not base.is_dir():
        return False, [f"โฟลเดอร์ไม่พบ: {base_path}"]

    log: list[str] = []

    def _log(msg: str) -> None:
        log.append(msg)
        if log_callback:
            log_callback(msg)

    episodes: list[tuple[Path, str]] = []
    for item in base.iterdir():
        if not item.is_dir():
            continue
        inp_dir = item / "inpainted"
        if inp_dir.exists() and inp_dir.is_dir():
            episodes.append((inp_dir, item.name))

    if not episodes:
        _log("ไม่พบโฟลเดอร์ inpainted ใน subfolder ใดๆ")
        return False, log

    episodes.sort(key=lambda x: x[1])
    out_base = base / output_folder

    try:
        for inp_dir, ep_name in episodes:
            dest_dir = out_base / ep_name / "inpainted"
            dest_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for f in inp_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, dest_dir / f.name)
                    count += 1
            _log(f"✓ {ep_name}/inpainted ({count} ไฟล์คลีน)")
        _log("ดึงไฟล์คลีนเสร็จ")
        return True, log
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        return False, log
