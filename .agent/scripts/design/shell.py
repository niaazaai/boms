#!/usr/bin/env python3
"""The BOMS application shell — sidebar, top bar, page header.

Drawn once here so every screen is provably the same chrome, and so the RTL
version is the identical code with `Canvas(rtl=True)`.
"""

from __future__ import annotations

from svg import btn, chip, icon, icon_btn, line, rect, txt
from tokens import C, FRAME_H, FRAME_W, GUTTER, RADIUS, SIDEBAR_W, TOPBAR_H, TYPE

NAV = [
    ("MAIN", [("home", "Home", None, [])]),
    ("OPERATIONS", [
        ("package", "Inventory", None,
         ["Items", "Stock ledger", "Reservations", "Transfers", "Reports"]),
        ("cart", "Sales", "8", []),
        ("truck", "Procurement", None, []),
    ]),
    ("MONEY", [("wallet", "Finance", None, [])]),
    ("INSIGHT", [("chart", "Reports", None, [])]),
    ("SYSTEM", [("settings", "Settings", None, [])]),
]


def sidebar(cv, T, active="Inventory", sub_active="Items"):
    rect(cv, 0, 0, SIDEBAR_W, FRAME_H, C["sidebar"])
    line(cv, SIDEBAR_W, 0, 0, C["border"])
    cv.add(f'<line x1="{cv.fx(SIDEBAR_W):.2f}" y1="0" x2="{cv.fx(SIDEBAR_W):.2f}" '
           f'y2="{FRAME_H}" stroke="{C["border"]}" stroke-width="1"/>')

    # brand
    rect(cv, 24, 28, 40, 40, C["primary"], None, RADIUS["control"])
    icon(cv, 34, 38, "sparkle", 20, C["primary_fg"], 1.6)
    txt(cv, 76, 32, T["brand"], "h3", C["ink"])
    txt(cv, 76, 52, T["brand_sub"], "caption", C["muted"])
    line(cv, 24, 88, SIDEBAR_W - 48, C["border"])

    y = 108
    for group, items in NAV:
        txt(cv, 28, y, T.get(group, group), "micro", C["muted"], upper=True)
        y += 22
        for ic, label, badge, subs in items:
            on = label == active
            if on:
                rect(cv, 16, y - 6, SIDEBAR_W - 32, 44, C["accent"], None, RADIUS["sm"])
            fg = C["accent_ink"] if on else C["body"]
            icon(cv, 32, y + 8, ic, 18, fg, 1.7)
            txt(cv, 62, y + 9, T.get(label, label), "body_medium" if on else "body", fg)
            if badge:
                rect(cv, SIDEBAR_W - 56, y + 8, 28, 20, C["primary"], None, RADIUS["chip"])
                txt(cv, SIDEBAR_W - 42, y + 11, badge, "caption", C["primary_fg"], "middle")
            y += 44
            if on and subs:
                for s in subs:
                    son = s == sub_active
                    if son:
                        rect(cv, 60, y + 2, 3, 16, C["primary"], None, 2)
                    txt(cv, 74, y + 3, T.get(s, s), "small",
                        C["ink"] if son else C["muted"])
                    y += 30
        y += 14

    # footer
    fy = FRAME_H - 116
    line(cv, 24, fy - 16, SIDEBAR_W - 48, C["border"])
    rect(cv, 24, fy, SIDEBAR_W - 48, 40, C["surface"], C["border"], RADIUS["control"])
    icon(cv, 38, fy + 11, "warehouse", 18, C["muted"], 1.6)
    txt(cv, 66, fy + 12, T["branch"], "small", C["body"])
    icon(cv, SIDEBAR_W - 48, fy + 11, "chevron", 16, C["muted"])

    uy = fy + 52
    rect(cv, 24, uy, 36, 36, C["tan"], None, RADIUS["chip"])
    txt(cv, 42, uy + 10, T["user_initial"], "body_medium", "#FFFFFF", "middle")
    txt(cv, 70, uy + 3, T["user"], "body_medium", C["ink"])
    txt(cv, 70, uy + 21, T["role"], "caption", C["muted"])


def topbar(cv, T):
    x = SIDEBAR_W
    w = FRAME_W - SIDEBAR_W
    rect(cv, x, 0, w, TOPBAR_H, C["bg"])
    line(cv, x, TOPBAR_H, w, C["border"])

    # search pill
    sx, sw = x + GUTTER, 420
    rect(cv, sx, 14, sw, 36, C["surface"], C["border"], RADIUS["pill"])
    icon(cv, sx + 14, 23, "search", 18, C["muted"], 1.7)
    txt(cv, sx + 42, 24, T["search_global"], "small", C["disabled"])
    rect(cv, sx + sw - 62, 22, 48, 20, C["divider"], None, RADIUS["sm"])
    txt(cv, sx + sw - 38, 24, "⌘K", "caption", C["muted"], "middle")

    # right cluster — the language switcher names the LANGUAGE, never a direction
    rx = FRAME_W - GUTTER
    rect(cv, rx - 112, 14, 112, 36, C["surface"], C["border"], RADIUS["pill"])
    rect(cv, rx - 104, 20, 24, 24, C["tan"], None, RADIUS["chip"])
    txt(cv, rx - 92, 25, T["user_initial"], "caption", "#FFFFFF", "middle")
    txt(cv, rx - 74, 24, T["user_short"], "small", C["ink"])
    icon(cv, rx - 32, 23, "chevron", 16, C["muted"])

    icon_btn(cv, rx - 160, 14, "bell", 36, C["body"], C["surface"])
    rect(cv, rx - 134, 16, 8, 8, C["danger"], None, 4)

    lw = 108
    rect(cv, rx - 160 - lw - 8, 14, lw, 36, C["surface"], C["border"], RADIUS["pill"])
    txt(cv, rx - 160 - lw + 8, 24, T["language"], "small", C["body"])
    icon(cv, rx - 160 - 32, 23, "chevron", 16, C["muted"])


def page_header(cv, y, title, subtitle=None, actions=None):
    """actions = [(label, kind, icon|None), …] laid out from the trailing edge."""
    x = SIDEBAR_W + GUTTER
    txt(cv, x, y, title, "h1", C["ink"])
    if subtitle:
        txt(cv, x, y + 36, subtitle, "small", C["muted"])
    bx = FRAME_W - GUTTER
    for label, kind, ic in reversed(actions or []):
        bw = max(112, len(label) * 7.6 + (60 if ic else 40))
        bx -= bw
        btn(cv, bx, y - 2, bw, 40, label, kind, ic)
        bx -= 10
    return y + (76 if subtitle else 60)


def content_box():
    """(x, width) of the page content column."""
    return SIDEBAR_W + GUTTER, FRAME_W - SIDEBAR_W - GUTTER * 2


def tabs(cv, x, y, w, labels, active=0):
    line(cv, x, y + 40, w, C["border"])
    xx = x
    for i, lab in enumerate(labels):
        tw = max(96, len(lab) * 7.4 + 36)
        on = i == active
        txt(cv, xx + tw / 2, y + 12, lab, "body_medium" if on else "body",
            C["ink"] if on else C["muted"], "middle")
        if on:
            cv.add(f'<rect x="{cv.fx(xx, tw):.2f}" y="{y + 38:.2f}" width="{tw:.2f}" '
                   f'height="2.5" rx="1.25" fill="{C["primary"]}"/>')
        xx += tw
    return y + 60


def drawer(cv, T, title, subtitle=None, width=560):
    """Offcanvas over the page. Opens from the trailing edge of the reading
    direction — right in English, left in Dari and Pashto."""
    rect(cv, 0, 0, FRAME_W, FRAME_H, "#1B1C1A", opacity=0.28)
    dx = FRAME_W - width
    cv.defs.append('<filter id="drawerShadow" x="-50%" y="-20%" width="200%" height="140%">'
                   '<feDropShadow dx="-16" dy="0" stdDeviation="20" flood-color="#1B1C1A" '
                   'flood-opacity="0.16"/></filter>')
    rect(cv, dx, 0, width, FRAME_H, C["surface"], None, 0, filt="drawerShadow")
    txt(cv, dx + 28, 26, title, "h2", C["ink"])
    if subtitle:
        txt(cv, dx + 28, 56, subtitle, "caption", C["muted"])
    icon_btn(cv, FRAME_W - 28 - 36, 24, "x", 36, C["body"], C["divider"])
    line(cv, dx, 92, width, C["border"])
    return dx + 28, 116, width - 56


def drawer_footer(cv, T, width=560, buttons=None):
    dx = FRAME_W - width
    fy = FRAME_H - 80
    line(cv, dx, fy, width, C["border"])
    rect(cv, dx, fy + 1, width, 79, C["surface"])
    bx = FRAME_W - 28
    for label, kind in reversed(buttons or []):
        bw = max(120, len(label) * 7.8 + 44)
        bx -= bw
        btn(cv, bx, fy + 20, bw, 44, label, kind)
        bx -= 10
