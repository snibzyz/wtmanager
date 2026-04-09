"""Install dependencies from requirements.txt."""

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
    print(
        "\n[คำเตือน] ไม่พบโฟลเดอร์ .git — น่าจะไม่ได้ clone จาก Git",
        flush=True,
    )
    print(
        "  แนะนำ: git clone <URL-รีโป> แล้วรัน install.bat ในโฟลเดอร์นั้น — จะได้ auto-update (git pull)",
        flush=True,
    )
    print(
        "  ถ้าแตกไฟล์ ZIP อย่างเดียว แอปยังเปิดได้ แต่จะไม่ดึงอัปเดตอัตโนมัติ\n",
        flush=True,
    )


def _verify_can_import_app_stack() -> int:
    """โหลด Flet ครั้งแรกตอน install เพื่อจับ SSL/เน็ตก่อนผู้ใช้รัน run.bat"""
    _ensure_root_on_path()
    from app.ssl_bundle import apply_certifi_defaults

    apply_certifi_defaults()
    print(
        "กำลังตรวจสอบว่าโหลด Flet ได้ (ครั้งแรกอาจดาวน์โหลด ใช้เวลาสักครู่)...",
        flush=True,
    )
    try:
        import certifi  # noqa: F401
        from PIL import Image  # noqa: F401
        import flet  # noqa: F401
    except Exception as e:
        print(
            "\n[ผิดพลาด] ติดตั้งแพ็กเกจแล้ว แต่โหลด Flet / ภาพ / SSL ไม่สำเร็จ",
            flush=True,
        )
        print(f"  รายละเอียด: {e}", flush=True)
        print(
            "  ลอง: ตรวจเน็ตและไฟร์วอลล์, อัปเดต pip, หรือถ้าเป็นเน็ตองค์กรให้ใส่ CA ของบริษัท",
            flush=True,
        )
        return 1
    print(
        "\n[ตรวจสอบ] พร้อมใช้งาน — เปิดด้วย run.bat ได้เลย",
        flush=True,
    )
    return 0


def main() -> int:
    if sys.version_info < MIN_PY:
        print(
            f"ต้องการ Python {MIN_PY[0]}.{MIN_PY[1]}+ (ตอนนี้เป็น {sys.version_info.major}.{sys.version_info.minor})"
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
    return _verify_can_import_app_stack()


if __name__ == "__main__":
    raise SystemExit(main())
