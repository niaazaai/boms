#!/usr/bin/env python3
"""SVG component layer for the finished BOMS screens.

SVG because Figma imports it natively and losslessly: every rectangle becomes a
frame, every run of text stays editable text. The existing brand screens in
`dd/` are Figma SVG exports, so these round-trip into the same file.

Everything here is presentation only. What is ON each screen comes from
`specs/wireframes/`; how it looks comes from `tokens.py`.
"""

from __future__ import annotations

import hashlib
from html import escape

from tokens import (C, FONT_LATIN, FONT_MONO, FONT_RTL, RADIUS, SHADOW, STATUS,
                    TYPE)


# ── document ──────────────────────────────────────────────────────

class Canvas:
    """Collects SVG fragments. `rtl` mirrors x-coordinates for Dari / Pashto."""

    def __init__(self, w, h, bg=None, rtl=False, title=""):
        self.w, self.h, self.rtl, self.title = w, h, rtl, title
        self.parts = []
        self.defs = []
        self._bg = bg or C["bg"]

    # x-mirror: one place, so every component below is written left-to-right
    def fx(self, x, w=0.0):
        return (self.w - x - w) if self.rtl else x

    def anchor(self, a):
        if not self.rtl:
            return a
        return {"start": "end", "end": "start", "middle": "middle"}[a]

    def add(self, s):
        self.parts.append(s)
        return self

    def render(self):
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" fill="none">'
            f'<title>{escape(self.title)}</title>'
        )
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        bg = (f'<rect width="{self.w}" height="{self.h}" fill="{self._bg}"/>')
        return head + defs + bg + "".join(self.parts) + "</svg>"


def shadow_def(cv, name="cardShadow", dy=8, blur=24, opacity=0.05):
    if any(name in d for d in cv.defs):
        return name
    cv.defs.append(
        f'<filter id="{name}" x="-40%" y="-40%" width="180%" height="180%">'
        f'<feDropShadow dx="0" dy="1" stdDeviation="1" flood-color="#1B1C1A" flood-opacity="0.04"/>'
        f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{blur / 2}" flood-color="#1B1C1A" '
        f'flood-opacity="{opacity}"/></filter>')
    return name


# ── primitives ────────────────────────────────────────────────────

def rect(cv, x, y, w, h, fill="none", stroke=None, r=0, sw=1, opacity=None, filt=None):
    a = [f'x="{cv.fx(x, w):.2f}"', f'y="{y:.2f}"', f'width="{w:.2f}"', f'height="{h:.2f}"',
         f'fill="{fill}"']
    if r:
        a.append(f'rx="{r}"')
    if stroke:
        a.append(f'stroke="{stroke}"')
        a.append(f'stroke-width="{sw}"')
    if opacity is not None:
        a.append(f'opacity="{opacity}"')
    if filt:
        a.append(f'filter="url(#{filt})"')
    cv.add(f'<rect {" ".join(a)}/>')


def line(cv, x, y, w, color=None, sw=1):
    color = color or C["divider"]
    x0 = cv.fx(x, w)
    cv.add(f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x0 + w:.2f}" y2="{y:.2f}" '
           f'stroke="{color}" stroke-width="{sw}"/>')


def is_arabic(s: str) -> bool:
    return any(0x0600 <= ord(ch) <= 0x06FF or 0xFB50 <= ord(ch) <= 0xFDFF for ch in s)


def txt(cv, x, y, s, style="body", fill=None, anchor="start", family=None,
        upper=False, opacity=None, ltr=False):
    """Text, positioned by the top of its box. `ltr` pins a run left-to-right on
    an RTL canvas — numbers, SKUs, barcodes and dates always use it."""
    size, lh, weight, track = TYPE[style]
    fill = fill or C["body"]
    arabic = is_arabic(s)
    # Perso-Arabic is a joining script: letter-spacing pulls the joins apart and
    # browsers fall back to unshaped glyphs. Never track Dari or Pashto.
    if arabic:
        track = 0
        s = s if not upper else s          # `upper` is meaningless in this script
    elif upper:
        s = s.upper()
    fam = family or (FONT_RTL if arabic else FONT_LATIN)
    # With direction="rtl", SVG already resolves `start` to the right edge, so an
    # Arabic run keeps its own anchor. A Latin run on the same canvas does not,
    # and has to be flipped by hand.
    a = anchor if (ltr or arabic) else cv.anchor(anchor)
    px = cv.fx(x)
    extra = ""
    if cv.rtl and ltr:
        extra = ' direction="ltr" unicode-bidi="isolate"'
    elif arabic:
        extra = ' direction="rtl"'
    op = f' opacity="{opacity}"' if opacity is not None else ""
    cv.add(f'<text x="{px:.2f}" y="{y + size * 0.78:.2f}" font-family="{fam}" '
           f'font-size="{size}" font-weight="{weight}" letter-spacing="{track}" '
           f'fill="{fill}" text-anchor="{a}"{extra}{op}>{escape(s)}</text>')


def wrap(s, width_chars):
    """Break on spaces, never mid-word — a label that splits "the" into "t/he"
    reads as a bug, and these screens are shown to clients."""
    out, line_ = [], ""
    for word in s.split():
        if line_ and len(line_) + 1 + len(word) > width_chars:
            out.append(line_)
            line_ = word
        else:
            line_ = f"{line_} {word}".strip()
    if line_:
        out.append(line_)
    return out


def paragraph(cv, x, y, s, width_chars, style="caption", fill=None, leading=None):
    size, lh, _, _ = TYPE[style]
    leading = leading or lh
    for i, ln in enumerate(wrap(s, width_chars)):
        txt(cv, x, y + i * leading, ln, style, fill)
    return y + len(wrap(s, width_chars)) * leading


def num(cv, x, y, s, style="body", fill=None, anchor="start"):
    """Tabular figures — columns of money have to line up."""
    size, lh, weight, track = TYPE[style]
    fill = fill or C["ink"]
    a = cv.anchor(anchor)
    cv.add(f'<text x="{cv.fx(x):.2f}" y="{y + size * 0.78:.2f}" font-family="{FONT_LATIN}" '
           f'font-size="{size}" font-weight="{weight}" letter-spacing="{track}" fill="{fill}" '
           f'text-anchor="{a}" direction="ltr" unicode-bidi="isolate" '
           f'style="font-variant-numeric:tabular-nums">{escape(s)}</text>')


def mono(cv, x, y, s, size=12, fill=None, anchor="start"):
    fill = fill or C["muted"]
    cv.add(f'<text x="{cv.fx(x):.2f}" y="{y + size * 0.78:.2f}" font-family="{FONT_MONO}" '
           f'font-size="{size}" fill="{fill}" text-anchor="{cv.anchor(anchor)}" '
           f'direction="ltr" unicode-bidi="isolate">{escape(s)}</text>')


# ── icons (Lucide geometry, 24×24, stroked) ───────────────────────
# shadcn ships lucide-react, so the built UI uses these exact shapes.

ICONS = {
    "home": "M3 10.5 12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z",
    "package": "M21 8 12 3 3 8v8l9 5 9-5zM3 8l9 5 9-5M12 13v8",
    "cart": "M8 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2M19 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2M2 3h2.5l2.6 12.4A2 2 0 0 0 9 17h9.3a2 2 0 0 0 2-1.6L22 7H5.2",
    "truck": "M10 17h4V5H2v12h2M14 9h4l4 4v4h-2M4.5 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3M18.5 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3",
    "wallet": "M19 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0 0 4h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5M16 12h3",
    "chart": "M3 3v16a2 2 0 0 0 2 2h16M7 15l3-4 3 2 4-6",
    "settings": "M12.2 2h-.4a2 2 0 0 0-2 2 1.7 1.7 0 0 1-2.6 1.5 2 2 0 0 0-2.4.3l-.3.3a2 2 0 0 0-.3 2.4A1.7 1.7 0 0 1 4 11.8a2 2 0 0 0-2 2v.4a2 2 0 0 0 2 2 1.7 1.7 0 0 1 1.5 2.6 2 2 0 0 0 .3 2.4l.3.3M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6",
    "search": "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16M21 21l-4.3-4.3",
    "plus": "M12 5v14M5 12h14",
    "chevron": "m6 9 6 6 6-6",
    "chevron_right": "m9 6 6 6-6 6",
    "bell": "M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0",
    "user": "M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8",
    "printer": "M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6z",
    "download": "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
    "filter": "M22 3H2l8 9.5V19l4 2v-8.5z",
    "calendar": "M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2",
    "alert": "M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0M12 9v4M12 17h.01",
    "check": "m20 6-11 11-5-5",
    "x": "M18 6 6 18M6 6l12 12",
    "image": "M3 5h18v14H3zM8.5 11a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3M21 15l-5-5L5 19",
    "clock": "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20M12 6v6l4 2",
    "bookmark": "M19 21l-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z",
    "warehouse": "M22 8.4V21H2V8.4a2 2 0 0 1 1.2-1.8l8-3.6a2 2 0 0 1 1.6 0l8 3.6A2 2 0 0 1 22 8.4M6 18h12v-6H6z",
    "transfer": "M17 2l4 4-4 4M3 6h18M7 22l-4-4 4-4M21 18H3",
    "trash": "M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M10 11v6M14 11v6",
    "scale": "M12 3v18M7 21h10M5 7l-3 7h6zM19 7l-3 7h6zM3 7h18",
    "scan": "M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 12h10",
    "more": "M12 13a1 1 0 1 0 0-2 1 1 0 0 0 0 2M19 13a1 1 0 1 0 0-2 1 1 0 0 0 0 2M5 13a1 1 0 1 0 0-2 1 1 0 0 0 0 2",
    "arrow_left": "M19 12H5M12 19l-7-7 7-7",
    "sparkle": "m12 3 2.2 6.3L21 11l-6.8 1.7L12 19l-2.2-6.3L3 11l6.8-1.7z",
    "lock": "M5 11h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2M7 11V7a5 5 0 0 1 10 0v4",
}


def icon(cv, x, y, name, size=20, color=None, sw=1.6):
    """Draw a Lucide icon with its top-left at (x, y)."""
    d = ICONS.get(name)
    if not d:
        return
    color = color or C["body"]
    s = size / 24.0
    px = cv.fx(x, size)
    flip = ""
    if cv.rtl and name in ("chevron_right", "arrow_left", "transfer"):
        flip = f" translate({size},0) scale(-1,1)"
    cv.add(f'<g transform="translate({px:.2f},{y:.2f}) scale({s:.4f}){flip}" '
           f'stroke="{color}" stroke-width="{sw / s:.2f}" stroke-linecap="round" '
           f'stroke-linejoin="round" fill="none"><path d="{d}"/></g>')


# ── components ────────────────────────────────────────────────────

def card(cv, x, y, w, h, pad_title=None, sub=None):
    f = shadow_def(cv)
    rect(cv, x, y, w, h, C["surface"], C["border"], RADIUS["card"], filt=f)
    if pad_title:
        txt(cv, x + 24, y + 20, pad_title, "h3", C["ink"])
    if sub:
        txt(cv, x + 24, y + 44, sub, "caption", C["muted"])
    return y + (70 if pad_title else 0)


def btn(cv, x, y, w, h, label, kind="primary", icon_name=None):
    fills = {
        "primary":   (C["primary"], C["primary_fg"], None),
        "secondary": (C["surface"], C["ink"], C["border"]),
        "ghost":     ("none", C["muted"], None),
        "soft":      (C["accent"], C["accent_ink"], None),
        "danger":    (C["danger"], "#FFFFFF", None),
    }
    bg, fg, stroke = fills[kind]
    rect(cv, x, y, w, h, bg, stroke, RADIUS["pill"])
    tx = x + w / 2
    if icon_name:
        icon(cv, x + 18, y + (h - 16) / 2, icon_name, 16, fg, 1.8)
        tx += 10
    txt(cv, tx, y + (h - TYPE["body_medium"][0]) / 2 - 1, label, "body_medium", fg, "middle")


def icon_btn(cv, x, y, name, size=40, color=None, bg=None):
    rect(cv, x, y, size, size, bg or C["divider"], None, RADIUS["control"])
    icon(cv, x + (size - 18) / 2, y + (size - 18) / 2, name, 18, color or C["body"])


def chip(cv, x, y, label, state=None, fg=None, bg=None, h=24):
    fg, bg = (STATUS.get(state, (fg or C["muted"], bg or C["surface_2"]))
              if state else (fg or C["muted"], bg or C["surface_2"]))
    w = max(56, len(label) * 6.6 + 24)
    rect(cv, x, y, w, h, bg, None, RADIUS["chip"])
    txt(cv, x + w / 2, y + (h - 12) / 2 - 1, label, "caption", fg, "middle")
    return x + w + 8


def field(cv, x, y, w, label, value="", h=44, locked=False, chevron=False,
          placeholder=False, hint=None):
    txt(cv, x, y, label, "label", C["muted"])
    ty = y + 22
    rect(cv, x, ty, w, h, C["surface_2"] if locked else C["input"], C["border"],
         RADIUS["control"])
    if value:
        txt(cv, x + 14, ty + (h - 14) / 2 - 1, value, "body",
            C["disabled"] if placeholder else C["ink"])
    if locked:
        icon(cv, x + w - 32, ty + (h - 16) / 2, "lock", 15, C["disabled"], 1.7)
    if chevron:
        icon(cv, x + w - 32, ty + (h - 16) / 2, "chevron", 16, C["muted"])
    ny = ty + h + 8
    if hint:
        txt(cv, x, ny, hint, "caption", C["muted"])
        ny += 20
    return ny + 12


def stat(cv, x, y, w, h, label, value, caption=None, icon_name=None, tone=None):
    rect(cv, x, y, w, h, C["surface_2"], None, RADIUS["tile"])
    if icon_name:
        rect(cv, x + 20, y + 20, 32, 32, C["surface"], None, RADIUS["sm"])
        icon(cv, x + 28, y + 28, icon_name, 16, tone or C["primary"], 1.7)
    txt(cv, x + (64 if icon_name else 20), y + 26, label, "label", C["muted"], upper=False)
    num(cv, x + 20, y + 60, value, "numeric", tone or C["ink"])
    if caption:
        txt(cv, x + 20, y + h - 30, caption, "caption", C["muted"])


def table(cv, x, y, w, cols, rows, widths=None, row_h=52, head_h=44, align=None):
    """cols = ['SKU', …]; rows = [[cell, …]]. A cell may be:
         "text"                     plain
         ("text", colour)           coloured
         ("text", None, "status")   status chip
         ("text", None, None, 1)    tabular number
    """
    n = len(cols)
    widths = widths or [1] * n
    total = sum(widths)
    align = align or ["start"] * n
    xs, acc = [], 0.0
    for wt in widths:
        xs.append(x + acc / total * w)
        acc += wt
    colw = [w * wt / total for wt in widths]

    rect(cv, x, y, w, head_h, C["surface_2"], None, 0)
    for i, c in enumerate(cols):
        cx = xs[i] + 16 if align[i] == "start" else xs[i] + colw[i] - 16
        txt(cv, cx, y + (head_h - 11) / 2 - 1, c, "micro", C["muted"],
            "start" if align[i] == "start" else "end", upper=True)
    yy = y + head_h
    for r in rows:
        line(cv, x, yy, w, C["divider"])
        for i, cell in enumerate(r[:n]):
            if isinstance(cell, tuple):
                val = cell[0]
                colour = cell[1] if len(cell) > 1 else None
                state = cell[2] if len(cell) > 2 else None
                tabular = cell[3] if len(cell) > 3 else False
            else:
                val, colour, state, tabular = cell, None, None, False
            cy = yy + (row_h - 14) / 2 - 1
            if state:
                chip(cv, xs[i] + 12, yy + (row_h - 24) / 2, val, state)
                continue
            a = "start" if align[i] == "start" else "end"
            cx = xs[i] + 16 if a == "start" else xs[i] + colw[i] - 16
            if tabular:
                num(cv, cx, cy, val, "body", colour or C["ink"], a)
            else:
                txt(cv, cx, cy, val, "body", colour or C["body"], a)
        yy += row_h
    line(cv, x, yy, w, C["divider"])
    return yy


# ── barcode & QR (generated from the SKU) ─────────────────────────

def _bits(payload, n):
    out, i = [], 0
    while len(out) < n:
        for byte in hashlib.sha256(payload.encode() + str(i).encode()).digest():
            for k in range(8):
                out.append((byte >> k) & 1)
        i += 1
    return out[:n]


def barcode(cv, x, y, w, h, code, caption=True):
    bits = _bits(code, 120)
    pattern = [2, 1, 1, 2] + [1 + b * 2 for b in bits] + [2, 3, 2]
    unit = w / float(sum(pattern))
    bh = h - (20 if caption else 0)
    xx = 0.0
    g = []
    for i, u in enumerate(pattern):
        bw = u * unit
        if i % 2 == 0:
            g.append(f'<rect x="{xx:.2f}" y="0" width="{max(0.7, bw):.2f}" '
                     f'height="{bh:.2f}" fill="{C["ink"]}"/>')
        xx += bw
    cv.add(f'<g transform="translate({cv.fx(x, w):.2f},{y:.2f})">{"".join(g)}</g>')
    if caption:
        mono(cv, x + w / 2, y + bh + 4, code, 12, C["muted"], "middle")


def qr(cv, x, y, size, payload, modules=21):
    q = size * 0.07
    grid = size - q * 2
    m = grid / modules
    bits = _bits(payload, modules * modules)
    g = [f'<rect width="{size}" height="{size}" fill="{C["surface"]}"/>']

    def finder(fx, fy):
        return (f'<rect x="{fx:.2f}" y="{fy:.2f}" width="{m*7:.2f}" height="{m*7:.2f}" fill="{C["ink"]}"/>'
                f'<rect x="{fx+m:.2f}" y="{fy+m:.2f}" width="{m*5:.2f}" height="{m*5:.2f}" fill="{C["surface"]}"/>'
                f'<rect x="{fx+m*2:.2f}" y="{fy+m*2:.2f}" width="{m*3:.2f}" height="{m*3:.2f}" fill="{C["ink"]}"/>')

    reserved = set()
    for r in range(8):
        for c in range(8):
            reserved |= {(r, c), (r, modules - 1 - c), (modules - 1 - r, c)}
    for r in range(modules):
        for c in range(modules):
            if (r, c) in reserved or not bits[r * modules + c]:
                continue
            g.append(f'<rect x="{q + c*m:.2f}" y="{q + r*m:.2f}" width="{m:.2f}" '
                     f'height="{m:.2f}" fill="{C["ink"]}"/>')
    g += [finder(q, q), finder(q + grid - m * 7, q), finder(q, q + grid - m * 7)]
    cv.add(f'<g transform="translate({cv.fx(x, size):.2f},{y:.2f})">{"".join(g)}</g>')


def label_card(cv, x, y, w, sku, sub, title, print_label, download_label, h=196):
    """The item-profile card: Code 128 + QR, both carrying the SKU.

    Never mirrored on an RTL canvas — a mirrored Code 128 does not scan — so it
    is drawn on a temporary left-to-right canvas and placed as one block.
    """
    f = shadow_def(cv)
    rect(cv, x, y, w, h, C["surface"], C["border"], RADIUS["card"], filt=f)
    txt(cv, x + 24, y + 20, title, "micro", C["muted"], upper=True)
    qs = 92
    bw = w - qs - 72
    # geometry inside the card is laid out LTR even when the page is RTL
    inner_x = cv.fx(x + 24, bw) if not cv.rtl else cv.fx(x + 24, bw)
    saved, cv.rtl = cv.rtl, False
    bx = (cv.w - x - w) + 24 if saved else x + 24
    barcode(cv, bx, y + 48, bw, 86, sku)
    qr(cv, bx + bw + 24, y + 48, qs, sku)
    txt(cv, bx + bw + 24 + qs / 2, y + 48 + qs + 10, "QR = SKU", "caption", C["muted"],
        "middle", family=FONT_LATIN)
    cv.rtl = saved
    txt(cv, x + 24, y + h - 54, sub, "caption", C["muted"])
    btn(cv, x + 24, y + h - 40, 132, 32, print_label, "secondary", "printer")
    btn(cv, x + 164, y + h - 40, 124, 32, download_label, "ghost", "download")
    return y + h + 20
