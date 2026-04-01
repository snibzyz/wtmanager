"""Config persistence - load/save app settings to config.json."""

import json
from pathlib import Path

_CONFIG_DIR = Path(__file__).resolve().parent
_CONFIG_FILE = _CONFIG_DIR / "config.json"

DEFAULTS = {
    "last_workspace": "",
    "selected_functions": [],
    "credit_paths": [],      # รายการไฟล์เครดิต (เลือกได้หลายไฟล์)
    "compress_format": "jpg",
    "compress_quality": 70,
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
    if path and Path(path).is_dir():
        return path
    return ""


def set_last_workspace_in_config(path: str) -> None:
    if not path or not Path(path).is_dir():
        return
    c = load_config()
    c["last_workspace"] = path
    save_config(c)
