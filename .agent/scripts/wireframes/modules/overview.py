#!/usr/bin/env python3
"""BOMS — system overview board: sidebar design system, module map, sitemap.

This is the board to open first. It defines the navigation shell every module
screen sits inside, and shows how procurement → inventory → sales → finance
connect.
"""

from __future__ import annotations

from dsl import *  # noqa: F401,F403


def _lab(x, y, s, color=MUTED, size=11.5):
    return [text(x, y, s, size, color)]


def _card(x, y, w, h, title, color=ACCENT, bg=None):
    return [rect(x, y, w, h, strokeColor=color, backgroundColor=bg or BG, strokeWidth=2),
            rect(x, y, w, 4, strokeColor=color, backgroundColor=color, strokeWidth=1),
            text(x + 18, y + 20, title, 14, color, width=w - 36)]


# ── 1. SIDEBAR DESIGN SYSTEM ──────────────────────────────────────

def _sidebar_spec(ox, oy):
    els = section_label(ox, oy - 60, "NAVIGATION SHELL — SIDEBAR & MOBILE TABS", ROSE)
    els.append(text(ox, oy - 18,
                    "The sidebar is the app's spine: icon + label, grouped by intent, with an active pill, "
                    "count badges, contextual sub-navigation, a branch switcher and a user block.",
                    13, MUTED, width=1800))

    # ── expanded sidebar, three states
    states = [("Expanded — Inventory active", "Inventory", "Items"),
              ("Expanded — Finance active", "Finance", "Dashboard"),
              ("Expanded — Sales active (badge)", "Sales", "Orders")]
    for i, (title, active, sub) in enumerate(states):
        x = ox + i * (SIDEBAR_W + 70)
        g = [nid()]
        els.append(text(x, oy + 30, title, 12, INK, width=SIDEBAR_W))
        els.append(rect(x, oy + 54, SIDEBAR_W + 2, 700, strokeColor=INK,
                        backgroundColor=SIDEBAR_BG, strokeWidth=1, groupIds=g))
        els += sidebar(x - 1, oy + 54, active, g, 700, sub)

    # ── collapsed rail
    x = ox + 3 * (SIDEBAR_W + 70)
    g = [nid()]
    els.append(text(x, oy + 30, "Collapsed rail (72px)", 12, INK, width=200))
    els.append(rect(x, oy + 54, 72, 700, strokeColor=INK, backgroundColor=SIDEBAR_BG,
                    strokeWidth=1, groupIds=g))
    els.append(rect(x + 18, oy + 74, 36, 36, strokeColor=ACCENT, backgroundColor=ACCENT,
                    strokeWidth=1, groupIds=g))
    els.append(text(x + 18, oy + 85, ICON["dress"], 16, "#ffffff", "center", 36, g))
    rail = [("home", False), ("inventory", True), ("sales", False), ("procurement", False),
            ("finance", False), ("reports", False), ("settings", False)]
    yy = oy + 142
    for key, on in rail:
        if on:
            els.append(rect(x + 10, yy - 8, 52, 44, strokeColor=ACCENT, backgroundColor=ACCENT,
                            strokeWidth=1, groupIds=g))
        els.append(text(x + 10, yy + 4, ICON[key], 17, "#ffffff" if on else SIDEBAR_FG,
                        "center", 52, g))
        yy += 52
    els.append(text(x, oy + 700, "▸", 14, SIDEBAR_FG, "center", 72, g))

    # ── mobile tab bar
    mx = x + 150
    g = [nid()]
    els.append(text(mx, oy + 30, "Mobile bottom tabs (5 max)", 12, INK, width=PHONE_W))
    els.append(rect(mx, oy + 54, PHONE_W, 90, strokeColor=INK, backgroundColor=BG,
                    strokeWidth=2, groupIds=g))
    tabs_ = [("Home", "home", False), ("Inventory", "inventory", True), ("Sales", "sales", False),
             ("Finance", "finance", False), ("More", "filter", False)]
    tw = PHONE_W / 5
    for i, (t, ik, on) in enumerate(tabs_):
        els.append(text(mx + i * tw, oy + 76, ICON[ik], 18, ACCENT if on else MUTED, "center", tw, g))
        els.append(text(mx + i * tw, oy + 106, t, 10, ACCENT if on else MUTED, "center", tw, g))
    els.append(text(mx, oy + 156,
                    "Procurement, Reports and Settings live under More —\n"
                    "the owner's daily loop is Home · Inventory · Sales · Finance.",
                    11.5, MUTED, width=PHONE_W))

    # ── icon legend
    ly = oy + 260
    els += _lab(mx, ly, "ICON SET", INK, 13)
    icons = [("home", "Home"), ("inventory", "Inventory"), ("sales", "Sales"),
             ("procurement", "Procurement"), ("finance", "Finance"), ("reports", "Reports"),
             ("settings", "Settings"), ("customers", "Customers"), ("suppliers", "Suppliers"),
             ("dress", "Item / dress"), ("rental", "Rental"), ("reserve", "Reservation"),
             ("truck", "Receive / GRN"), ("ledger", "Ledger"), ("adjust", "Adjust"),
             ("dispose", "Dispose"), ("transfer", "Transfer"), ("cash", "Cash"),
             ("bank", "Bank"), ("receipt", "Expense"), ("lock", "Liability / locked"),
             ("alert", "Alert"), ("calendar", "Calendar"), ("branch", "Branch")]
    for i, (k, lab) in enumerate(icons):
        iy = ly + 26 + (i % 12) * 26
        ix = mx + (i // 12) * 190
        els.append(text(ix, iy, ICON[k], 14, INK))
        els.append(text(ix + 26, iy + 2, lab, 11.5, MUTED, width=150))

    # ── rules
    rx = mx + 400
    els += _lab(rx, oy + 260, "SIDEBAR RULES", INK, 13)
    els.append(text(rx, oy + 288,
                    "1.  Groups are intent-based, not table-based:\n"
                    "        MAIN · OPERATIONS · MONEY · INSIGHT · SYSTEM\n\n"
                    "2.  Active item: teal pill, white icon + label.\n"
                    "        Sub-navigation expands only under the active item.\n\n"
                    "3.  Badges are counts that need action today\n"
                    "        (open orders, due returns) — never vanity metrics.\n\n"
                    "4.  Branch switcher and user block are pinned to the\n"
                    "        bottom; switching branch re-scopes every list.\n\n"
                    "5.  In RTL (Dari / Pashto) the whole rail mirrors to the\n"
                    "        right edge and chevrons flip.\n\n"
                    "6.  Collapsed rail keeps icons only; labels appear as\n"
                    "        tooltips. State persists per user.\n\n"
                    "7.  Items the user lacks permission for are hidden,\n"
                    "        not disabled.",
                    12, MUTED, width=460))
    return els


# ── 2. MODULE MAP ─────────────────────────────────────────────────

def _module_map(ox, oy):
    els = section_label(ox, oy - 60, "MODULE MAP — HOW MONEY AND STOCK FLOW", ROSE)
    els.append(text(ox, oy - 18,
                    "Build order is 1 → 6. Finance-Core moves BEFORE Sales and Procurement because their "
                    "payment tables hold FKs into finance_accounts (corrected flaw A4).",
                    13, MUTED, width=1800))

    BW, BH = 300, 190
    GAPX = 90
    row1_y = oy + 40

    mods = [
        ("1 · PLATFORM", ACCENT, [
            "tenants · users · roles",
            "branches · warehouses",
            "currencies · units · terms",
            "platform_sequences",
            "exchange rates · audit",
        ]),
        ("2 · FINANCE-CORE", VIOLET, [
            "finance_accounts",
            "finance_categories",
            "finance_transactions",
            "customer_deposits",
            "cogs_entries",
        ]),
        ("3 · INVENTORY", INFO, [
            "items · categories",
            "stock_transactions (ledger)",
            "stock_balances (WAC)",
            "reservations",
            "entries · adjust · dispose",
        ]),
        ("4 · PROCUREMENT", WARN, [
            "suppliers",
            "purchase_orders",
            "receipts (GRN)",
            "supplier_payments",
            "returns",
        ]),
        ("5 · SALES", OK, [
            "customers",
            "orders (sale/rental/mixed)",
            "order_payments",
            "sale_returns",
            "rental_claims",
        ]),
        ("6 · FINANCE-REPORTING", ROSE, [
            "expenses · other income",
            "payables (A/P)",
            "receivables (A/R)",
            "daily_summaries",
            "P&L · 5 pillars",
        ]),
    ]
    for i, (title, col, lines) in enumerate(mods):
        x = ox + i * (BW + GAPX)
        els += _card(x, row1_y, BW, BH, title, col)
        els.append(text(x + 18, row1_y + 52, "\n".join("·  " + L for L in lines),
                        12, MUTED, width=BW - 36))
        if i < len(mods) - 1:
            els += arrow(x + BW + 8, row1_y + BH / 2, x + BW + GAPX - 8, row1_y + BH / 2)

    # data-flow band
    fy = row1_y + BH + 90
    els += _lab(ox, fy - 30, "RUNTIME DATA FLOW", INK, 14)
    flows = [
        ("Procurement receipt posted", "→  stock_in at LANDED cost  ·  WAC recomputed  ·  A/P opened", WARN),
        ("Sale line completed", "→  stock_out at WAC  ·  cash IN  ·  A/R if balance  ·  sale_cogs entry", OK),
        ("Rental confirmed", "→  reservation row (NOT a ledger row)  ·  deposit → LIABILITY, not income", VIOLET),
        ("Rental marked out / returned", "→  rent_out / rent_return  ·  owned qty unchanged  ·  cleaning buffer blocks dates", INFO),
        ("Rental completed", "→  rental_amortisation COGS = acquisition_cost ÷ expected_rental_uses", VIOLET),
        ("Rental lost or damaged", "→  rental_claim  ·  deposit forfeited → income  ·  disposal  ·  balance → A/R", DANGER),
        ("Supplier paid", "→  cash OUT  ·  A/P reduced  ·  one finance_transactions row", WARN),
        ("Anything voided", "→  a REVERSING document  ·  original kept  ·  nothing edited, nothing deleted", DANGER),
    ]
    for i, (evt, eff, col) in enumerate(flows):
        yy = fy + i * 34
        els.append(rect(ox, yy, 340, 28, strokeColor=col, backgroundColor=
                        {WARN: WARN_BG, OK: OK_BG, VIOLET: VIOLET_BG, INFO: INFO_BG,
                         DANGER: DANGER_BG}.get(col, SOFT), strokeWidth=1))
        els.append(text(ox + 14, yy + 7, evt, 12, col, width=316))
        els.append(text(ox + 356, yy + 7, eff, 12, MUTED, width=1400))

    # the four quantities
    qx = ox + 1180
    els += _lab(qx, fy - 30, "THE FOUR QUANTITIES  (ADR-004)", INK, 14)
    els.append(rect(qx, fy, 620, 172, strokeColor=INFO, backgroundColor=INFO_BG, strokeWidth=2))
    els.append(text(qx + 20, fy + 18,
                    "on_hand    = Σ ledger quantity              physically in the warehouse\n"
                    "on_rent    = Σ rent_out − Σ rent_return     out with customers\n"
                    "owned      = on_hand + on_rent              ← VALUATION USES THIS\n"
                    "reserved   = Σ active reservations          NOT from the ledger\n"
                    "available  = on_hand − reserved             sellable / bookable today\n\n"
                    "A gown at a wedding is still an asset. v1 made rent_out negative against\n"
                    "the same sum that produced stock worth, so total inventory value collapsed\n"
                    "every busy weekend and recovered on Monday.",
                    12, INFO, width=580))
    return els


# ── 3. SITEMAP ────────────────────────────────────────────────────

def _sitemap(ox, oy):
    els = section_label(ox, oy - 60, "SCREEN SITEMAP — 84 SCREENS ACROSS 5 MODULES", ROSE)
    els.append(text(ox, oy - 18,
                    "Every screen below is drawn in its module board. Desktop counts first, mobile in brackets.",
                    13, MUTED, width=1800))

    cols = [
        ("PLATFORM  14 (9)", ACCENT, [
            "Login", "Forgot password → OTP → reset", "Home dashboard",
            "Users list", "Create user drawer", "Roles list",
            "Permission matrix", "Settings hub", "Tenants list (Super Admin)",
            "Tenant drawer", "Preferences", "Branches → warehouses",
            "Audit log", "RTL reference (Dari)",
        ]),
        ("INVENTORY  16 (10)", INFO, [
            "Inventory hub", "Items list", "Item detail", "Item stock & cost tab",
            "Add / edit item drawer", "Availability calendar", "Stock ledger",
            "Manual stock entry", "Receive PO (GRN)", "Adjustment", "Dispose",
            "Transfer", "Reservations + conflict", "Valuation report",
            "Stock movement / stock-in", "Rental utilisation & ROI",
        ]),
        ("SALES  16 (10)", OK, [
            "Sales hub", "Orders list", "Customer pick", "New sale checkout",
            "New rental checkout", "Availability conflict", "Collect payment",
            "Order detail — sale", "Order detail — rental", "Mark returned",
            "Rental claim", "Sale return", "Customers list", "Customer detail",
            "Sales summary report", "Rental performance report",
        ]),
        ("PROCUREMENT  14 (8)", WARN, [
            "Procurement hub", "Suppliers list", "Supplier detail",
            "Supplier drawer", "Purchase orders list", "Create PO", "PO detail",
            "Receive goods (GRN)", "GRN new-item form", "GRN posted confirmation",
            "Pay supplier", "Supplier return", "Purchase register",
            "Stock-in report",
        ]),
        ("FINANCE  12 (8)", VIOLET, [
            "Dashboard — 5 pillars", "Period comparison", "Cash & banks",
            "Account statement", "Add expense", "Unified ledger",
            "Void modal", "Accounts payable + aging", "Accounts receivable + aging",
            "Collect / pay drawer", "Profit & loss", "Deposits held register",
        ]),
    ]
    CW = 360
    for i, (title, col, screens) in enumerate(cols):
        x = ox + i * (CW + 30)
        els.append(rect(x, oy + 30, CW, 60 + len(screens) * 26, strokeColor=col,
                        backgroundColor=BG, strokeWidth=2))
        els.append(rect(x, oy + 30, CW, 4, strokeColor=col, backgroundColor=col, strokeWidth=1))
        els.append(text(x + 18, oy + 50, title, 13, col, width=CW - 36))
        for j, s in enumerate(screens):
            els.append(text(x + 18, oy + 82 + j * 26, f"{j + 1:2d}.  {s}", 12, MUTED, width=CW - 36))

    # cross-cutting states
    sy = oy + 30 + 60 + 16 * 26 + 40
    els += _lab(ox, sy, "REQUIRED ON EVERY SCREEN", INK, 14)
    states = [
        ("Empty", "No rows yet — explain what to do, give the primary action", FAINT),
        ("Loading", "Skeleton rows, never a blocking spinner on a list", MUTED),
        ("Error", "What failed, what to try, and the retry action", DANGER),
        ("Permission", "Hidden entirely when the role lacks it — not disabled", WARN),
        ("Offline", "Queue the posting with its idempotency_key, show pending", INFO),
        ("RTL", "Mirrored layout when the tenant language is Dari or Pashto", ROSE),
    ]
    for i, (name, desc, col) in enumerate(states):
        x = ox + i * 320
        els.append(rect(x, sy + 26, 300, 74, strokeColor=col, backgroundColor=BG, strokeWidth=1))
        els.append(text(x + 16, sy + 40, name, 12.5, col, width=268))
        els.append(text(x + 16, sy + 60, desc, 11, MUTED, width=268))
    return els


# ── 4. CORRECTIONS BOARD ──────────────────────────────────────────

def _corrections(ox, oy):
    els = section_label(ox, oy - 60, "WHAT CHANGED FROM v1 — AND WHY IT MATTERED", ROSE)
    rows = [
        ("Rented stock vanished from valuation",
         "rent_out was a negative quantity in the same sum that produced 'total stock worth'.",
         "Owned = on hand + on rent. Valuation uses owned.", DANGER),
        ("Reserving a dress reduced stock",
         "'reserve' was a ledger type AND reserved was subtracted again for availability — double count.",
         "Reservations are not ledger rows. One source: inventory_reservations.", DANGER),
        ("Deposits counted as profit",
         "A refundable deposit posted straight to Income, inflating the number the owner trusts most.",
         "Deposits are a liability. Cash shows 'of which held' and 'your cash'.", DANGER),
        ("Rentals had no cost at all",
         "P&L was Income − Expenses − COGS, but a rental consumed nothing, so margin looked like 100% forever.",
         "Per-use amortisation: acquisition_cost ÷ expected_rental_uses.", DANGER),
        ("Costing was undefined",
         "Item purchase_amount, ledger unit_cost and an 'avg_unit_cost' view disagreed three ways.",
         "Weighted average cost per (item, warehouse), snapshotted on every stock-out.", WARN),
        ("Landed cost had three homes",
         "other_cost sat on the PO header, the PO line and the receipt line with no allocation rule.",
         "Pro-rata by line value → landed_unit_cost is the only cost that reaches inventory.", WARN),
        ("Double-booking was possible",
         "Conflict detection was application-level only — two staff could book one gown for one wedding.",
         "Postgres EXCLUDE constraint over daterange, including the cleaning buffer.", DANGER),
        ("Every document number was global",
         "unique on sku, order_number, po_number… so tenant B collided with tenant A on day one.",
         "unique (tenant_id, number) + platform_sequences for atomic allocation.", DANGER),
        ("A/R and A/P lived in two tables",
         "Order balance and receivable balance both held the number, with nothing reconciling them.",
         "finance_receivables / finance_payables own it; order columns are display caches.", WARN),
        ("The 'unified' ledger was not unified",
         "Sales and supplier payments had no finance_transaction_id, so void had nothing to reverse.",
         "Every money movement has exactly one finance_transactions row, linked both ways.", WARN),
        ("Build order was circular",
         "Sales was scheduled before Finance, but sales payments FK into finance_accounts.",
         "Finance-Core moves to step 2; reporting stays last.", INFO),
        ("Postings were not idempotent",
         "A double tap or a retry on a flaky mobile connection duplicated stock and cash.",
         "Client-generated idempotency_key, unique per tenant, on every posting.", INFO),
    ]
    els.append(rect(ox, oy + 20, 1900, 42, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1))
    for lab, x, w in [("DEFECT", 16, 420), ("WHY IT BROKE", 450, 760), ("FIX", 1230, 660)]:
        els.append(text(ox + x, oy + 34, lab, 11, MUTED, width=w))
    yy = oy + 62
    for name, why, fix, col in rows:
        els.append(rect(ox, yy, 1900, 52, strokeColor="transparent",
                        backgroundColor=SOFT2 if rows.index((name, why, fix, col)) % 2 else BG,
                        strokeWidth=0))
        els.append(line(ox, yy + 52, 1900, HAIRLINE))
        els.append(rect(ox, yy + 10, 4, 32, strokeColor=col, backgroundColor=col, strokeWidth=1))
        els.append(text(ox + 16, yy + 18, name, 12.5, col, width=420))
        els.append(text(ox + 450, yy + 18, why, 11.5, MUTED, width=760))
        els.append(text(ox + 1230, yy + 18, fix, 11.5, INK, width=660))
        yy += 52
    els.append(text(ox, yy + 24,
                    "Full detail: specs/review/01-spec-review.md (43 defects)  ·  "
                    "Decisions and rationale: specs/review/02-decisions.md (12 ADRs)",
                    12.5, ACCENT, width=1200))
    return els


def board():
    els = board_title(0, -240, "BOMS — System Overview",
                      "Bridal Omnichannel Management System · navigation shell · module map · "
                      "sitemap · v1 → v2 corrections.  Open this board first.")
    els += _sidebar_spec(0, 60)
    els += _module_map(0, 1080)
    els += _sitemap(0, 1900)
    els += _corrections(0, 2760)
    return els
