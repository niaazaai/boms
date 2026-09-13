#!/usr/bin/env python3
"""BOMS — Platform module wireframes (auth, RBAC, tenant, settings).

Product rules drawn here:
  • Login-only public entry — no sign-up, NO INVITE FLOW anywhere
  • No language switcher on login; locale comes from tenants.default_language_id
  • English → LTR · Dari / Pashto → full RTL (drawer flips side)
  • Users are tenant-bound: Tenant * required, roles are multi-select
  • Login identifier is GLOBALLY unique email or phone (corrected flaw A8)
  • System roles are COPIED to the tenant, never shared/edited globally (A7)
  • Permission actions: view · create · edit · post · void · export · approve
  • Audit log records post and void, not just logins
"""

from __future__ import annotations

from dsl import *  # noqa: F401,F403

DESK_COLS = 4
PHONE_COLS = 5


def _sel(x, y, w, label, value="", g=None, required=False, h=36):
    g = g or []
    els, ny = field(x, y, w, label, value, g, required, None, h)
    els.append(text(x + w - 22, y + 18 + (h - 16) / 2, ICON["down"], 12, MUTED, g=g))
    return els, ny


def _inp(x, y, w, label, value="", g=None, required=False, h=36):
    return field(x, y, w, label, value, g, required, None, h)


def _lab(x, y, s, g, color=MUTED, size=11.5):
    return [text(x, y, s, size, color, g=g)]


def _check(x, y, label, on, g, color=ACCENT):
    els = [rect(x, y, 16, 16, strokeColor=color if on else LINE,
                backgroundColor=color if on else BG, strokeWidth=1, groupIds=g)]
    if on:
        els.append(text(x, y + 1, ICON["check"], 11, "#ffffff", "center", 16, g))
    els.append(text(x + 24, y + 1, label, 12, INK if on else MUTED, g=g))
    return els


def _tile(x, y, w, h, icon, title, sub, g, color=ACCENT):
    return [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
            rect(x + 16, y + 16, 36, 36, strokeColor=color, backgroundColor=
                 {ACCENT: ACCENT_BG, VIOLET: VIOLET_BG, INFO: INFO_BG, WARN: WARN_BG,
                  OK: OK_BG, ROSE: ROSE_BG}.get(color, SOFT), strokeWidth=1, groupIds=g),
            text(x + 16, y + 26, icon, 15, color, "center", 36, g),
            text(x + 64, y + 20, title, 13.5, INK, width=w - 80, g=g),
            text(x + 64, y + 40, sub, 10.5, MUTED, width=w - 80, g=g)]


# ══════════════════════════════════════════════════════════════════
#  DESKTOP
# ══════════════════════════════════════════════════════════════════

def _d1(ox, oy):
    """Login."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "1. Login — the only public page",
                                     "Login", g, show_sidebar=False)
    PW = 420
    px = cx + (cw - PW) / 2
    py = cy + 60
    els.append(rect(px, py, PW, 470, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
    els.append(rect(px + PW / 2 - 26, py + 36, 52, 52, strokeColor=ACCENT,
                    backgroundColor=ACCENT, strokeWidth=1, groupIds=G))
    els.append(text(px + PW / 2 - 26, py + 50, ICON["dress"], 22, "#ffffff", "center", 52, G))
    els.append(text(px, py + 104, "BOMS", 28, INK, "center", PW, G))
    els.append(text(px, py + 140, "Bridal Omnichannel Management", 12, MUTED, "center", PW, G))
    y = py + 180
    e, y = _inp(px + 40, y, PW - 80, "Email or phone", "ahmad@aldubaibridal.af", G, True, 42)
    els += e
    e, y = _inp(px + 40, y, PW - 80, "Password", "••••••••••", G, True, 42)
    els += e
    els.append(text(px + 40, y - 4, "Forgot password?", 12, ACCENT, g=G))
    els += btn(px + 40, y + 26, PW - 80, 48, "Sign in", "primary", G)
    els.append(text(px + 40, y + 92, "Your shop's language and layout direction are set by\n"
                                     "the tenant. There is no language switcher here.",
                    10.5, FAINT, "center", PW - 80, G))
    els += note(cx, cy + 570, cw,
                "PUBLIC SURFACE = this page + forgot password. Nothing else. No shop self-registration, no invite-accept route, no invite token — the invite flow is removed entirely.\n"
                "Reads users by GLOBALLY unique email or phone. This is the corrected flaw A8: v1 made email unique only per tenant, but login has no tenant context yet,\n"
                "so two users in different tenants with the same email made authentication non-deterministic. After sign-in the shell reads tenants.default_language_id and\n"
                "mounts the whole UI LTR (en) or RTL (fa / ps).",
                ACCENT, G)
    return els


def _d2(ox, oy):
    """Forgot password + reset."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "2. Forgot password → OTP → reset",
                                     "Login", g, show_sidebar=False)
    PW = 380
    for i, (title, fields, cta) in enumerate([
            ("Reset your password", [("Email or phone", "0700 12 34 56", True)], "Send reset code"),
            ("Enter the 6-digit code", [("Code", "• • • • • •", True)], "Verify code"),
            ("Choose a new password", [("New password", "••••••••••", True),
                                       ("Confirm password", "••••••••••", True)], "Save & sign in")]):
        px = cx + 40 + i * (PW + 30)
        els.append(rect(px, cy + 80, PW, 360, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(px + 32, cy + 112, f"Step {i + 1}", 10.5, ACCENT, width=PW - 64, g=G))
        els.append(text(px + 32, cy + 132, title, 18, INK, width=PW - 64, g=G))
        y = cy + 180
        for lab, val, req in fields:
            e, y = _inp(px + 32, y, PW - 64, lab, val, G, req, 40)
            els += e
        els += btn(px + 32, y + 10, PW - 64, 44, cta, "primary", G)
        els.append(text(px + 32, y + 70, "← Back to sign in", 11.5, MUTED, width=PW - 64, g=G))
        if i < 2:
            els += arrow(px + PW + 6, cy + 260, px + PW + 24, cy + 260)
    els += note(cx, cy + 480, cw,
                "OTP is sent to the phone or email on the user record. The code is single-use and time-limited; no session is created until step 3 succeeds.\n"
                "Every step writes an audit_logs row. There is no account-creation path here — a user who does not already exist inside a tenant cannot reach the app at all.",
                ACCENT, G)
    return els


def _d3(ox, oy):
    """Home dashboard."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "3. Home — the app landing page", "Home", g)
    e, y = page_header(cx, cy, cw, "Good morning, Ahmad",
                       actions=[("＋ New rental", "secondary"), ("＋ New sale", "primary")],
                       subtitle="Al Dubai Bridal · Main branch · Saturday 12 September 2026",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Net profit today", "AFN 61,180", ACCENT, "+18% vs yesterday", ICON["chart"]),
        ("Your cash", "AFN 344,000", OK, "412,000 − 68,000 deposits", ICON["cash"]),
        ("Owed to us (A/R)", "AFN 86,400", INFO, "11 customers", ICON["customers"]),
        ("We owe (A/P)", "AFN 252,388", WARN, "4 suppliers", ICON["suppliers"]),
        ("Due returns today", "3", DANGER, "1 already overdue", ICON["clock"]),
        ("Low stock", "11", WARN, "below reorder level", ICON["alert"]),
    ], h=92, gap=12, g=G)
    els += e
    LW = cw * 0.56
    els += _lab(cx, y, "TODAY'S SCHEDULE", G)
    e, _ = table(cx, y + 22, LW, ["Time", "What", "Customer", "Dress", "Status"],
                 [["10:00", ("Pickup", VIOLET), "Sara Ahmadi", "White A-Line Gown", ("ready", OK)],
                  ["12:30", ("Return", INFO), "Fatima Rahimi", "Gold Ball Gown", ("due", WARN)],
                  ["15:00", ("Fitting", ACCENT), "Maryam Noori", "Ivory Mermaid Gown", ("booked", OK)],
                  ["17:00", ("Return", INFO), "Nasrin Hakimi", "Champagne Ball Gown", ("overdue 2 d", DANGER)]],
                 G, row_h=44, widths=[0.5, 0.7, 1.2, 1.5, 0.85])
    els += e
    rx = cx + LW + 24
    RW = cw - LW - 24
    els += _lab(rx, y, "QUICK ACTIONS", G)
    acts = [(ICON["sales"], "New sale"), (ICON["rental"], "New rental"),
            (ICON["money_out"], "Add expense"), (ICON["truck"], "Receive PO"),
            (ICON["customers"], "Add customer"), (ICON["inventory"], "Add item")]
    tw = (RW - 2 * 12) / 3
    for i, (ic, lb) in enumerate(acts):
        bx = rx + (i % 3) * (tw + 12)
        by = y + 22 + (i // 3) * 82
        els.append(rect(bx, by, tw, 72, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(bx, by + 14, ic, 17, ACCENT, "center", tw, G))
        els.append(text(bx, by + 46, lb, 11, INK, "center", tw, G))
    els += _lab(rx, y + 204, "RECENT ACTIVITY", G)
    els.append(text(rx, y + 226,
                    "Zahra posted GRN26-0009 · 12 items in       09:14\n"
                    "Ahmad voided FIN26-000437 · wrong order     08:52\n"
                    "Nasrin created SO26-000022 · walk-in veil   08:31\n"
                    "System: Cash Drawer reconcile mismatch      07:00",
                    11, MUTED, width=RW, g=G))
    els += note(cx, y + 244, LW,
                "Home mirrors the Finance pillars so the owner sees the day's answer without opening a module. Reads finance_daily_summaries (or live when stale),\n"
                "sales_orders by rental_end_date for the schedule, and inventory_stock_balances for low stock. Every tile deep-links into its module.",
                ACCENT, G)
    return els


def _d4(ox, oy):
    """Users list."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "4. Users — tenant-bound, multi-role",
                                     "Settings", g, sub_active="Users & roles")
    e, y = page_header(cx, cy, cw, "Users",
                       actions=[("⬇ Export", "ghost"), ("＋ New user", "primary")],
                       subtitle="Created directly inside a tenant — there is no invitation flow",
                       g=G)
    els += e
    els += search_bar(cx, y, 320, "Name, email or phone", G)
    e, _ = _sel(cx + 336, y - 18, 180, "", "All tenants", G)
    els += e
    e, _ = _sel(cx + 532, y - 18, 160, "", "All roles", G)
    els += e
    e, _ = _sel(cx + 708, y - 18, 160, "", "All branches", G)
    els += e
    els += filter_chips(cx + 884, y + 5, ["Active", "Inactive"], 0, G)
    y += 56
    e, y2 = table(cx, y, cw,
                  ["Name", "Email", "Phone", "Tenant", "Roles", "Branch", "Last login", "Status", ""],
                  [["Ahmad Zaki", "ahmad@aldubaibridal.af", "0700 12 34 56", "Al Dubai Bridal", ("Owner", ACCENT), "Main", "12 Sep 08:02", ("active", OK), "Edit"],
                   ["Nasrin Hakimi", "nasrin@aldubaibridal.af", "0700 44 21 90", "Al Dubai Bridal", ("Manager · Cashier", ACCENT), "Main", "12 Sep 07:48", ("active", OK), "Edit"],
                   ["Zahra Ali", "zahra@aldubaibridal.af", "0700 90 11 23", "Al Dubai Bridal", ("Cashier", ACCENT), "Shar-e-Naw", "11 Sep 18:20", ("active", OK), "Edit"],
                   ["Farid Omar", "farid@aldubaibridal.af", "0700 55 78 34", "Al Dubai Bridal", ("Stock keeper", ACCENT), "Main", "10 Sep 09:15", ("active", OK), "Edit"],
                   ["Laila Sadat", "laila@roshanbridal.af", "0700 61 22 07", "Roshan Bridal", ("Owner", ACCENT), "Main", "09 Sep 11:40", ("inactive", MUTED), "Edit"]],
                  G, row_h=46, widths=[1.15, 1.75, 1.1, 1.25, 1.4, 0.8, 1.0, 0.7, 0.45])
    els += e
    e, y2 = pagination(cx, y2, cw, "1–5 of 12 users", G)
    els += e
    els += note(cx, y2 + 4, cw,
                "The Tenant column and filter are visible to Super Admin only; a tenant Owner sees their own tenant's users and the column is hidden.\n"
                "Roles render as chips because user_roles is many-to-many — Nasrin holds Manager AND Cashier, and her effective permissions are the UNION of both.\n"
                "There is no 'Invite' button, no 'Resend invitation', and no 'invited' status anywhere in this screen. Deactivate is preferred over delete (created_by FKs must survive).",
                ACCENT, G)
    return els


def _d5(ox, oy):
    """Create user drawer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "5. Create user — drawer (LTR → right)",
                                     "Settings", g, sub_active="Users & roles")
    e, y = page_header(cx, cy, cw, "Users", subtitle="Creating a new user", g=G)
    els += e
    e, _ = table(cx, y, cw * 0.5, ["Name", "Roles", "Status"],
                 [["Ahmad Zaki", "Owner", "active"], ["Nasrin Hakimi", "Manager · Cashier", "active"]],
                 G, row_h=42, widths=[1.2, 1.4, 0.7])
    els += e
    de, fx, fy, fw = drawer(cx, cy - 20, cw, ch, "New user", "right", 470,
                            "Opens from the right in LTR · from the left in RTL", G)
    els += de
    yy = fy
    e, yy = _sel(fx, yy, fw, "Tenant", "Al Dubai Bridal (ADF)", G, True)
    els += e
    els.append(text(fx, yy - 8, "Super Admin picks any tenant · an Owner sees their own, locked", 10, FAINT, width=fw, g=G))
    yy += 10
    e, yy = _inp(fx, yy, fw, "Full name", "Zahra Ali", G, True)
    els += e
    e, yy = _inp(fx, yy, fw * 0.55 - 6, "Email", "zahra@aldubaibridal.af", G, True)
    els += e
    e, _ = _inp(fx + fw * 0.55 + 6, yy - 64, fw * 0.45 - 6, "Phone", "0700 90 11 23", G)
    els += e
    e, yy = _inp(fx, yy, fw, "Password", "••••••••••", G, True)
    els += e
    e, yy = _sel(fx, yy, fw, "Default branch", "Shar-e-Naw", G)
    els += e
    els += _lab(fx, yy, "ROLES — SELECT ONE OR MORE *", G, ACCENT)
    ch_, xx = chip(fx, yy + 20, "Cashier  ✕", ACCENT, g=G); els += ch_
    ch_, _ = chip(xx, yy + 20, "Stock keeper  ✕", ACCENT, g=G); els += ch_
    yy += 54
    els.append(rect(fx, yy, fw, 146, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
    for i, (rn, on) in enumerate([("Owner", False), ("Manager", False), ("Cashier", True),
                                  ("Stock keeper", True), ("Accountant", False)]):
        els += _check(fx + 16, yy + 16 + i * 25, rn, on, G)
    yy += 162
    e, yy = _sel(fx, yy, fw, "Status", "Active", G, True)
    els += e
    els += btn(fx, yy + 6, fw * 0.48, 44, "Cancel", "secondary", G)
    els += btn(fx + fw * 0.52, yy + 6, fw * 0.48, 44, "Create user", "primary", G)
    els += note(fx, yy + 62, fw,
                "Writes users + one user_roles row per selected role.\n"
                "The account is ACTIVE immediately — no invitation is sent\n"
                "and no token is generated. unique (user_id, role_id,\n"
                "coalesce(branch_id,0)) prevents duplicate grants (flaw A6).", ACCENT, G)
    return els


def _d6(ox, oy):
    """Roles list."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "6. Roles — copied from system templates",
                                     "Settings", g, sub_active="Users & roles")
    e, y = page_header(cx, cy, cw, "Roles & permissions",
                       actions=[("＋ New role", "primary")],
                       subtitle="Each tenant owns its own copy of every role",
                       g=G)
    els += e
    els += filter_chips(cx, y, ["All", "From template", "Custom"], 0, G)
    y += 50
    e, y2 = table(cx, y, cw,
                  ["Role", "Code", "Origin", "Users", "Permissions", "Status", ""],
                  [["Owner", "owner", ("copied from template", INFO), "1", "48 of 48", ("active", OK), "Edit"],
                   ["Manager", "manager", ("copied from template", INFO), "1", "36 of 48", ("active", OK), "Edit"],
                   ["Cashier", "cashier", ("copied from template", INFO), "2", "14 of 48", ("active", OK), "Edit"],
                   ["Stock keeper", "stock_keeper", ("copied from template", INFO), "1", "17 of 48", ("active", OK), "Edit"],
                   ["Accountant", "accountant", ("custom", VIOLET), "0", "21 of 48", ("active", OK), "Edit"],
                   ["Weekend helper", "weekend_helper", ("custom", VIOLET), "0", "6 of 48", ("inactive", MUTED), "Edit"]],
                  G, row_h=46, widths=[1.3, 1.1, 1.5, 0.6, 0.95, 0.75, 0.45])
    els += e
    els += note(cx, y2 + 8, cw,
                "CORRECTED FLAW A7. In v1 a role with tenant_id NULL was a shared 'system template' and role_permissions hung off it — so one tenant editing the Manager\n"
                "permission matrix silently changed Manager for EVERY tenant in the database. Templates are now read-only outside seeding: when a tenant is created, each\n"
                "template is COPIED into a tenant-owned roles row (copied_from_role_id records the origin). A tenant can then edit its copy freely and in isolation.",
                ACCENT, G)
    return els


def _d7(ox, oy):
    """Permission matrix."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "7. Permission matrix — module × action",
                                     "Settings", g, sub_active="Users & roles")
    e, y = page_header(cx, cy, cw, "Manager  ·  permissions",
                       actions=[("Cancel", "ghost"), ("Save role", "primary")],
                       subtitle="36 of 48 permissions granted · copied from system template",
                       g=G)
    els += e
    ACTIONS = ["view", "create", "edit", "post", "void", "export", "approve"]
    MODULES = [
        ("Platform", [1, 1, 1, 0, 0, 1, 0]),
        ("Inventory", [1, 1, 1, 1, 1, 1, 0]),
        ("Sales", [1, 1, 1, 1, 1, 1, 0]),
        ("Procurement", [1, 1, 1, 1, 0, 1, 1]),
        ("Finance", [1, 1, 1, 1, 0, 1, 0]),
        ("Reports", [1, 0, 0, 0, 0, 1, 0]),
    ]
    colw = (cw - 200) / len(ACTIONS)
    els.append(rect(cx, y, cw, 44, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=G))
    els.append(text(cx + 16, y + 15, "MODULE", 11, MUTED, width=170, g=G))
    for i, a in enumerate(ACTIONS):
        els.append(text(cx + 200 + i * colw, y + 8, a, 11, MUTED, "center", colw, G))
        els.append(text(cx + 200 + i * colw, y + 24, "all", 9.5, ACCENT, "center", colw, G))
    yy = y + 44
    for mi, (mod, grants) in enumerate(MODULES):
        if mi % 2:
            els.append(rect(cx, yy, cw, 48, strokeColor="transparent", backgroundColor=SOFT2,
                            strokeWidth=0, groupIds=G))
        els.append(line(cx, yy + 48, cw, HAIRLINE, G))
        els.append(text(cx + 16, yy + 12, mod, 13, INK, width=150, g=G))
        els.append(text(cx + 16, yy + 30, f"{sum(grants)} of {len(ACTIONS)}  ·  select all", 9.5, ACCENT, width=170, g=G))
        for i, on in enumerate(grants):
            els += _check(cx + 200 + i * colw + colw / 2 - 8, yy + 16, "", bool(on), G)
        yy += 48
    els += note(cx, yy + 16, cw * 0.6,
                "Seven actions, deliberately including POST and VOID — the two that move stock and money.\n"
                "v1 listed only view/create/edit/void/export/approve, so 'who may post a receipt or void a\n"
                "payment' had no permission to attach to. Effective permissions for a user are the UNION\n"
                "across all their roles. Select-all is available per row and per column.",
                ACCENT, G)
    els += note(cx + cw * 0.62, yy + 16, cw * 0.38,
                "48 permissions = 6 modules × up to 7 actions, seeded in\n"
                "the permissions table with codes like inventory.items.create\n"
                "and finance.transactions.void. The full seed list lives in\n"
                "specs/features/01-platform.md.", VIOLET, G)
    return els


def _d8(ox, oy):
    """Settings hub."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "8. Settings hub", "Settings", g, sub_active="Tenant")
    e, y = page_header(cx, cy, cw, "Settings",
                       subtitle="Al Dubai Bridal · ADF · Kabul", g=G)
    els += e
    groups = [
        ("ORGANISATION", [(ICON["branch"], "Tenant profile", "Name, logo, city, currency, language, timezone", ACCENT),
                          (ICON["warehouse"], "Branches & warehouses", "2 branches · 4 warehouses", ACCENT),
                          (ICON["settings"], "Preferences", "Rental defaults, stock policy, day cutoff", ACCENT)]),
        ("ACCESS", [(ICON["user"], "Users", "5 active users", INFO),
                    (ICON["lock"], "Roles & permissions", "6 roles · 48 permissions", INFO),
                    (ICON["ledger"], "Audit log", "Posts, voids, logins, settings changes", INFO)]),
        ("MASTER DATA", [(ICON["cash"], "Currencies & rates", "AFN default · USD, EUR", VIOLET),
                         (ICON["tag"], "Units", "pcs, set, box", VIOLET),
                         (ICON["receipt"], "Payment methods & terms", "Cash, card, transfer, wallet", VIOLET)]),
        ("SYSTEM", [(ICON["globe"], "Languages", "English (LTR) · Dari (RTL) · Pashto (RTL)", WARN),
                    (ICON["bell"], "Notifications", "Low stock, due returns, overdue A/R", WARN),
                    (ICON["export"], "Data export", "CSV exports and backups", WARN)]),
    ]
    colw = (cw - 3 * 20) / 4
    for gi, (gname, tiles) in enumerate(groups):
        gx = cx + gi * (colw + 20)
        els += _lab(gx, y, gname, G)
        for ti, (ic, title, sub, col) in enumerate(tiles):
            els += _tile(gx, y + 24 + ti * 88, colw, 76, ic, title, sub, G, col)
    els += note(cx, y + 320, cw,
                "Settings are grouped by what the user is trying to change, not by table. Master data screens are all the same shape (list + drawer + search/filter)\n"
                "so they can share one implementation. Tenant profile is editable by the Owner; the Tenants LIST (next screen) is Super Admin only.",
                ACCENT, G)
    return els


def _d9(ox, oy):
    """Tenants list — Super Admin."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "9. Tenants — Super Admin only",
                                     "Settings", g, sub_active="Tenant")
    e, y = page_header(cx, cy, cw, "Tenants",
                       actions=[("⬇ Export", "ghost"), ("＋ New tenant", "primary")],
                       subtitle="Tenants are created here — there is no public sign-up",
                       g=G)
    els += e
    els += search_bar(cx, y, 320, "Name, code or city", G)
    els += filter_chips(cx + 336, y + 5, ["All", "Shop", "Boutique", "Mall"], 0, G)
    y += 56
    e, y2 = table(cx, y, cw,
                  ["Code", "Name", "Type", "City", "Currency", "Language", "Timezone", "Users", "Branches", "Status", ""],
                  [["ADF", "Al Dubai Bridal", "shop", "Kabul", "AFN", ("Dari (RTL)", VIOLET), "Asia/Kabul", "5", "2", ("active", OK), "Edit"],
                   ["RSB", "Roshan Bridal", "boutique", "Herat", "AFN", ("Pashto (RTL)", VIOLET), "Asia/Kabul", "3", "1", ("active", OK), "Edit"],
                   ["MZB", "Mazar Bridal Mall", "mall", "Mazar-i-Sharif", "AFN", ("English (LTR)", INFO), "Asia/Kabul", "8", "3", ("active", OK), "Edit"],
                   ["KDB", "Kandahar Bridal House", "shop", "Kandahar", "AFN", ("Pashto (RTL)", VIOLET), "Asia/Kabul", "2", "1", ("suspended", DANGER), "Edit"]],
                  G, row_h=46, widths=[0.55, 1.5, 0.7, 1.1, 0.75, 1.05, 1.0, 0.55, 0.7, 0.8, 0.45])
    els += e
    els += note(cx, y2 + 8, cw,
                "tenants.code is unique globally and becomes the SKU prefix (ADF → ADF26-0042). Every other document number is unique PER TENANT via platform_sequences —\n"
                "the corrected flaw A1, where v1 made every number globally unique so the second tenant to create SO26-000001 would collide on day one.\n"
                "Creating a tenant also seeds its role copies, default finance categories, currencies, units, payment methods and a main branch with a default warehouse.",
                ACCENT, G)
    return els


def _d10(ox, oy):
    """Tenant drawer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "10. Create / edit tenant — drawer",
                                     "Settings", g, sub_active="Tenant")
    e, y = page_header(cx, cy, cw, "Tenants", subtitle="Editing Al Dubai Bridal", g=G)
    els += e
    e, _ = table(cx, y, cw * 0.46, ["Code", "Name", "City", "Status"],
                 [["ADF", "Al Dubai Bridal", "Kabul", "active"],
                  ["RSB", "Roshan Bridal", "Herat", "active"]],
                 G, row_h=42, widths=[0.5, 1.4, 0.9, 0.7])
    els += e
    de, fx, fy, fw = drawer(cx, cy - 20, cw, ch, "Edit tenant", "right", 480,
                            "Al Dubai Bridal · created 02 Jan 2026", G)
    els += de
    yy = fy
    e, yy = _inp(fx, yy, fw * 0.3 - 6, "Code", "ADF", G, True)
    els += e
    e, _ = _inp(fx + fw * 0.3 + 6, yy - 64, fw * 0.7 - 6, "Business name", "Al Dubai Bridal", G, True)
    els += e
    e, yy = _sel(fx, yy, fw * 0.5 - 6, "Type", "Shop", G, True)
    els += e
    e, _ = _inp(fx + fw * 0.5 + 6, yy - 64, fw * 0.5 - 6, "Phone", "0700 12 34 56", G)
    els += e
    e, yy = _inp(fx, yy, fw, "Email / website", "info@aldubaibridal.af", G)
    els += e
    els += _lab(fx, yy, "LOCATION — CITY FIRST, THEN ADDRESS", G, ACCENT)
    yy += 18
    e, yy = _sel(fx, yy, fw, "City", "Kabul", G, True)
    els += e
    e, yy = textarea(fx, yy, fw, "Address (street / building)", "Shahr-e-Naw, Ansari Square,\nBuilding 4, 2nd floor", G, 2)
    els += e
    els += _lab(fx, yy, "THREE SEPARATE FIELDS — NEVER COMBINED", G, ACCENT)
    yy += 18
    e, yy = _sel(fx, yy, fw, "Default currency", "AFN — Afghan afghani", G, True)
    els += e
    e, yy = _sel(fx, yy, fw, "Default language", "دری  Dari  (RTL)", G, True)
    els += e
    e, yy = _sel(fx, yy, fw, "Timezone", "Asia/Kabul  (UTC+4:30)", G, True)
    els += e
    els.append(rect(fx, yy, fw, 60, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=G))
    els.append(text(fx, yy + 22, f"{ICON['photo']}   Replace logo", 12, ACCENT, "center", fw, G))
    els += btn(fx, yy + 74, fw, 44, "Save tenant", "primary", G)
    els += note(fx, yy + 128, fw,
                "Changing Default language remounts the whole shell:\nDari or Pashto → RTL, drawers open from the LEFT.\nThere is no per-user or per-page override.", VIOLET, G)
    return els


def _d11(ox, oy):
    """Tenant preferences."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "11. Preferences — business policy",
                                     "Settings", g, sub_active="Tenant")
    e, y = page_header(cx, cy, cw, "Preferences",
                       actions=[("Cancel", "ghost"), ("Save", "primary")],
                       subtitle="These settings drive costing, availability and the business day",
                       g=G)
    els += e
    COL = (cw - 48) / 3
    cols = [
        ("INVENTORY POLICY", ACCENT, [
            ("Business type", "Bridal — rental & sale", "sel"),
            ("SKU prefix", "ADF", "inp"),
            ("Costing method", "Weighted average cost", "sel"),
            ("Allow negative stock", "No — block oversell", "sel"),
            ("Low stock alerts", "On", "sel"),
        ]),
        ("RENTAL POLICY", VIOLET, [
            ("Default rental days", "3", "inp"),
            ("Default deposit %", "30", "inp"),
            ("Cleaning buffer days", "2", "inp"),
            ("Expected rental uses", "20", "inp"),
            ("Rental cost method", "Per use amortisation", "sel"),
        ]),
        ("ACCOUNTING & UI", INFO, [
            ("Business day cutoff", "00:00", "inp"),
            ("Date format", "YYYY-MM-DD", "sel"),
            ("Mobile navigation", "Bottom tabs", "sel"),
            ("Form drawer side", "Auto (follows direction)", "sel"),
            ("Default branch", "Main branch", "sel"),
        ]),
    ]
    for ci, (title, col, fields) in enumerate(cols):
        px = cx + ci * (COL + 24)
        els.append(rect(px, y, COL, 432, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(rect(px, y, COL, 4, strokeColor=col, backgroundColor=col, strokeWidth=1, groupIds=G))
        els.append(text(px + 20, y + 20, title, 11, col, width=COL - 40, g=G))
        yy = y + 48
        for lab, val, kind in fields:
            fn = _sel if kind == "sel" else _inp
            e, yy = fn(px + 20, yy, COL - 40, lab, val, G)
            els += e
    els += note(cx, y + 450, cw,
                "Two settings here decide how the whole system reports money and availability:\n"
                "   • Expected rental uses (20) is the ADR-002 divisor — rental COGS per use = acquisition_cost ÷ 20, accumulated until the dress has paid for itself.\n"
                "   • Cleaning buffer days (2) extends every reservation's blocked range, and the DB exclusion constraint guards that extended range (ADR-010).\n"
                "Business day cutoff makes 'today's profit' unambiguous: a sale rung up at 00:30 with a 02:00 cutoff belongs to the previous trading day.",
                VIOLET, G)
    return els


def _d12(ox, oy):
    """Branches → warehouses."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "12. Branches → warehouses",
                                     "Settings", g, sub_active="Branches")
    e, y = page_header(cx, cy, cw, "Branches & warehouses",
                       actions=[("＋ New warehouse", "secondary"), ("＋ New branch", "primary")],
                       subtitle="A warehouse belongs to exactly one branch · one default per branch",
                       g=G)
    els += e
    LW = cw * 0.42
    els += _lab(cx, y, "BRANCHES", G)
    e, _ = table(cx, y + 22, LW, ["Code", "Branch", "City", "Main", "Status"],
                 [["MAIN", "Main branch", "Kabul", ("✓", OK), ("active", OK)],
                  ["SHN", "Shar-e-Naw", "Kabul", "", ("active", OK)]],
                 G, row_h=46, widths=[0.6, 1.4, 0.9, 0.5, 0.7])
    els += e
    rx = cx + LW + 24
    RW = cw - LW - 24
    els += _lab(rx, y, "WAREHOUSES IN — MAIN BRANCH", G, ACCENT)
    e, y2 = table(rx, y + 22, RW,
                  ["Code", "Warehouse", "Location", "Default", "Items", "Stock worth", "Status"],
                  [["WH-A", "Main Store", "Ground floor", ("✓", OK), "212", "AFN 3,918,220", ("active", OK)],
                   ["WH-B", "Repair Room", "Back office", "", "9", "AFN 142,600", ("active", OK)],
                   ["WH-C", "Display Floor", "Shop window", "", "63", "AFN 760,520", ("active", OK)]],
                  G, row_h=46, widths=[0.6, 1.3, 1.1, 0.65, 0.55, 1.1, 0.7])
    els += e
    els += note(cx, y2 + 16, cw,
                "Stock lives per WAREHOUSE, not per item — inventory_items carries no branch_id or warehouse_id (corrected flaw B5). The same SKU can hold stock in\n"
                "Main Store and Display Floor simultaneously, and inventory_stock_balances is keyed on (item, warehouse). Transfers move quantity and cost between them.\n"
                "Branch scoping for RBAC: a user whose every user_roles row carries a branch_id sees only those branches; a role row with branch_id NULL is tenant-wide (A12).",
                ACCENT, G)
    return els


def _d13(ox, oy):
    """Audit log."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "13. Audit log — posts, voids, access",
                                     "Settings", g, sub_active="Audit log")
    e, y = page_header(cx, cy, cw, "Audit log",
                       actions=[("⬇ Export", "secondary")],
                       subtitle="Every post and void is recorded, not just logins",
                       g=G)
    els += e
    els += search_bar(cx, y, 300, "User, entity or summary", G)
    els += filter_chips(cx + 316, y + 5, ["All", "Post", "Void", "Login", "Settings", "Permissions"], 0, G)
    y += 56
    e, y2 = table(cx, y, cw,
                  ["When", "User", "Module", "Action", "Entity", "Summary", "IP"],
                  [["12 Sep 09:14", "Zahra Ali", "Procurement", ("post", OK), "GRN26-0009", "Received 18 units · AFN 246,404 landed", "10.0.4.22"],
                   ["12 Sep 08:52", "Ahmad Zaki", "Finance", ("void", DANGER), "FIN26-000437", "Voided — wrong order · reversal FIN26-000438", "10.0.4.11"],
                   ["12 Sep 08:31", "Nasrin Hakimi", "Sales", ("post", OK), "SO26-000022", "Walk-in sale completed · AFN 44,000", "10.0.4.15"],
                   ["12 Sep 08:04", "Ahmad Zaki", "Platform", ("update", INFO), "tenant_settings", "expected_rental_uses 18 → 20", "10.0.4.11"],
                   ["12 Sep 08:02", "Ahmad Zaki", "Platform", ("login", MUTED), "users/1", "Signed in", "10.0.4.11"],
                   ["11 Sep 17:40", "Ahmad Zaki", "Platform", ("update", WARN), "roles/3", "Cashier: granted sales.orders.void", "10.0.4.11"],
                   ["11 Sep 16:22", "Farid Omar", "Inventory", ("post", OK), "ADJ26-0011", "Adjustment −1 Champagne Gown · count", "10.0.4.31"],
                   ["11 Sep 14:05", "Nasrin Hakimi", "Inventory", ("post", DANGER), "DSP26-0004", "Disposed Rose Nikah Abaya · AFN 18,600", "10.0.4.15"]],
                  G, row_h=42, widths=[1.0, 1.1, 0.95, 0.65, 1.05, 2.4, 0.85])
    els += e
    els += note(cx, y2 + 8, cw,
                "MANDATORY audited events: every post, every void (with its void_reason), permission and role changes, tenant setting changes, price changes, login and logout.\n"
                "v1 scoped the audit log to 'login + critical settings changes', which left the two actions an owner most needs to trace — who moved stock, who moved money — unrecorded.\n"
                "before_json / after_json capture the change itself, so row 4 shows the exact setting transition and row 6 shows the permission that was granted.",
                ACCENT, G)
    return els


def _d14(ox, oy):
    """RTL mirror — Dari."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "14. RTL reference — Dari (دری)",
                                     "Settings", g, sub_active="Users & roles", rtl=True,
                                     topbar_extra=f"Ahmad {ICON['user']}    3 {ICON['bell']}    (RTL) دری {ICON['globe']}")
    els.append(rect(cx - 28 - SIDEBAR_W, cy - 86, SIDEBAR_W, 40, strokeColor=ROSE,
                    backgroundColor=ROSE_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx - 28 - SIDEBAR_W, cy - 74, "◀ sidebar mirrors to the RIGHT", 10.5, ROSE, "center", SIDEBAR_W, G))
    e, y = page_header(cx, cy, cw, "کاربران", subtitle="ایجاد کاربر جدید در این فروشگاه", g=G)
    els += e
    # right-aligned table header emulation
    e, y2 = table(cx, y, cw,
                  ["وضعیت", "شعبه", "نقش‌ها", "تلفن", "ایمیل", "نام"],
                  [[("فعال", OK), "مرکزی", ("مالک", ACCENT), "0700 12 34 56", "ahmad@aldubaibridal.af", "احمد ذکی"],
                   [("فعال", OK), "مرکزی", ("مدیر · صندوق‌دار", ACCENT), "0700 44 21 90", "nasrin@aldubaibridal.af", "نسرین حکیمی"],
                   [("فعال", OK), "شهر نو", ("صندوق‌دار", ACCENT), "0700 90 11 23", "zahra@aldubaibridal.af", "زهرا علی"]],
                  G, row_h=46, widths=[0.7, 0.8, 1.4, 1.1, 1.75, 1.15])
    els += e
    de, fx, fy, fw = drawer(cx, cy - 20, cw, ch, "کاربر جدید", "left", 470,
                            "در حالت راست‌چین، کشو از سمت چپ باز می‌شود", G)
    els += de
    yy = fy
    for lab, val, req in [("فروشگاه", "الدوبی برایدل (ADF)", True), ("نام کامل", "زهرا علی", True),
                          ("ایمیل", "zahra@aldubaibridal.af", True), ("تلفن", "0700 90 11 23", False),
                          ("رمز عبور", "••••••••••", True), ("شعبه پیش‌فرض", "شهر نو", False)]:
        e, yy = _inp(fx, yy, fw, lab, val, G, req)
        els += e
    els += _lab(fx, yy, "نقش‌ها — یک یا چند مورد *", G, ACCENT)
    ch_, xx = chip(fx, yy + 20, "✕  صندوق‌دار", ACCENT, g=G); els += ch_
    ch_, _ = chip(xx, yy + 20, "✕  انباردار", ACCENT, g=G); els += ch_
    els += btn(fx, yy + 62, fw, 44, "ایجاد کاربر", "primary", G)
    els += note(cx, oy + 800, cw,
                "RTL RULE SET — applies to every screen in the system when tenants.default_language_id is Dari (fa) or Pashto (ps):\n"
                "   1. Sidebar moves to the right edge · 2. Drawers open from the LEFT · 3. Text and table columns right-align, and column ORDER reverses\n"
                "   4. Back arrows, chevrons and progress steppers mirror · 5. Numbers, SKUs, currency amounts and dates stay LTR inside RTL text\n"
                "   6. Icons keep their meaning but directional ones (← →) flip. Direction is a tenant setting only — there is no per-user or per-page switcher.",
                ROSE, G)
    return els


# ══════════════════════════════════════════════════════════════════
#  MOBILE
# ══════════════════════════════════════════════════════════════════

def _m1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "1. Login", g, show_nav=False)
    y = cy + 60
    els.append(rect(cx + cw / 2 - 30, y, 60, 60, strokeColor=ACCENT, backgroundColor=ACCENT,
                    strokeWidth=1, groupIds=G))
    els.append(text(cx + cw / 2 - 30, y + 18, ICON["dress"], 24, "#ffffff", "center", 60, G))
    els.append(text(cx, y + 78, "BOMS", 30, INK, "center", cw, G))
    els.append(text(cx, y + 116, "Sign in to continue", 13, MUTED, "center", cw, G))
    y += 160
    e, y = _inp(cx, y, cw, "Email or phone", "0700 12 34 56", G, True, 46)
    els += e
    e, y = _inp(cx, y, cw, "Password", "••••••••••", G, True, 46)
    els += e
    els.append(text(cx, y - 4, "Forgot password?", 12.5, ACCENT, g=G))
    els += btn(cx, y + 28, cw, 50, "Sign in", "primary", G)
    els.append(text(cx, y + 104, "Language and layout direction come\nfrom your shop's settings.", 11, FAINT, "center", cw, G))
    return els


def _m2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "2. Forgot password", g, show_nav=False)
    e, y = phone_header(cx, cy, cw, "Reset password", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y, "We'll send a 6-digit code to your phone\nor email.", 12.5, MUTED, width=cw, g=G))
    y += 44
    e, y = _inp(cx, y, cw, "Email or phone", "0700 12 34 56", G, True, 46)
    els += e
    els += btn(cx, y + 6, cw, 48, "Send reset code", "primary", G)
    y += 76
    els.append(line(cx, y, cw, HAIRLINE, G))
    y += 20
    els.append(text(cx, y, "ENTER CODE", 10, MUTED, width=cw, g=G))
    y += 20
    for i in range(6):
        bx = cx + i * ((cw - 40) / 6 + 8)
        els.append(rect(bx, y, (cw - 40) / 6, 52, strokeColor=LINE, backgroundColor=BG,
                        strokeWidth=1, groupIds=G))
        els.append(text(bx, y + 16, "•" if i < 3 else "", 18, INK, "center", (cw - 40) / 6, G))
    els += btn(cx, y + 68, cw, 48, "Verify code", "primary", G)
    els.append(text(cx, y + 128, "Resend in 00:42", 11.5, MUTED, "center", cw, G))
    return els


def _m3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "3. Home dashboard", g, "Home")
    els.append(text(cx, cy, "Good morning, Ahmad", 19, INK, width=cw, g=G))
    els.append(text(cx, cy + 26, "Al Dubai Bridal · Main branch · Sat 12 Sep", 11, MUTED, width=cw, g=G))
    y = cy + 56
    els.append(rect(cx, y, cw, 92, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=2, groupIds=G))
    els.append(text(cx + 16, y + 12, "NET PROFIT TODAY", 10, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 30, "AFN 61,180", 30, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 68, "your cash 344,000 · deposits held 68,000", 9.5, ACCENT, width=cw - 32, g=G))
    y += 108
    for i, (lab, val, col) in enumerate([("A/R owed to us", "86,400", INFO), ("A/P we owe", "252,388", WARN),
                                         ("Due returns", "3", DANGER), ("Low stock", "11", WARN)]):
        bx = cx + (i % 2) * (cw / 2 + 4)
        by = y + (i // 2) * 70
        els += kpi_card(bx, by, cw / 2 - 4, 62, lab, val, col, g=G)
    y += 152
    els.append(text(cx, y, "TODAY'S SCHEDULE", 10, MUTED, width=cw, g=G))
    y += 18
    for t, kind, cust, col in [("10:00", "Pickup", "Sara Ahmadi", VIOLET),
                               ("12:30", "Return", "Fatima Rahimi", INFO),
                               ("17:00", "Return · overdue 2 d", "Nasrin Hakimi", DANGER)]:
        els.append(rect(cx, y, cw, 56, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, t, 12, MUTED, width=50, g=G))
        els.append(text(cx + 66, y + 9, cust, 12.5, INK, width=cw - 80, g=G))
        els.append(text(cx + 66, y + 29, kind, 11, col, width=cw - 80, g=G))
        y += 64
    return els


def _m4(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "4. More / settings", g, "More")
    e, y = phone_header(cx, cy, cw, "More", g=G)
    els += e
    groups = [("OPERATIONS", [(ICON["procurement"], "Procurement"), (ICON["reports"], "Reports")]),
              ("ORGANISATION", [(ICON["branch"], "Tenant profile"), (ICON["warehouse"], "Branches & warehouses"),
                                (ICON["settings"], "Preferences")]),
              ("ACCESS", [(ICON["user"], "Users"), (ICON["lock"], "Roles & permissions"),
                          (ICON["ledger"], "Audit log")]),
              ("SYSTEM", [(ICON["globe"], "Languages"), (ICON["bell"], "Notifications")])]
    for gname, items in groups:
        els.append(text(cx, y, gname, 9.5, MUTED, width=cw, g=G))
        y += 18
        for ic, lab in items:
            els.append(rect(cx, y, cw, 48, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
            els.append(text(cx + 16, y + 15, ic, 14, ACCENT, g=G))
            els.append(text(cx + 46, y + 16, lab, 13, INK, width=cw - 80, g=G))
            els.append(text(cx + cw - 26, y + 16, "›", 14, MUTED, g=G))
            y += 54
        y += 10
    return els


def _m5(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "5. Users list", g, "More")
    e, y = phone_header(cx, cy, cw, "Users", left=ICON["back"], right=ICON["filter"], g=G)
    els += e
    els += search_bar(cx, y, cw, "Name, email or phone", G)
    y += 52
    for nm, roles, br, st, col in [("Ahmad Zaki", "Owner", "Main", "active", OK),
                                   ("Nasrin Hakimi", "Manager · Cashier", "Main", "active", OK),
                                   ("Zahra Ali", "Cashier", "Shar-e-Naw", "active", OK),
                                   ("Farid Omar", "Stock keeper", "Main", "active", OK),
                                   ("Laila Sadat", "Owner", "Main", "inactive", MUTED)]:
        els.append(rect(cx, y, cw, 70, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(base("ellipse", cx + 12, y + 16, 38, 38, strokeColor=LINE,
                        backgroundColor=SOFT, strokeWidth=1, groupIds=G))
        els.append(text(cx + 12, y + 27, nm[0], 14, MUTED, "center", 38, G))
        els.append(text(cx + 60, y + 12, nm, 13, INK, width=cw - 150, g=G))
        els.append(text(cx + 60, y + 31, roles, 11, ACCENT, width=cw - 150, g=G))
        els.append(text(cx + 60, y + 48, br, 10, MUTED, width=cw - 150, g=G))
        ch_, _ = chip(cx + cw - 84, y + 24, st, col, g=G)
        els += ch_
        y += 78
    els += fab(cx + cw, cy + ch - 130, "＋ New user", G)
    return els


def _m6(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "6. Create user (sheet)", g, "More", show_nav=False)
    els.append(rect(ox + 1, oy + TITLE_H + 90, PHONE_W - 2, PHONE_H - 90, strokeColor=LINE,
                    backgroundColor=BG, strokeWidth=2, groupIds=G))
    sy = oy + TITLE_H + 108
    els.append(text(cx, sy, "New user", 19, INK, width=cw - 40, g=G))
    els.append(text(cx + cw - 20, sy + 2, ICON["cross"], 15, MUTED, g=G))
    y = sy + 36
    for lab, val, req in [("Tenant", "Al Dubai Bridal (ADF)", True), ("Full name", "Zahra Ali", True),
                          ("Email", "zahra@aldubaibridal.af", True), ("Phone", "0700 90 11 23", False),
                          ("Password", "••••••••••", True), ("Default branch", "Shar-e-Naw", False)]:
        e, y = _inp(cx, y, cw, lab, val, G, req, 34)
        els += e
    els.append(text(cx, y, "ROLES — ONE OR MORE *", 10, ACCENT, width=cw, g=G))
    y += 18
    ch_, xx = chip(cx, y, "Cashier ✕", ACCENT, g=G); els += ch_
    ch_, _ = chip(xx, y, "Stock keeper ✕", ACCENT, g=G); els += ch_
    y += 32
    for i, (rn, on) in enumerate([("Owner", False), ("Manager", False), ("Accountant", False)]):
        els += _check(cx, y + i * 26, rn, on, G)
    els += btn(cx, y + 92, cw, 46, "Create user", "primary", G)
    els.append(text(cx, y + 146, "Active immediately — no invitation is sent.", 10.5, MUTED, "center", cw, G))
    return els


def _m7(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "7. Permission matrix", g, "More")
    e, y = phone_header(cx, cy, cw, "Manager", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y, "36 of 48 permissions · copied from template", 11, MUTED, width=cw, g=G))
    y += 26
    MODULES = [("Inventory", ["view", "create", "edit", "post", "void"], [1, 1, 1, 1, 1]),
               ("Sales", ["view", "create", "edit", "post", "void"], [1, 1, 1, 1, 1]),
               ("Finance", ["view", "create", "edit", "post", "void"], [1, 1, 1, 1, 0]),
               ("Procurement", ["view", "create", "post", "approve"], [1, 1, 1, 1])]
    for mod, acts, grants in MODULES:
        els.append(rect(cx, y, cw, 30, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 8, mod, 12, INK, width=cw - 100, g=G))
        els.append(text(cx + cw - 70, y + 9, "select all", 10, ACCENT, "right", 56, G))
        y += 34
        for i, a in enumerate(acts):
            els += _check(cx + 16, y, a, bool(grants[i]), G)
            y += 24
        y += 8
    return els


def _m8(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "8. Branches → warehouses", g, "More")
    e, y = phone_header(cx, cy, cw, "Branches", left=ICON["back"], right="＋", g=G)
    els += e
    for br, city, main, whs in [("Main branch", "Kabul", True,
                                 [("WH-A", "Main Store", "212 items", True),
                                  ("WH-B", "Repair Room", "9 items", False),
                                  ("WH-C", "Display Floor", "63 items", False)]),
                                ("Shar-e-Naw", "Kabul", False,
                                 [("WH-D", "Floor 2", "84 items", True)])]:
        els.append(rect(cx, y, cw, 48, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 9, br, 13, ACCENT, width=cw - 100, g=G))
        els.append(text(cx + 14, y + 28, city, 10.5, ACCENT, width=cw - 100, g=G))
        if main:
            els.append(text(cx + cw - 70, y + 16, "main ✓", 10.5, ACCENT, "right", 56, G))
        y += 54
        for code, nm, cnt, dflt in whs:
            els.append(rect(cx + 16, y, cw - 16, 46, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
            els.append(text(cx + 30, y + 8, nm, 12.5, INK, width=cw - 130, g=G))
            els.append(text(cx + 30, y + 26, f"{code} · {cnt}", 10, MUTED, width=cw - 130, g=G))
            if dflt:
                els.append(text(cx + cw - 74, y + 16, "default", 10, OK, "right", 60, G))
            y += 52
        y += 10
    return els


def _m9(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "9. RTL — Dari (دری)", g, "Home")
    els.append(rect(cx, cy - 30, cw, 24, strokeColor=ROSE, backgroundColor=ROSE_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx, cy - 26, "RTL reference — everything mirrors", 10, ROSE, "center", cw, G))
    els.append(text(cx, cy + 6, "صبح بخیر، احمد", 19, INK, "right", cw, G))
    els.append(text(cx, cy + 32, "الدوبی برایدل · شعبه مرکزی · ۱۲ سپتامبر", 11, MUTED, "right", cw, G))
    y = cy + 62
    els.append(rect(cx, y, cw, 92, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=2, groupIds=G))
    els.append(text(cx + 16, y + 12, "سود خالص امروز", 10, ACCENT, "right", cw - 32, G))
    els.append(text(cx + 16, y + 30, "AFN 61,180", 30, ACCENT, "right", cw - 32, G))
    els.append(text(cx + 16, y + 68, "پول شما ۳۴۴٬۰۰۰ · ودیعه ۶۸٬۰۰۰", 9.5, ACCENT, "right", cw - 32, G))
    y += 108
    for i, (lab, val, col) in enumerate([("طلب از مشتریان", "86,400", INFO), ("بدهی به تأمین‌کنندگان", "252,388", WARN),
                                         ("بازگشت امروز", "3", DANGER), ("موجودی کم", "11", WARN)]):
        bx = cx + (i % 2) * (cw / 2 + 4)
        by = y + (i // 2) * 70
        els.append(rect(bx, by, cw / 2 - 4, 62, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(bx + 10, by + 12, lab, 10, MUTED, "right", cw / 2 - 24, G))
        els.append(text(bx + 10, by + 32, val, 18, col, "right", cw / 2 - 24, G))
    y += 152
    els.append(text(cx, y, "برنامه امروز", 10, MUTED, "right", cw, G))
    y += 18
    for t, kind, cust, col in [("۱۰:۰۰", "تحویل", "سارا احمدی", VIOLET),
                               ("۱۲:۳۰", "بازگشت", "فاطمه رحیمی", INFO)]:
        els.append(rect(cx, y, cw, 56, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + cw - 60, y + 10, t, 12, MUTED, "right", 46, G))
        els.append(text(cx + 14, y + 9, cust, 12.5, INK, "right", cw - 80, G))
        els.append(text(cx + 14, y + 29, kind, 11, col, "right", cw - 80, G))
        y += 64
    return els


# ══════════════════════════════════════════════════════════════════

def desktop():
    els = board_title(0, -170, "BOMS Desktop — Platform, Auth & Settings",
                      "Login-only entry · no invite flow · tenant-bound users with multi-role RBAC · "
                      "tenant-driven locale (EN LTR / Dari · Pashto RTL) · drawers follow direction")
    screens = [_d1, _d2, _d3, _d4, _d5, _d6, _d7, _d8, _d9, _d10, _d11, _d12, _d13, _d14]
    labels = {0: "AUTH & HOME", 4: "USERS & ACCESS", 8: "TENANT & STRUCTURE", 12: "AUDIT & RTL"}
    for i, fn in enumerate(screens):
        ox, oy = grid_pos(i, DESK_COLS)
        if i in labels:
            els += section_label(ox, oy - 74, labels[i])
        els += fn(ox, oy)
    els += flow_arrows(len(screens), DESK_COLS)
    return els


def mobile():
    els = board_title(0, -150, "BOMS Mobile — Platform, Auth & Settings",
                      "Login · home dashboard · settings · users & roles · branches · RTL reference")
    screens = [_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8, _m9]
    for i, fn in enumerate(screens):
        ox, oy = grid_pos(i, PHONE_COLS, PHONE_W, PHONE_H)
        els += fn(ox, oy)
    els += flow_arrows(len(screens), PHONE_COLS, PHONE_W, PHONE_H)
    return els
