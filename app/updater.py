"""Self-update สำหรับ .exe build: เช็ค GitHub Releases → โหลดตัวใหม่ → สลับ → เปิดใหม่.

ทำงานเฉพาะตอนเป็น .exe (sys.frozen). รันจาก source ใช้ git pull แทน (scripts/run.py).
ถ้าเช็ค/โหลดพลาด (เน็ตล่ม, rate limit ฯลฯ) จะข้ามเงียบ ๆ แล้วเปิดเวอร์ชันปัจจุบันต่อ
— ไม่บล็อกผู้ใช้.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import urllib.request

from app import __version__

REPO = "snibzyz/wtmanager"
API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"
ASSET_NAME = "WTManager.exe"
_API_TIMEOUT = 8
_DL_TIMEOUT = 120


def _ver_tuple(tag: str) -> tuple:
    """'v1.0.2' -> (1, 0, 2); ทนต่อรูปแบบแปลก ๆ."""
    parts = (tag or "").lstrip("vV").split(".")
    out = []
    for p in parts:
        digits = ""
        for ch in p:
            if ch.isdigit():
                digits += ch
            else:
                break
        out.append(int(digits) if digits else 0)
    return tuple(out) or (0,)


def _fetch_latest() -> dict | None:
    req = urllib.request.Request(
        API_LATEST,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "WTManager-Updater",
        },
    )
    with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as r:
        return json.load(r)


def _asset_url(data: dict) -> str | None:
    for a in data.get("assets", []):
        if (a.get("name") or "").lower() == ASSET_NAME.lower():
            return a.get("browser_download_url")
    return None


def _download_with_splash(url: str, dest: str, latest_tag: str) -> None:
    """โหลดไฟล์ใน thread พร้อมโชว์หน้าต่างเล็ก ๆ ว่ากำลังอัปเดต."""
    import tkinter as tk
    from tkinter import ttk

    win = tk.Tk()
    win.title("WTManager")
    win.configure(bg="#0F0F0F")
    win.resizable(False, False)
    tk.Label(
        win, text=f"พบเวอร์ชันใหม่ {latest_tag}\nกำลังดาวน์โหลดอัปเดต...",
        bg="#0F0F0F", fg="#FFFFFF", font=("Tahoma", 11), justify="center",
    ).pack(padx=24, pady=(20, 10))
    pb = ttk.Progressbar(win, mode="indeterminate", length=300)
    pb.pack(padx=24, pady=(0, 20))
    pb.start(12)

    # จัดกลางจอ
    win.update_idletasks()
    w, h = 360, 120
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    state = {"done": False, "err": None}

    def worker() -> None:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "WTManager-Updater"})
            with urllib.request.urlopen(req, timeout=_DL_TIMEOUT) as r, open(dest, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:  # noqa: BLE001
            state["err"] = e
        state["done"] = True

    threading.Thread(target=worker, daemon=True).start()

    def poll() -> None:
        if state["done"]:
            win.destroy()
            return
        win.after(100, poll)

    win.after(100, poll)
    win.mainloop()
    if state["err"]:
        raise state["err"]


def _spawn_swap_and_exit(target: str, new: str) -> None:
    """.exe สลับตัวเองไม่ได้ขณะรัน → เขียน .bat รอโปรเซสปิด แล้ว move ทับ + เปิดใหม่."""
    bat = os.path.join(os.path.dirname(target), "_wt_update.bat")
    script = (
        "@echo off\r\n"
        "setlocal\r\n"
        ":wait\r\n"
        f'del "{target}" >nul 2>&1\r\n'
        f'if exist "{target}" ( ping -n 2 127.0.0.1 >nul & goto wait )\r\n'
        f'move /y "{new}" "{target}" >nul\r\n'
        f'start "" "{target}"\r\n'
        'del "%~f0" >nul 2>&1\r\n'
    )
    with open(bat, "w", encoding="ascii") as f:
        f.write(script)
    # DETACHED_PROCESS | CREATE_NO_WINDOW — รันต่อหลังแอปปิด ไม่มีหน้าต่าง cmd เด้ง
    flags = 0x00000008 | 0x08000000
    subprocess.Popen(["cmd", "/c", bat], creationflags=flags, close_fds=True)
    sys.exit(0)


def check_and_update() -> None:
    """ถ้าเป็น .exe และมีเวอร์ชันใหม่กว่า → โหลด + สลับ + เปิดใหม่. error = ข้ามเงียบ."""
    if not getattr(sys, "frozen", False):
        return  # source mode ใช้ git pull (scripts/run.py) แทน
    new = None
    try:
        data = _fetch_latest()
        if not data:
            return
        if _ver_tuple(data.get("tag_name", "")) <= _ver_tuple(__version__):
            return  # เป็นเวอร์ชันล่าสุดแล้ว
        url = _asset_url(data)
        if not url:
            return
        target = sys.executable
        new = target + ".new"
        _download_with_splash(url, new, data.get("tag_name", ""))
        if os.path.isfile(new) and os.path.getsize(new) > 0:
            _spawn_swap_and_exit(target, new)  # ออกจากโปรแกรม แล้ว .bat เปิดตัวใหม่
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 — เน็ตล่ม/ใด ๆ ก็เปิดเวอร์ชันปัจจุบันต่อ
        try:
            if new and os.path.isfile(new):
                os.remove(new)
        except Exception:
            pass
        return
