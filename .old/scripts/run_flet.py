"""WTManager - Workspace Collector"""

import sys
import os
import subprocess
from pathlib import Path

if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app.ssl_bundle import apply_certifi_defaults


def _auto_update() -> None:
    """ดึงอัปเดตล่าสุดจาก GitHub ก่อนเปิดแอปทุกครั้ง"""
    git_dir = APP_DIR / ".git"
    if not git_dir.exists():
        print("[update] ไม่พบ .git — ข้ามการอัปเดต")
        return
    print("[update] กำลังตรวจสอบอัปเดต...")
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=str(APP_DIR),
            capture_output=True,
            text=True,
            timeout=15,
        )
        msg = (result.stdout + result.stderr).strip()
        if result.returncode == 0:
            if "Already up to date" in msg or "up to date" in msg.lower():
                print("[update] โปรแกรมเป็นเวอร์ชันล่าสุดแล้ว")
            else:
                print(f"[update] อัปเดตสำเร็จ:\n{msg}")
        else:
            print(f"[update] pull ไม่สำเร็จ (ข้ามได้):\n{msg}")
    except FileNotFoundError:
        print("[update] ไม่พบ git — ข้ามการอัปเดต")
    except subprocess.TimeoutExpired:
        print("[update] หมดเวลา — ข้ามการอัปเดต")
    except Exception as e:
        print(f"[update] ผิดพลาด: {e}")


try:
    apply_certifi_defaults()
    import flet as ft
    from app.gui.main import main

    if __name__ == "__main__":
        _auto_update()
        ft.run(main)
except Exception as ex:
    print(f"\n=== ERROR ===\n{ex}\n")
    input("Press Enter to close...")
