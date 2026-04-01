"""Post-processor: compress images in output episode folders (res only)."""

import shutil
import re
from pathlib import Path
from typing import Callable

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _natural_sort_key(text: str) -> tuple:
    """Natural sorting key for filenames with numbers."""
    # Extract numbers from filename for proper sorting
    parts = re.findall(r'\d+|\D+', text)
    return tuple(int(p) if p.isdigit() else p.lower() for p in parts)


def _compress_file(
    src: Path,
    dest: Path,
    fmt: str,
    quality: int,
) -> tuple[bool, int, int]:
    """Compress a single image. Returns (success, original_size, compressed_size)."""
    if not HAS_PIL:
        shutil.copy2(src, dest)
        return False, 0, 0
    
    original_size = src.stat().st_size
    
    try:
        img = Image.open(src)
        if img.mode in ("RGBA", "P") and fmt in ("jpg", "jpeg"):
            img = img.convert("RGB")
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if fmt in ("jpg", "jpeg"):
            # Ensure quality is properly applied
            actual_quality = min(100, max(1, quality))
            img.save(dest, "JPEG", quality=actual_quality, optimize=True, progressive=True)
        else:
            # For PNG, adjust compression level based on quality
            actual_quality = min(100, max(1, quality))
            level = round(9 - (actual_quality / 100) * 9)
            img.save(dest, "PNG", compress_level=level, optimize=True)
        
        compressed_size = dest.stat().st_size if dest.exists() else 0
        # If compressed is not smaller, discard and signal caller to keep original
        if compressed_size >= original_size:
            dest.unlink(missing_ok=True)
            return False, original_size, original_size
        return True, original_size, compressed_size
    except Exception as e:
        print(f"Compression error for {src}: {e}")
        if dest.exists():
            dest.unlink(missing_ok=True)
        return False, original_size, original_size


def apply_compress(
    base_path: str,
    output_folder: str,
    fmt: str = "jpg",
    quality: int = 70,
    log_callback: Callable[[str], None] | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> tuple[bool, list[str]]:
    """
    Compress images in base_path/<output_folder>/<episode>/*.
    progress_callback(done, total, filename) fires after each file.
    Returns (success, log_lines).
    """
    base = Path(base_path)
    out_dir = base / output_folder
    if not out_dir.exists():
        return False, [f"Output folder ไม่พบ: {out_dir}"]

    if not HAS_PIL:
        return False, ["ไม่มี Pillow ไม่สามารถย่อภาพได้"]

    fmt = (fmt or "jpg").strip().lower()
    if fmt not in ("jpg", "jpeg", "png"):
        fmt = "jpg"
    quality = min(100, max(1, int(quality) if quality else 70))

    log: list[str] = []

    def _log(msg: str) -> None:
        log.append(msg)
        if log_callback:
            log_callback(msg)

    # Pre-count total images for progress_callback
    all_image_files: list[Path] = []
    for ep_dir in sorted(out_dir.iterdir()):
        if not ep_dir.is_dir():
            continue
        for f in ep_dir.iterdir():
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith("9999"):
                all_image_files.append(f)
    grand_total = len(all_image_files)
    grand_done = 0

    total = 0
    total_original_size = 0
    total_compressed_size = 0

    try:
        for ep_dir in sorted(out_dir.iterdir()):
            if not ep_dir.is_dir():
                continue
            
            # Get and sort image files numerically
            image_files = []
            for f in ep_dir.iterdir():
                if not f.is_file() or f.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                # Skip credit files
                if f.name.startswith("9999"):
                    continue
                image_files.append(f)
            
            # Sort files numerically (1, 2, 3... 99)
            image_files.sort(key=lambda x: _natural_sort_key(x.name))
            
            if not image_files:
                continue
                
            count = 0
            ep_original_size = 0
            ep_compressed_size = 0
            
            _log(f"กำลังย่อ {ep_dir.name} ({len(image_files)} ภาพ)...")
            
            for i, f in enumerate(image_files, 1):
                # Calculate progress percentage
                progress = (i / len(image_files)) * 100
                
                if fmt in ("jpg", "jpeg"):
                    new_name = f.stem + ".jpg"
                else:
                    new_name = f.stem + ".png"
                
                tmp = ep_dir / (f.stem + "._tmp_compress")
                
                # Show progress with filename
                _log(f"  [{i}/{len(image_files)}] {progress:.1f}% - กำลังย่อ {f.name}")
                
                success, orig_size, comp_size = _compress_file(f, tmp, fmt, quality)

                dest = ep_dir / new_name
                if success:
                    if tmp.exists():
                        tmp.replace(dest)  # replace() overwrites on Windows (no WinError 183)
                    if f.exists() and f.resolve() != dest.resolve():
                        f.unlink()
                    count += 1
                    ep_original_size += orig_size
                    ep_compressed_size += comp_size

                    if orig_size > 0:
                        reduction = ((orig_size - comp_size) / orig_size) * 100
                        _log(f"      ✓ ลดขนาด {reduction:.1f}% ({orig_size//1024}KB → {comp_size//1024}KB)")
                else:
                    # tmp already cleaned up in _compress_file; keep original
                    if tmp.exists():
                        tmp.unlink(missing_ok=True)
                    if orig_size == comp_size:
                        _log(f"      − ไม่ลดขนาด เก็บต้นฉบับ ({orig_size//1024}KB)")
                    else:
                        _log(f"      ✗ ย่อไม่สำเร็จ เก็บต้นฉบับ")

                # Always advance progress after each file (success or not)
                grand_done += 1
                if progress_callback:
                    progress_callback(grand_done, grand_total, f.name)
            
            total += count
            total_original_size += ep_original_size
            total_compressed_size += ep_compressed_size
            
            # Show episode summary
            if ep_original_size > 0:
                ep_reduction = ((ep_original_size - ep_compressed_size) / ep_original_size) * 100
                _log(f"✓ {ep_dir.name} เสร็จ ({count} ภาพ, ลดขนาด {ep_reduction:.1f}%)")
            else:
                _log(f"✓ {ep_dir.name} เสร็จ ({count} ภาพ)")
        
        # Show final summary
        if total_original_size > 0:
            total_reduction = ((total_original_size - total_compressed_size) / total_original_size) * 100
            _log(f"ย่อไฟล์ทั้งหมดเสร็จ ({total} ภาพ, {fmt.upper()} {quality}%)")
            _log(f"ขนาดรวม: {total_original_size//1024//1024}MB → {total_compressed_size//1024//1024}MB (ลด {total_reduction:.1f}%)")
        else:
            _log(f"ย่อไฟล์เสร็จ ({total} ภาพ, {fmt.upper()} {quality}%)")
            
        return True, log
    except Exception as e:
        _log(f"ผิดพลาด: {e}")
        return False, log
