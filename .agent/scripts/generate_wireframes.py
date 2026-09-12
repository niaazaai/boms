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


def search_bar(x, y, w, placeholder: str, g=None):
    g = g or []
    return [
        rect(x, y, w, 36, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
        text(x + 10, y + 10, f"🔍 {placeholder}", size=13, color=LINE, width=w - 20),
    ]


def filter_chips(x, y, labels: list[str], g=None):
    g = g or []
    els = []
    xx = x
    for i, lab in enumerate(labels):
        w = max(64, len(lab) * 7 + 16)
        bg = SOFT if i else "#ccfbf1"
        fg = MUTED if i else ACCENT
        els.append(rect(xx, y, w, 28, strokeColor=LINE if i else ACCENT, backgroundColor=bg, strokeWidth=1, groupIds=g))
        els.append(text(xx + 8, y + 6, lab, size=12, color=fg, width=w - 16))
        xx += w + 8
    return els


def page_header(x, y, w, title: str, actions: list[tuple[str, bool]], g=None):
    """Title left, action buttons right. Returns (els, y_after)."""
    g = g or []
    els = [text(x, y + 4, title, size=22, color=INK)]
    bx = x + w
    for label, primary in reversed(actions):
        bw = max(110, len(label) * 8 + 24)
        bx -= bw
        els += btn(bx, y, bw, 36, label, primary, g)
        bx -= 10
    return els, y + 52


def note(x, y, w, content: str, g=None):
    g = g or []
    return [
        rect(x, y, w, 36, strokeColor=ACCENT, backgroundColor="#ecfdf5", strokeWidth=1, groupIds=g),
        text(x + 12, y + 10, content, size=12, color=ACCENT, width=w - 24),
    ]


ROW_GAP = 160


def grid_pos(i: int, cols: int, frame_w: float, frame_h: float):
    return (i % cols) * (frame_w + GAP_X), (i // cols) * (frame_h + ROW_GAP)


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
    els = [text(0, -80, "BOMS Mobile — Auth & Authorization", size=28, color=INK)]
    # 1. Login only (public)
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Login (public only)", g)
    els += pe
    els.append(text(cx, cy + 40, "BOMS", size=28, color=ACCENT, width=cw, align="center"))
    els.append(text(cx, cy + 80, "Sign in to continue", size=14, color=MUTED, width=cw, align="center"))
    f, y = field(cx, cy + 130, cw, "Phone or Email", "0700 000 0000", [g])
    els += f
    f, y = field(cx, y + 4, cw, "Password", "••••••••", [g])
    els += f
    els.append(text(cx, y + 6, "Forgot password?", size=13, color=ACCENT))
    els += btn(cx, y + 40, cw, 48, "Sign in", True, [g])
    els.append(text(cx, y + 110, "No public register — tenants\nare created by Super Admin", size=11, color=MUTED, width=cw, align="center"))

    # 2. Forgot password
    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Forgot password", g)
    els += pe
    els.append(text(cx, cy + 20, "Reset password", size=20, color=INK))
    f, y = field(cx, cy + 70, cw, "Phone or Email", "", [g])
    els += f
    els += btn(cx, y + 16, cw, 48, "Send reset code", True, [g])

    # 3. Accept invite
    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. Accept invite", g)
    els += pe
    els.append(text(cx, cy + 24, "Join Al Dubai Bridal", size=18, color=INK, width=cw, align="center"))
    els.append(text(cx, cy + 56, "Role: Cashier", size=13, color=MUTED, width=cw, align="center"))
    f, y = field(cx, cy + 100, cw, "Your name", "", [g])
    els += f
    f, y = field(cx, y, cw, "Set password", "", [g])
    els += f
    els += btn(cx, y + 20, cw, 48, "Join tenant", True, [g])

    # 4. Users list
    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. Users list", g)
    els += pe
    els.append(text(cx, cy + 4, "Users                         +", size=16, color=INK, width=cw))
    els += search_bar(cx, cy + 36, cw, "Name / phone / email", [g])
    els += filter_chips(cx, cy + 80, ["All", "Active", "Invited", "Role▾"], [g])
    for i, (name, role) in enumerate([("Ahmad · Owner", "Active"), ("Laila · Cashier", "Active"), ("Omar · Staff", "Invited")]):
        yy = cy + 120 + i * 72
        els.append(rect(cx, yy, cw, 64, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 10, yy + 8, name, size=13, color=INK))
        els += chip(cx + 10, yy + 32, role, OK if role == "Active" else WARN, [g])
        els.append(text(cx + cw - 90, yy + 22, "⋮ Edit", size=12, color=MUTED))

    # 5. User create / actions
    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. User form / actions", g)
    els += pe
    els.append(text(cx, cy + 4, "← Create user", size=16, color=INK))
    f, y = field(cx, cy + 40, cw, "Name *", "Laila", [g])
    els += f
    f, y = field(cx, y, cw, "Phone / Email *", "", [g])
    els += f
    f, y = field(cx, y, cw, "Role *", "Cashier ▾", [g])
    els += f
    f, y = field(cx, y, cw, "Default branch", "Main ▾", [g])
    els += f
    els += btn(cx, y + 8, cw, 40, "Save user", True, [g])
    els += btn(cx, y + 56, cw, 36, "Send invitation", False, [g])
    els += btn(cx, y + 100, cw, 36, "Change role", False, [g])
    els += btn(cx, y + 144, cw, 36, "Delete / Deactivate", False, [g])

    # 6. Roles & permissions
    x = 5 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "6. Roles & permissions", g)
    els += pe
    els.append(text(cx, cy + 4, "Roles                          +", size=16, color=INK, width=cw))
    els += search_bar(cx, cy + 36, cw, "Role name", [g])
    for i, (name, sub) in enumerate([("Owner · system", "All permissions"), ("Manager", "24 permissions"), ("Cashier", "12 permissions")]):
        yy = cy + 84 + i * 70
        els.append(rect(cx, yy, cw, 62, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 10, yy + 12, f"{name}\n{sub}", size=13, color=INK))
    els.append(text(cx, cy + 310, "Edit role → permission matrix\nView · Create · Edit · Void / module", size=12, color=MUTED, width=cw))

    els += flow_arrows(6, PHONE_W, TITLE_H + PHONE_H / 2)
    return doc(els)


def m_platform():
    els = [text(0, -80, "BOMS Mobile — Platform / Settings", size=28, color=INK)]
    # 1. Settings hub
    g = nid()
    pe, cx, cy, cw = phone_shell(0, 0, "1. Settings hub", g)
    els += pe
    els.append(text(cx, cy + 4, "Settings", size=20, color=INK))
    items = [
        "Tenants (Super Admin) ›",
        "Tenant profile ›",
        "Branches & warehouses ›",
        "Currencies ›",
        "Units ›",
        "Payment methods ›",
        "Payment terms ›",
        "Preferences ›",
        "Languages ›",
        "Audit log ›",
    ]
    for i, it in enumerate(items):
        yy = cy + 40 + i * 36
        els.append(rect(cx, yy, cw, 32, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 10, yy + 8, it, size=12, color=INK))
    els += nav_bar(0, "More", [g])

    # 2. Tenants list
    x = PHONE_W + GAP_X
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "2. Tenants (Super Admin)", g)
    els += pe
    els.append(text(cx, cy + 4, "Tenants                       +", size=16, color=INK, width=cw))
    els += search_bar(cx, cy + 36, cw, "Name / code", [g])
    els += filter_chips(cx, cy + 80, ["All", "Shop", "Mall", "Active"], [g])
    for i, row in enumerate(["ADF · Al Dubai · Shop", "KBM · Kabul Mall · Mall"]):
        yy = cy + 120 + i * 70
        els.append(rect(cx, yy, cw, 62, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 10, yy + 18, row, size=13, color=INK))

    # 3. Tenant profile
    x = 2 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "3. Tenant profile", g)
    els += pe
    els.append(text(cx, cy + 4, "← Tenant profile", size=16, color=INK))
    f, y = field(cx, cy + 40, cw, "Name *", "Al Dubai Bridal", [g])
    els += f
    f, y = field(cx, y, cw, "Code * / Type", "ADF · Shop ▾", [g])
    els += f
    f, y = field(cx, y, cw, "Contact phone / email", "", [g])
    els += f
    f, y = field(cx, y, cw, "Address", "Kabul · Street…", [g])
    els += f
    els += btn(cx, y + 12, cw, 44, "Save", True, [g])

    # 4. Branches + warehouses
    x = 3 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "4. Branch → warehouses", g)
    els += pe
    els.append(text(cx, cy + 4, "← Main Branch              +", size=15, color=INK, width=cw))
    els.append(text(cx, cy + 36, "Warehouses (1 branch → many)", size=12, color=MUTED, width=cw))
    for i, (name, sub) in enumerate([("WH-A Default", "Main floor"), ("WH-B Storage", "Back room"), ("WH-C Repair", "Tailor desk")]):
        yy = cy + 64 + i * 72
        els.append(rect(cx, yy, cw, 64, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 10, yy + 14, f"{name}\n{sub}", size=13, color=INK))

    # 5. Master data sample
    x = 4 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "5. Master data (CRUD)", g)
    els += pe
    els.append(text(cx, cy + 4, "Currencies                    +", size=15, color=INK, width=cw))
    els += search_bar(cx, cy + 36, cw, "Code / name", [g])
    els.append(rect(cx, cy + 84, cw, 52, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, cy + 100, "AFN · Default · Edit · Del", size=13, color=INK))
    els.append(rect(cx, cy + 144, cw, 52, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 10, cy + 160, "USD · rate 70.5 · Edit · Del", size=13, color=INK))
    els.append(text(cx, cy + 220, "Same list pattern for:\nUnits · Pay methods · Terms\nLanguages · Preferences", size=12, color=MUTED, width=cw))

    # 6. Audit log
    x = 5 * (PHONE_W + GAP_X)
    g = nid()
    pe, cx, cy, cw = phone_shell(x, 0, "6. Audit log", g)
    els += pe
    els.append(text(cx, cy + 4, "← Audit log", size=16, color=INK))
    els += search_bar(cx, cy + 36, cw, "User / action", [g])
    els += filter_chips(cx, cy + 80, ["All", "Login", "Settings"], [g])
    for i, row in enumerate(["Ahmad · login · 09:12", "Ahmad · tenant edit", "Laila · role change"]):
        yy = cy + 120 + i * 56
        els.append(rect(cx, yy, cw, 48, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
        els.append(text(cx + 10, yy + 14, row, size=12, color=INK))

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
    """Public login only + in-app users / roles & permissions."""
    els = [text(0, -100, "BOMS Desktop — Auth & Authorization", size=28, color=INK)]
    els.append(
        text(
            0,
            -60,
            "Public: Login only. Users & Roles live behind auth (Owner/Admin). Tenant self-signup removed — Super Admin creates tenants in Settings.",
            size=14,
            color=MUTED,
            width=2400,
        )
    )
    card_w = 420

    # ── Row 1: public auth ──
    # 1. Login only
    ox, oy = grid_pos(0, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "1. Login (system entry)", "Home", g, show_sidebar=False)
    els += pe
    card_x = cx + (cw - card_w) / 2
    els.append(rect(card_x, cy + 40, card_w, 460, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=[g]))
    els.append(text(card_x + 40, cy + 80, "BOMS", size=32, color=ACCENT, width=card_w - 80, align="center"))
    els.append(text(card_x + 40, cy + 130, "Sign in to your tenant", size=14, color=MUTED, width=card_w - 80, align="center"))
    f, y = field(card_x + 40, cy + 180, card_w - 80, "Phone or Email", "0700… / name@mail.com", [g])
    els += f
    f, y = field(card_x + 40, y, card_w - 80, "Password", "••••••••", [g])
    els += f
    els.append(text(card_x + 40, y + 6, "Forgot password?", size=13, color=ACCENT))
    els += btn(card_x + 40, y + 44, card_w - 80, 48, "Sign in", True, [g])
    els.append(text(card_x + 40, y + 110, "Language: EN | دری | پښتو | عربی", size=12, color=MUTED, width=card_w - 80, align="center"))
    els += note(card_x + 24, cy + 460, card_w - 48, "Unauthenticated: only this page is visible", [g])

    # 2. Forgot password
    ox, oy = grid_pos(1, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "2. Forgot password", "Home", g, show_sidebar=False)
    els += pe
    card_x = cx + (cw - card_w) / 2
    els.append(rect(card_x, cy + 80, card_w, 360, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=[g]))
    els.append(text(card_x + 40, cy + 110, "Reset password", size=22, color=INK, width=card_w - 80, align="center"))
    f, y = field(card_x + 40, cy + 170, card_w - 80, "Phone or Email", "", [g])
    els += f
    els += btn(card_x + 40, y + 24, card_w - 80, 48, "Send reset code / link", True, [g])
    els.append(text(card_x + 40, y + 90, "← Back to login", size=13, color=ACCENT, width=card_w - 80, align="center"))

    # 3. Accept invite
    ox, oy = grid_pos(2, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "3. Accept invitation", "Home", g, show_sidebar=False)
    els += pe
    card_x = cx + (cw - card_w) / 2
    els.append(rect(card_x, cy + 60, card_w, 420, strokeColor=LINE, backgroundColor=BG, strokeWidth=2, groupIds=[g]))
    els.append(text(card_x + 40, cy + 90, "Join Al Dubai Bridal", size=20, color=INK, width=card_w - 80, align="center"))
    els.append(text(card_x + 40, cy + 130, "Invited as Cashier · Branch Main", size=13, color=MUTED, width=card_w - 80, align="center"))
    f, y = field(card_x + 40, cy + 180, card_w - 80, "Full name *", "", [g])
    els += f
    f, y = field(card_x + 40, y, card_w - 80, "Set password *", "", [g])
    els += f
    f, y = field(card_x + 40, y, card_w - 80, "Confirm password *", "", [g])
    els += f
    els += btn(card_x + 40, y + 24, card_w - 80, 48, "Accept & join", True, [g])

    # 4. Users list
    ox, oy = grid_pos(3, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "4. Users — list / search / filter", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Users", [("+ Create user", True), ("Send invitation", False)], [g])
    els += he
    els += search_bar(cx, y, cw * 0.42, "Search name / phone / email", [g])
    els += filter_chips(cx + cw * 0.44, y + 4, ["All", "Active", "Invited", "Inactive", "Role ▾", "Branch ▾"], [g])
    y += 52
    els += table_header(cx, y, cw, ["Name", "Contact", "Role", "Branch", "Status", "Actions"], [g])
    rows = [
        "Ahmad Karimi   0700…   Owner     Main   Active    Edit | Change role | Invite | Delete",
        "Laila Nazari   0780…   Cashier   Main   Active    Edit | Change role | Invite | Delete",
        "Omar Rahimi    o@…     Staff     Floor2 Invited   Edit | Change role | Resend | Delete",
        "Sara Admin     s@…     Manager   Main   Active    Edit | Change role | Invite | Delete",
    ]
    for i, r in enumerate(rows):
        els += table_row(cx, y + 40 + i * 48, cw, r, [g], 46)
    els += note(cx, y + 250, cw, "Row actions: Edit · Delete/Deactivate · Send invitation · Change role", [g])

    # ── Row 2: user form, invite/role, roles list, permissions ──
    # 5. Create / Edit user
    ox, oy = grid_pos(4, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "5. Create / Edit user", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Create user", [("Cancel", False), ("Save user", True)], [g])
    els += he
    f, y = field(cx, y, 420, "Full name *", "Laila Nazari", [g])
    els += f
    f, _ = field(cx + 450, cy + 52, 420, "Phone *", "0780…", [g])
    els += f
    f, y = field(cx, y, 420, "Email", "laila@…", [g])
    els += f
    f, _ = field(cx + 450, cy + 114, 420, "Role *", "Cashier ▾", [g])
    els += f
    f, y = field(cx, y, 420, "Default branch *", "Main ▾", [g])
    els += f
    f, _ = field(cx + 450, cy + 176, 420, "Status", "Active ▾", [g])
    els += f
    els.append(text(cx, y + 8, "[✓] Send invitation email/SMS after save", size=13, color=INK))
    els += btn(cx, y + 48, 160, 40, "Save user", True, [g])
    els += btn(cx + 170, y + 48, 160, 40, "Save & invite", False, [g])
    els += btn(cx + 340, y + 48, 180, 40, "Deactivate user", False, [g])

    # 6. Invite + Change role panels
    ox, oy = grid_pos(5, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "6. Invite user · Change role", "Settings", g)
    els += pe
    left_w = cw * 0.48 - 8
    els.append(rect(cx, cy, left_w, 520, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 20, cy + 20, "Send invitation", size=18, color=INK))
    f, y = field(cx + 20, cy + 60, left_w - 40, "Phone or Email *", "", [g])
    els += f
    f, y = field(cx + 20, y, left_w - 40, "Role *", "Cashier ▾", [g])
    els += f
    f, y = field(cx + 20, y, left_w - 40, "Branch *", "Main ▾", [g])
    els += f
    els.append(text(cx + 20, y + 8, "Expires in 7 days · link + OTP", size=12, color=MUTED))
    els += btn(cx + 20, y + 40, left_w - 40, 44, "Send invitation", True, [g])
    rx = cx + cw * 0.52
    els.append(rect(rx, cy, left_w, 520, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(rx + 20, cy + 20, "Change role", size=18, color=INK))
    els.append(text(rx + 20, cy + 60, "User: Laila Nazari\nCurrent role: Cashier", size=14, color=MUTED, width=left_w - 40))
    f, y = field(rx + 20, cy + 120, left_w - 40, "New role *", "Manager ▾", [g])
    els += f
    els.append(text(rx + 20, y + 8, "Permissions update immediately on save", size=12, color=MUTED, width=left_w - 40))
    els += btn(rx + 20, y + 40, left_w - 40, 44, "Update role", True, [g])

    # 7. Roles list
    ox, oy = grid_pos(6, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "7. Roles — list / search / filter", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Roles & permissions", [("+ Create role", True)], [g])
    els += he
    els += search_bar(cx, y, cw * 0.4, "Search role name", [g])
    els += filter_chips(cx + cw * 0.42, y + 4, ["All", "System", "Custom", "Active"], [g])
    y += 52
    els += table_header(cx, y, cw, ["Role", "Type", "Users", "Permissions", "Status", "Actions"], [g])
    for i, r in enumerate([
        "Owner     System   1   All modules     Active   View (locked)",
        "Manager   Custom   1   24 permissions  Active   Edit | Delete",
        "Cashier   Custom   2   12 permissions  Active   Edit | Delete",
        "Staff     Custom   3    8 permissions  Active   Edit | Delete",
    ]):
        els += table_row(cx, y + 40 + i * 48, cw, r, [g], 46)
    els += note(cx, y + 250, cw, "System roles (Owner) cannot be deleted. Custom roles support full CRUD.", [g])

    # 8. Role edit + permission matrix
    ox, oy = grid_pos(7, 4, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "8. Role edit · permission matrix", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Edit role: Cashier", [("Cancel", False), ("Save role", True)], [g])
    els += he
    f, y = field(cx, y, 360, "Role name *", "Cashier", [g])
    els += f
    f, _ = field(cx + 380, cy + 52, 360, "Description", "POS & rental desk", [g])
    els += f
    els.append(text(cx, y + 8, "Permissions by module", size=14, color=MUTED))
    y += 36
    els += table_header(cx, y, cw, ["Module", "View", "Create", "Edit", "Void / Delete"], [g])
    matrix = [
        "Inventory      [✓]   [ ]   [ ]   [ ]",
        "Sales          [✓]   [✓]   [✓]   [ ]",
        "Procurement    [ ]   [ ]   [ ]   [ ]",
        "Finance        [✓]   [ ]   [ ]   [ ]",
        "Settings       [ ]   [ ]   [ ]   [ ]",
        "Users / Roles  [ ]   [ ]   [ ]   [ ]",
    ]
    for i, r in enumerate(matrix):
        els += table_row(cx, y + 40 + i * 44, cw, r, [g], 42)

    # flow arrows row1
    for i in range(3):
        x1 = i * (DESK_W + GAP_X) + DESK_W + 8
        x2 = (i + 1) * (DESK_W + GAP_X) - 8
        els += arrow(x1, TITLE_H + DESK_H / 2, x2, TITLE_H + DESK_H / 2)
    # flow arrows row2
    row2_y = DESK_H + ROW_GAP + TITLE_H + DESK_H / 2
    for i in range(3):
        x1 = i * (DESK_W + GAP_X) + DESK_W + 8
        x2 = (i + 1) * (DESK_W + GAP_X) - 8
        els += arrow(x1, row2_y, x2, row2_y)
    return doc(els)


def d_platform():
    """Tenant + branches/warehouses + master data CRUD."""
    els = [text(0, -100, "BOMS Desktop — Platform / Settings", size=28, color=INK)]
    els.append(
        text(
            0,
            -60,
            "Super Admin: Tenants CRUD. Tenant admins: Tenant profile, Branches (1→N Warehouses), Currencies, Units, Payment methods/terms, Preferences, Languages, Audit log.",
            size=14,
            color=MUTED,
            width=2600,
        )
    )

    # 1. Settings hub
    ox, oy = grid_pos(0, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "1. Settings hub", "Settings", g)
    els += pe
    cards = [
        "Tenants (Super Admin)",
        "Tenant profile",
        "Branches & warehouses",
        "Currencies",
        "Units",
        "Payment methods",
        "Payment terms",
        "Preferences",
        "Languages",
        "Audit log",
        "Users → Auth",
        "Roles → Auth",
    ]
    for i, cname in enumerate(cards):
        xx = cx + (i % 3) * ((cw - 24) / 3 + 12)
        yy = cy + (i // 3) * 90
        els.append(rect(xx, yy, (cw - 24) / 3, 76, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
        els.append(text(xx + 14, yy + 28, cname + "  ›", size=14, color=INK, width=(cw - 24) / 3 - 28))

    # 2. Tenants list
    ox, oy = grid_pos(1, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "2. Tenants — Super Admin CRUD", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Tenants", [("+ Create tenant", True)], [g])
    els += he
    els += note(cx, y - 4, cw, "Visible only with Super Admin permission", [g])
    y += 44
    els += search_bar(cx, y, cw * 0.38, "Search name / code", [g])
    els += filter_chips(cx + cw * 0.4, y + 4, ["All types", "Shop", "Mall", "Other", "Active", "Inactive"], [g])
    y += 52
    els += table_header(cx, y, cw, ["Code", "Name", "Type", "Contact", "Branches", "Status", "Actions"], [g])
    for i, r in enumerate([
        "ADF   Al Dubai Bridal    Shop   0700…   2   Active    Edit | Profile | Delete",
        "KBM   Kabul City Mall    Mall   0780…   5   Active    Edit | Profile | Delete",
        "GWN   Green Wedding Co   Shop   g@…     1   Inactive  Edit | Profile | Delete",
    ]):
        els += table_row(cx, y + 40 + i * 48, cw, r, [g], 46)

    # 3. Create / Edit tenant
    ox, oy = grid_pos(2, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "3. Create / Edit tenant", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Create tenant", [("Cancel", False), ("Save tenant", True)], [g])
    els += he
    f, y = field(cx, y, 420, "Tenant name *", "Al Dubai Bridal", [g])
    els += f
    f, _ = field(cx + 450, cy + 52, 420, "Code * (SKU prefix)", "ADF", [g])
    els += f
    f, y = field(cx, y, 420, "Tenant type * (enum)", "Shop ▾   [ + Manage types ]", [g])
    els += f
    f, _ = field(cx + 450, cy + 114, 420, "Business mode", "Both ▾  Sale | Rental | Both", [g])
    els += f
    els.append(text(cx, y + 4, "Contact", size=14, color=MUTED))
    f, y = field(cx, y + 28, 420, "Phone *", "0700…", [g])
    els += f
    f, _ = field(cx + 450, cy + 210, 420, "Email / Website", "info@… / aldubai.af", [g])
    els += f
    els.append(text(cx, y + 4, "Address", size=14, color=MUTED))
    f, y = field(cx, y + 28, 420, "Country / City", "Afghanistan / Kabul", [g])
    els += f
    f, _ = field(cx + 450, cy + 300, 420, "Street / Building", "Shar-e-Naw · Block 4", [g])
    els += f
    f, y = field(cx, y, 420, "Default currency / Language / TZ", "AFN · EN · Asia/Kabul", [g])
    els += f
    els.append(text(cx, y + 8, "Type enum examples: Shop · Mall · Boutique · Other (extensible)", size=12, color=MUTED, width=cw))

    # 4. Tenant profile
    ox, oy = grid_pos(3, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "4. Tenant profile (not shop profile)", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Tenant profile", [("Save changes", True)], [g])
    els += he
    els.append(rect(cx, y, 120, 120, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 32, y + 50, "Logo", size=13, color=MUTED))
    f, yy = field(cx + 150, y, 400, "Tenant name", "Al Dubai Bridal", [g])
    els += f
    f, yy = field(cx + 150, yy, 400, "Code / Type", "ADF · Shop", [g])
    els += f
    f, yy = field(cx + 150, yy, 400, "Contact phone / email / website", "0700… · info@…", [g])
    els += f
    f, yy = field(cx, yy + 20, cw * 0.48 - 8, "Address line", "Shar-e-Naw, Block 4", [g])
    els += f
    f, _ = field(cx + cw * 0.52, yy + 20, cw * 0.48 - 8, "City / Country / Postal", "Kabul · AF · —", [g])
    els += f
    els += note(cx, yy + 100, cw, "Renamed from Shop profile → Tenant profile (works for Shop, Mall, …)", [g])

    # 5. Branches list
    ox, oy = grid_pos(4, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "5. Branches — CRUD / search / filter", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Branches", [("+ Add branch", True)], [g])
    els += he
    els += search_bar(cx, y, cw * 0.4, "Search code / name / city", [g])
    els += filter_chips(cx + cw * 0.42, y + 4, ["All", "Active", "Main only", "Inactive"], [g])
    y += 52
    els += table_header(cx, y, cw, ["Code", "Name", "City", "Warehouses", "Main?", "Status", "Actions"], [g])
    for i, r in enumerate([
        "MAIN   Main Branch     Kabul   3 WH   Yes   Active   Open | Edit | Delete",
        "FL2    Second Floor    Kabul   1 WH   No    Active   Open | Edit | Delete",
        "HRT    Herat Outlet    Herat   2 WH   No    Active   Open | Edit | Delete",
    ]):
        els += table_row(cx, y + 40 + i * 48, cw, r, [g], 46)
    els += note(cx, y + 200, cw, "Open branch → manage its warehouses (1 branch : many warehouses)", [g])

    # ── Row 2 ──
    # 6. Branch detail + warehouses
    ox, oy = grid_pos(5, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "6. Branch detail · warehouses 1→N", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Branch: Main · MAIN", [("Edit branch", False), ("+ Add warehouse", True)], [g])
    els += he
    els.append(text(cx, y, "Address: Shar-e-Naw · Manager: Ahmad · Status: Active", size=13, color=MUTED, width=cw))
    y += 36
    els.append(text(cx, y, "Warehouses under this branch", size=15, color=INK))
    y += 28
    els += search_bar(cx, y, cw * 0.4, "Search warehouse", [g])
    els += filter_chips(cx + cw * 0.42, y + 4, ["All", "Default", "Active"], [g])
    y += 52
    els += table_header(cx, y, cw, ["Code", "Name", "Location", "Default?", "Status", "Actions"], [g])
    for i, r in enumerate([
        "WH-A   Showroom      Floor 1     Yes   Active   Edit | Delete",
        "WH-B   Back storage  Basement    No    Active   Edit | Delete",
        "WH-C   Repair desk   Tailor area No    Active   Edit | Delete",
    ]):
        els += table_row(cx, y + 40 + i * 48, cw, r, [g], 46)

    # 7. Currencies + Units
    ox, oy = grid_pos(6, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "7. Currencies · Units", "Settings", g)
    els += pe
    left = cw * 0.48 - 8
    els.append(text(cx, cy, "Currencies                         [ + Add ]", size=16, color=INK, width=left))
    els += search_bar(cx, cy + 36, left, "Code / name", [g])
    els += table_header(cx, cy + 84, left, ["Code", "Name", "Rate", "Default", "Actions"], [g])
    els += table_row(cx, cy + 124, left, "AFN  Afghani   1      Yes   Edit|Del", [g])
    els += table_row(cx, cy + 168, left, "USD  US Dollar 70.5   No    Edit|Del", [g])
    rx = cx + cw * 0.52
    els.append(text(rx, cy, "Units                              [ + Add ]", size=16, color=INK, width=left))
    els += search_bar(rx, cy + 36, left, "Name / code", [g])
    els += table_header(rx, cy + 84, left, ["Code", "Name", "Status", "Actions"], [g])
    els += table_row(rx, cy + 124, left, "pcs  Piece   Active  Edit|Del", [g])
    els += table_row(rx, cy + 168, left, "set  Set     Active  Edit|Del", [g])
    els += table_row(rx, cy + 212, left, "box  Box     Active  Edit|Del", [g])
    els += note(cx, cy + 280, cw, "Each master list: Create · Read · Update · Delete + search/filter", [g])

    # 8. Payment methods + terms
    ox, oy = grid_pos(7, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "8. Payment methods · terms", "Settings", g)
    els += pe
    left = cw * 0.48 - 8
    els.append(text(cx, cy, "Payment methods                    [ + Add ]", size=16, color=INK, width=left))
    els += search_bar(cx, cy + 36, left, "Name", [g])
    els += filter_chips(cx, cy + 80, ["All", "Active"], [g])
    els += table_header(cx, cy + 120, left, ["Name", "Status", "Actions"], [g])
    for i, r in enumerate(["Cash     Active  Edit|Del", "Card     Active  Edit|Del", "Transfer Active  Edit|Del"]):
        els += table_row(cx, cy + 160 + i * 44, left, r, [g], 42)
    rx = cx + cw * 0.52
    els.append(text(rx, cy, "Payment terms                      [ + Add ]", size=16, color=INK, width=left))
    els += search_bar(rx, cy + 36, left, "Name", [g])
    els += table_header(rx, cy + 120, left, ["Name", "Rule", "Actions"], [g])
    for i, r in enumerate(["Immediate   due 0d     Edit|Del", "Deposit 50% 50% up front Edit|Del", "Net 7       due +7d    Edit|Del"]):
        els += table_row(rx, cy + 160 + i * 44, left, r, [g], 42)

    # 9. Preferences + Languages
    ox, oy = grid_pos(8, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "9. Preferences · Languages", "Settings", g)
    els += pe
    left = cw * 0.48 - 8
    els.append(rect(cx, cy, left, 520, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=[g]))
    els.append(text(cx + 20, cy + 20, "Preferences", size=18, color=INK))
    f, y = field(cx + 20, cy + 60, left - 40, "Default rental days", "3", [g])
    els += f
    f, y = field(cx + 20, y, left - 40, "Low-stock alert qty", "1", [g])
    els += f
    f, y = field(cx + 20, y, left - 40, "Nav style / RTL", "Sidebar ▾ · Auto RTL", [g])
    els += f
    f, y = field(cx + 20, y, left - 40, "Timezone", "Asia/Kabul ▾", [g])
    els += f
    els += btn(cx + 20, y + 20, 160, 40, "Save preferences", True, [g])
    rx = cx + cw * 0.52
    els.append(rect(rx, cy, left, 520, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=[g]))
    els.append(text(rx + 20, cy + 20, "Languages                    [ + Add ]", size=16, color=INK, width=left - 40))
    els += search_bar(rx + 20, cy + 60, left - 40, "Language / code", [g])
    els += table_header(rx + 20, cy + 110, left - 40, ["Code", "Name", "Default", "Actions"], [g])
    for i, r in enumerate(["en  English  Yes  Edit", "fa  Dari     No   Edit", "ps  Pashto   No   Edit", "ar  Arabic   No   Edit"]):
        els += table_row(rx + 20, cy + 150 + i * 44, left - 40, r, [g], 42)

    # 10. Audit log
    ox, oy = grid_pos(9, 5, DESK_W, DESK_H)
    g = nid()
    pe, cx, cy, cw, ch = desk_shell(ox, oy, "10. Audit log", "Settings", g)
    els += pe
    he, y = page_header(cx, cy, cw, "Audit log", [("Export", False)], [g])
    els += he
    els += search_bar(cx, y, cw * 0.36, "User / action / entity", [g])
    els += filter_chips(cx + cw * 0.38, y + 4, ["All", "Login", "Tenant", "Users", "Settings", "Date ▾"], [g])
    y += 52
    els += table_header(cx, y, cw, ["Time", "User", "Action", "Entity", "Detail", "IP"], [g])
    for i, r in enumerate([
        "11 Sep 09:12  Ahmad   LOGIN          session   success           1.2.3.4",
        "11 Sep 09:40  Ahmad   TENANT_UPDATE   tenant    type Shop→Mall     1.2.3.4",
        "11 Sep 10:05  Ahmad   USER_INVITE     user      Laila / Cashier    1.2.3.4",
        "11 Sep 10:22  Ahmad   ROLE_UPDATE      role      Cashier perms      1.2.3.4",
        "11 Sep 11:01  Sara    BRANCH_CREATE   branch    Herat Outlet       5.6.7.8",
    ]):
        els += table_row(cx, y + 40 + i * 48, cw, r, [g], 46)

    # arrows
    for row in range(2):
        base_y = row * (DESK_H + ROW_GAP) + TITLE_H + DESK_H / 2
        for i in range(4):
            x1 = i * (DESK_W + GAP_X) + DESK_W + 8
            x2 = (i + 1) * (DESK_W + GAP_X) - 8
            els += arrow(x1, base_y, x2, base_y)
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
