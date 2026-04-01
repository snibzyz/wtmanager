"""Collector: copy *_translation.txt from episode subfolders."""

import shutil
from pathlib import Path
from typing import Callable


def collect_trans(
    base_path: str,
    output_folder: str,
    per_episode: bool = False,
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str]]:
    """
    Copy all *_translation.txt files from episode subfolders.

    per_episode=False: flat to base_path/<output_folder>/
    per_episode=True:  into base_path/<output_folder>/<episode_name>/

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

    # (episode_dir_name, src_path, filename)
    to_copy: list[tuple[str, Path, str]] = []
    for sub in base.iterdir():
        if not sub.is_dir():
            continue
        for f in sub.iterdir():
            if f.is_file() and f.name.endswith("_translation.txt"):
                to_copy.append((sub.name, f, f.name))

    if not to_copy:
        _log("ไม่พบไฟล์ *_translation.txt ใน subfolder ใดๆ")
        return False, log

    out_base = base / output_folder
    out_base.mkdir(parents=True, exist_ok=True)

    try:
        for ep_name, src, name in sorted(to_copy, key=lambda x: (x[0], x[2])):
            if per_episode:
                dest_dir = out_base / ep_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest_dir / name)
                _log(f"✓ {ep_name}/{name}")
            else:
                shutil.copy2(src, out_base / name)
                _log(f"✓ {name}")
        _log(f"ดึงไฟล์แปลเสร็จ ({len(to_copy)} ไฟล์)")
        return True, log
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        return False, log
