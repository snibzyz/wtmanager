"""Collector: copy raw source images from episode root."""

import shutil
from pathlib import Path
from typing import Callable

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def collect_raw(
    base_path: str,
    output_folder: str,
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str]]:
    """
    Copy raw images (files in episode root with image extensions)
    into base_path/<output_folder>/<episode_name>/.

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
        has_images = any(
            f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS for f in item.iterdir()
        )
        if has_images:
            episodes.append((item, item.name))

    if not episodes:
        _log("ไม่พบไฟล์ภาพดิบใน subfolder ใดๆ")
        return False, log

    episodes.sort(key=lambda x: x[1])
    out_base = base / output_folder
    out_base.mkdir(parents=True, exist_ok=True)

    try:
        for ep_dir, ep_name in episodes:
            dest_dir = out_base / ep_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for f in ep_dir.iterdir():
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
                    shutil.copy2(f, dest_dir / f.name)
                    count += 1
            _log(f"✓ {ep_name} ({count} ภาพดิบ)")
        _log("ดึงไฟล์ดิบเสร็จ")
        return True, log
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        return False, log
