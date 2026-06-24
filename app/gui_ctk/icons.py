"""Monochrome icons from the Segoe MDL2 Assets font (ships with Windows 10/11).

tkinter cannot render colour emoji and a single button uses one font, so we
rasterise each glyph from the font file with PIL and feed it to the button as an
image. Crisp on every machine, no reliance on Tk font fallback. If the font file
is missing (e.g. non-Windows) glyph() returns None and buttons fall back to
text-only without crashing.
"""

from __future__ import annotations

import os

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

_FONT_PATH = os.path.join(
    os.environ.get("WINDIR", r"C:\\Windows"), "Fonts", "segmdl2.ttf"
)
_RENDER_PX = 64  # render hi-res; CTkImage downsamples crisply (HiDPI-safe)

# semantic name -> codepoint in Segoe MDL2 Assets (confirmed via contact sheet)
GLYPH = {
    "folder":     "\uE838", # folder
    "library":    "\uE8F1", # books (stories)
    "functions":  "\uE943", # { } functions
    "settings":   "\uE713", # gear (settings)
    "progress":   "\uE9D9", # chart (progress)
    "image":      "\uEB9F", # photo - raw
    "edit":       "\uE70F", # pencil - inp
    "picture":    "\uE91B", # framed picture - res
    "cut":        "\uE8C6", # scissors - split
    "globe":      "\uE774", # globe - trans
    "page":       "\uE7C3", # document - text
    "newfolder":  "\uE8F4", # new - ep
    "star":       "\uE735", # star - cred
    "compress":   "\uE9A6", # fit/shrink - com
    "play":       "\uE768", # play - Execute
    "plus":       "\uE710", # plus
    "copy":       "\uE8C8", # copy
    "check":      "\uE930", # check
    "close":      "\uE711", # close x
    "trash":      "\uE74D", # trash
}


_img_cache: dict = {}
_font_obj = None


def available() -> bool:
    return os.path.isfile(_FONT_PATH)


def _font():
    global _font_obj
    if _font_obj is None:
        _font_obj = ImageFont.truetype(_FONT_PATH, _RENDER_PX)
    return _font_obj


def glyph(name: str, size: int, color: str):
    """Return a cached CTkImage for the icon, or None if font/name missing."""
    if not available() or name not in GLYPH:
        return None
    key = (name, size, color)
    cached = _img_cache.get(key)
    if cached is not None:
        return cached
    im = Image.new("RGBA", (_RENDER_PX, _RENDER_PX), (0, 0, 0, 0))
    ImageDraw.Draw(im).text(
        (_RENDER_PX // 2, _RENDER_PX // 2), GLYPH[name],
        font=_font(), fill=color, anchor="mm",
    )
    ctk_img = ctk.CTkImage(light_image=im, dark_image=im, size=(size, size))
    _img_cache[key] = ctk_img
    return ctk_img
