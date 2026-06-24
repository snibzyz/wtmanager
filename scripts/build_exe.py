"""Build a standalone WTManager.exe with PyInstaller.

ได้ไฟล์เดียว dist/WTManager.exe — รันได้โดยไม่ต้องลง Python (มี self-update ในตัว).
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("ติดตั้ง PyInstaller...", flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def main() -> int:
    _ensure_pyinstaller()
    sys.path.insert(0, str(ROOT))
    from app import __version__

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile",                       # ไฟล์เดียว
        "--windowed",                      # ไม่มีหน้าต่าง console
        "--name", "WTManager",
        "--collect-data", "customtkinter",  # assets/themes ของ customtkinter
        "--paths", str(ROOT),
        str(ROOT / "main.py"),
    ]
    print(f"กำลัง build WTManager.exe (v{__version__})...", flush=True)
    print("  " + " ".join(args), flush=True)
    rc = subprocess.call(args, cwd=str(ROOT))
    if rc == 0:
        exe = ROOT / "dist" / "WTManager.exe"
        size = exe.stat().st_size / 1024 / 1024 if exe.exists() else 0
        print(f"\nเสร็จ → {exe}  ({size:.1f} MB, v{__version__})", flush=True)
    else:
        print("\nbuild ไม่สำเร็จ — ดู error ด้านบน", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
