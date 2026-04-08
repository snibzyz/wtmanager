"""Post-processor: split images horizontally (res only, webtoon style)."""

import re
from pathlib import Path
from typing import Any, Callable

from app.collectors.credit import CREDIT_OUTPUT_NAME

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# ไม่นำไฟล์ค้างจากรอบหั่นก่อน (เช่น 01_part1.png) มาหั่นซ้ำ — จะทำให้ rename พังและ WinError 2
_PART_STEM = re.compile(r"_part\d+$", re.IGNORECASE)


def _is_credit_file(name: str) -> bool:
    """ไม่หั่นไฟล์เครดิต (ชื่อตรงหรือมี 'credit' ในชื่อ)"""
    lower = name.lower()
    return name == CREDIT_OUTPUT_NAME or "credit" in lower


def _is_intermediate_split_file(stem: str) -> bool:
    """True if this looks like a piece from a previous split (01_part1, image_part2)."""
    return bool(_PART_STEM.search(stem))


def _empty_split_stats(parts: int) -> dict[str, Any]:
    return {
        "total_pieces": 0,
        "episodes_done": 0,
        "parts_setting": parts,
        "source_images_touched": 0,
    }


def _save_cropped(img, piece_path: Path) -> None:
    """Save crop with options that match the extension (PNG + quality= is unsafe on some Pillow builds)."""
    suffix = piece_path.suffix.lower()
    if suffix in (".jpg", ".jpeg"):
        img.save(piece_path, "JPEG", quality=95, optimize=True)
    elif suffix == ".png":
        img.save(piece_path, "PNG", optimize=True)
    else:
        img.save(piece_path)


def apply_split(
    base_path: str,
    output_folder: str,
    parts: int = 2,
    log_callback: Callable[[str], None] | None = None,
) -> tuple[bool, list[str], dict[str, Any]]:
    """
    Split all images in episode subfolders horizontally (top→bottom).
    Each image becomes `parts` pieces; order preserved for webtoon reading.

    Only operates on base_path/<output_folder>/<episode_name>/ (res output).
    Requires Pillow.

    Returns (success, log_lines, stats).
    """
    base = Path(base_path)
    out_dir = base / output_folder
    parts = max(2, min(20, int(parts) if parts else 2))
    stats: dict[str, Any] = _empty_split_stats(parts)

    log: list[str] = []

    def _log(msg: str) -> None:
        log.append(msg)
        if log_callback:
            log_callback(msg)

    if not out_dir.exists():
        _log(f"Output folder ไม่พบ: {out_dir}")
        return False, log, stats

    if not HAS_PIL:
        _log("ไม่มี Pillow ไม่สามารถหั่นภาพได้")
        return False, log, stats

    try:
        total_splits = 0
        episodes_done = 0
        source_images_touched = 0
        for ep_dir in sorted(out_dir.iterdir()):
            if not ep_dir.is_dir():
                continue

            images = sorted(
                f
                for f in ep_dir.iterdir()
                if f.is_file()
                and f.suffix.lower() in IMAGE_EXTENSIONS
                and not _is_credit_file(f.name)
                and not _is_intermediate_split_file(f.stem)
            )
            if not images:
                _log(
                    f"− ตอน [{ep_dir.name}] ข้าม — ไม่มีภาพให้หั่น "
                    f"(ไม่มีไฟล์รูป / เหลือแต่เครดิตหรือเศษ _part)"
                )
                continue

            _log(f"ตอน [{ep_dir.name}] — หั่นบน→ล่าง ชิ้นละ {parts} ส่วน — พบภาพต้นฉบับ {len(images)} ไฟล์")

            new_pieces: list[Path] = []
            for img_path in images:
                try:
                    img = Image.open(img_path).convert("RGB")
                    w, h = img.size
                    piece_h = h // parts
                    if piece_h <= 0:
                        _log(f"  ⊗ {img_path.name} ข้าม (ความสูง {h}px ไม่พอหั่น {parts} ชิ้น)")
                        continue

                    for i in range(parts):
                        top = i * piece_h
                        bottom = (i + 1) * piece_h if i < parts - 1 else h
                        crop = img.crop((0, top, w, bottom))
                        piece_path = ep_dir / f"{img_path.stem}_part{i + 1}{img_path.suffix}"
                        _save_cropped(crop, piece_path)
                        new_pieces.append(piece_path)

                    img_path.unlink()
                    source_images_touched += 1
                    _log(f"  ✓ {img_path.name} → แบ่งเป็น {parts} ชิ้น")
                except Exception as e:
                    _log(f"  ⊗ หั่น {img_path.name} ไม่ได้: {e}")

            if not new_pieces and images:
                _log(
                    f"⚠ ตอน [{ep_dir.name}] ไม่ได้ไฟล์หลังหั่น — "
                    f"ภาพทั้งหมดถูกข้าม (เช่น สั้นเกิน) หรือผิดพลาด"
                )
            elif new_pieces:
                # สองขั้นตอน: กันชนกับไฟล์เลขค้าง (01.png ยังอยู่) และกันลำดับ rename บน Windows
                tmp_tag = ".__wt_split_tmp_"
                tmp_paths: list[Path] = []
                for i, p in enumerate(new_pieces):
                    tmp = ep_dir / f"{tmp_tag}{i:05d}{p.suffix.lower()}"
                    if tmp.exists():
                        tmp.unlink()
                    p.rename(tmp)
                    tmp_paths.append(tmp)
                for idx, tmp in enumerate(tmp_paths, start=1):
                    final = ep_dir / f"{idx:02d}{tmp.suffix}"
                    if final.exists() and final.resolve() != tmp.resolve():
                        final.unlink()
                    tmp.rename(final)
                total_splits += len(new_pieces)
                episodes_done += 1
                _log(
                    f"✓ ตอน [{ep_dir.name}] หั่นภาพเสร็จแล้ว — {len(new_pieces)} ไฟล์ "
                    f"(เรียงเป็น 01…{len(new_pieces):02d})"
                )

        stats["total_pieces"] = total_splits
        stats["episodes_done"] = episodes_done
        stats["source_images_touched"] = source_images_touched

        if total_splits == 0:
            _log(
                "ไม่มีภาพถูกหั่น (ตรวจสอบว่าโฟลเดอร์ตอนมีไฟล์รูป "
                "และความสูงรูปพอให้หั่นตามจำนวนชิ้นที่ตั้งไว้)"
            )
        _log(f"หั่นภาพเสร็จ — รวม {total_splits} ไฟล์ จาก {episodes_done} ตอน ({source_images_touched} ภาพต้นฉบับ)")
        return True, log, stats
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        stats["total_pieces"] = total_splits
        stats["episodes_done"] = episodes_done
        stats["source_images_touched"] = source_images_touched
        return False, log, stats
