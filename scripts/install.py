"""Install dependencies from requirements.txt and verify the UI stack.

UI ใหม่ใช้ CustomTkinter (อยู่บน Tkinter ที่ติดมากับ Python) → ไม่ต้องโหลด
engine ตอนติดตั้ง ไม่ต้องต่อเน็ต ไม่มี SSL ให้พลาด.
"""

import subprocess
import sys
from pathlib import Path

MIN_PY = (3, 10)
ROOT = Path(__file__).resolve().parent.parent


def _ensure_root_on_path() -> None:
    r = str(ROOT)
    if r not in sys.path:
        sys.path.insert(0, r)


def _warn_if_not_git_repo() -> None:
    if (ROOT / ".git").is_dir():
        return
    print("\n[คำเตือน] ไม่พบโฟลเดอร์ .git — น่าจะไม่ได้ clone จาก Git", flush=True)
    print(
        "  แนะนำ: git clone <URL-รีโป> แล้วรัน install.bat ในโฟลเดอร์นั้น "
        "— จะได้ auto-update (git pull) ตอนเปิดแอป",
        flush=True,
    )
    print("  ถ้าแตกไฟล์ ZIP อย่างเดียว แอปยังเปิดได้ แต่จะไม่ดึงอัปเดตอัตโนมัติ\n", flush=True)


def _verify_stack() -> int:
    """ตรวจว่าโหลด UI stack ได้ครบ (offline ล้วน ไม่ต่อเน็ต)."""
    _ensure_root_on_path()
    print("กำลังตรวจสอบว่าโหลด UI ได้...", flush=True)
    missing = []
    try:
        import tkinter  # noqa: F401  (ติดมากับ Python มาตรฐาน)
    except Exception:
        missing.append(
            "tkinter — ติดตั้ง Python จาก python.org แล้วติ๊ก 'tcl/tk and IDLE' "
            "(หรือบน Linux: sudo apt install python3-tk)"
        )
    try:
        import customtkinter  # noqa: F401
    except Exception as e:
        missing.append(f"customtkinter ({e})")
    try:
        from PIL import Image  # noqa: F401
    except Exception as e:
        missing.append(f"Pillow ({e})")

    if missing:
        print("\n[ผิดพลาด] ยังโหลดไม่ครบ:", flush=True)
        for m in missing:
            print(f"  - {m}", flush=True)
        return 1

    # ลอง import ตัวแอปจริง เพื่อจับ error ตั้งแต่ตอนติดตั้ง
    try:
        import app.gui_ctk  # noqa: F401
    except Exception as e:
        print(f"\n[ผิดพลาด] โหลดโมดูลแอปไม่สำเร็จ: {e}", flush=True)
        return 1

    print("\n[ตรวจสอบ] พร้อมใช้งาน — เปิดด้วย run.bat ได้เลย", flush=True)
    return 0


def main() -> int:
    if sys.version_info < MIN_PY:
        print(
            f"ต้องการ Python {MIN_PY[0]}.{MIN_PY[1]}+ "
            f"(ตอนนี้เป็น {sys.version_info.major}.{sys.version_info.minor})"
        )
        print("ดาวน์โหลด: https://www.python.org/downloads/ — ติ๊ก Add python.exe to PATH")
        return 1
    req = ROOT / "requirements.txt"
    if not req.exists():
        print(f"ไม่พบ {req}")
        return 1
    print("กำลังติดตั้ง dependencies...", flush=True)
    print(f"ใช้ Python: {sys.executable}", flush=True)
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(req)],
        )
    except subprocess.CalledProcessError:
        print("\nติดตั้งไม่สำเร็จ — ลองรันใน CMD แบบ Administrator หรืออัปเดต pip:")
        print(f'  "{sys.executable}" -m pip install --upgrade pip')
        print(f'  "{sys.executable}" -m pip install -r "{req}"')
        return 1
    print("\nติดตั้งแพ็กเกจจาก requirements.txt เรียบร้อยแล้ว", flush=True)
    _warn_if_not_git_repo()
    return _verify_stack()


if __name__ == "__main__":
    raise SystemExit(main())
