"""Collector: copy result/ images from episode subfolders."""

import shutil
from pathlib import Path
from typing import Callable


def collect_res(
    base_path: str,
    output_folder: str,
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str]]:
    """
    Copy all files from episode/result/ into
    base_path/<output_folder>/<episode_name>/.

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
        result_dir = item / "result"
        if result_dir.exists() and result_dir.is_dir():
            episodes.append((result_dir, item.name))

    if not episodes:
        _log("ไม่พบโฟลเดอร์ result ใน subfolder ใดๆ")
        return False, log

    episodes.sort(key=lambda x: x[1])
    out_base = base / output_folder
    out_base.mkdir(parents=True, exist_ok=True)

    try:
        for result_dir, ep_name in episodes:
            dest_dir = out_base / ep_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for f in result_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, dest_dir / f.name)
                    count += 1
            _log(f"✓ {ep_name} ({count} ไฟล์ลงคำ)")
        _log("ดึงไฟล์ลงคำเสร็จ")
        return True, log
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        return False, log
