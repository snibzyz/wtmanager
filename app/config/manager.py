"""Config persistence - load/save app settings to config.json."""

import json
import os
import sys
from pathlib import Path

from app.paths import canonical_dir


def _resolve_config_file() -> Path:
    """ที่เก็บ config.

    - .exe (frozen): %LOCALAPPDATA%\\WTManager\\config.json — เพราะ onefile แตกไฟล์
      ลงโฟลเดอร์ temp ที่ถูกลบทุกครั้งที่ปิด ถ้าเก็บข้างโค้ดในนั้นค่าจะหาย.
    - รันจาก source: เก็บข้าง ๆ โมดูลเหมือนเดิม (app/config/config.json).
    """
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "WTManager"
        try:
            base.mkdir(parents=True, exist_ok=True)
        except Exception:
            base = Path(__file__).resolve().parent
        return base / "config.json"
    return Path(__file__).resolve().parent / "config.json"


_CONFIG_FILE = _resolve_config_file()

DEFAULTS = {
    "last_workspace": "",
    "selected_functions": [],
    "credit_paths": [],      # รายการไฟล์เครดิต (เลือกได้หลายไฟล์)
    "compress_format": "jpg",
    "compress_quality": 70,
    "split_parts": 2,        # จำนวนชิ้นต่อภาพเมื่อใช้ split (2–20)
}


def load_config() -> dict:
    """Load config from file; returns defaults on error."""
    if not _CONFIG_FILE.exists():
        return DEFAULTS.copy()
    try:
        data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
        out = DEFAULTS.copy()
        for k in DEFAULTS:
            if k in data:
                out[k] = data[k]
        # backward-compat: config เก่าที่บันทึก credit_path (string เดียว)
        if not out["credit_paths"] and data.get("credit_path"):
            out["credit_paths"] = [data["credit_path"]]
        return out
    except Exception:
        return DEFAULTS.copy()


def save_config(c: dict) -> None:
    """Save config to file (only known keys)."""
    try:
        to_save = {k: c.get(k, DEFAULTS[k]) for k in DEFAULTS}
        _CONFIG_FILE.write_text(
            json.dumps(to_save, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def get_last_workspace_from_config() -> str:
    path = load_config().get("last_workspace", "") or ""
    return canonical_dir(path)


def set_last_workspace_in_config(path: str) -> None:
    norm = canonical_dir(path)
    if not norm:
        return
    c = load_config()
    c["last_workspace"] = norm
    save_config(c)
