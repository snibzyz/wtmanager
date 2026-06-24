"""WTManager — CustomTkinter UI.

หน้าจอเดียว แบ่งซ้าย/ขวา เหมือนเวอร์ชัน Flet เดิม:
  ซ้าย  = เลือก workspace + เลือกเรื่อง
  ขวา   = เลือกฟังก์ชัน + ตั้งค่า + log/ความคืบหน้า + Execute

หลักการความปลอดภัย: Tkinter เป็น single-thread. งานหนักรันใน background
thread แล้วส่งงานอัปเดต UI กลับมาที่ main thread ผ่าน queue (pump ด้วย after()).
ไม่มีการแตะ widget ข้าม thread เลย.
"""

from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import TclError, filedialog

import customtkinter as ctk

# ── Logic เดิม (ไม่แตะ ใช้ร่วมกับเวอร์ชัน Flet) ────────────────────────────
from app.collectors.compress import apply_compress
from app.collectors.credit import apply_credit, default_credit_path
from app.collectors.inpainted import collect_inpainted
from app.collectors.raw import collect_raw
from app.collectors.res import collect_res
from app.collectors.split import apply_split
from app.collectors.text import collect_text
from app.collectors.trans import collect_trans
from app.config import load_config, save_config
from app.paths import canonical_file
from app.workspace import (
    get_last_workspace, get_workspace_subfolders, set_last_workspace,
)

from app.gui_ctk import icons
from app.gui_ctk.constants import (
    EXTRA_FUNCS, FUNC_ICON, FUNC_LABELS, SOURCE_FUNCS, build_folder_name,
)
from app.gui_ctk.theme import (
    BADGE_BG, CARD_BORDER, CARD_FG, CHIP_DISABLED_TEXT, ERROR, LOG_BG, PINK,
    PINK_LIGHT, SUCCESS, TEXT_MUTED, TEXT_WHITE, WARN, WINDOW_BG, chip_style,
    font,
)
from app.gui_ctk.widgets import make_card, section_header


# ── ตัวช่วยกำหนดสีบรรทัด log (ตาม "เนื้อหา" ของบรรทัด เหมือนเวอร์ชันเดิม) ──
def _color_collect(line: str) -> str:
    s = line.strip()
    if "ผิดพลาด" in line or ("ไม่พบ" in line and "✓" not in s):
        return "error"
    if s.startswith("✓"):
        return "success"
    return "muted"


def _color_split(line: str) -> str:
    s = line.strip()
    if "ไม่ได้:" in line or "⊗" in line or "ผิดพลาด" in line or "ไม่พบ" in line:
        return "error"
    if s.startswith("⚠"):
        return "warn"
    if s.startswith("−"):
        return "muted"
    if s.startswith("✓") or "หั่นภาพเสร็จ" in s:
        return "success"
    if s.startswith("ตอน [") or "แบ่งเป็น" in s:
        return "pink"
    return "muted"


def _color_credit(line: str) -> str:
    s = line.strip()
    if "ผิดพลาด" in line:
        return "error"
    if "เสร็จ" in s and "เครดิต" in s:
        return "success"
    if s.startswith("เครดิต") or s.lstrip().startswith("•"):
        return "pink"
    return "muted"


def _color_compress(line: str) -> str:
    s = line.strip()
    if "ผิดพลาด" in line or s.startswith("✗"):
        return "error"
    if s.startswith("✓"):
        return "success"
    return "muted"


def _clampi(value, lo: int, hi: int, default: int) -> int:
    try:
        return min(hi, max(lo, int(value)))
    except (ValueError, TypeError):
        return default


def _short(name: str, n: int = 22) -> str:
    return name if len(name) <= n else name[: n - 1] + "…"


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        # ── window ──
        from app import __version__
        self.title(f"WTManager {__version__}")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=WINDOW_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._closing = False
        self._running = False

        # ── state ──
        cfg = load_config()
        self.parent_path: str = get_last_workspace()
        self.selected_paths: set[str] = set()
        self.story_buttons: dict[str, ctk.CTkButton] = {}
        self.selected_funcs: set[str] = set(cfg.get("selected_functions", []))
        self._func_disabled: set[str] = set()
        self.func_buttons: dict[str, ctk.CTkButton] = {}

        saved_credit: list[str] = cfg.get("credit_paths") or []
        default_cred = default_credit_path()
        if not saved_credit and Path(default_cred).exists():
            saved_credit = [default_cred]
        self.credit_paths: list[str] = [
            c for p in saved_credit if (c := canonical_file(p))
        ]

        self.compress_fmt: str = (cfg.get("compress_format") or "jpg").strip().lower()
        if self.compress_fmt not in ("jpg", "png"):
            self.compress_fmt = "jpg"
        comp_q = _clampi(cfg.get("compress_quality", 70), 1, 100, 70)
        split_parts = _clampi(cfg.get("split_parts", 2), 2, 20, 2)

        self.quality_var = ctk.StringVar(value=str(comp_q))
        self.split_var = ctk.StringVar(value=str(split_parts))
        self.quality_var.trace_add("write", lambda *a: self._save_cfg())
        self.split_var.trace_add("write", lambda *a: self._save_cfg())

        # ── UI <- worker bridge ──
        self._ui_queue: "queue.Queue" = queue.Queue()

        # ── build ──
        self._build_header()
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        body.grid_columnconfigure(0, weight=2, uniform="col")
        body.grid_columnconfigure(1, weight=3, uniform="col")
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        self._build_left(left)
        self._build_right(right)

        # toast overlay (วางทับด้วย place ทีหลัง)
        self._toast_after = None
        self.toast = ctk.CTkFrame(
            self, corner_radius=10, fg_color=CARD_FG,
            border_width=1, border_color=CARD_BORDER,
        )
        self.toast_label = ctk.CTkLabel(
            self.toast, text="", font=font(12), text_color=TEXT_WHITE,
            justify="left", wraplength=640,
        )
        self.toast_label.pack(padx=14, pady=10)

        # โหลดสถานะเริ่มต้น
        if self.parent_path:
            self._apply_folder(self.parent_path)
        self._refresh_func_ui()

        # เริ่ม pump queue + ขยายเต็มจอ
        self.after(40, self._pump)
        self.after(120, self._safe_zoom)

    # ════════════════════════════════════════════════════════════════════
    #  HEADER
    # ════════════════════════════════════════════════════════════════════
    def _build_header(self) -> None:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=16, pady=(14, 8))

        badge = ctk.CTkLabel(
            bar, text="WT", fg_color=PINK, text_color=TEXT_WHITE,
            corner_radius=12, width=44, height=44, font=font(16, bold=True),
        )
        badge.pack(side="left")
        ctk.CTkLabel(
            bar, text="WTManager", text_color=TEXT_WHITE, font=font(22, bold=True),
        ).pack(side="left", padx=(14, 0))
        from app import __version__
        ctk.CTkLabel(
            bar, text=f"workspace collector · v{__version__}",
            text_color=TEXT_MUTED, font=font(11),
        ).pack(side="right")

    # ════════════════════════════════════════════════════════════════════
    #  LEFT: workspace + stories
    # ════════════════════════════════════════════════════════════════════
    def _build_left(self, parent) -> None:
        # workspace card
        ws_card = make_card(parent)
        ws_card.pack(fill="x")
        section_header(ws_card, "Workspace", icon="folder")
        ws_row = ctk.CTkFrame(ws_card, fg_color="transparent")
        ws_row.pack(fill="x", padx=14, pady=(0, 14))
        self.workspace_label = ctk.CTkLabel(
            ws_row,
            text=self.parent_path or "ยังไม่ได้เลือก",
            text_color=TEXT_WHITE if self.parent_path else TEXT_MUTED,
            font=font(12), anchor="w",
        )
        self.workspace_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            ws_row, text="เลือก", width=92, height=34, corner_radius=10,
            font=font(12, bold=True), fg_color=PINK, hover_color="#C75A7A",
            text_color=TEXT_WHITE, image=icons.glyph("folder", 15, TEXT_WHITE),
            compound="left", command=self._pick_workspace,
        ).pack(side="right")

        # stories card
        st_card = make_card(parent)
        st_card.pack(fill="both", expand=True, pady=(14, 0))
        section_header(st_card, "เรื่อง", icon="library")

        actions = ctk.CTkFrame(st_card, fg_color="transparent")
        actions.pack(fill="x", padx=14)
        ctk.CTkButton(
            actions, text="เลือกทั้งหมด", width=110, height=30, corner_radius=8,
            font=font(12), fg_color="transparent", hover_color=BADGE_BG,
            text_color=PINK, border_width=1, border_color=CARD_BORDER,
            image=icons.glyph("check", 14, PINK), compound="left",
            command=self._select_all,
        ).pack(side="right", padx=(6, 0))
        ctk.CTkButton(
            actions, text="ล้าง", width=72, height=30, corner_radius=8,
            font=font(12), fg_color="transparent", hover_color=BADGE_BG,
            text_color=TEXT_MUTED, border_width=1, border_color=CARD_BORDER,
            image=icons.glyph("close", 13, TEXT_MUTED), compound="left",
            command=self._clear_all,
        ).pack(side="right")

        self.stories_frame = ctk.CTkScrollableFrame(
            st_card, fg_color="transparent",
        )
        self.stories_frame.pack(fill="both", expand=True, padx=8, pady=(8, 12))
        self.stories_frame.grid_columnconfigure((0, 1), weight=1, uniform="story")
        self._stories_placeholder()

    def _stories_placeholder(self, text: str = "เลือกโฟลเดอร์ workspace ก่อน") -> None:
        for w in self.stories_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.stories_frame, text=text, text_color=TEXT_MUTED, font=font(12),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=6)

    # ════════════════════════════════════════════════════════════════════
    #  RIGHT: functions + settings + progress + execute
    # ════════════════════════════════════════════════════════════════════
    def _build_right(self, parent) -> None:
        # functions card
        fn_card = make_card(parent)
        fn_card.pack(fill="x")
        section_header(fn_card, "ฟังก์ชัน", icon="functions")

        ctk.CTkLabel(
            fn_card, text="ดึงไฟล์ (เลือกได้หลายอย่าง)", text_color=TEXT_MUTED,
            font=font(11), anchor="w",
        ).pack(fill="x", padx=14)
        src_row = ctk.CTkFrame(fn_card, fg_color="transparent")
        src_row.pack(fill="x", padx=14, pady=(2, 8))
        for c in range(len(SOURCE_FUNCS)):
            src_row.grid_columnconfigure(c, weight=1, uniform="src")
        for idx, key in enumerate(SOURCE_FUNCS):
            self._make_chip(src_row, key).grid(
                row=0, column=idx, sticky="ew", padx=3, pady=3
            )

        ctk.CTkLabel(
            fn_card, text="ตัวเลือกเพิ่มเติม", text_color=TEXT_MUTED,
            font=font(11), anchor="w",
        ).pack(fill="x", padx=14)
        extra = ctk.CTkFrame(fn_card, fg_color="transparent")
        extra.pack(fill="x", padx=14, pady=(2, 14))
        for c in range(4):
            extra.grid_columnconfigure(c, weight=1, uniform="fn")
        for idx, key in enumerate(EXTRA_FUNCS):
            r, c = divmod(idx, 4)
            self._make_chip(extra, key).grid(
                row=r, column=c, sticky="ew", padx=3, pady=3
            )

        # settings card
        set_card = make_card(parent)
        set_card.pack(fill="x", pady=(14, 0))
        section_header(set_card, "ตั้งค่า", icon="settings")
        self._build_credit_section(set_card)
        self._build_split_section(set_card)
        self._build_compress_section(set_card)
        self.output_label = ctk.CTkLabel(
            set_card, text="", text_color=PINK_LIGHT, font=font(13, bold=True),
            anchor="w",
        )
        self.output_label.pack(fill="x", padx=14, pady=(2, 14))

        # progress card
        self._build_progress(parent)

        # execute button
        self.btn_execute = ctk.CTkButton(
            parent, text="Execute", height=48, width=200, corner_radius=12,
            font=font(15, bold=True), fg_color=PINK, hover_color="#C75A7A",
            text_color=TEXT_WHITE, image=icons.glyph("play", 18, TEXT_WHITE),
            compound="left", command=self._on_execute,
        )
        self.btn_execute.pack(pady=(14, 0))

    # ── function chips ──
    _CHIP_ICON_COLOR = {"on": TEXT_WHITE, "off": PINK, "disabled": CHIP_DISABLED_TEXT}

    def _chip_icon(self, key: str, state: str):
        return icons.glyph(FUNC_ICON.get(key, ""), 16, self._CHIP_ICON_COLOR[state])

    def _make_chip(self, parent, key: str) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            parent, text=FUNC_LABELS[key], height=36, corner_radius=8,
            font=font(12), image=self._chip_icon(key, "off"), compound="left",
            anchor="w", command=lambda k=key: self._on_func_click(k),
            **chip_style("off"),
        )
        self.func_buttons[key] = btn
        return btn

    def _on_func_click(self, key: str) -> None:
        if key in self._func_disabled:
            return
        if key in self.selected_funcs:
            self.selected_funcs.discard(key)
        else:
            self.selected_funcs.add(key)
        self._refresh_func_ui()

    def _refresh_func_ui(self) -> None:
        has_res = "res" in self.selected_funcs
        has_tt = ("trans" in self.selected_funcs) or ("text" in self.selected_funcs)

        # raw/inp/res เลือกอิสระแยกกันได้ทั้งหมด (ไม่บังคับซึ่งกันและกัน)
        # คงไว้เฉพาะ dependency เชิงการทำงาน: split/com ทำงานบน res, ep ต้องมี trans/text
        self._func_disabled = set()
        for key, btn in self.func_buttons.items():
            disabled = (
                (key == "split" and not has_res)
                or (key == "com" and not has_res)
                or (key == "ep" and not has_tt)
            )
            if disabled:
                self._func_disabled.add(key)
                self.selected_funcs.discard(key)
                btn.configure(image=self._chip_icon(key, "disabled"), **chip_style("disabled"))
            elif key in self.selected_funcs:
                btn.configure(image=self._chip_icon(key, "on"), **chip_style("on"))
            else:
                btn.configure(image=self._chip_icon(key, "off"), **chip_style("off"))

        folder_name = build_folder_name(self.selected_funcs)
        self.output_label.configure(
            text=f"Output:  {folder_name}/" if folder_name else ""
        )
        self._save_cfg()

    # ── credit section ──
    def _build_credit_section(self, parent) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 2))
        ctk.CTkLabel(
            row, text="ไฟล์เครดิต", text_color=TEXT_MUTED, font=font(12), anchor="w",
        ).pack(side="left")
        ctk.CTkButton(
            row, text="เพิ่มไฟล์", width=110, height=30, corner_radius=8,
            font=font(12), fg_color="transparent", hover_color=BADGE_BG,
            text_color=PINK, border_width=1, border_color=CARD_BORDER,
            image=icons.glyph("plus", 14, PINK), compound="left",
            command=self._pick_credit,
        ).pack(side="right")

        self.credit_list = ctk.CTkFrame(parent, fg_color="transparent")
        self.credit_list.pack(fill="x", padx=14, pady=(0, 6))
        self._rebuild_credit_list()

    def _rebuild_credit_list(self) -> None:
        for w in self.credit_list.winfo_children():
            w.destroy()
        if not self.credit_paths:
            ctk.CTkLabel(
                self.credit_list, text="ยังไม่ได้เลือกไฟล์เครดิต",
                text_color=TEXT_MUTED, font=font(11), anchor="w",
            ).pack(fill="x")
            return
        for idx, path in enumerate(self.credit_paths):
            r = ctk.CTkFrame(self.credit_list, fg_color="transparent")
            r.pack(fill="x", pady=1)
            rm = ctk.CTkButton(
                r, text="", width=28, height=26, corner_radius=6,
                fg_color="transparent", hover_color=BADGE_BG,
                image=icons.glyph("trash", 14, TEXT_MUTED),
                command=lambda i=idx: self._remove_credit(i),
            )
            if icons.glyph("trash", 14, TEXT_MUTED) is None:
                rm.configure(text="✕", font=font(11), text_color=TEXT_MUTED)
            rm.pack(side="right")
            ctk.CTkLabel(
                r, text=_short(Path(path).name, 40), text_color=TEXT_MUTED,
                font=font(12), anchor="w",
            ).pack(side="left", fill="x", expand=True)

    def _remove_credit(self, idx: int) -> None:
        if 0 <= idx < len(self.credit_paths):
            self.credit_paths.pop(idx)
            self._save_cfg()
            self._rebuild_credit_list()

    def _pick_credit(self) -> None:
        paths = filedialog.askopenfilenames(
            parent=self, title="เลือกไฟล์เครดิต (เลือกได้หลายไฟล์)",
            filetypes=[("รูปภาพ", "*.png *.jpg *.jpeg"), ("ทั้งหมด", "*.*")],
        )
        if not paths:
            return
        existing = set(self.credit_paths)
        for p in paths:
            c = canonical_file(p)
            if c and c not in existing:
                self.credit_paths.append(c)
                existing.add(c)
        self._save_cfg()
        self._rebuild_credit_list()

    # ── split section ──
    def _build_split_section(self, parent) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(
            row, text="หั่นแนวนอน (บน→ล่าง):", text_color=TEXT_MUTED, font=font(13),
        ).pack(side="left")
        ctk.CTkEntry(
            row, textvariable=self.split_var, width=60, height=34,
            corner_radius=10, border_color=CARD_BORDER, font=font(13),
            justify="center",
        ).pack(side="left", padx=8)
        ctk.CTkLabel(
            row, text="ชิ้น", text_color=TEXT_MUTED, font=font(13),
        ).pack(side="left")

    # ── compress section ──
    def _build_compress_section(self, parent) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(
            row, text="รูปแบบ:", text_color=TEXT_MUTED, font=font(13),
        ).pack(side="left")
        self.btn_jpg = ctk.CTkButton(
            row, text="JPG", width=56, height=34, corner_radius=8, font=font(12),
            command=lambda: self._set_fmt("jpg"),
        )
        self.btn_png = ctk.CTkButton(
            row, text="PNG", width=56, height=34, corner_radius=8, font=font(12),
            command=lambda: self._set_fmt("png"),
        )
        self.btn_jpg.pack(side="left", padx=(8, 6))
        self.btn_png.pack(side="left")
        ctk.CTkLabel(
            row, text="คุณภาพ %", text_color=TEXT_MUTED, font=font(13),
        ).pack(side="left", padx=(14, 6))
        ctk.CTkEntry(
            row, textvariable=self.quality_var, width=64, height=34,
            corner_radius=10, border_color=CARD_BORDER, font=font(13),
            justify="center",
        ).pack(side="left")
        self._refresh_fmt_buttons()

    def _set_fmt(self, fmt: str) -> None:
        self.compress_fmt = fmt
        self._refresh_fmt_buttons()
        self._save_cfg()

    def _refresh_fmt_buttons(self) -> None:
        self.btn_jpg.configure(**chip_style("on" if self.compress_fmt == "jpg" else "off"))
        self.btn_png.configure(**chip_style("on" if self.compress_fmt == "png" else "off"))

    # ── progress card ──
    def _build_progress(self, parent) -> None:
        card = make_card(parent)
        card.pack(fill="both", expand=True, pady=(14, 0))

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(12, 0))
        prog_badge = ctk.CTkLabel(
            head, text="", fg_color=BADGE_BG, corner_radius=6, width=30, height=30,
        )
        prog_icon = icons.glyph("progress", 16, PINK)
        if prog_icon is not None:
            prog_badge.configure(image=prog_icon)
        else:
            prog_badge.configure(text="▍", text_color=PINK, font=font(14, bold=True))
        prog_badge.pack(side="left")
        ctk.CTkLabel(
            head, text="ความคืบหน้า", text_color=TEXT_WHITE, font=font(14, bold=True),
        ).pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            head, text="คัดลอก log", width=110, height=28, corner_radius=8,
            font=font(11), fg_color="transparent", hover_color=BADGE_BG,
            text_color=TEXT_MUTED, border_width=1, border_color=CARD_BORDER,
            image=icons.glyph("copy", 13, TEXT_MUTED), compound="left",
            command=self._copy_log,
        ).pack(side="right")
        self.progress_label = ctk.CTkLabel(
            head, text="", text_color=TEXT_MUTED, font=font(12),
        )
        self.progress_label.pack(side="right", padx=(0, 10))

        divider = ctk.CTkFrame(card, height=1, fg_color=CARD_BORDER)
        divider.pack(fill="x", padx=14, pady=(8, 6))

        self.progress_bar = ctk.CTkProgressBar(
            card, height=8, corner_radius=4, progress_color=PINK,
            fg_color=CARD_BORDER,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=14)

        self.log_box = ctk.CTkTextbox(
            card, fg_color=LOG_BG, corner_radius=8, font=font(11),
            text_color=TEXT_MUTED, wrap="word", border_width=0,
        )
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(8, 14))
        tb = self.log_box._textbox
        tb.tag_config("muted", foreground=TEXT_MUTED)
        tb.tag_config("success", foreground=SUCCESS)
        tb.tag_config("error", foreground=ERROR)
        tb.tag_config("warn", foreground=WARN)
        tb.tag_config("pink", foreground=PINK_LIGHT)
        tb.tag_config("head", foreground=PINK_LIGHT)
        self.log_box.configure(state="disabled")

    # ════════════════════════════════════════════════════════════════════
    #  workspace / stories actions
    # ════════════════════════════════════════════════════════════════════
    def _pick_workspace(self) -> None:
        path = filedialog.askdirectory(
            parent=self, title="เลือกโฟลเดอร์ workspace",
            mustexist=True,
        )
        if path:
            self._apply_folder(path)

    def _apply_folder(self, path: str) -> None:
        from app.paths import canonical_dir
        norm = canonical_dir(path)
        if not norm:
            return
        self.parent_path = norm
        set_last_workspace(norm)
        self.workspace_label.configure(text=norm, text_color=TEXT_WHITE)

        stories = get_workspace_subfolders(path)
        self.story_buttons = {}
        self.selected_paths = set()
        for w in self.stories_frame.winfo_children():
            w.destroy()

        if not stories:
            self._stories_placeholder("ไม่พบ subfolder")
            return

        for idx, (full_path, name) in enumerate(stories):
            btn = ctk.CTkButton(
                self.stories_frame, text=_short(name), anchor="w", height=36,
                corner_radius=8, font=font(12),
                command=lambda fp=full_path: self._toggle_story(fp),
                **chip_style("off"),
            )
            r, c = divmod(idx, 2)
            btn.grid(row=r, column=c, sticky="ew", padx=4, pady=3)
            self.story_buttons[full_path] = btn

    def _toggle_story(self, fp: str) -> None:
        if fp in self.selected_paths:
            self.selected_paths.discard(fp)
        else:
            self.selected_paths.add(fp)
        self._restyle_story(fp)

    def _restyle_story(self, fp: str) -> None:
        btn = self.story_buttons.get(fp)
        if btn is not None:
            btn.configure(**chip_style("on" if fp in self.selected_paths else "off"))

    def _update_story_styles(self) -> None:
        for fp in self.story_buttons:
            self._restyle_story(fp)

    def _select_all(self) -> None:
        self.selected_paths = set(self.story_buttons.keys())
        self._update_story_styles()

    def _clear_all(self) -> None:
        self.selected_paths = set()
        self._update_story_styles()

    # ════════════════════════════════════════════════════════════════════
    #  config persistence
    # ════════════════════════════════════════════════════════════════════
    def _save_cfg(self) -> None:
        c = load_config()
        c["selected_functions"] = sorted(self.selected_funcs)
        c["credit_paths"] = self.credit_paths
        c["compress_format"] = self.compress_fmt
        c["compress_quality"] = _clampi(self.quality_var.get(), 1, 100, 70)
        c["split_parts"] = _clampi(self.split_var.get(), 2, 20, 2)
        save_config(c)

    # ════════════════════════════════════════════════════════════════════
    #  UI <- worker bridge (queue pumped on main thread)
    # ════════════════════════════════════════════════════════════════════
    def _post(self, fn) -> None:
        """เรียกจาก worker thread: คิวงานอัปเดต UI ไว้ให้ main thread ทำ."""
        self._ui_queue.put(fn)

    def _pump(self) -> None:
        try:
            while True:
                fn = self._ui_queue.get_nowait()
                try:
                    fn()
                except TclError:
                    pass
        except queue.Empty:
            pass
        if not self._closing:
            self.after(40, self._pump)

    # ── log helpers (main thread เท่านั้น) ──
    def _append_log(self, text: str, tag: str = "muted") -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n", tag)
        self.log_box._textbox.see("end")
        self.log_box.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _set_progress(self, frac: float, text: str = "") -> None:
        self.progress_bar.set(max(0.0, min(1.0, frac)))
        if text:
            self.progress_label.configure(text=text)

    def _copy_log(self) -> None:
        text = self.log_box.get("1.0", "end").strip()
        if not text:
            self._toast("ยังไม่มี log ให้คัดลอก", error=True)
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update_idletasks()
            self._toast("คัดลอก log แล้ว")
        except TclError:
            self._toast("คัดลอกไม่สำเร็จ (clipboard)", error=True)

    # ── toast ──
    def _toast(self, msg: str, error: bool = False) -> None:
        symbol = "✕  " if error else "✓  "
        self.toast_label.configure(
            text=symbol + msg, text_color=ERROR if error else SUCCESS,
        )
        self.toast.configure(border_color=ERROR if error else SUCCESS)
        self.toast.place(relx=0.5, rely=1.0, anchor="s", y=-18)
        self.toast.lift()
        if self._toast_after is not None:
            try:
                self.after_cancel(self._toast_after)
            except (ValueError, TclError):
                pass
        dur = 6000 if error else 5000
        self._toast_after = self.after(dur, self._hide_toast)

    def _hide_toast(self) -> None:
        try:
            self.toast.place_forget()
        except TclError:
            pass

    # ════════════════════════════════════════════════════════════════════
    #  EXECUTE
    # ════════════════════════════════════════════════════════════════════
    def _on_execute(self) -> None:
        if self._running:
            return
        if not self.parent_path:
            self._toast("กรุณาเลือกโฟลเดอร์ workspace ก่อน", error=True)
            return
        stories = sorted(self.selected_paths)
        if not stories:
            self._toast("กรุณาเลือกอย่างน้อย 1 เรื่อง", error=True)
            return
        funcs = set(self.selected_funcs)
        if not funcs & {"raw", "inp", "res", "trans", "text"}:
            self._toast("กรุณาเลือกอย่างน้อย 1 ฟังก์ชันดึงไฟล์ (raw/inp/res/trans/text)", error=True)
            return
        if "cred" in funcs and not self.credit_paths:
            self._toast("กรุณาเพิ่มไฟล์เครดิตอย่างน้อย 1 ไฟล์ (หรือปิดฟังก์ชัน cred)", error=True)
            return

        folder_name = build_folder_name(funcs)
        if not folder_name:
            return

        cred_paths = list(self.credit_paths) if "cred" in funcs else None
        comp_q = _clampi(self.quality_var.get(), 1, 100, 70)
        comp_fmt = self.compress_fmt
        parts = _clampi(self.split_var.get(), 2, 20, 2)

        self._running = True
        self.btn_execute.configure(state="disabled", text="กำลังทำงาน…")
        self._clear_log()
        self._set_progress(0, "")

        t = threading.Thread(
            target=self._run_worker,
            args=(stories, funcs, folder_name, cred_paths, comp_fmt, comp_q, parts),
            daemon=True,
        )
        t.start()

    def _log_cb(self, color_fn):
        """คืน callback ที่ collector เรียกได้จาก worker thread แล้ว stream เข้า log."""
        def cb(msg: str) -> None:
            self._post(lambda m=msg: self._append_log("    " + m, color_fn(m)))
        return cb

    def _run_worker(self, stories, funcs, folder_name, cred_paths,
                    comp_fmt, comp_q, parts) -> None:
        total = len(stories)
        ok_count = 0
        err_msg = None
        agg = {
            "split_pieces": 0, "split_eps": 0,
            "cred_templates": 0, "cred_eps": 0, "cred_files_total": 0,
        }

        cb_collect = self._log_cb(_color_collect)
        cb_split = self._log_cb(_color_split)
        cb_credit = self._log_cb(_color_credit)
        cb_compress = self._log_cb(_color_compress)

        try:
            for idx, base_path in enumerate(stories):
                story_name = Path(base_path).name
                self._post(lambda n=story_name, i=idx: self._append_log(
                    f"── {n} ({i + 1}/{total}) ──", "head"))
                story_ok = True

                if "raw" in funcs:
                    self._post(lambda: self._append_log("  ดึงไฟล์ดิบ (raw)…"))
                    ok, _ = collect_raw(base_path, folder_name, log_callback=cb_collect)
                    story_ok = story_ok and ok

                if "inp" in funcs:
                    self._post(lambda: self._append_log("  ดึงไฟล์คลีน (inp)…"))
                    ok, _ = collect_inpainted(base_path, folder_name, log_callback=cb_collect)
                    story_ok = story_ok and ok

                if "res" in funcs:
                    self._post(lambda: self._append_log("  ดึงไฟล์ลงคำ (res)…"))
                    ok, _ = collect_res(base_path, folder_name, log_callback=cb_collect)
                    story_ok = story_ok and ok

                if "trans" in funcs:
                    self._post(lambda: self._append_log("  ดึงไฟล์แปล (trans)…"))
                    ok, _ = collect_trans(base_path, folder_name, "ep" in funcs,
                                          log_callback=cb_collect)
                    story_ok = story_ok and ok

                if "text" in funcs:
                    self._post(lambda: self._append_log("  ดึงไฟล์ถอดคำ (text)…"))
                    ok, _ = collect_text(base_path, folder_name, "ep" in funcs,
                                         log_callback=cb_collect)
                    story_ok = story_ok and ok

                if "split" in funcs:
                    self._post(lambda: self._append_log("  หั่นภาพ (split)…"))
                    ok, _, st = apply_split(base_path, folder_name, parts,
                                            log_callback=cb_split)
                    agg["split_pieces"] += int(st.get("total_pieces", 0))
                    agg["split_eps"] += int(st.get("episodes_done", 0))
                    story_ok = story_ok and ok

                if "cred" in funcs and cred_paths:
                    n = len(cred_paths)
                    self._post(lambda k=n: self._append_log(f"  เพิ่มเครดิต {k} แบบ (cred)…"))
                    ok, _, cst = apply_credit(base_path, folder_name, cred_paths,
                                              log_callback=cb_credit)
                    agg["cred_templates"] = max(agg["cred_templates"],
                                                int(cst.get("templates", n)))
                    agg["cred_eps"] += int(cst.get("episodes", 0))
                    agg["cred_files_total"] += int(cst.get("files_copied_total", 0))
                    story_ok = story_ok and ok

                if "com" in funcs:
                    self._post(lambda: self._append_log("  ย่อไฟล์ (com)…", "pink"))

                    def _prog(done, tot, fname, i=idx):
                        frac = (i + (done / tot if tot else 1)) / total
                        self._post(lambda: self._set_progress(
                            frac, f"ย่อ {done}/{tot}  ({_short(fname, 24)})"))

                    apply_compress(base_path, folder_name, comp_fmt, comp_q,
                                   log_callback=cb_compress, progress_callback=_prog)

                if story_ok:
                    ok_count += 1
                    self._post(lambda n=story_name: self._append_log(f"  ✓ {n} เสร็จ", "success"))
                else:
                    self._post(lambda n=story_name: self._append_log(f"  ✗ {n} มีข้อผิดพลาด", "error"))

                self._post(lambda i=idx: self._set_progress(
                    (i + 1) / total, f"{i + 1}/{total} เรื่อง"))

        except Exception as ex:  # noqa: BLE001 — แสดงทุก error ใน log แทนการ crash
            err_msg = str(ex)
            self._post(lambda e=err_msg: self._append_log(f"ผิดพลาด: {e}", "error"))

        self._post(lambda: self._finish(ok_count, total, folder_name, funcs,
                                        agg, parts, cred_paths, err_msg))

    def _finish(self, ok_count, total, folder_name, funcs, agg, parts,
                cred_paths, err_msg) -> None:
        self._running = False
        self.btn_execute.configure(state="normal", text="Execute")
        self.progress_bar.set(1)

        if err_msg:
            self._toast(f"ผิดพลาด: {err_msg}", error=True)
            return

        lines = [f"เสร็จ {ok_count}/{total} เรื่อง → {folder_name}/"]
        if "split" in funcs:
            lines.append(
                f"หั่นรวม {agg['split_pieces']} ไฟล์ ใน {agg['split_eps']} ตอน "
                f"(ตั้งหั่น {parts} ชิ้นต่อภาพ)"
            )
        if "cred" in funcs and cred_paths:
            lines.append(
                f"เครดิต {agg['cred_templates']} แบบ × {agg['cred_eps']} ตอน "
                f"(คัดลอกรวม {agg['cred_files_total']} ไฟล์)"
            )
        self._toast("\n".join(lines))

    # ════════════════════════════════════════════════════════════════════
    def _safe_zoom(self) -> None:
        try:
            self.state("zoomed")
        except TclError:
            pass

    def _on_close(self) -> None:
        self._closing = True
        try:
            self.destroy()
        except TclError:
            pass


def run() -> None:
    ctk.set_appearance_mode("Dark")
    App().mainloop()
