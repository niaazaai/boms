#!/usr/bin/env python3
"""BOMS wireframe DSL — Excalidraw primitives, components and app shells.

Every module file imports from here. Coordinates are absolute; each screen is
placed on a grid via `grid_pos()`. Nothing here knows about BOMS content.
"""

from __future__ import annotations

import copy
import hashlib
import json
import random
import string
import time
from pathlib import Path

# ── Canvas geometry ───────────────────────────────────────────────
PHONE_W, PHONE_H = 390, 844          # iPhone 14-ish
DESK_W, DESK_H = 1440, 900           # desktop browser
SIDEBAR_W = 248
TOPBAR_H = 60
GAP_X = 120
ROW_GAP = 200
TITLE_H = 44
NOW = int(time.time() * 1000)

# ── Design tokens ─────────────────────────────────────────────────
INK = "#0f172a"        # primary text
MUTED = "#64748b"      # secondary text
FAINT = "#94a3b8"      # placeholder text
LINE = "#cbd5e1"       # borders
HAIRLINE = "#e2e8f0"   # subtle dividers
BG = "#ffffff"
SOFT = "#f1f5f9"
SOFT2 = "#f8fafc"

PRIMARY = "#0f172a"    # primary button fill
ACCENT = "#0d9488"     # teal — brand / active
ACCENT_BG = "#ccfbf1"
ROSE = "#be123c"       # bridal accent
ROSE_BG = "#ffe4e6"
OK = "#059669"
OK_BG = "#d1fae5"
WARN = "#d97706"
WARN_BG = "#fef3c7"
DANGER = "#dc2626"
DANGER_BG = "#fee2e2"
INFO = "#2563eb"
INFO_BG = "#dbeafe"
VIOLET = "#7c3aed"
VIOLET_BG = "#ede9fe"

SIDEBAR_BG = "#0f172a"
SIDEBAR_FG = "#cbd5e1"
SIDEBAR_MUTED = "#64748b"

# ── Icon set (Excalidraw renders emoji in text elements) ──────────
ICON = {
    "home": "🏠", "inventory": "📦", "sales": "🛒", "procurement": "🚚",
    "finance": "💰", "reports": "📊", "settings": "⚙️", "customers": "👥",
    "suppliers": "🏭", "calendar": "📅", "search": "🔍", "add": "＋",
    "alert": "⚠️", "cash": "💵", "bank": "🏦", "tag": "🏷️", "dress": "👗",
    "truck": "🚚", "receipt": "🧾", "ledger": "📒", "transfer": "🔁",
    "adjust": "⚖️", "dispose": "🗑️", "reserve": "🔖", "rental": "⏱️",
    "user": "👤", "lock": "🔒", "globe": "🌐", "branch": "🏬", "bell": "🔔",
    "chart": "📈", "down": "▾", "check": "✓", "cross": "✕", "filter": "☰",
    "export": "⬇", "print": "🖨", "photo": "🖼", "star": "⭐", "clock": "🕑",
    "warehouse": "🏚", "money_in": "↘", "money_out": "↗", "back": "←",
    "sort": "↕", "scan": "▣",
}


def nid(n: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(random.choice(alphabet) for _ in range(n))


def base(el_type: str, x, y, w, h, **kw):
    return {
        "id": nid(), "type": el_type, "x": x, "y": y, "width": w, "height": h,
        "angle": 0,
        "strokeColor": kw.get("strokeColor", INK),
        "backgroundColor": kw.get("backgroundColor", "transparent"),
        "fillStyle": "solid",
        "strokeWidth": kw.get("strokeWidth", 1),
        "strokeStyle": kw.get("strokeStyle", "solid"),
        "roughness": 0, "opacity": kw.get("opacity", 100),
        "groupIds": kw.get("groupIds", []), "frameId": None,
        "index": kw.get("index", "a0"),
        "roundness": kw.get("roundness", {"type": 3} if el_type in ("rectangle", "diamond") else None),
        "version": 1, "versionNonce": random.randint(1, 2**31 - 1),
        "isDeleted": False, "boundElements": [], "updated": NOW,
        "link": None, "locked": False, "seed": random.randint(1, 2**31 - 1),
    }


def rect(x, y, w, h, **kw):
    return base("rectangle", x, y, w, h, **kw)


def line(x, y, w, color=HAIRLINE, g=None):
    """Horizontal hairline divider."""
    el = base("line", x, y, w, 0, strokeColor=color, roundness=None, groupIds=g or [])
    el["points"] = [[0, 0], [w, 0]]
    return el


def _measure(s: str, size: float) -> float:
    """Rough advance width. Emoji and Perso-Arabic glyphs are much wider than
    Latin, and the estimate matters: `mirror()` reflects an element by its box,
    so an under-measured emoji lands on top of the label beside it."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x1F000 or 0x2190 <= o <= 0x2BFF:      # emoji, arrows, symbols
            w += 1.25
        elif 0x0600 <= o <= 0x06FF:                    # Perso-Arabic
            w += 0.62
        else:
            w += 0.56
    return w * size


def text(x, y, content, size=14, color=INK, align="left", width=None, g=None):
    lines = content.split("\n")
    tw = width if width is not None else max(8.0, max(_measure(L, size) for L in lines))
    el = base("text", x, y, tw, size * 1.25 * len(lines),
              strokeColor=color, roundness=None, groupIds=g or [])
    el.update({
        "text": content, "fontSize": size, "fontFamily": 5,
        "textAlign": align, "verticalAlign": "top", "containerId": None,
        "originalText": content, "autoResize": True, "lineHeight": 1.25,
    })
    if width is None:
        # Remember that this box was measured, not specified — i18n re-measures
        # it after substitution so a longer Dari string does not overlap.
        el["customData"] = {"auto": True}
    return el


def vrule(x, y, h, color=HAIRLINE, g=None):
    """Vertical hairline divider."""
    el = base("line", x, y, 0, h, strokeColor=color, roundness=None, groupIds=g or [])
    el["points"] = [[0, 0], [0, h]]
    return el


def mono(x, y, content, size=13, color=INK, width=None, g=None):
    """Monospace-ish text — use for table rows so columns line up."""
    el = text(x, y, content, size, color, "left", width, g)
    el["fontFamily"] = 3
    return el


def arrow(x1, y1, x2, y2, label=None, color=MUTED, dashed=False):
    els = []
    a = base("arrow", x1, y1, abs(x2 - x1) or 1, abs(y2 - y1) or 1,
             strokeWidth=2, strokeColor=color, roundness={"type": 2},
             strokeStyle="dashed" if dashed else "solid")
    a["points"] = [[0, 0], [x2 - x1, y2 - y1]]
    a["startArrowhead"] = None
    a["endArrowhead"] = "arrow"
    a["elbowed"] = False
    els.append(a)
    if label:
        els.append(text((x1 + x2) / 2 - len(label) * 3, (y1 + y2) / 2 - 20, label, 12, color))
    return els


# ── Components ────────────────────────────────────────────────────

def btn(x, y, w, h, label, kind="primary", g=None):
    """kind: primary | secondary | ghost | danger | success"""
    g = g or []
    fills = {
        "primary": (PRIMARY, "#ffffff", PRIMARY),
        "secondary": (BG, INK, LINE),
        "ghost": ("transparent", MUTED, "transparent"),
        "danger": (DANGER, "#ffffff", DANGER),
        "success": (OK, "#ffffff", OK),
        "accent": (ACCENT, "#ffffff", ACCENT),
    }
    bg, fg, stroke = fills.get(kind, fills["primary"])
    return [
        rect(x, y, w, h, strokeColor=stroke, backgroundColor=bg, strokeWidth=1, groupIds=g),
        text(x + 8, y + (h - 16) / 2, label, 14, fg, "center", w - 16, g),
    ]


def field(x, y, w, label, value="", g=None, required=False, hint=None, h=40):
    """Labelled input. Returns (elements, next_y)."""
    g = g or []
    els = [text(x, y, label + (" *" if required else ""), 12, MUTED, width=w, g=g)]
    els.append(rect(x, y + 18, w, h, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=g))
    if value:
        is_ph = value.startswith("…") or value.startswith("e.g.")
        els.append(text(x + 12, y + 18 + (h - 16) / 2, value, 13, FAINT if is_ph else INK, width=w - 24, g=g))
    ny = y + 18 + h + 10
    if hint:
        els.append(text(x, ny - 6, hint, 11, FAINT, width=w, g=g))
        ny += 14
    return els, ny


def select(x, y, w, label, value="", g=None, required=False):
    els, ny = field(x, y, w, label, value, g, required)
    els.append(text(x + w - 22, y + 30, ICON["down"], 13, MUTED, g=g))
    return els, ny


def textarea(x, y, w, label, value="", g=None, rows=3):
    return field(x, y, w, label, value, g, h=22 * rows + 16)


def chip(x, y, label, color=OK, bg=None, g=None, size=11):
    g = g or []
    bgmap = {OK: OK_BG, WARN: WARN_BG, DANGER: DANGER_BG, INFO: INFO_BG,
             ACCENT: ACCENT_BG, VIOLET: VIOLET_BG, ROSE: ROSE_BG, MUTED: SOFT}
    w = max(52, len(label) * size * 0.62 + 16)
    return [
        rect(x, y, w, 22, strokeColor=color, backgroundColor=bg or bgmap.get(color, SOFT),
             strokeWidth=1, groupIds=g),
        text(x + 8, y + 4, label, size, color, width=w - 16, g=g),
    ], x + w + 6


def search_bar(x, y, w, placeholder, g=None):
    g = g or []
    return [
        rect(x, y, w, 40, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
        text(x + 12, y + 12, f"{ICON['search']}  {placeholder}", 13, FAINT, width=w - 24, g=g),
    ]


def filter_chips(x, y, labels, active=0, g=None):
    g = g or []
    els, xx = [], x
    for i, lab in enumerate(labels):
        w = max(60, len(lab) * 7.2 + 22)
        on = i == active
        els.append(rect(xx, y, w, 30, strokeColor=ACCENT if on else LINE,
                        backgroundColor=ACCENT_BG if on else BG, strokeWidth=1, groupIds=g))
        els.append(text(xx + 11, y + 8, lab, 12, ACCENT if on else MUTED, width=w - 22, g=g))
        xx += w + 8
    return els


def tabs(x, y, w, labels, active=0, g=None):
    """Underlined tab strip. Returns (elements, next_y)."""
    g = g or []
    els = [line(x, y + 38, w, HAIRLINE, g)]
    xx = x
    for i, lab in enumerate(labels):
        tw = max(80, len(lab) * 7.6 + 28)
        on = i == active
        els.append(text(xx + 14, y + 11, lab, 13, INK if on else MUTED, width=tw - 28, g=g))
        if on:
            els.append(base("line", xx, y + 38, tw, 0, strokeColor=ACCENT, strokeWidth=3,
                            roundness=None, groupIds=g) | {"points": [[0, 0], [tw, 0]]})
        xx += tw
    return els, y + 54


def page_header(x, y, w, title, actions=None, subtitle=None, g=None):
    """Title (+subtitle) left, actions right. Returns (elements, next_y)."""
    g = g or []
    els = [text(x, y, title, 24, INK, g=g)]
    if subtitle:
        els.append(text(x, y + 32, subtitle, 13, MUTED, width=w * 0.6, g=g))
    bx = x + w
    for label, kind in reversed(actions or []):
        bw = max(112, len(label) * 7.6 + 28)
        bx -= bw
        els += btn(bx, y, bw, 40, label, kind, g)
        bx -= 10
    return els, y + (64 if subtitle else 56)


def breadcrumb(x, y, parts, g=None):
    return text(x, y, "  /  ".join(parts), 12, MUTED, g=g or [])


def note(x, y, w, content, color=ACCENT, g=None):
    """Spec annotation box — explains what the screen does to the data.

    Notes are developer annotations, not UI: they name real tables, columns and
    SQL. They are tagged `spec` so the localised boards leave them in English —
    translating `inventory_stock_transactions` would help nobody.
    """
    g = g or []
    bgmap = {ACCENT: ACCENT_BG, WARN: WARN_BG, DANGER: DANGER_BG, INFO: INFO_BG, VIOLET: VIOLET_BG}
    rows = content.count("\n") + 1
    h = 20 + rows * 17
    body = text(x + 12, y + 10, content, 12, color, width=w - 24, g=g)
    body["customData"] = {"spec": True}
    return [
        rect(x, y, w, h, strokeColor=color, backgroundColor=bgmap.get(color, ACCENT_BG),
             strokeWidth=1, groupIds=g),
        body,
    ]


# ── Barcode & QR ──────────────────────────────────────────────────
#
# Both are DERIVED from the SKU — nothing here is ever typed by a user.
#   barcode  = Code128-B encoding of inventory_items.sku
#   qr       = QR (ECC-M) whose payload is the same SKU
# The drawings are schematic: real bar widths / modules come from the encoder
# at render time. What the wireframe fixes is the SIZE, the caption and the
# placement, so the printed label and the on-screen profile agree.


def _bits(payload: str, n: int):
    """Deterministic bit stream for a payload — same SKU always draws the same."""
    out, buf = [], b""
    i = 0
    while len(out) < n:
        buf = hashlib.sha256(payload.encode() + str(i).encode()).digest()
        for byte in buf:
            for k in range(8):
                out.append((byte >> k) & 1)
        i += 1
    return out[:n]


def barcode(x, y, w, h, code, g=None, caption=True, symbology="Code 128"):
    """Code-128 barcode drawn from `code`. Returns (elements, next_y)."""
    g = g or []
    els = [rect(x, y, w, h, strokeColor=BG, backgroundColor=BG, strokeWidth=0, groupIds=g)]
    pad = 10.0
    inner_w = w - pad * 2
    bar_h = h - (22 if caption else 6)
    bits = _bits(code, 120)
    # quiet zone · start guard · data · stop guard
    pattern = [2, 1, 1, 2] + [1 + (b * 2) for b in bits] + [2, 3, 2]
    unit = inner_w / float(sum(pattern))
    xx = x + pad
    for i, width_units in enumerate(pattern):
        bw = width_units * unit
        if i % 2 == 0:                                   # bar
            els.append(rect(xx, y + 4, max(0.8, bw), bar_h,
                            strokeColor=INK, backgroundColor=INK, strokeWidth=0, groupIds=g))
        xx += bw
    if caption:
        els.append(text(x, y + h - 16, code, 12, INK, "center", w, g))
    return els, y + h + 4


def qr(x, y, size, payload, g=None, caption=None, modules=21):
    """QR code (schematic, 21×21 = version 1) whose payload is `payload`."""
    g = g or []
    els = [rect(x, y, size, size, strokeColor=BG, backgroundColor=BG, strokeWidth=0, groupIds=g)]
    quiet = size * 0.08
    grid = size - quiet * 2
    m = grid / modules
    bits = _bits(payload, modules * modules)

    def finder(fx, fy):
        out = [rect(fx, fy, m * 7, m * 7, strokeColor=INK, backgroundColor=INK,
                    strokeWidth=0, roundness=None, groupIds=g),
               rect(fx + m, fy + m, m * 5, m * 5, strokeColor=BG, backgroundColor=BG,
                    strokeWidth=0, roundness=None, groupIds=g),
               rect(fx + m * 2, fy + m * 2, m * 3, m * 3, strokeColor=INK,
                    backgroundColor=INK, strokeWidth=0, roundness=None, groupIds=g)]
        return out

    reserved = set()
    for r in range(8):
        for c in range(8):
            reserved |= {(r, c), (r, modules - 1 - c), (modules - 1 - r, c)}
    for r in range(modules):
        for c in range(modules):
            if (r, c) in reserved:
                continue
            if bits[r * modules + c]:
                els.append(rect(x + quiet + c * m, y + quiet + r * m, m, m,
                                strokeColor=INK, backgroundColor=INK, strokeWidth=0,
                                roundness=None, groupIds=g))
    els += finder(x + quiet, y + quiet)
    els += finder(x + quiet + grid - m * 7, y + quiet)
    els += finder(x + quiet, y + quiet + grid - m * 7)
    if caption:
        els.append(text(x, y + size + 6, caption, 10.5, MUTED, "center", size, g))
    return els, y + size + (22 if caption else 6)


def label_card(x, y, w, sku, name, sub, g=None, h=178, title="BARCODE & QR — generated from the SKU"):
    """Item-profile card: Code128 of the SKU + QR of the same SKU + print actions.

    Both codes carry the SAME payload — the SKU — so one scan resolves to one
    item whichever symbol the staff member happens to point the reader at.
    """
    g = g or []
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
           text(x + 16, y + 13, title, 11, MUTED, width=w - 32, g=g)]
    qs = min(96.0, h - 86)
    bcw = w - qs - 48
    e, _ = barcode(x + 16, y + 32, bcw, h - 118, sku, g)
    els += e
    els.append(text(x + 16, y + h - 82, f"Code 128  ·  {sub}", 10, FAINT, width=bcw, g=g))
    e, _ = qr(x + w - qs - 16, y + 32, qs, sku, g)
    els += e
    els.append(text(x + w - qs - 16, y + qs + 36, "QR = SKU", 10, FAINT, "center", qs, g))
    els += btn(x + 16, y + h - 44, 124, 32, "🖨 Print label", "secondary", g)
    els += btn(x + 148, y + h - 44, 110, 32, "⬇ Download", "ghost", g)
    return els, y + h + 12


def kpi_card(x, y, w, h, label, value, color=INK, delta=None, icon=None, g=None):
    g = g or []
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g)]
    lx = x + 16
    if icon:
        els.append(text(x + 16, y + 14, icon, 15, MUTED, g=g))
        lx = x + 40
    els.append(text(lx, y + 15, label, 11, MUTED, width=w - (lx - x) - 16, g=g))
    els.append(text(x + 16, y + 40, value, 22, color, width=w - 32, g=g))
    if delta:
        dc = OK if delta.startswith("+") else (DANGER if delta.startswith("−") or delta.startswith("-") else MUTED)
        els.append(text(x + 16, y + h - 24, delta, 11, dc, width=w - 32, g=g))
    return els


def stat_row(x, y, w, cards, h=92, gap=14, g=None):
    """cards = [(label, value, color, delta|None, icon|None), …]"""
    els = []
    n = len(cards)
    cw = (w - gap * (n - 1)) / n
    for i, c in enumerate(cards):
        lab, val, col = c[0], c[1], c[2]
        delta = c[3] if len(c) > 3 else None
        icon = c[4] if len(c) > 4 else None
        els += kpi_card(x + i * (cw + gap), y, cw, h, lab, val, col, delta, icon, g)
    return els, y + h + 20


def table(x, y, w, cols, rows, g=None, row_h=44, widths=None, zebra=True, sheet=False):
    """cols = ['SKU', …]; rows = [[c1, c2, …], …]. Returns (elements, next_y).

    `widths` are relative weights; defaults to equal columns.
    A cell may be a (text, color) tuple to colour it.
    `sheet=True` draws an Excel-like header: sort + per-column filter, then a
    filter row. Default stays a simple list header so existing boards do not move.
    """
    g = g or []
    n = len(cols)
    widths = widths or [1] * n
    total = sum(widths)
    xs, acc = [], 0.0
    for wt in widths:
        xs.append(x + acc / total * w)
        acc += wt
    header_h = 42 if sheet else 38
    els = [rect(x, y, w, header_h, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=g)]
    for i, c in enumerate(cols):
        col_w = w * widths[i] / total
        cw = col_w - 20
        if sheet:
            els.append(text(xs[i] + 10, y + 13, str(c), 11, MUTED, width=max(16, cw - 28), g=g))
            els.append(text(xs[i] + col_w - 28, y + 12, ICON["sort"], 11, FAINT, g=g))
        else:
            els.append(text(xs[i] + 12, y + 12, c, 11, MUTED, width=max(20, cw), g=g))
    yy = y + header_h
    if sheet:
        els.append(rect(x, yy, w, 30, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g))
        for i, c in enumerate(cols):
            col_w = w * widths[i] / total
            els.append(rect(xs[i] + 6, yy + 4, max(24, col_w - 12), 22,
                            strokeColor=HAIRLINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=g))
            els.append(text(xs[i] + 12, yy + 8, ICON["filter"] + "  Filter", 10, FAINT,
                            width=max(20, col_w - 24), g=g))
        yy += 30
    for r_i, row in enumerate(rows):
        if zebra and r_i % 2:
            els.append(rect(x, yy, w, row_h, strokeColor="transparent", backgroundColor=SOFT2,
                            strokeWidth=0, groupIds=g))
        els.append(line(x, yy + row_h, w, HAIRLINE, g))
        for i, cell in enumerate(row[:n]):
            val, col = (cell if isinstance(cell, tuple) else (cell, INK))
            cw = (w * widths[i] / total) - 20
            els.append(text(xs[i] + 12, yy + (row_h - 15) / 2, str(val), 12.5, col,
                            width=max(20, cw), g=g))
        yy += row_h
    return els, yy + 12


def pagination(x, y, w, summary="1–10 of 124", g=None):
    g = g or []
    els = [text(x, y + 10, summary, 12, MUTED, g=g)]
    bx = x + w - 288          # 5 buttons + 4 gaps — keeps the strip inside w
    for lab in ["‹ Prev", "1", "2", "3", "Next ›"]:
        bw = 44 if lab.isdigit() else 66
        els.append(rect(bx, y, bw, 34, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=g))
        els.append(text(bx + 6, y + 9, lab, 12, MUTED, "center", bw - 12, g))
        bx += bw + 6
    return els, y + 46


def empty_state(x, y, w, h, icon, title, body, cta=None, g=None):
    g = g or []
    els = [rect(x, y, w, h, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                strokeStyle="dashed", groupIds=g),
           text(x, y + h / 2 - 60, icon, 30, FAINT, "center", w, g),
           text(x, y + h / 2 - 16, title, 16, INK, "center", w, g),
           text(x, y + h / 2 + 8, body, 12, MUTED, "center", w, g)]
    if cta:
        els += btn(x + w / 2 - 80, y + h / 2 + 40, 160, 38, cta, "primary", g)
    return els


def drawer(ox, oy, cw, ch, title, side="right", width=440, subtitle=None, g=None):
    """Modal side drawer. Returns (elements, form_x, form_y, form_w)."""
    g = g or []
    dx = ox + cw - width if side == "right" else ox
    els = [
        rect(ox, oy, cw, ch, strokeColor="transparent", backgroundColor="#0f172a",
             strokeWidth=0, opacity=25, groupIds=g),
        rect(dx, oy, width, ch, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=g),
        text(dx + 24, oy + 20, title, 18, INK, width=width - 60, g=g),
        text(dx + width - 36, oy + 20, ICON["cross"], 16, MUTED, g=g),
        line(dx, oy + (72 if not subtitle else 86), width, HAIRLINE, g),
    ]
    if subtitle:
        els.append(text(dx + 24, oy + 46, subtitle, 11, MUTED, width=width - 60, g=g))
    return els, dx + 24, oy + (96 if not subtitle else 110), width - 48


def modal(ox, oy, cw, ch, title, body, w=460, h=240, actions=None, g=None):
    g = g or []
    mx, my = ox + (cw - w) / 2, oy + (ch - h) / 2
    els = [
        rect(ox, oy, cw, ch, strokeColor="transparent", backgroundColor="#0f172a",
             strokeWidth=0, opacity=30, groupIds=g),
        rect(mx, my, w, h, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=g),
        text(mx + 24, my + 24, title, 17, INK, width=w - 48, g=g),
        text(mx + 24, my + 56, body, 13, MUTED, width=w - 48, g=g),
    ]
    bx = mx + w - 24
    for label, kind in reversed(actions or [("Cancel", "secondary"), ("Confirm", "primary")]):
        bw = max(96, len(label) * 7.4 + 24)
        bx -= bw
        els += btn(bx, my + h - 60, bw, 38, label, kind, g)
        bx -= 10
    return els


def timeline(x, y, w, steps, g=None):
    """steps = [(label, state)] where state in done|current|todo. Horizontal stepper."""
    g = g or []
    els = []
    n = len(steps)
    seg = w / n
    for i, (lab, state) in enumerate(steps):
        cxx = x + i * seg + seg / 2
        col = {"done": OK, "current": ACCENT, "todo": LINE}[state]
        bgc = {"done": OK_BG, "current": ACCENT_BG, "todo": BG}[state]
        if i < n - 1:
            els.append(line(cxx + 16, y + 14, seg - 32, HAIRLINE, g))
        els.append(base("ellipse", cxx - 14, y, 28, 28, strokeColor=col,
                        backgroundColor=bgc, strokeWidth=2, groupIds=g))
        els.append(text(cxx - 14, y + 7, ICON["check"] if state == "done" else str(i + 1),
                        12, col, "center", 28, g))
        els.append(text(cxx - seg / 2, y + 36, lab, 11,
                        INK if state != "todo" else FAINT, "center", seg, g))
    return els, y + 64


def money_row(x, y, w, pairs, g=None, total=None):
    """Right-aligned totals block. pairs = [(label, value)]."""
    g = g or []
    els, yy = [], y
    for lab, val in pairs:
        v, col = (val if isinstance(val, tuple) else (val, INK))
        els.append(text(x, yy, lab, 13, MUTED, width=w * 0.55, g=g))
        els.append(text(x + w * 0.55, yy, str(v), 13, col, "right", w * 0.45, g=g))
        yy += 26
    if total:
        tv, tcol = (total[1] if isinstance(total[1], tuple) else (total[1], ACCENT))
        els.append(line(x, yy + 4, w, LINE, g))
        yy += 16
        els.append(text(x, yy, total[0], 15, INK, width=w * 0.55, g=g))
        els.append(text(x + w * 0.55, yy, str(tv), 18, tcol, "right", w * 0.45, g=g))
        yy += 30
    return els, yy


def bar_chart(x, y, w, h, title, bars, g=None, color=ACCENT):
    """bars = [(label, value_0_to_1, caption)] — schematic only."""
    g = g or []
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
           text(x + 16, y + 14, title, 13, INK, width=w - 32, g=g)]
    n = len(bars)
    plot_y, plot_h = y + 44, h - 88
    bw = (w - 48) / n
    for i, (lab, v, cap) in enumerate(bars):
        bh = max(4, plot_h * v)
        bx = x + 24 + i * bw
        els.append(rect(bx + bw * 0.18, plot_y + plot_h - bh, bw * 0.64, bh,
                        strokeColor=color, backgroundColor=color, strokeWidth=1, groupIds=g))
        els.append(text(bx, plot_y + plot_h + 8, lab, 10, MUTED, "center", bw, g))
        els.append(text(bx, plot_y + plot_h - bh - 16, cap, 10, INK, "center", bw, g))
    return els, y + h + 16


def calendar_grid(x, y, w, h, title, marks=None, g=None):
    """Month grid for rental availability. marks = {day: color}"""
    g = g or []
    marks = marks or {}
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
           text(x + 16, y + 14, title, 13, INK, width=w - 32, g=g)]
    cols, rows = 7, 5
    cell_w = (w - 32) / cols
    cell_h = (h - 72) / rows
    for i, d in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
        els.append(text(x + 16 + i * cell_w, y + 42, d, 10, MUTED, "center", cell_w, g))
    for r in range(rows):
        for c in range(cols):
            day = r * cols + c + 1
            if day > 31:
                continue
            cx0 = x + 16 + c * cell_w
            cy0 = y + 58 + r * cell_h
            col = marks.get(day)
            if col:
                els.append(rect(cx0 + 2, cy0 + 2, cell_w - 4, cell_h - 4,
                                strokeColor=col, backgroundColor=
                                {OK: OK_BG, WARN: WARN_BG, DANGER: DANGER_BG,
                                 ACCENT: ACCENT_BG}.get(col, SOFT),
                                strokeWidth=1, groupIds=g))
            els.append(text(cx0, cy0 + cell_h / 2 - 8, str(day), 10,
                            col or MUTED, "center", cell_w, g))
    return els, y + h + 16


# ── Shells ────────────────────────────────────────────────────────

NAV = [
    ("Home", "home", None),
    ("Inventory", "inventory", None),
    ("Sales", "sales", "8"),
    ("Procurement", "procurement", None),
    ("Finance", "finance", None),
    ("Reports", "reports", None),
    ("Settings", "settings", None),
]

SUBNAV = {
    "Inventory": ["Items", "Stock ledger", "Reservations", "Transfers", "Reports"],
    "Sales": ["Counter", "Orders", "Returns", "Customers", "Reports"],
    "Procurement": ["Suppliers", "Purchase orders", "Receipts (GRN)", "Reports"],
    "Finance": ["Dashboard", "Cash & banks", "Expenses", "A/P", "A/R", "P&L"],
    "Settings": ["Tenant", "Users & roles", "Branches", "Master data", "Audit log"],
}


def sidebar(ox, top, active, g, h=None, sub_active=None):
    """Icon sidebar with groups, active pill, sub-nav, branch switcher, user block."""
    h = h or (DESK_H - 35)
    els = [rect(ox + 1, top, SIDEBAR_W, h, strokeColor=SIDEBAR_BG,
                backgroundColor=SIDEBAR_BG, strokeWidth=1, groupIds=g)]
    # brand
    els.append(rect(ox + 20, top + 20, 34, 34, strokeColor=ACCENT,
                    backgroundColor=ACCENT, strokeWidth=1, groupIds=g))
    els.append(text(ox + 20, top + 28, ICON["dress"], 16, "#ffffff", "center", 34, g))
    els.append(text(ox + 64, top + 22, "BOMS", 18, "#ffffff", width=SIDEBAR_W - 80, g=g))
    els.append(text(ox + 64, top + 42, "Al Dubai Bridal", 11, SIDEBAR_MUTED,
                    width=SIDEBAR_W - 80, g=g))
    els.append(line(ox + 16, top + 72, SIDEBAR_W - 32, "#1e293b", g))

    groups = [("MAIN", NAV[:1]), ("OPERATIONS", NAV[1:4]), ("MONEY", NAV[4:5]),
              ("INSIGHT", NAV[5:6]), ("SYSTEM", NAV[6:])]
    yy = top + 88
    for gname, items in groups:
        els.append(text(ox + 24, yy, gname, 9.5, SIDEBAR_MUTED, width=SIDEBAR_W - 48, g=g))
        yy += 20
        for label, icon_key, badge in items:
            on = label == active
            if on:
                els.append(rect(ox + 12, yy - 6, SIDEBAR_W - 24, 36, strokeColor=ACCENT,
                                backgroundColor=ACCENT, strokeWidth=1, groupIds=g))
            els.append(text(ox + 26, yy + 3, ICON[icon_key], 14,
                            "#ffffff" if on else SIDEBAR_FG, g=g))
            els.append(text(ox + 52, yy + 4, label, 13.5,
                            "#ffffff" if on else SIDEBAR_FG, width=SIDEBAR_W - 90, g=g))
            if badge:
                els.append(rect(ox + SIDEBAR_W - 46, yy + 2, 26, 19, strokeColor=ROSE,
                                backgroundColor=ROSE, strokeWidth=1, groupIds=g))
                els.append(text(ox + SIDEBAR_W - 46, yy + 5, badge, 10, "#ffffff", "center", 26, g))
            yy += 38
            if on and label in SUBNAV:
                for s in SUBNAV[label]:
                    son = s == sub_active
                    els.append(text(ox + 56, yy + 2, ("• " if son else "  ") + s, 12,
                                    "#ffffff" if son else SIDEBAR_MUTED,
                                    width=SIDEBAR_W - 80, g=g))
                    yy += 26
        yy += 10

    # footer: branch + user
    fy = top + h - 92
    els.append(line(ox + 16, fy - 12, SIDEBAR_W - 32, "#1e293b", g))
    els.append(text(ox + 24, fy, f"{ICON['branch']}  Main branch  {ICON['down']}", 12,
                    SIDEBAR_FG, width=SIDEBAR_W - 48, g=g))
    els.append(base("ellipse", ox + 22, fy + 30, 30, 30, strokeColor=SIDEBAR_MUTED,
                    backgroundColor="#1e293b", strokeWidth=1, groupIds=g))
    els.append(text(ox + 22, fy + 38, "A", 12, "#ffffff", "center", 30, g))
    els.append(text(ox + 60, fy + 32, "Ahmad Zaki", 12, "#ffffff", width=SIDEBAR_W - 80, g=g))
    els.append(text(ox + 60, fy + 48, "Owner", 10, SIDEBAR_MUTED, width=SIDEBAR_W - 80, g=g))
    return els


def desk_shell(ox, oy, title, active_nav, group, show_sidebar=True, sub_active=None,
               topbar_extra=None, rtl=False):
    """Browser window + icon sidebar + top bar.
    Returns (elements, content_x, content_y, content_w, content_h)."""
    g = [group]
    els = [text(ox, oy, title, 17, INK)]
    els.append(rect(ox, oy + TITLE_H, DESK_W, DESK_H, strokeColor=INK,
                    backgroundColor=SOFT2, strokeWidth=2, groupIds=g))
    # browser chrome
    els.append(rect(ox + 1, oy + TITLE_H + 1, DESK_W - 2, 34, strokeColor=HAIRLINE,
                    backgroundColor=SOFT, strokeWidth=1, groupIds=g))
    els.append(text(ox + 16, oy + TITLE_H + 10, "● ● ●", 12, FAINT, g=g))
    els.append(rect(ox + 70, oy + TITLE_H + 6, 360, 22, strokeColor=HAIRLINE,
                    backgroundColor=BG, strokeWidth=1, groupIds=g))
    els.append(text(ox + 82, oy + TITLE_H + 11, f"{ICON['lock']} boms.app/{active_nav.lower()}",
                    11, MUTED, width=340, g=g))

    top = oy + TITLE_H + 36
    if show_sidebar:
        els += sidebar(ox, top, active_nav, g, DESK_H - 37, sub_active)
        cx = ox + SIDEBAR_W + 28
        cw = DESK_W - SIDEBAR_W - 56
        # top bar
        els.append(rect(ox + SIDEBAR_W + 1, top, DESK_W - SIDEBAR_W - 2, TOPBAR_H,
                        strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g))
        els.append(text(ox + SIDEBAR_W + 28, top + 21, sub_active or active_nav, 15, INK,
                        width=300, g=g))
        # Language switcher shows the LANGUAGE ONLY — never a direction badge.
        right = topbar_extra or f"{ICON['globe']} English {ICON['down']}    {ICON['bell']} 3    {ICON['user']} Ahmad {ICON['down']}"
        els.append(text(ox + DESK_W - 420, top + 21, right, 12.5, MUTED, "right", 390, g=g))
        cy = top + TOPBAR_H + 26
        ch = DESK_H - TOPBAR_H - 74
    else:
        cx, cw = ox + 60, DESK_W - 120
        cy, ch = top + 30, DESK_H - 80
    return els, cx, cy, cw, ch


def phone_shell(ox, oy, title, group, active_tab="Home", show_nav=True):
    """Phone frame. Returns (elements, content_x, content_y, content_w, content_h)."""
    g = [group]
    els = [text(ox, oy, title, 15, INK)]
    els.append(rect(ox, oy + TITLE_H, PHONE_W, PHONE_H, strokeColor=INK,
                    backgroundColor=BG, strokeWidth=2, groupIds=g))
    els.append(text(ox + 18, oy + TITLE_H + 12, "9:41", 11, INK, g=g))
    els.append(text(ox + PHONE_W - 90, oy + TITLE_H + 12, "▮▮▮  ᯤ  100%", 10, INK, width=72, g=g))
    cy = oy + TITLE_H + 40
    ch = PHONE_H - 40 - (72 if show_nav else 0)
    if show_nav:
        els += phone_nav(ox, oy, active_tab, g)
    return els, ox + 18, cy, PHONE_W - 36, ch


def phone_nav(ox, oy, active, g=None):
    g = g or []
    y = oy + TITLE_H + PHONE_H - 72
    els = [rect(ox + 1, y, PHONE_W - 2, 71, strokeColor=HAIRLINE, backgroundColor=BG,
                strokeWidth=1, groupIds=g)]
    tabs_ = [("Home", "home"), ("Inventory", "inventory"), ("Sales", "sales"),
             ("Finance", "finance"), ("More", "filter")]
    tw = PHONE_W / len(tabs_)
    for i, (t, ik) in enumerate(tabs_):
        on = t == active
        els.append(text(ox + i * tw, y + 14, ICON[ik], 17, ACCENT if on else MUTED, "center", tw, g))
        els.append(text(ox + i * tw, y + 42, t, 9.5, ACCENT if on else MUTED, "center", tw, g))
    return els


def phone_header(x, y, w, title, left=None, right=None, g=None):
    g = g or []
    els = [text(x, y, title, 20, INK, width=w - 60, g=g)]
    if left:
        els = [text(x, y + 2, left, 16, INK, g=g),
               text(x + 28, y, title, 20, INK, width=w - 90, g=g)]
    if right:
        els.append(text(x + w - 30, y + 2, right, 16, MUTED, g=g))
    return els, y + 40


def fab(x, y, label, g=None):
    """Mobile floating action button."""
    g = g or []
    w = max(120, len(label) * 7.4 + 40)
    return [rect(x - w, y, w, 48, strokeColor=ACCENT, backgroundColor=ACCENT,
                 strokeWidth=1, groupIds=g),
            text(x - w, y + 15, label, 14, "#ffffff", "center", w, g)]


def list_card(x, y, w, lines, g=None, h=None, thumb=False, badge=None):
    """Mobile list row: optional thumb, stacked lines, optional status chip."""
    g = g or []
    h = h or (24 + len(lines) * 20)
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g)]
    tx = x + 14
    if thumb:
        els.append(rect(x + 12, y + 12, h - 24, h - 24, strokeColor=HAIRLINE,
                        backgroundColor=SOFT, strokeWidth=1, groupIds=g))
        els.append(text(x + 12, y + h / 2 - 10, ICON["dress"], 16, FAINT, "center", h - 24, g))
        tx = x + h + 4
    for i, ln in enumerate(lines):
        val, col, sz = (ln if isinstance(ln, tuple) else (ln, INK if i == 0 else MUTED, 14 if i == 0 else 12))
        els.append(text(tx, y + 13 + i * 20, val, sz, col, width=w - (tx - x) - 90, g=g))
    if badge:
        lab, col = badge
        ch_, _ = chip(x + w - 14 - max(52, len(lab) * 7), y + 13, lab, col, g=g)
        els += ch_
    return els, y + h + 10


# ── Document assembly ─────────────────────────────────────────────

def board_title(x, y, title, subtitle=""):
    els = [text(x, y, title, 30, INK)]
    if subtitle:
        els.append(text(x, y + 42, subtitle, 14, MUTED, width=3400))
    return els


def section_label(x, y, label, color=ROSE):
    return [rect(x, y, 8, 30, strokeColor=color, backgroundColor=color, strokeWidth=1),
            text(x + 20, y + 4, label, 20, color)]


def grid_pos(i, cols, frame_w=DESK_W, frame_h=DESK_H, gap_x=GAP_X, row_gap=ROW_GAP):
    return (i % cols) * (frame_w + gap_x), (i // cols) * (frame_h + row_gap)


def grouped_board(groups, cols, frame_w=DESK_W, frame_h=DESK_H,
                  gap_x=GAP_X, row_gap=ROW_GAP, colors=None, arrows=True):
    """Lay screens out section by section — every section starts on a fresh row.

    groups = [(SECTION LABEL, [fn, fn, …]), …] where each fn(ox, oy) -> elements.
    This is what makes a board readable top-to-bottom: a reader sees one heading,
    then only the screens that belong under it, in the order they are used.
    """
    els = []
    row = 0
    for gi, (label, fns) in enumerate(groups):
        colour = (colors or {}).get(label, ROSE)
        els += section_label(0, row * (frame_h + row_gap) - 74,
                             f"{chr(65 + gi)}.  {label}", colour)
        for i, fn in enumerate(fns):
            ox = (i % cols) * (frame_w + gap_x)
            oy = (row + i // cols) * (frame_h + row_gap)
            els += fn(ox, oy)
            if arrows and i and i % cols:
                y = oy + TITLE_H + frame_h / 2
                els += arrow(ox - gap_x + 10, y, ox - 10, y)
        row += (len(fns) + cols - 1) // cols
    return els


# ── Right-to-left mirroring ───────────────────────────────────────
#
# The Dari / Pashto boards are the SAME drawing, mirrored. Building them by
# reflection rather than by hand guarantees the two versions can never drift:
# one layout change updates both. Mirroring is geometric only — the strings are
# swapped separately by i18n.localise().

_ALIGN_FLIP = {"left": "right", "right": "left", "center": "center"}


def mirror(elements, x0, width):
    """Reflect every element about the vertical axis of [x0, x0 + width]."""
    out = []
    for el in elements:
        e = copy.deepcopy(el)
        if e.get("points"):
            # Lines and arrows are anchored at their first point, so mirror the
            # anchor and negate the x offsets — an arrow that pointed right now
            # points left, which is what a mirrored flow needs.
            e["x"] = 2 * x0 + width - el.get("x", 0)
            e["points"] = [[-px, py] for px, py in el["points"]]
        else:
            e["x"] = 2 * x0 + width - el.get("x", 0) - el.get("width", 0)
        if e.get("type") == "text" and not (e.get("customData") or {}).get("spec"):
            # Spec notes stay in English, so they keep their left alignment even
            # on a mirrored board — only UI text follows the reading direction.
            e["textAlign"] = _ALIGN_FLIP.get(e.get("textAlign", "left"), "left")
        out.append(e)
    return out


def flow_arrows(count, cols, frame_w=DESK_W, frame_h=DESK_H, gap_x=GAP_X, row_gap=ROW_GAP):
    """Left→right arrows between consecutive frames on each row."""
    els = []
    for i in range(count - 1):
        if (i + 1) % cols == 0:
            continue
        row = i // cols
        y = row * (frame_h + row_gap) + TITLE_H + frame_h / 2
        x1 = (i % cols) * (frame_w + gap_x) + frame_w + 10
        els += arrow(x1, y, x1 + gap_x - 20, y)
    return els


def doc(elements):
    return {
        "type": "excalidraw", "version": 2,
        "source": "https://boms.local/wireframes",
        "elements": elements,
        "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
        "files": {},
    }


def write(path: Path, elements):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc(elements), indent=1))
    return f"{path}  ({len(elements)} elements)"
