"""Right panel: Function toggles + Settings + Output preview + Execute."""

import threading
from pathlib import Path
from typing import Callable

import flet as ft

from app.collectors.credit import default_credit_path
from app.config import load_config, save_config
from app.gui.constants import FUNC_ICONS, FUNC_LABELS, FUNC_ORDER, build_folder_name
from app.gui.styles import chip_disabled, chip_off, chip_on, fmt_style
from app.theme import (
    CARD_BG, CARD_BORDER, PINK, PINK_LIGHT, PINK_SOFT,
    SUCCESS, TEXT_MUTED, TEXT_WHITE, opacity,
)


def build_right_panel(
    page: ft.Page,
    file_picker: ft.FilePicker,
    selected_funcs: set[str],
    parent_path_ref: dict,
    selected_paths_ref: dict,
) -> ft.Container:

    cfg = load_config()

    # ── Credit settings ──────────────────────────────────────────────────
    # โหลดรายการไฟล์เครดิตที่บันทึกไว้ (credit_paths เป็น list)
    # รองรับ backward-compat: ถ้ายังไม่มี credit_paths ลองดึง default
    saved_credit_paths: list[str] = cfg.get("credit_paths") or []
    default_cred = default_credit_path()
    if not saved_credit_paths and Path(default_cred).exists():
        saved_credit_paths = [default_cred]
    # เก็บรายการใน dict เพื่อให้ closure แก้ค่าได้
    credit_paths_ref: dict[str, list[str]] = {
        "value": [p for p in saved_credit_paths if Path(p).exists()]
    }

    # ListView แสดงรายการไฟล์ที่เลือก (แต่ละแถว = 1 ไฟล์ + ปุ่มลบ)
    _credit_list = ft.ListView(spacing=2, padding=0)

    def _rebuild_credit_list() -> None:
        """วาดรายการไฟล์เครดิตใหม่ทั้งหมด"""
        _credit_list.controls.clear()
        for idx, path in enumerate(credit_paths_ref["value"]):
            file_name = Path(path).name
            # ปุ่มลบต้องจำ index ณ เวลาที่สร้าง
            def _make_remove(i: int):
                def _remove(e: ft.ControlEvent) -> None:
                    credit_paths_ref["value"].pop(i)
                    _save_cfg()
                    _rebuild_credit_list()
                    page.update()
                return _remove
            row = ft.Row(
                [
                    ft.Icon(ft.Icons.IMAGE_OUTLINED, color=PINK, size=14),
                    ft.Text(
                        file_name, size=12, color=TEXT_MUTED,
                        expand=True, no_wrap=True,
                        tooltip=path,  # hover เห็น full path
                    ),
                    ft.IconButton(
                        ft.Icons.CLOSE, icon_color=TEXT_MUTED, icon_size=14,
                        tooltip="ลบออก", padding=2,
                        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=2),
                        on_click=_make_remove(idx),
                    ),
                ],
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            _credit_list.controls.append(row)
        # ถ้าไม่มีไฟล์ → แสดงข้อความบอก
        if not credit_paths_ref["value"]:
            _credit_list.controls.append(
                ft.Text("ยังไม่ได้เลือกไฟล์เครดิต", size=11, color=TEXT_MUTED, italic=True)
            )

    _rebuild_credit_list()

    credit_browse_btn = ft.IconButton(
        ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED, tooltip="เพิ่มไฟล์เครดิต (เลือกได้หลายไฟล์)",
        icon_color=PINK, icon_size=20,
        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=8),
    )

    async def on_credit_browse(e: ft.ControlEvent) -> None:
        """เปิด file picker เลือกได้หลายไฟล์ แล้วเพิ่มเข้า list (ไม่ซ้ำ)"""
        result = await file_picker.pick_files(
            dialog_title="เลือกไฟล์เครดิต (เลือกได้หลายไฟล์)",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["png", "jpg", "jpeg"],
            allow_multiple=True,
        )
        if result and result.files:
            existing = set(credit_paths_ref["value"])
            for f in result.files:
                if f.path and f.path not in existing:
                    credit_paths_ref["value"].append(f.path)
                    existing.add(f.path)
            _save_cfg()
            _rebuild_credit_list()
            page.update()

    credit_browse_btn.on_click = on_credit_browse

    credit_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.COLLECTIONS_OUTLINED, color=PINK, size=14),
                        ft.Text("ไฟล์เครดิต", size=12, color=TEXT_MUTED, expand=True),
                        credit_browse_btn,
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                _credit_list,
            ],
            spacing=2,
        ),
    )

    # ── Compress settings ────────────────────────────────────────────────
    compress_fmt_ref: dict[str, str] = {
        "value": (cfg.get("compress_format") or "jpg").strip().lower()
    }
    if compress_fmt_ref["value"] not in ("jpg", "png"):
        compress_fmt_ref["value"] = "jpg"
    compress_q = cfg.get("compress_quality", 70)
    compress_q = min(100, max(1, int(compress_q) if compress_q else 70))

    quality_field = ft.TextField(
        value=str(compress_q), label="คุณภาพ %", width=90,
        border_radius=10, border_color=CARD_BORDER, focused_border_color=PINK,
        keyboard_type=ft.KeyboardType.NUMBER, text_size=13, height=42,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
    )
    quality_field.on_change = lambda e: _save_cfg()

    btn_jpg = ft.FilledTonalButton(
        "JPG", style=fmt_style(compress_fmt_ref["value"] == "jpg"),
        height=36, on_click=lambda e: _set_fmt("jpg"),
    )
    btn_png = ft.FilledTonalButton(
        "PNG", style=fmt_style(compress_fmt_ref["value"] == "png"),
        height=36, on_click=lambda e: _set_fmt("png"),
    )

    def _set_fmt(fmt: str) -> None:
        compress_fmt_ref["value"] = fmt
        btn_jpg.style = fmt_style(fmt == "jpg")
        btn_png.style = fmt_style(fmt == "png")
        _save_cfg()
        page.update()

    compress_section = ft.Container(
        content=ft.Row(
            [ft.Text("รูปแบบ:", size=13, color=TEXT_MUTED), btn_jpg, btn_png,
             ft.Container(width=8), quality_field],
            spacing=8, alignment=ft.MainAxisAlignment.START,
        ),
    )

    # ── Split settings ───────────────────────────────────────────────────
    split_parts = cfg.get("split_parts", 2)
    split_parts = min(20, max(2, int(split_parts) if split_parts else 2))

    split_parts_field = ft.TextField(
        value=str(split_parts), label="หั่นเป็นกี่ชิ้น",
        width=100,
        border_radius=10, border_color=CARD_BORDER, focused_border_color=PINK,
        keyboard_type=ft.KeyboardType.NUMBER, text_size=13, height=42,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
    )
    split_parts_field.on_change = lambda e: _save_cfg()

    split_section = ft.Container(
        content=ft.Row(
            [ft.Text("หั่นแนวนอน (บน→ล่าง):", size=13, color=TEXT_MUTED),
             split_parts_field, ft.Text("ชิ้น", size=13, color=TEXT_MUTED)],
            spacing=8, alignment=ft.MainAxisAlignment.START,
        ),
    )

    # ── Output preview ───────────────────────────────────────────────────
    output_label = ft.Text("", size=14, color=PINK_LIGHT, weight=ft.FontWeight.W_600, italic=True)
    output_preview = ft.Container(
        content=ft.Row(
            [ft.Icon(ft.Icons.FOLDER_SPECIAL, color=PINK, size=18),
             ft.Text("Output:", size=13, color=TEXT_MUTED), output_label],
            spacing=8,
        ),
        visible=False,
    )

    # ── Config persistence ───────────────────────────────────────────────
    def _save_cfg() -> None:
        c = load_config()
        c["selected_functions"] = sorted(selected_funcs)
        c["credit_paths"] = credit_paths_ref["value"]  # บันทึกเป็น list
        c["compress_format"] = compress_fmt_ref["value"]
        try:
            c["compress_quality"] = min(100, max(1, int(quality_field.value or "70")))
        except (ValueError, TypeError):
            c["compress_quality"] = 70
        try:
            c["split_parts"] = min(20, max(2, int(split_parts_field.value or "2")))
        except (ValueError, TypeError):
            c["split_parts"] = 2
        save_config(c)

    # ── Function toggle logic ────────────────────────────────────────────
    func_buttons: dict[str, ft.FilledTonalButton] = {}

    def _refresh_func_ui() -> None:
        has_raw = "raw" in selected_funcs
        has_res = "res" in selected_funcs
        has_trans_or_text = ("trans" in selected_funcs) or ("text" in selected_funcs)

        for key, btn in func_buttons.items():
            is_active = key in selected_funcs
            disabled = False
            if key == "inp" and not has_raw:
                disabled = True
            if key == "split" and not has_res:
                disabled = True
            if key == "com" and not has_res:
                disabled = True
            if key == "ep" and not has_trans_or_text:
                disabled = True

            btn.disabled = disabled
            if disabled:
                btn.style = chip_disabled()
                selected_funcs.discard(key)
            elif is_active:
                btn.style = chip_on()
            else:
                btn.style = chip_off()

        folder_name = build_folder_name(selected_funcs)
        if folder_name:
            output_label.value = folder_name + "/"
            output_preview.visible = True
        else:
            output_preview.visible = False
        _save_cfg()

    def _on_func_click(key: str) -> Callable:
        def handler(e: ft.ControlEvent) -> None:
            if key in selected_funcs:
                selected_funcs.discard(key)
            else:
                if key == "raw":
                    selected_funcs.discard("res")
                elif key == "res":
                    selected_funcs.discard("raw")
                selected_funcs.add(key)
            _refresh_func_ui()
            page.update()
        return handler

    for key in FUNC_ORDER:
        btn = ft.FilledTonalButton(
            content=ft.Row(
                [ft.Icon(FUNC_ICONS[key], size=18), ft.Text(FUNC_LABELS[key], size=13)],
                spacing=6, tight=True,
            ),
            style=chip_off(), height=38, on_click=_on_func_click(key),
        )
        func_buttons[key] = btn

    _refresh_func_ui()

    # ── Progress panel ─────────────────────────────────────────────────
    _progress_bar = ft.ProgressBar(
        value=0, color=PINK, bgcolor=CARD_BORDER,
        border_radius=4, height=6,
    )
    _progress_label = ft.Text("", size=12, color=TEXT_MUTED)
    _log_list = ft.ListView(
        spacing=2, padding=ft.padding.symmetric(horizontal=8, vertical=6),
        auto_scroll=True, expand=True,
    )

    def _copy_log(e: ft.ControlEvent) -> None:
        lines = [c.value for c in _log_list.controls if hasattr(c, "value")]
        page.clipboard = "\n".join(lines)
        _toast("คัดลอก log แล้ว")

    _copy_btn = ft.IconButton(
        ft.Icons.COPY_ALL_OUTLINED, tooltip="คัดลอก log ทั้งหมด",
        icon_color=TEXT_MUTED, icon_size=16,
        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=4),
        on_click=_copy_log,
    )

    _progress_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.TERMINAL, color=PINK, size=18),
                        bgcolor=opacity(PINK_SOFT, 0.2), border_radius=6, padding=6,
                    ),
                    ft.Text("ความคืบหน้า", size=14, weight=ft.FontWeight.W_600, color=TEXT_WHITE),
                    ft.Container(expand=True),
                    _progress_label,
                    _copy_btn,
                ], spacing=6),
                ft.Divider(height=1, color=CARD_BORDER),
                _progress_bar,
                ft.Container(
                    content=_log_list,
                    expand=True,
                    border_radius=8,
                    bgcolor=opacity(CARD_BORDER, 0.4),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
            ],
            spacing=6, expand=True,
        ),
        padding=14, border_radius=14, bgcolor=CARD_BG,
        border=ft.border.all(1, CARD_BORDER),
        expand=True,
    )

    _progress_state: dict = {"total": 0, "done": 0}

    def _progress_reset(total_files: int) -> None:
        _progress_state["total"] = total_files
        _progress_state["done"] = 0
        _progress_bar.value = 0
        _progress_label.value = ""
        _log_list.controls.clear()
        page.update()

    def _progress_log(msg: str, color: str = TEXT_MUTED, advance: bool = False) -> None:
        if advance:
            _progress_state["done"] += 1
            done = _progress_state["done"]
            total = _progress_state["total"]
            _progress_bar.value = done / total if total else 0
            _progress_label.value = f"{done} / {total}"
        _log_list.controls.append(
            ft.Text(msg, size=11, color=color, selectable=True, no_wrap=False)
        )
        page.update()

    def _progress_done() -> None:
        _progress_bar.value = 1
        page.update()

    # ── Toast ────────────────────────────────────────────────────────────
    _snackbar = ft.SnackBar(content=ft.Text(""), duration=4000, bgcolor=CARD_BG)
    page.overlay.append(_snackbar)

    def _toast(msg: str, error: bool = False) -> None:
        icon = ft.Icons.ERROR_OUTLINE if error else ft.Icons.CHECK_CIRCLE_OUTLINE
        color = "#EF4444" if error else SUCCESS
        _snackbar.content = ft.Row(
            [ft.Icon(icon, color=color, size=20), ft.Text(msg, color=TEXT_WHITE, size=13)],
            spacing=10,
        )
        _snackbar.bgcolor = CARD_BG
        _snackbar.open = True
        page.update()

    # ── Execute ──────────────────────────────────────────────────────────
    btn_execute = ft.ElevatedButton(
        "Execute",
        style=ft.ButtonStyle(
            color=TEXT_WHITE, bgcolor=PINK,
            overlay_color=opacity(PINK_LIGHT, 0.3),
            padding=ft.padding.symmetric(horizontal=32, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=12), elevation=0,
        ),
        height=48, icon=ft.Icons.PLAY_ARROW,
    )

    def _do_execute(
        selected_stories: list,
        funcs: set,
        folder_name: str,
        cred_path: list[str] | None,  # รับ list ของ paths
        comp_fmt: str,
        comp_q: int,
        parts: int,
    ) -> None:
        from app.collectors.compress import apply_compress
        from app.collectors.credit import apply_credit
        from app.collectors.split import apply_split
        from app.collectors.inpainted import collect_inpainted
        from app.collectors.raw import collect_raw
        from app.collectors.res import collect_res
        from app.collectors.text import collect_text
        from app.collectors.trans import collect_trans

        ok_count = 0
        err_msg = None

        try:
            for story_idx, base_path in enumerate(selected_stories):
                story_name = Path(base_path).name
                story_ok = True

                _progress_log(f"── {story_name} ({story_idx+1}/{len(selected_stories)}) ──",
                              color=PINK_LIGHT)

                # Phase 1: collect base files
                if "raw" in funcs:
                    _progress_log("  ดึงไฟล์ดิบ (raw)...", color=TEXT_MUTED)
                    ok, logs = collect_raw(base_path, folder_name)
                    for l in logs:
                        _progress_log(f"    {l}", color=TEXT_MUTED)
                    if not ok:
                        story_ok = False

                if "inp" in funcs:
                    _progress_log("  ดึงไฟล์คลีน (inp)...", color=TEXT_MUTED)
                    ok, logs = collect_inpainted(base_path, folder_name)
                    for l in logs:
                        _progress_log(f"    {l}", color=TEXT_MUTED)
                    if not ok:
                        story_ok = False

                if "res" in funcs:
                    _progress_log("  ดึงไฟล์ลงคำ (res)...", color=TEXT_MUTED)
                    ok, logs = collect_res(base_path, folder_name)
                    for l in logs:
                        _progress_log(f"    {l}", color=TEXT_MUTED)
                    if not ok:
                        story_ok = False

                if "trans" in funcs:
                    _progress_log("  ดึงไฟล์แปล (trans)...", color=TEXT_MUTED)
                    ok, logs = collect_trans(base_path, folder_name, per_episode="ep" in funcs)
                    for l in logs:
                        _progress_log(f"    {l}", color=TEXT_MUTED)
                    if not ok:
                        story_ok = False

                if "text" in funcs:
                    _progress_log("  ดึงไฟล์ถอดคำ (text)...", color=TEXT_MUTED)
                    ok, logs = collect_text(base_path, folder_name, per_episode="ep" in funcs)
                    for l in logs:
                        _progress_log(f"    {l}", color=TEXT_MUTED)
                    if not ok:
                        story_ok = False

                # Phase 2: post-processing
                if "split" in funcs:
                    _progress_log("  หั่นภาพ (split)...", color=TEXT_MUTED)
                    apply_split(base_path, folder_name, parts=parts)

                if "cred" in funcs and cred_path:
                    n = len(cred_path)
                    _progress_log(f"  เพิ่มเครดิต {n} ไฟล์ (cred)...", color=TEXT_MUTED)
                    ok, logs = apply_credit(base_path, folder_name, cred_path)
                    for l in logs:
                        _progress_log(f"    {l}", color=TEXT_MUTED)
                    if not ok:
                        story_ok = False

                if "com" in funcs:
                    _progress_log("  ย่อไฟล์ (com)...", color=PINK_LIGHT)

                    def _com_log(msg: str) -> None:
                        stripped = msg.strip()
                        color = SUCCESS if stripped.startswith("✓") else TEXT_MUTED
                        _progress_log(f"    {msg}", color=color)

                    def _com_progress(done: int, total: int, filename: str) -> None:
                        _progress_state["total"] = total
                        _progress_state["done"] = done
                        _progress_bar.value = done / total if total else 0
                        _progress_label.value = f"{done} / {total}  ({filename})"
                        page.update()

                    apply_compress(base_path, folder_name, comp_fmt, comp_q,
                                   log_callback=_com_log,
                                   progress_callback=_com_progress)

                if story_ok:
                    ok_count += 1
                    _progress_log(f"  ✓ {story_name} เสร็จ", color=SUCCESS)
                else:
                    _progress_log(f"  ✗ {story_name} มีข้อผิดพลาด", color="#EF4444")

        except Exception as ex:
            err_msg = str(ex)
            _progress_log(f"ผิดพลาด: {ex}", color="#EF4444")
        finally:
            _progress_done()
            btn_execute.disabled = False
            btn_execute.text = "Execute"
            if err_msg:
                _toast(f"ผิดพลาด: {err_msg}", error=True)
            else:
                _toast(f"เสร็จแล้ว {ok_count} เรื่อง → {folder_name}/")
            page.update()

    def run_execute(e: ft.ControlEvent) -> None:
        parent = parent_path_ref["value"]
        if not parent:
            _toast("กรุณาเลือกโฟลเดอร์ workspace ก่อน", error=True)
            return
        selected_stories = list(selected_paths_ref["value"])
        if not selected_stories:
            _toast("กรุณาเลือกอย่างน้อย 1 เรื่อง", error=True)
            return
        funcs = selected_funcs.copy()
        if not funcs & {"raw", "res", "trans", "text"}:
            _toast("กรุณาเลือกอย่างน้อย 1 ฟังก์ชัน (raw/res/trans/text)", error=True)
            return

        folder_name = build_folder_name(funcs)
        if not folder_name:
            return

        cred_path = credit_paths_ref["value"] if "cred" in funcs else None
        try:
            comp_q = min(100, max(1, int(quality_field.value or "70")))
        except (ValueError, TypeError):
            comp_q = 70
        comp_fmt = compress_fmt_ref["value"]
        try:
            parts = min(20, max(2, int(split_parts_field.value or "2")))
        except (ValueError, TypeError):
            parts = 2

        btn_execute.disabled = True
        btn_execute.text = "กำลังทำงาน..."
        _progress_reset(0)
        page.update()

        threading.Thread(
            target=_do_execute,
            args=(selected_stories, funcs, folder_name, cred_path, comp_fmt, comp_q, parts),
            daemon=True,
        ).start()

    btn_execute.on_click = run_execute

    # ── Layout ───────────────────────────────────────────────────────────
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Container(content=ft.Icon(ft.Icons.DASHBOARD, color=PINK, size=18),
                                             bgcolor=opacity(PINK_SOFT, 0.2), border_radius=6, padding=6),
                                ft.Text("ฟังก์ชัน", size=14, weight=ft.FontWeight.W_600, color=TEXT_WHITE),
                            ], spacing=10),
                            ft.Divider(height=1, color=CARD_BORDER),
                            ft.Container(height=4),
                            ft.Text("แหล่งภาพ (เลือกได้อย่างเดียว)", size=11, color=TEXT_MUTED),
                            ft.Row([func_buttons["raw"], func_buttons["res"]], spacing=8),
                            ft.Container(height=4),
                            ft.Text("ตัวเลือกเพิ่มเติม", size=11, color=TEXT_MUTED),
                            ft.Row(
                                [func_buttons["inp"], func_buttons["split"], func_buttons["trans"],
                                 func_buttons["text"], func_buttons["ep"], func_buttons["cred"],
                                 func_buttons["com"]],
                                spacing=8, wrap=True, run_spacing=8,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=14, border_radius=14, bgcolor=CARD_BG,
                    border=ft.border.all(1, CARD_BORDER),
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Container(content=ft.Icon(ft.Icons.SETTINGS, color=PINK, size=18),
                                             bgcolor=opacity(PINK_SOFT, 0.2), border_radius=6, padding=6),
                                ft.Text("ตั้งค่า", size=14, weight=ft.FontWeight.W_600, color=TEXT_WHITE),
                            ], spacing=10),
                            ft.Divider(height=1, color=CARD_BORDER),
                            ft.Container(height=4),
                            credit_section,
                            split_section,
                            compress_section,
                            output_preview,
                        ],
                        spacing=6,
                    ),
                    padding=14, border_radius=14, bgcolor=CARD_BG,
                    border=ft.border.all(1, CARD_BORDER),
                ),
                ft.Container(height=8),
                _progress_panel,
                ft.Container(height=8),
                ft.Row([btn_execute], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=0, expand=True,
        ),
        expand=3,
    )
