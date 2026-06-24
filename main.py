"""Standalone entry point for WTManager (ใช้ตอน build เป็น .exe).

ต่างจาก scripts/run.py ตรงที่ไม่มี git auto-update (ไฟล์ .exe เป็น build สำเร็จรูป
อัปเดตด้วยการโหลด .exe ใหม่). ถ้าเปิดแล้ว error จะเด้ง messagebox + เขียน log
ข้างไฟล์ exe เพื่อ debug ได้ (เพราะ build แบบ windowed ไม่มี console).
"""

import os
import sys
import traceback


def _show_error(msg: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("WTManager — เกิดข้อผิดพลาด", msg)
        root.destroy()
    except Exception:
        pass
    try:
        base = (
            os.path.dirname(sys.executable)
            if getattr(sys, "frozen", False)
            else os.getcwd()
        )
        with open(os.path.join(base, "wtmanager_error.log"), "w", encoding="utf-8") as f:
            f.write(msg)
    except Exception:
        pass


def main() -> None:
    # .exe: เช็ค/อัปเดตจาก GitHub Releases ก่อนเปิด (no-op เมื่อรันจาก source)
    try:
        from app.updater import check_and_update

        check_and_update()
    except SystemExit:
        raise
    except Exception:
        pass  # อัปเดตพลาดก็เปิดเวอร์ชันปัจจุบันต่อ

    from app.gui_ctk import run

    run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        _show_error(traceback.format_exc())
        sys.exit(1)
