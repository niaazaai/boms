#!/usr/bin/env python3
"""Generate BOMS Excalidraw wireframes for mobile/ and desktop/."""

from __future__ import annotations

import json
import random
import string
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "specs" / "wireframes"
OUT_MOBILE = ROOT / "mobile"
OUT_DESKTOP = ROOT / "desktop"

# Mobile phone
PHONE_W, PHONE_H = 375, 812
# Desktop browser window
DESK_W, DESK_H = 1280, 800
SIDEBAR_W = 220
TOPBAR_H = 56

GAP_X = 100
TITLE_H = 40
NOW = int(time.time() * 1000)

INK = "#1e1e1e"
MUTED = "#6b7280"
LINE = "#9ca3af"
BG = "#ffffff"
SOFT = "#f3f4f6"
SOFT2 = "#f9fafb"
PRIMARY = "#111827"
ACCENT = "#0f766e"
WARN = "#d97706"
DANGER = "#dc2626"
OK = "#059669"
SIDEBAR_BG = "#0f172a"
SIDEBAR_FG = "#e2e8f0"


def nid(n: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(random.choice(alphabet) for _ in range(n))


def base(el_type: str, x: float, y: float, w: float, h: float, **kw):
    return {
        "id": nid(),
        "type": el_type,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": kw.get("strokeColor", INK),
        "backgroundColor": kw.get("backgroundColor", "transparent"),
        "fillStyle": "solid",
        "strokeWidth": kw.get("strokeWidth", 1),
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": kw.get("groupIds", []),
        "frameId": None,
        "index": kw.get("index", "a0"),
        "roundness": kw.get("roundness", {"type": 3} if el_type in ("rectangle", "diamond") else None),
        "version": 1,
        "versionNonce": random.randint(1, 2**31 - 1),
        "isDeleted": False,
        "boundElements": [],
        "updated": NOW,
        "link": None,
        "locked": False,
        "seed": random.randint(1, 2**31 - 1),
    }


def rect(x, y, w, h, **kw):
    return base("rectangle", x, y, w, h, **kw)


def text(x, y, content: str, size: float = 16, color: str = INK, align: str = "left", width: float | None = None):
    lines = content.split("\n")
    line_h = size * 1.25
    tw = width if width is not None else max(8.0, max(len(L) for L in lines) * size * 0.55)
    th = line_h * len(lines)
    el = base("text", x, y, tw, th, strokeColor=color, roundness=None)
    el.update(
        {
            "text": content,
            "fontSize": size,
            "fontFamily": 5,
            "textAlign": align,
            "verticalAlign": "top",
            "containerId": None,
            "originalText": content,
            "autoResize": True,
            "lineHeight": 1.25,
        }
    )
    return el


def arrow(x1, y1, x2, y2, label: str | None = None):
    els = []
    a = base("arrow", x1, y1, abs(x2 - x1) or 1, abs(y2 - y1) or 1, strokeWidth=2, roundness={"type": 2})
    a["points"] = [[0, 0], [x2 - x1, y2 - y1]]
    a["startArrowhead"] = None
    a["endArrowhead"] = "arrow"
    a["elbowed"] = False
    els.append(a)
    if label:
        els.append(text((x1 + x2) / 2 - 30, (y1 + y2) / 2 - 18, label, size=12, color=MUTED))
    return els


def btn(x, y, w, h, label: str, primary: bool = True, g=None):
    g = g or []
    bg = PRIMARY if primary else SOFT
    fg = "#ffffff" if primary else INK
    return [
        rect(x, y, w, h, strokeColor=INK, backgroundColor=bg, strokeWidth=1, groupIds=g),
        text(x + 8, y + (h - 18) / 2, label, size=14, color=fg, width=w - 16, align="center"),
    ]


def field(x, y, w, label: str, placeholder: str = "", g=None):
    g = g or []
    els = [text(x, y, label, size=12, color=MUTED, width=w)]
    els.append(rect(x, y + 18, w, 36, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=g))
    if placeholder:
        els.append(text(x + 10, y + 26, placeholder, size=13, color=LINE, width=w - 20))
    return els, y + 62


def chip(x, y, label: str, color: str = OK, g=None):
    g = g or []
    w = max(56, len(label) * 8)
    return [
        rect(x, y, w, 22, strokeColor=color, backgroundColor="#ecfdf5" if color == OK else "#fff7ed", strokeWidth=1, groupIds=g),
        text(x + 6, y + 3, label, size=11, color=color, width=w - 12),
    ]


def doc(elements: list) -> dict:
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://boms.local/wireframes",
        "elements": elements,
        "appState": {"gridSize": None, "viewBackgroundColor": "#f8fafc"},
        "files": {},
    }


def flow_arrows(count: int, frame_w: float, mid_y: float):
    els = []
    for i in range(count - 1):
        x1 = i * (frame_w + GAP_X) + frame_w + 8
        x2 = (i + 1) * (frame_w + GAP_X) - 8
        els += arrow(x1, mid_y, x2, mid_y)
    return els


# ─── Mobile shell ─────────────────────────────────────────────

def phone_shell(ox, oy, title, group):
    g = [group]
    els = [text(ox, oy, title, size=18, color=INK)]
    els.append(rect(ox, oy + TITLE_H, PHONE_W, PHONE_H, strokeColor=INK, backgroundColor=BG, strokeWidth=2, groupIds=g))
    els.append(rect(ox + 1, oy + TITLE_H + 1, PHONE_W - 2, 28, strokeColor=SOFT, backgroundColor=SOFT2, strokeWidth=1, groupIds=g))
    els.append(text(ox + 16, oy + TITLE_H + 6, "9:41          BOMS          100%", size=11, color=MUTED, width=PHONE_W - 32))
    return els, ox + 16, oy + TITLE_H + 36, PHONE_W - 32


def nav_bar(ox, active: str, g=None):
    g = g or []
    y = TITLE_H + PHONE_H - 56
    els = [rect(ox, y, PHONE_W, 56, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=g)]
    tabs = ["Home", "Inventory", "Sales", "More"]
    tw = PHONE_W / 4
    for i, t in enumerate(tabs):
        els.append(text(ox + i * tw + 8, y + 18, t, size=11, color=ACCENT if t == active else MUTED, width=tw - 16, align="center"))
    return els


# ─── Desktop shell ────────────────────────────────────────────

def desk_shell(ox, oy, title: str, active_nav: str, group: str, show_sidebar: bool = True):
    """Browser window with optional left sidebar. Returns els, content_x, content_y, content_w, content_h."""
    g = [group]
    els = [text(ox, oy, title, size=18, color=INK)]
    # outer window
    els.append(rect(ox, oy + TITLE_H, DESK_W, DESK_H, strokeColor=INK, backgroundColor=BG, strokeWidth=2, groupIds=g))
    # title bar / chrome
    els.append(rect(ox + 1, oy + TITLE_H + 1, DESK_W - 2, 32, strokeColor=SOFT, backgroundColor=SOFT2, strokeWidth=1, groupIds=g))
    els.append(text(ox + 16, oy + TITLE_H + 8, "● ● ●   boms.app / " + active_nav.lower(), size=12, color=MUTED, width=600))

    top = oy + TITLE_H + 34
    if show_sidebar:
        els.append(rect(ox + 1, top, SIDEBAR_W, DESK_H - 35, strokeColor=SIDEBAR_BG, backgroundColor=SIDEBAR_BG, strokeWidth=1, groupIds=g))
        els.append(text(ox + 20, top + 20, "BOMS", size=20, color="#ffffff", width=SIDEBAR_W - 40))
        els.append(text(ox + 20, top + 48, "Al Dubai Bridal", size=12, color="#94a3b8", width=SIDEBAR_W - 40))
        nav = ["Home", "Inventory", "Sales", "Procurement", "Finance", "Settings"]
        for i, n in enumerate(nav):
            yy = top + 90 + i * 40
            active = n == active_nav
            if active:
                els.append(rect(ox + 10, yy - 6, SIDEBAR_W - 20, 32, strokeColor=ACCENT, backgroundColor=ACCENT, strokeWidth=1, groupIds=g))
            els.append(text(ox + 24, yy, n, size=14, color="#ffffff" if active else SIDEBAR_FG, width=SIDEBAR_W - 48))
        cx = ox + SIDEBAR_W + 24
        cw = DESK_W - SIDEBAR_W - 48
    else:
        cx = ox + 40
        cw = DESK_W - 80
    cy = top + 24
    ch = DESK_H - 70
    # top app bar in content
    if show_sidebar:
        els.append(rect(ox + SIDEBAR_W + 1, top, DESK_W - SIDEBAR_W - 2, TOPBAR_H, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=g))
        els.append(text(ox + SIDEBAR_W + 24, top + 18, f"{active_nav}                          Branch: Main ▾     🔔  Ahmad ▾", size=14, color=INK, width=DESK_W - SIDEBAR_W - 60))
        cy = top + TOPBAR_H + 20
        ch = DESK_H - TOPBAR_H - 70
    return els, cx, cy, cw, ch


# ═══════════════════════════════════════════════════════════════
# MOBILE MODULES
# ═══════════════════════════════════════════════════════════════

def m_auth():
    els = [text(0, -80, "BOMS Mobile — Auth", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Welcome", g)
    els += pe
    els.append(text(cx, cy + 80, "BOMS", size=32, color=ACCENT, width=cw, align="center"))
    els.append(text(cx, cy + 130, "Bridal Shop Manager", size=16, color=INK, width=cw, align="center"))
    els.append(text(cx, cy + 170, "Rentals · Sales · Daily profit", size=13, color=MUTED, width=cw, align="center"))
    els += btn(cx, cy + 280, cw, 48, "Login to shop", True, [g])
    els += btn(cx, cy + 344, cw, 48, "Register new shop", False, [g])
    els.append(text(cx, cy + 420, "Language: EN | دری | پښتو", size=12, color=MUTED, width=cw, align="center"))

    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Login", g)
    els += pe
    els.append(text(cx, cy + 8, "← Back", size=14, color=MUTED))
    els.append(text(cx, cy + 50, "Login", size=24, color=INK, width=cw, align="center"))
    f, y = field(cx, cy + 110, cw, "Phone or Email", "0700 000 0000", [g])
    els += f
    f, y = field(cx, y + 8, cw, "Password", "••••••••", [g])
    els += f
    els.append(text(cx, y + 8, "Forgot password?", size=13, color=ACCENT))
    els += btn(cx, y + 48, cw, 48, "Sign in", True, [g])

    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. Forgot password", g)
    els += pe
    els.append(text(cx, cy + 20, "Reset password", size=22, color=INK))
    f, y = field(cx, cy + 80, cw, "Phone or Email", "", [g])
    els += f
    els += btn(cx, y + 20, cw, 48, "Send reset code", True, [g])

    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. Register shop", g)
    els += pe
    els.append(text(cx, cy + 8, "Create your shop · Step 1/3", size=16, color=INK))
    f, y = field(cx, cy + 50, cw, "Shop name *", "Al Dubai Bridal", [g])
    els += f
    f, y = field(cx, y, cw, "Shop code *", "ADF", [g])
    els += f
    f, y = field(cx, y, cw, "Phone *", "", [g])
    els += f
    els.append(text(cx, y + 4, "Business: (•) Both  ( ) Sale  ( ) Rental", size=12, color=INK, width=cw))
    els += btn(cx, y + 50, cw, 48, "Continue", True, [g])

    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. Accept invite", g)
    els += pe
    els.append(text(cx, cy + 40, "Join Al Dubai Bridal", size=20, color=INK, width=cw, align="center"))
    els.append(text(cx, cy + 80, "Invited as: Cashier", size=14, color=MUTED, width=cw, align="center"))
    f, y = field(cx, cy + 130, cw, "Your name", "", [g])
    els += f
    f, y = field(cx, y, cw, "Set password", "", [g])
    els += f
    els += btn(cx, y + 24, cw, 48, "Join shop", True, [g])

    els += flow_arrows(5, PHONE_W, TITLE_H + PHONE_H / 2)
    return doc(els)


def m_platform():
    els = [text(0, -80, "BOMS Mobile — Platform / Settings", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Home dashboard", g)
    els += pe
    els.append(text(cx, cy + 4, "Al Dubai Bridal          🔔 👤", size=13, color=INK, width=cw))
    card_w = (cw - 8) / 2
    for i, (t, v, c) in enumerate([("Profit", "+2.4k", OK), ("Cash", "18.2k", ACCENT), ("A/R", "3.1k", WARN), ("A/P", "1.2k", DANGER)]):
        xx = cx + (i % 2) * (card_w + 8)
        yy = cy + 40 + (i // 2) * 70
        els.append(rect(xx, yy, card_w, 62, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 10, yy + 8, t, size=11, color=MUTED))
        els.append(text(xx + 10, yy + 28, v, size=18, color=c))
    els += btn(cx, cy + 200, (cw - 8) / 2, 40, "+ Sale", True, [g])
    els += btn(cx + (cw - 8) / 2 + 8, cy + 200, (cw - 8) / 2, 40, "+ Rent", False, [g])
    els.append(text(cx, cy + 260, "Due returns\n👗 Sara — due today", size=13, color=INK, width=cw))
    els += nav_bar(0, "Home", [g])

    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Settings hub", g)
    els += pe
    els.append(text(cx, cy + 8, "Settings", size=22, color=INK))
    for i, it in enumerate(["Shop profile ›", "Branches & warehouses ›", "Users & roles ›", "Currencies ›", "Units ›", "Payment methods ›", "Preferences ›"]):
        yy = cy + 50 + i * 40
        els.append(rect(cx, yy, cw, 36, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 12, yy + 10, it, size=13, color=INK))
    els += nav_bar(x, "More", [g])

    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. Shop profile", g)
    els += pe
    els.append(text(cx, cy + 8, "← Shop profile", size=16, color=INK))
    f, y = field(cx, cy + 50, cw, "Name", "Al Dubai Bridal", [g])
    els += f
    f, y = field(cx, y, cw, "Code", "ADF", [g])
    els += f
    f, y = field(cx, y, cw, "Phone", "", [g])
    els += f
    els += btn(cx, y + 20, cw, 48, "Save", True, [g])

    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. Branches", g)
    els += pe
    els.append(text(cx, cy + 8, "← Branches                    +", size=16, color=INK, width=cw))
    for i, (name, sub) in enumerate([("Main Branch (default)", "2 warehouses"), ("Second Floor", "1 warehouse")]):
        yy = cy + 50 + i * 80
        els.append(rect(cx, yy, cw, 70, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 12, yy + 16, f"{name}\n{sub}", size=14, color=INK))

    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. Users & roles", g)
    els += pe
    els.append(text(cx, cy + 8, "← Users                       +", size=16, color=INK, width=cw))
    for i, (name, role) in enumerate([("Ahmad · Owner", "Active"), ("Laila · Cashier", "Active"), ("Omar · Staff", "Invited")]):
        yy = cy + 50 + i * 64
        els.append(rect(cx, yy, cw, 56, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 12, yy + 10, name, size=14, color=INK))
        els += chip(cx + 12, yy + 30, role, OK if role == "Active" else WARN, [g])

    x = 5 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "6. Currencies", g)
    els += pe
    els.append(text(cx, cy + 8, "← Currencies                  +", size=16, color=INK, width=cw))
    els.append(rect(cx, cy + 50, cw, 56, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 66, "AFN · Default", size=14, color=INK))
    els.append(rect(cx, cy + 116, cw, 56, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 132, "USD · rate 70.5", size=14, color=INK))

    els += flow_arrows(6, PHONE_W, TITLE_H + PHONE_H / 2)
    return doc(els)


def m_inventory():
    els = [text(0, -80, "BOMS Mobile — Inventory", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Inventory list", g)
    els += pe
    els.append(text(cx, cy + 4, "Inventory                      +", size=16, color=INK, width=cw))
    els.append(rect(cx, cy + 36, cw, 36, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, cy + 44, "🔍 Search name / SKU / size", size=12, color=LINE))
    for i, (sku, name, st) in enumerate([("ADF26-0042", "White A-Line M", "Available"), ("ADF26-0038", "Gold Ball Gown L", "Rented"), ("ADF26-0031", "Veil set", "Available")]):
        yy = cy + 90 + i * 100
        els.append(rect(cx, yy, cw, 90, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(rect(cx + 8, yy + 12, 66, 66, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 86, yy + 14, f"{sku}\n{name}", size=13, color=INK))
        els += chip(cx + 86, yy + 56, st, OK if st == "Available" else WARN, [g])
    els += nav_bar(0, "Inventory", [g])

    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Item detail", g)
    els += pe
    els.append(text(cx, cy + 4, "← ADF26-0042", size=14, color=INK))
    els.append(rect(cx, cy + 30, cw, 140, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=[g]))
    els.append(text(cx, cy + 184, "White A-Line Dress", size=18, color=INK))
    els += chip(cx, cy + 214, "Available", OK, [g])
    els.append(text(cx, cy + 250, "Sale 12,000 · Rent 2,500 / 3d\nQty 1 · Main WH", size=13, color=MUTED, width=cw))
    els += btn(cx, cy + 320, (cw - 8) / 2, 40, "Adjust", False, [g])
    els += btn(cx + (cw - 8) / 2 + 8, cy + 320, (cw - 8) / 2, 40, "Edit", True, [g])

    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. Add item", g)
    els += pe
    els.append(text(cx, cy + 4, "← New item", size=16, color=INK))
    f, y = field(cx, cy + 36, cw, "Name *", "White A-Line", [g])
    els += f
    els.append(text(cx, y, "SKU auto · Purpose: Sale|Rent|Both", size=12, color=MUTED, width=cw))
    f, y = field(cx, y + 28, cw, "Size / Color", "M / White", [g])
    els += f
    f, y = field(cx, y, cw, "Sale / Rental price", "12000 / 2500", [g])
    els += f
    els += btn(cx, y + 16, cw, 48, "Save item", True, [g])

    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. Adjust stock", g)
    els += pe
    els.append(text(cx, cy + 8, "← Adjust · On hand: 1", size=16, color=INK))
    f, y = field(cx, cy + 50, cw, "Reason", "Damage ▾", [g])
    els += f
    f, y = field(cx, y, cw, "Counted qty", "0", [g])
    els += f
    els += btn(cx, y + 20, cw, 48, "Post adjustment", True, [g])

    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. Transfer", g)
    els += pe
    els.append(text(cx, cy + 8, "← Transfer", size=16, color=INK))
    f, y = field(cx, cy + 50, cw, "From → To", "Main → Floor 2", [g])
    els += f
    els.append(rect(cx, y + 8, cw, 50, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, y + 24, "White A-Line · qty 1", size=13, color=INK))
    els += btn(cx, y + 80, cw, 48, "Send transfer", True, [g])

    els += flow_arrows(5, PHONE_W, TITLE_H + PHONE_H / 2)
    return doc(els)


def m_sales():
    els = [text(0, -80, "BOMS Mobile — Sales", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Sales home", g)
    els += pe
    els.append(text(cx, cy + 4, "Sales · Today 5 · 41k", size=18, color=INK, width=cw))
    els += btn(cx, cy + 50, cw, 48, "+ New Sale", True, [g])
    els += btn(cx, cy + 108, cw, 48, "+ New Rental", False, [g])
    els.append(rect(cx, cy + 180, cw, 64, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 196, "SO-019 · Sara · Rental due today", size=13, color=INK, width=cw - 24))
    els += nav_bar(0, "Sales", [g])

    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Pick customer", g)
    els += pe
    els.append(rect(cx, cy + 20, cw, 40, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, cy + 30, "🔍 Phone or name", size=13, color=LINE))
    els.append(rect(cx, cy + 80, cw, 50, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 96, "Sara · 0700… · wedding 20 Sep", size=13, color=INK))
    els += btn(cx, cy + 160, cw, 48, "+ New customer", False, [g])

    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. New sale", g)
    els += pe
    els.append(text(cx, cy + 4, "← Sale · Sara", size=16, color=INK))
    els.append(rect(cx, cy + 40, cw, 44, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, cy + 52, "White A-Line ×1     12,000", size=13, color=INK))
    els.append(text(cx, cy + 100, "Total 13,000 AFN", size=16, color=INK))
    els += btn(cx, cy + 150, cw, 48, "Complete sale", True, [g])

    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. New rental", g)
    els += pe
    els.append(text(cx, cy + 4, "← Rental · Sara", size=16, color=INK))
    f, y = field(cx, cy + 40, cw, "Event / From → To", "20 Sep / 19→21", [g])
    els += f
    els.append(rect(cx, y + 8, cw, 56, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, y + 20, "Gold Gown · 2,500 · dep 1,000", size=12, color=INK))
    els += btn(cx, y + 90, cw, 48, "Confirm booking", True, [g])

    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. Order detail", g)
    els += pe
    els.append(text(cx, cy + 4, "← SO-019 · Rental", size=16, color=INK))
    els += chip(cx, cy + 36, "Confirmed", WARN, [g])
    els.append(text(cx, cy + 70, "Balance 1,500 · Deposit 1,000", size=13, color=MUTED))
    els += btn(cx, cy + 120, cw, 40, "Mark rented out", True, [g])
    els += btn(cx, cy + 170, cw, 40, "Mark returned", False, [g])

    x = 5 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "6. Sales return", g)
    els += pe
    els.append(text(cx, cy + 8, "← Return · SO-018", size=16, color=INK))
    els.append(text(cx, cy + 50, "[✓] White A-Line ×1", size=14, color=INK))
    f, y = field(cx, cy + 90, cw, "Reason", "Customer change ▾", [g])
    els += f
    els += btn(cx, y + 20, cw, 48, "Post return", True, [g])

    els += flow_arrows(6, PHONE_W, TITLE_H + PHONE_H / 2)
    return doc(els)


def m_procurement():
    els = [text(0, -80, "BOMS Mobile — Procurement", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Procurement home", g)
    els += pe
    els.append(text(cx, cy + 4, "Procurement · AP 1.2k", size=18, color=INK, width=cw))
    els += btn(cx, cy + 50, cw, 48, "+ New purchase", True, [g])
    els += btn(cx, cy + 108, cw, 48, "Suppliers", False, [g])
    els.append(rect(cx, cy + 180, cw, 64, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 196, "PO-012 · Fashion Co · Ordered", size=13, color=INK))

    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Suppliers", g)
    els += pe
    els.append(text(cx, cy + 8, "← Suppliers                   +", size=16, color=INK, width=cw))
    els.append(rect(cx, cy + 50, cw, 56, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 66, "Fashion Import Co · Active", size=13, color=INK))

    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. Create PO", g)
    els += pe
    els.append(text(cx, cy + 4, "← New purchase", size=16, color=INK))
    f, y = field(cx, cy + 40, cw, "Supplier / Warehouse", "Fashion · Main", [g])
    els += f
    els.append(rect(cx, y + 8, cw, 50, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, y + 24, "New dress · qty1 · 7,500", size=12, color=INK))
    els += btn(cx, y + 80, cw, 48, "Mark ordered", True, [g])

    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. Receive goods", g)
    els += pe
    els.append(text(cx, cy + 8, "← Receive · PO-012", size=16, color=INK))
    els.append(text(cx, cy + 50, "Receive [1] → create SKU\nSize M · Color White", size=14, color=INK, width=cw))
    els += btn(cx, cy + 140, cw, 48, "Post receive", True, [g])

    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. Pay supplier", g)
    els += pe
    els.append(text(cx, cy + 8, "← Pay · Balance 8,000", size=16, color=INK))
    f, y = field(cx, cy + 60, cw, "Amount / Account", "8000 / Bank", [g])
    els += f
    els += btn(cx, y + 20, cw, 48, "Record payment", True, [g])

    els += flow_arrows(5, PHONE_W, TITLE_H + PHONE_H / 2)
    return doc(els)


def m_finance():
    els = [text(0, -80, "BOMS Mobile — Finance", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Finance dashboard", g)
    els += pe
    els.append(text(cx, cy + 4, "Finance · Today", size=18, color=INK))
    yy = cy + 40
    for title, val, col in [("1. Cash & Banks", "18,200", ACCENT), ("2. Income", "15,500", OK), ("3. Expenses", "2,100", DANGER), ("4. A/P we owe", "1,200", WARN), ("5. A/R they owe", "3,100", WARN)]:
        els.append(rect(cx, yy, cw, 48, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 12, yy + 6, title, size=11, color=MUTED))
        els.append(text(cx + 12, yy + 24, val, size=15, color=col))
        yy += 54
    els.append(text(cx, yy + 4, "Net profit +4,200", size=16, color=OK))
    els += btn(cx, yy + 36, cw, 40, "+ Expense", True, [g])

    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Cash & Banks", g)
    els += pe
    els.append(text(cx, cy + 8, "← Cash & Banks", size=16, color=INK))
    for i, (n, v) in enumerate([("Cash Drawer", "4,200"), ("Bank", "12,000"), ("Wallet", "2,000")]):
        yy = cy + 50 + i * 60
        els.append(rect(cx, yy, cw, 52, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 12, yy + 16, f"{n}  {v} AFN", size=14, color=INK))

    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. Add expense", g)
    els += pe
    els.append(text(cx, cy + 8, "← New expense", size=16, color=INK))
    f, y = field(cx, cy + 50, cw, "Category", "Shop rent ▾", [g])
    els += f
    f, y = field(cx, y, cw, "Amount *", "", [g])
    els += f
    els += btn(cx, y + 16, cw, 48, "Save expense", True, [g])

    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. Payables", g)
    els += pe
    els.append(text(cx, cy + 8, "← We owe (A/P)", size=16, color=INK))
    els.append(rect(cx, cy + 50, cw, 70, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 66, "Fashion Co · 8,000 → [Pay]", size=13, color=INK))

    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. Receivables", g)
    els += pe
    els.append(text(cx, cy + 8, "← They owe (A/R)", size=16, color=INK))
    els.append(rect(cx, cy + 50, cw, 70, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 12, cy + 66, "Sara · 1,500 → [Collect]", size=13, color=INK))

    x = 5 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "6. P&L report", g)
    els += pe
    els.append(text(cx, cy + 8, "← Profit & Loss · Month", size=16, color=INK))
    els.append(text(cx, cy + 50, "Income 167k\nCOGS -70k\nGross 97k\nExpenses -28k\nNet 69k", size=15, color=INK, width=cw))

    els += flow_arrows(6, PHONE_W, TITLE_H + PHONE_H / 2)
    return doc(els)


# ═══════════════════════════════════════════════════════════════
# DESKTOP MODULES
# ═══════════════════════════════════════════════════════════════

def table_header(x, y, w, cols, g):
    els = [rect(x, y, w, 36, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=g)]
    els.append(text(x + 12, y + 10, "   |   ".join(cols), size=12, color=MUTED, width=w - 24))
    return els


def table_row(x, y, w, label, g, h=40):
    return [
        rect(x, y, w, h, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
        text(x + 12, y + 12, label, size=13, color=INK, width=w - 24),
    ]


def d_auth():
    els = [text(0, -80, "BOMS Desktop — Auth (centered cards, no sidebar)", size=28, color=INK)]
    # Welcome
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(0, 0, "1. Welcome", "Home", g, show_sidebar=False)
    els += pe
    card_w = 420
    card_x = cx + (cw - card_w) / 2
    els.append(rect(card_x, cy + 80, card_w, 420, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=[g]))
    els.append(text(card_x + 40, cy + 140, "BOMS", size=36, color=ACCENT, width=card_w - 80, align="center"))
    els.append(text(card_x + 40, cy + 200, "Bridal Shop Manager\nRentals · Sales · Daily profit", size=16, color=MUTED, width=card_w - 80, align="center"))
    els += btn(card_x + 60, cy + 300, card_w - 120, 48, "Login to shop", True, [g])
    els += btn(card_x + 60, cy + 364, card_w - 120, 48, "Register new shop", False, [g])

    x = DESK_W + GAP_X
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "2. Login", "Home", g, show_sidebar=False)
    els += pe
    card_x = cx + (cw - card_w) / 2
    els.append(rect(card_x, cy + 60, card_w, 400, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=[g]))
    els.append(text(card_x + 40, cy + 90, "Login", size=24, color=INK, width=card_w - 80, align="center"))
    f, y = field(card_x + 40, cy + 150, card_w - 80, "Phone or Email", "0700…", [g])
    els += f
    f, y = field(card_x + 40, y, card_w - 80, "Password", "••••••••", [g])
    els += f
    els.append(text(card_x + 40, y + 4, "Forgot password?", size=13, color=ACCENT))
    els += btn(card_x + 40, y + 40, card_w - 80, 48, "Sign in", True, [g])

    x = 2 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "3. Register shop", "Home", g, show_sidebar=False)
    els += pe
    card_x = cx + (cw - 520) / 2
    els.append(rect(card_x, cy + 40, 520, 520, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=[g]))
    els.append(text(card_x + 40, cy + 60, "Create your shop · Step 1/3", size=18, color=INK))
    f, y = field(card_x + 40, cy + 110, 440, "Shop name *", "Al Dubai Bridal", [g])
    els += f
    f, y = field(card_x + 40, y, 440, "Shop code *", "ADF", [g])
    els += f
    f, y = field(card_x + 40, y, 440, "Phone *", "", [g])
    els += f
    f, y = field(card_x + 40, y, 440, "Default currency", "AFN ▾", [g])
    els += f
    els.append(text(card_x + 40, y + 8, "Business type: (•) Both  ( ) Sale  ( ) Rental", size=13, color=INK))
    els += btn(card_x + 40, y + 50, 440, 48, "Continue", True, [g])

    x = 3 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "4. Accept invite", "Home", g, show_sidebar=False)
    els += pe
    card_x = cx + (cw - card_w) / 2
    els.append(rect(card_x, cy + 80, card_w, 360, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=[g]))
    els.append(text(card_x + 40, cy + 120, "Join Al Dubai Bridal\nRole: Cashier", size=18, color=INK, width=card_w - 80, align="center"))
    f, y = field(card_x + 40, cy + 200, card_w - 80, "Name / Password", "", [g])
    els += f
    els += btn(card_x + 40, y + 30, card_w - 80, 48, "Join shop", True, [g])

    els += flow_arrows(4, DESK_W, TITLE_H + DESK_H / 2)
    return doc(els)


def d_platform():
    els = [text(0, -80, "BOMS Desktop — Platform / Settings", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(0, 0, "1. Home dashboard", "Home", g)
    els += pe
    # KPI row
    kw = (cw - 36) / 4
    for i, (t, v, c) in enumerate([("Today profit", "+4,200", OK), ("Cash & Banks", "18,200", ACCENT), ("Receivables", "3,100", WARN), ("Payables", "1,200", DANGER)]):
        xx = cx + i * (kw + 12)
        els.append(rect(xx, cy, kw, 90, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 16, cy + 16, t, size=13, color=MUTED))
        els.append(text(xx + 16, cy + 44, v, size=24, color=c))
    els.append(text(cx, cy + 110, "Quick actions", size=14, color=MUTED))
    for i, lab in enumerate(["+ Sale", "+ Rental", "+ Expense", "Open inventory"]):
        els += btn(cx + i * 160, cy + 135, 148, 40, lab, i == 0, [g])
    # two panels
    els.append(rect(cx, cy + 200, cw * 0.55 - 8, 280, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 16, cy + 216, "Due returns today", size=15, color=INK))
    els += table_row(cx + 16, cy + 250, cw * 0.55 - 40, "SO-019  Sara   Gold Gown   due today", [g])
    els += table_row(cx + 16, cy + 298, cw * 0.55 - 40, "SO-021  Fatima Veil set    due Fri", [g])
    els.append(rect(cx + cw * 0.55 + 8, cy + 200, cw * 0.45 - 8, 280, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + cw * 0.55 + 24, cy + 216, "Today activity", size=15, color=INK))
    els.append(text(cx + cw * 0.55 + 24, cy + 250, "3 sales · 2 rentals\n2 low stock alerts\n1 PO to receive", size=14, color=MUTED, width=280))

    x = DESK_W + GAP_X
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "2. Settings hub", "Settings", g)
    els += pe
    cards = ["Shop profile", "Branches & warehouses", "Users & roles", "Currencies", "Units", "Payment methods", "Payment terms", "Preferences", "Languages", "Audit log"]
    for i, cname in enumerate(cards):
        xx = cx + (i % 3) * ((cw - 24) / 3 + 12)
        yy = cy + (i // 3) * 100
        els.append(rect(xx, yy, (cw - 24) / 3, 84, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 16, yy + 30, cname + "  ›", size=15, color=INK))

    x = 2 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "3. Shop profile", "Settings", g)
    els += pe
    els.append(text(cx, cy, "Shop profile", size=22, color=INK))
    els.append(rect(cx, cy + 40, 120, 120, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 35, cy + 90, "Logo", size=13, color=MUTED))
    f, y = field(cx + 150, cy + 40, 400, "Shop name", "Al Dubai Bridal", [g])
    els += f
    f, y = field(cx + 150, y, 400, "Code / Phone / Website", "ADF · 0700…", [g])
    els += f
    f, y = field(cx + 150, y, 400, "Default currency / Language", "AFN · English", [g])
    els += f
    els += btn(cx + 150, y + 20, 160, 44, "Save changes", True, [g])

    x = 3 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "4. Branches & users", "Settings", g)
    els += pe
    els.append(text(cx, cy, "Branches                              [ + Add ]", size=18, color=INK, width=cw * 0.48))
    els += table_header(cx, cy + 40, cw * 0.48 - 8, ["Code", "Name", "Warehouses", "Status"], [g])
    els += table_row(cx, cy + 80, cw * 0.48 - 8, "MAIN   Main Branch   2 WH   Active", [g])
    els += table_row(cx, cy + 124, cw * 0.48 - 8, "FL2    Second Floor  1 WH   Active", [g])
    rx = cx + cw * 0.52
    els.append(text(rx, cy, "Users                                 [ + Invite ]", size=18, color=INK, width=cw * 0.48))
    els += table_header(rx, cy + 40, cw * 0.48 - 8, ["Name", "Role", "Branch", "Status"], [g])
    els += table_row(rx, cy + 80, cw * 0.48 - 8, "Ahmad   Owner    Main   Active", [g])
    els += table_row(rx, cy + 124, cw * 0.48 - 8, "Laila   Cashier  Main   Active", [g])
    els += table_row(rx, cy + 168, cw * 0.48 - 8, "Omar    Staff    Main   Invited", [g])

    els += flow_arrows(4, DESK_W, TITLE_H + DESK_H / 2)
    return doc(els)


def d_inventory():
    els = [text(0, -80, "BOMS Desktop — Inventory", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(0, 0, "1. Inventory list", "Inventory", g)
    els += pe
    els.append(text(cx, cy, "Inventory", size=22, color=INK))
    els.append(rect(cx + 200, cy, 280, 36, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 210, cy + 8, "🔍 Search SKU / name / size", size=13, color=LINE))
    els += btn(cx + cw - 140, cy, 140, 36, "+ Add item", True, [g])
    els.append(text(cx, cy + 50, "Filters: All · Available · Rented · Sale · Repair   Branch ▾  Category ▾", size=12, color=MUTED, width=cw))
    els += table_header(cx, cy + 80, cw, ["Image", "SKU", "Name", "Size", "Status", "Sale", "Rent", "Qty", "Actions"], [g])
    rows = [
        "□  ADF26-0042  White A-Line     M   Available  12,000  2,500  1  Open",
        "□  ADF26-0038  Gold Ball Gown   L   Rented     —      2,500  0  Open",
        "□  ADF26-0031  Veil set         —   Available  1,500  500    4  Open",
        "□  ADF26-0029  Engagement set   S   Repairing  8,000  1,800  1  Open",
    ]
    for i, r in enumerate(rows):
        els += table_row(cx, cy + 120 + i * 44, cw, r, [g], 42)

    x = DESK_W + GAP_X
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "2. Item detail", "Inventory", g)
    els += pe
    els.append(rect(cx, cy, 320, 360, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 120, cy + 170, "photos", size=14, color=MUTED))
    els.append(text(cx + 350, cy, "White A-Line Dress", size=24, color=INK))
    els += chip(cx + 350, cy + 40, "Available", OK, [g])
    els.append(text(cx + 350, cy + 80, "SKU ADF26-0042 · Size M · Color White\nPurpose: Both · Branch Main · WH A\n\nSale price     12,000 AFN\nRental         2,500 / 3 days\nDeposit        1,000 AFN\nCost basis     7,500 AFN\nQty on hand    1", size=14, color=MUTED, width=500))
    els += btn(cx + 350, cy + 320, 120, 40, "Edit", True, [g])
    els += btn(cx + 480, cy + 320, 120, 40, "Adjust", False, [g])
    els += btn(cx + 610, cy + 320, 120, 40, "Transfer", False, [g])
    els += btn(cx + 740, cy + 320, 140, 40, "Reserve", False, [g])

    x = 2 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "3. Add / Edit item", "Inventory", g)
    els += pe
    els.append(text(cx, cy, "New inventory item", size=22, color=INK))
    f, y = field(cx, cy + 50, 420, "Name *", "White A-Line", [g])
    els += f
    f, _ = field(cx + 450, cy + 50, 420, "SKU (auto)", "ADF26-0043", [g])
    els += f
    f, y = field(cx, y, 420, "Category / Type / Model", "Dresses ▾", [g])
    els += f
    f, _ = field(cx + 450, cy + 112, 420, "Purpose", "Both ▾", [g])
    els += f
    f, y = field(cx, y, 200, "Size", "M", [g])
    els += f
    f, _ = field(cx + 220, cy + 174, 200, "Color", "White", [g])
    els += f
    f, _ = field(cx + 450, cy + 174, 420, "Sale price / Rental / Deposit", "12000 / 2500 / 1000", [g])
    els += f
    f, y = field(cx, y, 420, "Purchase cost / Other / Currency", "7500 / 0 / AFN", [g])
    els += f
    f, _ = field(cx + 450, cy + 236, 420, "Branch / Warehouse", "Main / WH-A", [g])
    els += f
    els += btn(cx, y + 40, 180, 44, "Save item", True, [g])

    x = 3 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "4. Adjust & Transfer", "Inventory", g)
    els += pe
    els.append(text(cx, cy, "Stock adjustment", size=18, color=INK))
    els.append(rect(cx, cy + 40, cw * 0.48 - 8, 360, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    f, y = field(cx + 20, cy + 60, cw * 0.48 - 48, "Item", "White A-Line · on hand 1", [g])
    els += f
    f, y = field(cx + 20, y, cw * 0.48 - 48, "Reason / Counted qty", "Damage / 0", [g])
    els += f
    els += btn(cx + 20, y + 20, 160, 40, "Post adjustment", True, [g])
    rx = cx + cw * 0.52
    els.append(text(rx, cy, "Warehouse transfer", size=18, color=INK))
    els.append(rect(rx, cy + 40, cw * 0.48 - 8, 360, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    f, y = field(rx + 20, cy + 60, cw * 0.48 - 48, "From → To", "Main → Floor 2", [g])
    els += f
    els += table_row(rx + 20, y + 10, cw * 0.48 - 48, "White A-Line · qty 1", [g])
    els += btn(rx + 20, y + 80, 160, 40, "Send transfer", True, [g])

    els += flow_arrows(4, DESK_W, TITLE_H + DESK_H / 2)
    return doc(els)


def d_sales():
    els = [text(0, -80, "BOMS Desktop — Sales", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(0, 0, "1. Sales home", "Sales", g)
    els += pe
    els.append(text(cx, cy, "Sales center", size=22, color=INK))
    els += btn(cx + cw - 300, cy, 140, 40, "+ New Sale", True, [g])
    els += btn(cx + cw - 150, cy, 150, 40, "+ New Rental", False, [g])
    for i, (t, v) in enumerate([("Open orders", "8"), ("Due returns", "2"), ("Today sales", "41k"), ("Unpaid A/R", "3.1k")]):
        xx = cx + i * ((cw - 36) / 4 + 12)
        els.append(rect(xx, cy + 60, (cw - 36) / 4, 80, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 16, cy + 76, t, size=12, color=MUTED))
        els.append(text(xx + 16, cy + 100, v, size=22, color=INK))
    els.append(text(cx, cy + 160, "Tabs: Open | Due returns | Completed | Customers", size=13, color=MUTED))
    els += table_header(cx, cy + 190, cw, ["Order", "Customer", "Type", "Dates", "Total", "Paid", "Status", "Actions"], [g])
    for i, r in enumerate([
        "SO-019  Sara    Rental  19–21 Sep  2,500  1,000  Confirmed  Open",
        "SO-018  Maryam  Sale    Today      12,000 12,000 Completed Open",
        "SO-017  Fatima  Rental  12–14 Sep  3,000  3,000  Returned   Open",
    ]):
        els += table_row(cx, cy + 230 + i * 44, cw, r, [g], 42)

    x = DESK_W + GAP_X
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "2. New sale checkout", "Sales", g)
    els += pe
    els.append(text(cx, cy, "New sale", size=22, color=INK))
    # left customer + items, right totals
    els.append(rect(cx, cy + 50, cw * 0.62 - 8, 500, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    f, y = field(cx + 20, cy + 70, cw * 0.62 - 48, "Customer", "Sara · 0700… ✎  [ + New ]", [g])
    els += f
    els.append(text(cx + 20, y + 8, "Line items                         [ + Add item ]", size=14, color=MUTED))
    els += table_header(cx + 20, y + 36, cw * 0.62 - 48, ["Item", "Qty", "Price", "Total"], [g])
    els += table_row(cx + 20, y + 76, cw * 0.62 - 48, "White A-Line   1   12,000   12,000", [g])
    els += table_row(cx + 20, y + 120, cw * 0.62 - 48, "Veil set       1    1,500    1,500", [g])
    rx = cx + cw * 0.62 + 8
    els.append(rect(rx, cy + 50, cw * 0.38 - 8, 500, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(rx + 20, cy + 80, "Summary", size=18, color=INK))
    els.append(text(rx + 20, cy + 120, "Subtotal     13,500\nDiscount       -500\nTotal        13,000\n\nPay: Full / Partial\nMethod: Cash ▾\nAccount: Drawer ▾", size=14, color=INK, width=280))
    els += btn(rx + 20, cy + 360, cw * 0.38 - 48, 48, "Complete sale", True, [g])

    x = 2 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "3. New rental checkout", "Sales", g)
    els += pe
    els.append(text(cx, cy, "New rental booking", size=22, color=INK))
    els.append(rect(cx, cy + 50, cw * 0.62 - 8, 500, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    f, y = field(cx + 20, cy + 70, 280, "Customer", "Sara", [g])
    els += f
    f, _ = field(cx + 320, cy + 70, 280, "Event date", "20 Sep 2026", [g])
    els += f
    f, y = field(cx + 20, y, 280, "Rental from", "19 Sep", [g])
    els += f
    f, _ = field(cx + 320, cy + 132, 280, "Rental to", "21 Sep", [g])
    els += f
    els += table_row(cx + 20, y + 20, cw * 0.62 - 48, "Gold Ball Gown L · 2,500 · dep 1,000 · ✓ no conflict", [g], 48)
    rx = cx + cw * 0.62 + 8
    els.append(rect(rx, cy + 50, cw * 0.38 - 8, 500, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(rx + 20, cy + 100, "Rental total   2,500\nDeposit due    1,000\nBalance later  1,500\n\nTake deposit now [✓]\nMethod Cash ▾", size=14, color=INK, width=280))
    els += btn(rx + 20, cy + 360, cw * 0.38 - 48, 48, "Confirm booking", True, [g])

    x = 3 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "4. Order detail + return", "Sales", g)
    els += pe
    els.append(text(cx, cy, "SO-019 · Rental · Confirmed", size=22, color=INK))
    els.append(text(cx, cy + 40, "Sara · 19–21 Sep · Event 20 Sep · Balance 1,500", size=14, color=MUTED, width=cw))
    els += btn(cx, cy + 80, 160, 40, "Collect payment", False, [g])
    els += btn(cx + 170, cy + 80, 160, 40, "Mark rented out", True, [g])
    els += btn(cx + 340, cy + 80, 160, 40, "Mark returned", False, [g])
    els += btn(cx + 510, cy + 80, 140, 40, "Return / refund", False, [g])
    els += table_header(cx, cy + 140, cw, ["Item", "Type", "Qty", "Price", "Deposit", "Status"], [g])
    els += table_row(cx, cy + 180, cw, "Gold Ball Gown L   Rental   1   2,500   1,000   Reserved", [g])
    els.append(rect(cx, cy + 250, cw, 200, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 20, cy + 270, "Return panel (when returning)\nCondition: Good | Cleaning | Damaged | Lost\nLate fee auto · Collect balance / Refund deposit remainder", size=14, color=INK, width=cw - 40))

    els += flow_arrows(4, DESK_W, TITLE_H + DESK_H / 2)
    return doc(els)


def d_procurement():
    els = [text(0, -80, "BOMS Desktop — Procurement", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(0, 0, "1. Procurement home", "Procurement", g)
    els += pe
    els.append(text(cx, cy, "Procurement", size=22, color=INK))
    els += btn(cx + cw - 300, cy, 140, 40, "+ Purchase", True, [g])
    els += btn(cx + cw - 150, cy, 150, 40, "Suppliers", False, [g])
    for i, (t, v) in enumerate([("Open POs", "2"), ("To receive", "1"), ("A/P open", "1.2k"), ("Suppliers", "12")]):
        xx = cx + i * ((cw - 36) / 4 + 12)
        els.append(rect(xx, cy + 60, (cw - 36) / 4, 80, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 16, cy + 76, t, size=12, color=MUTED))
        els.append(text(xx + 16, cy + 100, v, size=22, color=INK))
    els += table_header(cx, cy + 170, cw, ["PO", "Supplier", "Date", "Total", "Received", "Payment", "Status", "Actions"], [g])
    els += table_row(cx, cy + 210, cw, "PO-012  Fashion Co   08 Sep  8,000  0/1  Unpaid  Ordered   Receive", [g])
    els += table_row(cx, cy + 254, cw, "PO-011  Local Tailor 01 Sep  3,200  2/2  Paid    Received  View", [g])

    x = DESK_W + GAP_X
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "2. Suppliers", "Procurement", g)
    els += pe
    els.append(text(cx, cy, "Suppliers                              [ + Add ]", size=20, color=INK, width=cw))
    els += table_header(cx, cy + 50, cw, ["Code", "Name", "Phone", "Currency", "Term", "Status", "Actions"], [g])
    els += table_row(cx, cy + 90, cw, "SUP-01  Fashion Import Co   0700…  USD  Net 7   Active  Open", [g])
    els += table_row(cx, cy + 134, cw, "SUP-02  Kabul Local Tailor  0780…  AFN  Cash    Active  Open", [g])

    x = 2 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "3. Create PO + receive", "Procurement", g)
    els += pe
    els.append(text(cx, cy, "Purchase order PO-012", size=20, color=INK))
    f, y = field(cx, cy + 40, 300, "Supplier", "Fashion Co ▾", [g])
    els += f
    f, _ = field(cx + 320, cy + 40, 300, "Warehouse", "Main ▾", [g])
    els += f
    els += table_header(cx, cy + 120, cw, ["Item", "Ordered", "Received", "Unit cost", "Line total"], [g])
    els += table_row(cx, cy + 160, cw, "New white gown (create on receive)   1   0   7,500   7,500", [g])
    els += table_row(cx, cy + 204, cw, "Veil pack (existing)                 10  0     200   2,000", [g])
    els.append(text(cx, cy + 270, "Other cost 500 · Total 10,000 · Status Ordered", size=14, color=MUTED))
    els += btn(cx, cy + 310, 160, 44, "Receive goods", True, [g])
    els += btn(cx + 180, cy + 310, 160, 44, "Pay supplier", False, [g])

    x = 3 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "4. Receive & pay", "Procurement", g)
    els += pe
    els.append(rect(cx, cy, cw * 0.55 - 8, 480, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 20, cy + 20, "Receive goods", size=18, color=INK))
    els.append(text(cx + 20, cy + 60, "For new lines: create inventory item\nSize · Color · Purpose · Photos\nThen post → stock_in + open A/P", size=14, color=MUTED, width=400))
    els += btn(cx + 20, cy + 200, 180, 44, "Post receive", True, [g])
    rx = cx + cw * 0.55 + 8
    els.append(rect(rx, cy, cw * 0.45 - 8, 480, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(rx + 20, cy + 20, "Pay supplier", size=18, color=INK))
    f, y = field(rx + 20, cy + 70, cw * 0.45 - 48, "Amount due", "10,000", [g])
    els += f
    f, y = field(rx + 20, y, cw * 0.45 - 48, "From account / Method", "Bank / Transfer", [g])
    els += f
    els += btn(rx + 20, y + 30, 180, 44, "Record payment", True, [g])

    els += flow_arrows(4, DESK_W, TITLE_H + DESK_H / 2)
    return doc(els)


def d_finance():
    els = [text(0, -80, "BOMS Desktop — Finance (5 pillars)", size=28, color=INK)]
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(0, 0, "1. Finance dashboard", "Finance", g)
    els += pe
    els.append(text(cx, cy, "Finance · Today ▾ · All branches ▾", size=20, color=INK, width=cw))
    kw = (cw - 48) / 5
    pillars = [("1 Cash", "18,200", ACCENT), ("2 Income", "15,500", OK), ("3 Expenses", "2,100", DANGER), ("4 A/P", "1,200", WARN), ("5 A/R", "3,100", WARN)]
    for i, (t, v, c) in enumerate(pillars):
        xx = cx + i * (kw + 12)
        els.append(rect(xx, cy + 50, kw, 100, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 12, cy + 66, t, size=12, color=MUTED))
        els.append(text(xx + 12, cy + 96, v, size=22, color=c))
    els.append(rect(cx, cy + 170, cw, 70, strokeColor=OK, backgroundColor="#ecfdf5", strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 20, cy + 192, "Net profit today  +4,200 AFN    (Income − Expenses − COGS)", size=18, color=OK, width=cw - 40))
    els += btn(cx, cy + 260, 140, 40, "+ Expense", True, [g])
    els += btn(cx + 150, cy + 260, 140, 40, "+ Income", False, [g])
    els += btn(cx + 300, cy + 260, 140, 40, "Pay A/P", False, [g])
    els += btn(cx + 450, cy + 260, 140, 40, "Collect A/R", False, [g])
    els.append(text(cx, cy + 320, "Recent transactions", size=14, color=MUTED))
    els += table_header(cx, cy + 350, cw, ["Time", "Type", "Counterparty", "Account", "Amount", "Ref"], [g])
    els += table_row(cx, cy + 390, cw, "11:20  IN   Sale SO-018   Cash drawer   +12,000   PAY-88", [g])
    els += table_row(cx, cy + 434, cw, "10:05  OUT  Shop rent     Bank          -2,100    EXP-12", [g])

    x = DESK_W + GAP_X
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "2. Cash / Expense / A/P / A/R", "Finance", g)
    els += pe
    # 2x2 panels
    panels = [
        (0, 0, "Cash & Banks", "Cash Drawer  4,200\nBank Azizi  12,000\nWallet       2,000\n[ Transfer ]"),
        (1, 0, "Add expense", "Category  Shop rent ▾\nAmount   ______\nPay from Cash ▾\n[ Save expense ]"),
        (0, 1, "Payables (we owe)", "Fashion Co  8,000 open → [Pay]\nTailor          paid ✓"),
        (1, 1, "Receivables (they owe)", "Sara SO-019  1,500 → [Collect]\nMaryam SO-015 3,000 → [Collect]"),
    ]
    pw, ph = cw * 0.48 - 8, 260
    for col, row, title, body in panels:
        xx = cx + col * (cw * 0.52)
        yy = cy + row * 280
        els.append(rect(xx, yy, pw, ph, strokeColor=LINE, backgroundColor=BG if col + row != 1 else SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 16, yy + 16, title, size=16, color=INK))
        els.append(text(xx + 16, yy + 56, body, size=14, color=MUTED, width=pw - 32))

    x = 2 * (DESK_W + GAP_X)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(x, 0, "3. P&L report", "Finance", g)
    els += pe
    els.append(text(cx, cy, "Profit & Loss · This month ▾ · Branch All ▾", size=20, color=INK, width=cw))
    els.append(rect(cx, cy + 50, cw * 0.55, 420, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(
        text(
            cx + 24,
            cy + 80,
            "Sales income              120,000\nRental income              45,000\nOther income                2,000\n────────────────────────────────\nTotal income              167,000\nCOGS                      -70,000\nGross profit               97,000\nOperating expenses        -28,000\n────────────────────────────────\nNet profit                 69,000",
            size=16,
            color=INK,
            width=cw * 0.55 - 48,
        )
    )
    els.append(rect(cx + cw * 0.55 + 16, cy + 50, cw * 0.45 - 16, 420, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + cw * 0.55 + 36, cy + 80, "Charts (placeholder)\n\n· Income vs expense bars\n· Pillar breakdown pie\n· Daily profit trend\n\n[ Share ]  [ Export CSV ]", size=15, color=MUTED, width=300))

    els += flow_arrows(3, DESK_W, TITLE_H + DESK_H / 2)
    return doc(els)


# ═══════════════════════════════════════════════════════════════

MOBILE = {
    "01-Auth.excalidraw": m_auth,
    "02-Platform-Settings.excalidraw": m_platform,
    "03-Inventory.excalidraw": m_inventory,
    "04-Sales.excalidraw": m_sales,
    "05-Procurement.excalidraw": m_procurement,
    "06-Finance.excalidraw": m_finance,
}

DESKTOP = {
    "01-Auth.excalidraw": d_auth,
    "02-Platform-Settings.excalidraw": d_platform,
    "03-Inventory.excalidraw": d_inventory,
    "04-Sales.excalidraw": d_sales,
    "05-Procurement.excalidraw": d_procurement,
    "06-Finance.excalidraw": d_finance,
}


def write_all(out: Path, mapping: dict):
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in mapping.items():
        data = fn()
        path = out / name
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT.parent.parent)} ({len(data['elements'])} elements)")


def cleanup_old():
    # remove legacy root excalidraw + markdown companions
    for p in ROOT.glob("*.excalidraw"):
        p.unlink()
        print(f"removed {p.name}")
    for p in ROOT.glob("*.md"):
        if p.name == "README.md":
            continue
        p.unlink()
        print(f"removed {p.name}")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    cleanup_old()
    write_all(OUT_MOBILE, MOBILE)
    write_all(OUT_DESKTOP, DESKTOP)
    (ROOT / "README.md").write_text(
        """# Wireframes

| Folder | Contents |
|--------|----------|
| [`mobile/`](./mobile/) | Mobile-first phone frames (375×812) |
| [`desktop/`](./desktop/) | Desktop browser frames (1280×800 + sidebar) |

Each folder:

- `01-Auth.excalidraw`
- `02-Platform-Settings.excalidraw`
- `03-Inventory.excalidraw`
- `04-Sales.excalidraw`
- `05-Procurement.excalidraw`
- `06-Finance.excalidraw`

Regenerate:

```bash
python3 .agent/scripts/generate_wireframes.py
```
""",
        encoding="utf-8",
    )
    print("updated specs/wireframes/README.md")


if __name__ == "__main__":
    main()
