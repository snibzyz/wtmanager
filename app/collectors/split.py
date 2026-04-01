"""Post-processor: split images horizontally (res only, webtoon style)."""

from pathlib import Path
from typing import Callable

from app.collectors.credit import CREDIT_OUTPUT_NAME

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _is_credit_file(name: str) -> bool:
    """ไม่หั่นไฟล์เครดิต (ชื่อตรงหรือมี 'credit' ในชื่อ)"""
    lower = name.lower()
    return name == CREDIT_OUTPUT_NAME or "credit" in lower


def apply_split(
    base_path: str,
    output_folder: str,
    parts: int = 2,
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str]]:
    """
    Split all images in episode subfolders horizontally (top→bottom).
    Each image becomes `parts` pieces; order preserved for webtoon reading.

    Only operates on base_path/<output_folder>/<episode_name>/ (res output).
    Requires Pillow.

    Returns (success, log_lines).
    """
    base = Path(base_path)
    out_dir = base / output_folder
    if not out_dir.exists():
        return False, [f"Output folder ไม่พบ: {out_dir}"]

    if not HAS_PIL:
        return False, ["ไม่มี Pillow ไม่สามารถหั่นภาพได้"]

    parts = max(2, min(20, int(parts) if parts else 2))

    log: list[str] = []

    def _log(msg: str) -> None:
        log.append(msg)
        if log_callback:
            log_callback(msg)

    try:
        total_splits = 0
        for ep_dir in sorted(out_dir.iterdir()):
            if not ep_dir.is_dir():
                continue

            images = sorted(
                f for f in ep_dir.iterdir()
                if f.is_file()
                and f.suffix.lower() in IMAGE_EXTENSIONS
                and not _is_credit_file(f.name)
            )
            if not images:
                continue

            new_pieces: list[Path] = []
            for img_path in images:
                try:
                    img = Image.open(img_path).convert("RGB")
                    w, h = img.size
                    piece_h = h // parts
                    if piece_h <= 0:
                        continue

                    for i in range(parts):
                        top = i * piece_h
                        bottom = (i + 1) * piece_h if i < parts - 1 else h
                        crop = img.crop((0, top, w, bottom))
                        piece_path = ep_dir / f"{img_path.stem}_part{i + 1}{img_path.suffix}"
                        crop.save(piece_path, quality=95)
                        new_pieces.append(piece_path)

                    img_path.unlink()
                except Exception as e:
                    _log(f"หั่น {img_path.name} ไม่ได้: {e}")

            if new_pieces:
                # Renumber: 01.jpg, 02.jpg, ... to preserve order
                for idx, p in enumerate(new_pieces, start=1):
                    new_name = ep_dir / f"{idx:02d}{p.suffix}"
                    if p != new_name:
                        p.rename(new_name)
                total_splits += len(new_pieces)
                _log(f"✓ {ep_dir.name} ({len(new_pieces)} ชิ้น)")

        _log(f"หั่นภาพเสร็จ ({total_splits} ชิ้นรวม)")
        return True, log
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        return False, log
