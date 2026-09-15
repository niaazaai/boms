#!/usr/bin/env python3
"""BOMS — Procurement module wireframes (desktop + mobile).

READING ORDER — one heading per row, same pattern as Inventory:

    A. DASHBOARD        A1
    B. SUPPLIERS        B1 list · B2 new drawer · B3 edit drawer ·
                        B4–B9 supplier profile, one screen per tab
    C. PURCHASE ORDERS  C1 list · C2 new drawer · C3 detail
    D. RECEIVING        D1 list · D2 receive drawer · D3 new-item drawer · D4 posted
    E. PAY & RETURN     E1 pay drawer · E2 return drawer
    F. REPORTS          F1 register · F2 stock-in · F3 aging

Rules this module draws:
  • There is NO PO approval step. Draft → Place order → Ordered.
  • Every create / edit is a drawer over its list. A list and a form never share a page.
  • Language switcher shows the language name only.
  • Qty to receive cannot exceed remaining — no over-receipt approval path.
  • Header other_cost is split pro-rata at post time → landed_unit_cost is what posts.
  • Posted receipts are immutable — Void writes reversing rows.
  • A/P lives in finance_payables; PO balance is a derived display.
"""

from __future__ import annotations

from dsl import *  # noqa: F401,F403

DESK_COLS = 4
PHONE_COLS = 6

SUPPLIER_TABS = [
    "Overview", "Purchase orders", "Receipts", "Payments", "Items supplied", "Price history",
]

SECTION_COLORS = {
    "DASHBOARD": ACCENT,
    "SUPPLIERS": ROSE,
    "PURCHASE ORDERS": INFO,
    "RECEIVING": WARN,
    "PAY & RETURN": VIOLET,
    "REPORTS": OK,
}

RATE = "USD @ 71.20 AFN"

SUPPLIER_ROWS = [
    ["SUP26-0001", "Istanbul Bridal Co.", "Elif Demir", "+90 532 441 8820", "USD", "Net 30", "3",
     ("441,440", ROSE), ("Active", OK)],
    ["SUP26-0002", "Dubai Fashion House", "Rashid Al Nuaimi", "+971 50 774 1190", "USD", "Net 15", "1",
     ("202,920", ROSE), ("Active", OK)],
    ["SUP26-0003", "Kabul Textile Traders", "Najib Ahmadi", "+93 700 214 556", "AFN", "Net 7", "1",
     ("118,000", DANGER), ("Active", OK)],
    ["SUP26-0004", "Herat Silk House", "Farid Rasouli", "+93 799 330 118", "AFN", "Cash", "1",
     "0.00", ("Active", OK)],
    ["SUP26-0005", "Mashhad Veil Supply", "Zahra Karimi", "+98 915 220 4471", "AFN", "Net 30", "0",
     ("92,000", ROSE), ("Active", OK)],
    ["SUP26-0006", "Lahore Embroidery Wks", "Imran Butt", "+92 300 844 2010", "AFN", "Net 30", "0",
     "0.00", ("Inactive", MUTED)],
]

PO_ROWS = [
    ["PO26-000012", "Istanbul Bridal Co.", "04 Sep", "18 Sep", "6", "345,320", ("60%", WARN),
     "120,000", ("225,320", ROSE), ("Partial", WARN)],
    ["PO26-000013", "Dubai Fashion House", "07 Sep", "21 Sep", "4", "202,920", ("0%", MUTED),
     "0", ("202,920", ROSE), ("Ordered", INFO)],
    ["PO26-000015", "Kabul Textile Traders", "09 Sep", "14 Sep", "5", "148,000", ("100%", OK),
     "148,000", "0.00", ("Received", OK)],
    ["PO26-000014", "Herat Silk House", "11 Sep", "25 Sep", "3", "86,400", ("—", FAINT),
     "0", ("86,400", MUTED), ("Draft", MUTED)],
    ["PO26-000010", "Mashhad Veil Supply", "22 Aug", "02 Sep", "5", "92,000", ("100%", OK),
     "0", ("92,000", ROSE), ("Closed", MUTED)],
    ["PO26-000009", "Lahore Embroidery Wks", "14 Aug", "—", "2", "38,000", ("—", FAINT),
     "0", "0.00", ("Cancelled", DANGER)],
]

GRN_LINES = [
    ["1 · White A-Line Gown", "6", "4", "2", "13,172.00", "2,654.00", ("14,499.00", ACCENT), "28,998.00"],
    ["2 · Ivory Ball Gown", "4", "2", "2", "17,088.00", "3,444.00", ("18,810.00", ACCENT), "37,620.00"],
    ["3 · Chantilly Veil · NEW", "12", "0", "12", "1,994.00", "2,411.00", ("2,194.92", ACCENT), "26,339.00"],
    ["4 · Pearl Hair Comb · NEW", "20", "0", "20", "641.00", "1,291.00", ("705.55", ACCENT), "14,111.00"],
]


# ── local compositions ────────────────────────────────────────────

def _lab(x, y, s, g, color=MUTED, size=11.5):
    return [text(x, y, s, size, color, g=g)]


def _panel(x, y, w, h, title, g, bg=BG, color=MUTED):
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=bg, strokeWidth=1, groupIds=g)]
    if title:
        els.append(text(x + 16, y + 13, title, 12, color, width=w - 32, g=g))
    return els


def _kv(x, y, w, label, value, g, color=INK, size=13):
    return [text(x, y, label, 10.5, MUTED, width=w, g=g),
            text(x, y + 15, value, size, color, width=w, g=g)]


def _kvr(x, y, w, pairs, g, size=12, step=22):
    els, yy = [], y
    for lab, val in pairs:
        col = INK
        if isinstance(val, tuple):
            val, col = val
        els.append(text(x, yy, lab, size, MUTED, width=w * 0.55, g=g))
        els.append(text(x + w * 0.45, yy, val, size, col, "right", w * 0.55, g=g))
        yy += step
    return els, yy


def _spec(cx, ox, oy, cw, body, color=ACCENT):
    return note(cx, oy + TITLE_H + DESK_H - 92, cw, body, color)


def _sheet_bar(cx, y, cw, g, search="Search…", extra=None):
    els = search_bar(cx, y, 440, search, g)
    els += btn(cx + 456, y, 130, 40, f"{ICON['filter']}  Filters", "secondary", g)
    els += btn(cx + cw - 150, y, 150, 40, "Columns ▾", "secondary", g)
    if extra:
        els += extra
    return els, y + 52


def _suppliers_backdrop(cx, cy, cw, g):
    els, y = page_header(cx, cy, cw, "Suppliers",
                         actions=[("＋ New supplier", "primary")],
                         subtitle="6 suppliers · 2 with overdue balances", g=g)
    els += search_bar(cx, y, 420, "Search name, code, phone…", g)
    e, _ = table(cx, y + 52, cw,
                 ["Code", "Name", "Contact", "Phone", "Curr.", "Terms", "A/P", "Status"],
                 [r[:5] + r[5:6] + r[7:9] for r in SUPPLIER_ROWS[:5]],
                 g, row_h=42, sheet=True,
                 widths=[0.95, 1.7, 1.2, 1.3, 0.55, 0.7, 1.0, 0.8])
    els += e
    return els


def _po_backdrop(cx, cy, cw, g):
    els, y = page_header(cx, cy, cw, "Purchase orders",
                         actions=[("＋ New PO", "primary")],
                         subtitle="September 2026 · all branches", g=g)
    els += search_bar(cx, y, 400, "Search PO number or supplier…", g)
    e, _ = table(cx, y + 52, cw,
                 ["PO #", "Supplier", "Date", "Expected", "Total AFN", "Status"],
                 [r[:4] + r[5:6] + r[9:10] for r in PO_ROWS[:5]],
                 g, row_h=40, sheet=True,
                 widths=[1.2, 1.8, 0.8, 0.9, 1.1, 1.0])
    els += e
    return els


def _receipts_backdrop(cx, cy, cw, g):
    els, y = page_header(cx, cy, cw, "Receipts (GRN)",
                         actions=[("Receive goods", "primary")],
                         subtitle="Posted receipts cannot be edited — void only", g=g)
    e, _ = table(cx, y, cw,
                 ["GRN #", "PO #", "Supplier", "Date", "Landed AFN", "Status"],
                 [["GRN26-0008", "PO26-000012", "Istanbul Bridal Co.", "18 Sep", "107,068", ("Draft", MUTED)],
                  ["GRN26-0007", "PO26-000012", "Istanbul Bridal Co.", "09 Sep", "94,116", ("Posted", OK)],
                  ["GRN26-0006", "PO26-000015", "Kabul Textile Traders", "14 Sep", "148,000", ("Posted", OK)],
                  ["GRN26-0005", "PO26-000008", "Istanbul Bridal Co.", "16 Aug", "241,400", ("Posted", OK)]],
                 g, row_h=40, sheet=True,
                 widths=[1.2, 1.2, 1.8, 0.9, 1.1, 0.9])
    els += e
    return els


def _supplier_head(cx, cy, cw, g, active_tab, actions=None):
    els = [breadcrumb(cx, cy, ["Procurement", "Suppliers", "SUP26-0001"], g)]
    e, y = page_header(cx, cy + 18, cw, "Istanbul Bridal Co.",
                       actions=actions or [("＋ New PO", "primary"), ("Edit", "secondary")],
                       subtitle="SUP26-0001 · Active · USD · Net 30 · supplier since Feb 2026",
                       g=g)
    els += e
    e, y = tabs(cx, y, cw, SUPPLIER_TABS, SUPPLIER_TABS.index(active_tab), g)
    els += e
    return els, y


# ══════════════════════════════════════════════════════════════════
#  A. DASHBOARD
# ══════════════════════════════════════════════════════════════════

def _a1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "A1.  Procurement dashboard", "Procurement", g,
                                     sub_active="Purchase orders")
    e, y = page_header(cx, cy, cw, "Procurement",
                       actions=[("Receive goods", "secondary"), ("＋ New PO", "primary")],
                       subtitle="Main branch · September 2026 · AFN", g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Open POs", "5", INK, "3 ordered · 2 draft", ICON["truck"]),
        ("Awaiting receipt", "3", WARN, "1 delivery overdue", ICON["clock"]),
        ("Received this month", "6", OK, "GRNs posted", ICON["receipt"]),
        ("Total A/P", "745,308", ROSE, "AFN owed to suppliers", ICON["ledger"]),
        ("Overdue A/P", "118,000", DANGER, "Kabul Textile Traders", ICON["alert"]),
        ("Spend MTD", "782,640", INK, "+18% vs Aug", ICON["chart"]),
    ], g=G)
    els += e

    LW, RW = 716, 404
    rx = cx + LW + 16
    els += _lab(cx, y, "OPEN PURCHASE ORDERS", G)
    els.append(text(cx + LW - 90, y, "View all →", 11.5, ACCENT, "right", 90, G))
    e, ly = table(cx, y + 22, LW,
                  ["PO #", "Supplier", "Expected", "Total AFN", "Recv", "Status"],
                  [r[:1] + r[1:2] + r[3:4] + r[5:7] + r[9:10] for r in PO_ROWS[:5]],
                  G, row_h=40, sheet=True, widths=[1.15, 1.8, 0.95, 1.1, 0.7, 0.95])
    els += e
    e, _ = bar_chart(cx, ly + 4, LW, 168, "Purchase spend by month · AFN", [
        ("May", 0.34, "268k"), ("Jun", 0.51, "402k"), ("Jul", 0.43, "340k"),
        ("Aug", 0.85, "664k"), ("Sep", 1.0, "783k")], G)
    els += e

    els += _lab(rx, y, "QUICK ACTIONS", G)
    bw = (RW - 12) / 2
    els += btn(rx, y + 22, bw, 40, "New PO", "primary", G)
    els += btn(rx + bw + 12, y + 22, bw, 40, "Receive goods", "secondary", G)
    els += btn(rx, y + 70, bw, 40, "Pay supplier", "secondary", G)
    els += btn(rx + bw + 12, y + 70, bw, 40, "＋ Supplier", "secondary", G)

    els += _lab(rx, y + 126, "UPCOMING DELIVERIES", G)
    e, _ = table(rx, y + 148, RW, ["When", "PO · supplier", "Lines"], [
        [("14 Sep · overdue", DANGER), "PO26-000015 · Kabul", "5"],
        ["18 Sep", "PO26-000012 · Istanbul", "6"],
        ["21 Sep", "PO26-000013 · Dubai", "4"],
    ], G, row_h=38, widths=[1.3, 1.8, 0.6])
    els += e
    els += _lab(rx, y + 330, "OVERDUE PAYABLES", G, DANGER)
    e, _ = table(rx, y + 352, RW, ["Payable #", "Supplier", "Balance"], [
        ["AP26-0031", "Kabul Textile", ("88,000", DANGER)],
        ["AP26-0028", "Kabul Textile", ("30,000", DANGER)],
    ], G, row_h=36, widths=[1.1, 1.3, 0.9])
    els += e

    els += _spec(cx, ox, oy, cw,
                 "Read-only. Open POs = procurement_purchase_orders.status IN (draft, ordered, partial_received). "
                 "Total A/P = SUM(finance_payables.balance_amount) — never from the PO cache. "
                 "＋ New PO and ＋ Supplier open drawers over their lists, they do not open extra pages.")
    return els


# ══════════════════════════════════════════════════════════════════
#  B. SUPPLIERS
# ══════════════════════════════════════════════════════════════════

def _b1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B1.  Suppliers list", "Procurement", g,
                                     sub_active="Suppliers")
    e, y = page_header(cx, cy, cw, "Suppliers",
                       actions=[("Export", "ghost"), ("＋ New supplier", "primary")],
                       subtitle="6 suppliers · 2 with overdue balances", g=G)
    els += e
    e, y = _sheet_bar(cx, y, cw, G, "Search name, code, phone or contact…")
    els += e
    els += filter_chips(cx, y, ["All", "Active", "Inactive", "Has open PO", "Overdue A/P"], 0, G)
    y += 42
    e, y = table(cx, y, cw,
                 ["Code", "Name", "Contact person", "Phone", "Curr.", "Terms", "Open POs",
                  "A/P balance AFN", "Status"],
                 SUPPLIER_ROWS, G, row_h=44, sheet=True,
                 widths=[0.95, 1.55, 1.3, 1.25, 0.55, 0.75, 0.75, 1.15, 0.8])
    els += e
    e, y = pagination(cx, y, cw, "1–6 of 6 suppliers", G)
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Reads procurement_suppliers LEFT JOIN finance_payables (balance) and procurement_purchase_orders (open PO count). "
                 "This page NEVER shows a form. ＋ New supplier and row Edit open B2 / B3 drawers — the list stays behind. "
                 "Filter, sort and column picker live inside the table header, like a sheet.")
    return els


def _b2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B2.  New supplier — drawer over the list",
                                     "Procurement", g, sub_active="Suppliers")
    els += _suppliers_backdrop(cx, cy, cw, G)
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New supplier",
                            side="right", width=460,
                            subtitle="Minimum fields to buy from this house", g=G)
    els += de
    half = (fw - 16) / 2
    e, fy = field(fx, fy, fw, "Supplier name", "Istanbul Bridal Co.", G, True)
    els += e
    e, _ = field(fx, fy, half, "Supplier code", "SUP26-0007 (auto)", G)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Status", "Active", G)
    els += e
    e, _ = field(fx, fy, half, "Contact person", "Elif Demir", G)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Phone", "+90 532 441 8820", G, True)
    els += e
    e, fy = field(fx, fy, fw, "Email", "elif@istanbulbridal.com", G)
    els += e
    e, fy = textarea(fx, fy, fw, "Address", "Nişantaşı Mah. No 44, Istanbul, Türkiye", G, rows=2)
    els += e
    e, _ = select(fx, fy, half, "Payment term", "Net 30", G, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Currency", "USD", G, True)
    els += e
    e, fy = textarea(fx, fy, fw, "Note", "Ships via Kabul customs broker", G, rows=2)
    els += e
    els += note(fx, fy, fw, "Opening A/P is not entered here — create a payable in Finance.", INFO, G)
    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, half, 44, "Cancel", "secondary", G)
    els += btn(fx + half + 16, by, half, 44, "Save supplier", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "INSERT procurement_suppliers. supplier_code is generated (SUP26-nnnn). "
                 "No balance is written — the ledger stays the single source of truth.")
    return els


def _b3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B3.  Edit supplier — same drawer, code locked",
                                     "Procurement", g, sub_active="Suppliers")
    els += _suppliers_backdrop(cx, cy, cw, G)
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Edit supplier · SUP26-0001",
                            side="right", width=460,
                            subtitle="Istanbul Bridal Co. · code cannot change once used on a PO", g=G)
    els += de
    half = (fw - 16) / 2
    e, fy = field(fx, fy, fw, "Supplier name", "Istanbul Bridal Co.", G, True)
    els += e
    els.append(rect(fx, fy, fw, 52, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=G))
    els.append(text(fx + 12, fy + 8, "Supplier code", 11, MUTED, width=fw - 40, g=G))
    els.append(text(fx + 12, fy + 26, "SUP26-0001", 13, INK, width=fw - 40, g=G))
    els.append(text(fx + fw - 28, fy + 18, ICON["lock"], 12, FAINT, g=G))
    fy += 64
    e, fy = select(fx, fy, fw, "Status", "Active", G)
    els += e
    e, _ = field(fx, fy, half, "Contact person", "Elif Demir", G)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Phone", "+90 532 441 8820", G, True)
    els += e
    e, fy = field(fx, fy, fw, "Email", "elif@istanbulbridal.com", G)
    els += e
    e, _ = select(fx, fy, half, "Payment term", "Net 30", G, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Currency", "USD", G, True)
    els += e
    els += note(fx, fy, fw, "Inactive suppliers cannot be chosen on a new PO.", WARN, G)
    fy += 62
    els += btn(fx, fy, half, 44, "Cancel", "secondary", G)
    els += btn(fx + half + 16, fy, half, 44, "Save changes", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "UPDATE procurement_suppliers. supplier_code is locked — 7 POs already point at it. "
                 "Currency change affects FUTURE POs only; posted documents keep their snapshot.")
    return els


def _b4(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B4.  Supplier profile · Overview",
                                     "Procurement", g, sub_active="Suppliers")
    e, y = _supplier_head(cx, cy, cw, G, "Overview",
                          [("Record payment", "secondary"), ("＋ New PO", "primary")])
    els += e
    pw, RW = 340, cw - 364
    rx = cx + 364
    els += _panel(cx, y, pw, 268, "PROFILE", G)
    e, _ = _kvr(cx + 16, y + 48, pw - 32, [
        ("Contact person", "Elif Demir"),
        ("Phone", "+90 532 441 8820"),
        ("Email", "elif@istanbulbridal.com"),
        ("Address", "Nişantaşı, Istanbul, TR"),
        ("Payment term", "Net 30"),
        ("Currency", (RATE, INFO)),
        ("Created by", "Ahmad Zaki · 12 Feb 2026"),
    ], G, step=26)
    els += e
    els += _panel(cx, y + 284, pw, 200, "A/P — finance_payables", G, VIOLET_BG, VIOLET)
    e, _ = money_row(cx + 16, y + 324, pw - 32, [
        ("Open payables (2)", "AFN 332,388.00"),
        ("Current (not due)", "AFN 107,068.00"),
        ("1–30 days", "AFN 225,320.00"),
        ("Overdue 30+", "AFN 0.00"),
    ], G, total=("Balance owed", "AFN 332,388.00"))
    els += e

    els += _lab(rx, y, "RECENT ACTIVITY", G)
    e, ry = table(rx, y + 22, RW,
                  ["When", "Document", "What happened", "AFN"],
                  [["18 Sep", "GRN26-0008", "Goods received · 36 units", "107,068"],
                   ["12 Sep", "SPAY26-0014", "Payment out", ("−120,000", OK)],
                   ["09 Sep", "GRN26-0007", "Goods received · 6 units", "94,116"],
                   ["04 Sep", "PO26-000012", "Order placed", "345,320"]],
                  G, row_h=40, sheet=True, widths=[0.8, 1.2, 2.2, 1.0])
    els += e
    els += _lab(rx, ry + 4, "ON-TIME DELIVERY", G)
    e, _ = table(rx, ry + 26, RW, ["Last 12 months", "POs", "On time", "Late", "Fill %"],
                 [["Istanbul Bridal Co.", "7", "5", "2", ("71%", WARN)]],
                 G, row_h=40, widths=[1.8, 0.7, 0.8, 0.7, 0.8])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Reads procurement_suppliers + last documents + finance_payables aging. "
                 "The supplier row itself never stores a balance. Other tabs (B5–B9) complete the profile.")
    return els


def _b5(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B5.  Supplier profile · Purchase orders",
                                     "Procurement", g, sub_active="Suppliers")
    e, y = _supplier_head(cx, cy, cw, G, "Purchase orders",
                          [("＋ New PO", "primary")])
    els += e
    e, y = _sheet_bar(cx, y, cw, G, "Search this supplier's POs…")
    els += e
    e, y = table(cx, y, cw,
                 ["PO #", "Order date", "Expected", "Lines", "Total AFN", "Recv", "Paid", "Balance", "Status"],
                 [["PO26-000012", "04 Sep 2026", "18 Sep", "6", "345,320", ("60%", WARN),
                   "120,000", ("225,320", ROSE), ("Partial", WARN)],
                  ["PO26-000008", "02 Aug 2026", "16 Aug", "5", "241,400", ("100%", OK),
                   "241,400", "0.00", ("Closed", MUTED)],
                  ["PO26-000004", "19 Jun 2026", "03 Jul", "4", "198,700", ("100%", OK),
                   "198,700", "0.00", ("Closed", MUTED)]],
                 G, row_h=42, sheet=True,
                 widths=[1.15, 1.1, 0.9, 0.6, 1.05, 0.7, 1.0, 1.1, 0.9])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "READS procurement_purchase_orders WHERE supplier_id = this row. "
                 "Row click → C3 PO detail. ＋ New PO opens the C2 drawer with this supplier pre-filled.")
    return els


def _b6(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B6.  Supplier profile · Receipts",
                                     "Procurement", g, sub_active="Suppliers")
    e, y = _supplier_head(cx, cy, cw, G, "Receipts")
    els += e
    e, y = table(cx, y, cw,
                 ["GRN #", "PO #", "Date", "Warehouse", "Lines", "Landed AFN", "New SKUs", "Status"],
                 [["GRN26-0008", "PO26-000012", "18 Sep 2026", "Main store", "4", "107,068",
                   ("2", VIOLET), ("Draft", MUTED)],
                  ["GRN26-0007", "PO26-000012", "09 Sep 2026", "Main store", "2", "94,116",
                   "0", ("Posted", OK)],
                  ["GRN26-0005", "PO26-000008", "16 Aug 2026", "Main store", "5", "241,400",
                   "0", ("Posted", OK)]],
                 G, row_h=42, sheet=True,
                 widths=[1.15, 1.15, 1.1, 1.1, 0.6, 1.1, 0.85, 0.9])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "READS procurement_receipts for this supplier. Landed AFN is SUM(landed_unit_cost × qty) — "
                 "the same number that hit inventory. Draft rows can still be posted from D2.")
    return els


def _b7(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B7.  Supplier profile · Payments",
                                     "Procurement", g, sub_active="Suppliers")
    e, y = _supplier_head(cx, cy, cw, G, "Payments",
                          [("Record payment", "primary")])
    els += e
    e, y = table(cx, y, cw,
                 ["Payment #", "Date", "Method", "Account", "Allocated to", "Amount AFN", "Status"],
                 [["SPAY26-0014", "12 Sep 2026", "Cash", "Cash drawer — Main", "AP26-0039",
                   "120,000.00", ("Posted", OK)],
                  ["SPAY26-0009", "18 Aug 2026", "Bank transfer", "Azizi Bank", "AP26-0021",
                   "241,400.00", ("Posted", OK)],
                  ["SPAY26-0004", "02 Jul 2026", "Cash", "Cash drawer — Main", "AP26-0014",
                   "198,700.00", ("Posted", OK)]],
                 G, row_h=42, sheet=True,
                 widths=[1.2, 1.1, 1.1, 1.5, 1.0, 1.15, 0.85])
    els += e
    e, _ = money_row(cx + cw - 380, y, 380, [
        ("Paid this year", "AFN 560,100.00"),
        ("Open A/P", "AFN 332,388.00"),
    ], G, total=("Lifetime paid", "AFN 1,142,400.00"))
    els += e
    els += _spec(cx, ox, oy, cw,
                 "READS procurement_supplier_payments + finance_transactions. "
                 "Record payment opens the E1 drawer with this supplier's open payables pre-ticked.")
    return els


def _b8(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B8.  Supplier profile · Items supplied",
                                     "Procurement", g, sub_active="Suppliers")
    e, y = _supplier_head(cx, cy, cw, G, "Items supplied")
    els += e
    e, y = table(cx, y, cw,
                 ["SKU", "Item", "Times bought", "Qty received", "Last unit cost", "Last landed", "Last GRN"],
                 [["BD-AL-0114", "White A-Line Gown", "4", "16", "USD 185.00", ("14,499.00", ACCENT), "GRN26-0008"],
                  ["BD-BG-0077", "Ivory Ball Gown", "3", "10", "USD 240.00", ("18,810.00", ACCENT), "GRN26-0008"],
                  ["AC-VL-0308", "Chantilly Veil (ivory)", "1", "12", "USD 28.00", ("2,194.92", ACCENT), "GRN26-0008"],
                  ["AC-HC-0309", "Pearl Hair Comb", "1", "20", "USD 9.00", ("705.55", ACCENT), "GRN26-0008"]],
                 G, row_h=42, sheet=True,
                 widths=[1.1, 1.9, 1.0, 1.05, 1.15, 1.15, 1.1])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Derived from procurement_receipt_items GROUP BY inventory_item_id for this supplier. "
                 "Last landed is what moved the weighted average cost.")
    return els


def _b9(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B9.  Supplier profile · Price history",
                                     "Procurement", g, sub_active="Suppliers")
    e, y = _supplier_head(cx, cy, cw, G, "Price history")
    els += e
    els += _lab(cx, y, "WHITE A-LINE GOWN · BD-AL-0114", G)
    e, y = table(cx, y + 20, cw,
                 ["Document", "Date", "Qty", "Unit cost USD", "Unit cost AFN", "Landed unit AFN", "Change"],
                 [["PO26-000004 · GRN26-0002", "21 Jun 2026", "4", "172.00", "12,212.00", "12,470.00", ("—", FAINT)],
                  ["PO26-000008 · GRN26-0005", "16 Aug 2026", "6", "178.00", "12,638.00", "13,010.00", ("+4.3%", WARN)],
                  ["PO26-000012 · GRN26-0007", "09 Sep 2026", "4", "185.00", "13,172.00", "13,860.00", ("+6.5%", WARN)],
                  ["PO26-000012 · GRN26-0008", "18 Sep 2026", "2", "185.00", "13,172.00", ("14,499.00", ACCENT), ("+4.6%", DANGER)]],
                 G, row_h=40, sheet=True,
                 widths=[1.8, 1.1, 0.55, 1.1, 1.15, 1.25, 0.8])
    els += e
    e, _ = bar_chart(cx, y, cw, 180, "Landed unit cost over time · AFN", [
        ("Jun", 0.86, "12.5k"), ("Aug", 0.90, "13.0k"), ("09 Sep", 0.96, "13.9k"),
        ("18 Sep", 1.0, "14.5k")], G)
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Price history = procurement_receipt_items per inventory_item_id, newest last. "
                 "The landed column is what drives WAC. Pick another item from B8 to swap this chart.")
    return els


# ══════════════════════════════════════════════════════════════════
#  C. PURCHASE ORDERS
# ══════════════════════════════════════════════════════════════════

def _c1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C1.  Purchase orders list", "Procurement", g,
                                     sub_active="Purchase orders")
    e, y = page_header(cx, cy, cw, "Purchase orders",
                       actions=[("Export", "ghost"), ("＋ New PO", "primary")],
                       subtitle="September 2026 · all branches", g=G)
    els += e
    e, y = _sheet_bar(cx, y, cw, G, "Search PO number, supplier or item…")
    els += e
    els += filter_chips(cx, y, ["All", "Draft", "Ordered", "Partial", "Received", "Cancelled"], 0, G)
    y += 42
    e, y = table(cx, y, cw,
                 ["PO #", "Supplier", "Date", "Expected", "Lines", "Total AFN", "Received",
                  "Paid", "Balance", "Status"],
                 PO_ROWS, G, row_h=42, sheet=True,
                 widths=[1.15, 1.55, 0.8, 0.85, 0.6, 1.05, 0.85, 0.95, 1.0, 0.95])
    els += e
    e, y = pagination(cx, y, cw, "1–6 of 23 purchase orders", G)
    els += e
    els += _spec(cx, ox, oy, cw,
                 "No approval column — a draft is placed with Place order on C3. "
                 "＋ New PO opens the C2 drawer over this list. Received % is recomputed from receipts.")
    return els


def _c2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C2.  New purchase order — drawer over the list",
                                     "Procurement", g, sub_active="Purchase orders")
    els += _po_backdrop(cx, cy, cw, G)
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New purchase order",
                            side="right", width=640,
                            subtitle="Draft · PO26-000016 · nothing is ordered until you Place order", g=G)
    els += de
    half = (fw - 16) / 2
    e, _ = select(fx, fy, half, "Supplier", "Istanbul Bridal Co. (USD)", G, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Receive into", "Main store — Kabul", G, True)
    els += e
    e, _ = field(fx, fy, half, "Order date", "12 Sep 2026", G, True)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Expected delivery", "26 Sep 2026", G)
    els += e
    els.append(text(fx, fy, f"Currency snapshot  {RATE}  ·  taken from the supplier, locked on Place order",
                    11, MUTED, width=fw, g=G))
    fy += 22
    els += _lab(fx, fy, "LINES — search an item, or type a new name", G)
    fy += 18
    e, fy = table(fx, fy, fw,
                  ["Item", "Qty", "Unit USD", "Line AFN", ""],
                  [["White A-Line Gown", "6", "185.00", "79,032", ("✕", FAINT)],
                   ["Ivory Ball Gown", "4", "240.00", "68,352", ("✕", FAINT)],
                   [("Chantilly Veil — NEW", VIOLET), "12", "28.00", "23,923", ("✕", FAINT)]],
                  G, row_h=36, widths=[2.4, 0.6, 0.9, 1.0, 0.35])
    els += e
    els.append(rect(fx, fy, fw, 36, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=G))
    els.append(text(fx + 12, fy + 10, f"{ICON['add']}  Add line", 12, MUTED, width=fw - 24, g=G))
    fy += 48
    e, fy = field(fx, fy, fw, "Shipping & customs (USD) — split across lines when you receive",
                  "137.64", G)
    els += e
    e, fy = money_row(fx, fy, fw, [
        ("Subtotal", "USD 2,586.00"),
        ("Shipping & customs", "USD 137.64"),
    ], G, total=("PO total", "USD 2,723.64  ·  AFN 194,011"))
    els += e
    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, 130, 44, "Cancel", "secondary", G)
    els += btn(fx + fw - 280, by, 130, 44, "Save draft", "secondary", G)
    els += btn(fx + fw - 140, by, 140, 44, "Place order", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "Save draft / Place order → INSERT procurement_purchase_orders + items. "
                 "NO approval step. Place order writes status='ordered' immediately. "
                 "A free-text line keeps inventory_item_id NULL until the GRN creates the item.")
    return els


def _c3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C3.  Purchase order detail",
                                     "Procurement", g, sub_active="Purchase orders")
    e, y = page_header(cx, cy, cw, "PO26-000012",
                       actions=[("Print", "ghost"), ("Record payment", "secondary"),
                                ("Receive goods", "primary")],
                       subtitle="Istanbul Bridal Co. · ordered 04 Sep 2026 · USD @ 71.20 AFN · expected 18 Sep",
                       g=G)
    els += e
    e, y = timeline(cx, y, cw, [
        ("Draft", "done"), ("Ordered", "done"), ("Partially received", "current"),
        ("Received", "todo"), ("Paid", "todo"),
    ], G)
    els += e
    e, y = table(cx, y, cw,
                 ["Line", "SKU", "Ordered", "Received", "Remaining", "Unit USD", "Landed AFN", "Status"],
                 [["White A-Line Gown", "BD-AL-0114", "6", "4", ("2", WARN), "185.00", "13,860.00", ("Partial", WARN)],
                  ["Ivory Ball Gown", "BD-BG-0077", "4", "2", ("2", WARN), "240.00", "18,120.00", ("Partial", WARN)],
                  ["Chantilly Veil (ivory)", ("on receipt", VIOLET), "12", "0", ("12", DANGER),
                   "28.00", "—", ("Pending", MUTED)],
                  ["Pearl Hair Comb", ("on receipt", VIOLET), "20", "0", ("20", DANGER),
                   "9.00", "—", ("Pending", MUTED)]],
                 G, row_h=40, sheet=True,
                 widths=[1.8, 1.2, 0.7, 0.8, 0.9, 0.9, 1.1, 0.85])
    els += e
    hw = (cw - 24) / 2
    els += _lab(cx, y, "RECEIPTS", G)
    e, _ = table(cx, y + 20, hw, ["GRN #", "Date", "Landed", "Status"],
                 [["GRN26-0007", "09 Sep", "94,116", ("Posted", OK)],
                  ["GRN26-0008", "18 Sep", "107,068", ("Draft", MUTED)]],
                 G, row_h=36, widths=[1.2, 1.0, 1.1, 0.9])
    els += e
    els += _lab(cx + hw + 24, y, "PAYMENTS & A/P", G)
    e, ry = table(cx + hw + 24, y + 20, hw, ["Doc #", "Date", "Amount", "Type"],
                  [["AP26-0039", "09 Sep", "94,116", ("Payable opened", ROSE)],
                   ["SPAY26-0014", "12 Sep", "120,000", ("Payment out", OK)]],
                  G, row_h=36, widths=[1.2, 0.9, 1.0, 1.3])
    els += e
    e, _ = money_row(cx + hw + 24, ry, hw, [
        ("PO total", "AFN 345,320.00"),
        ("Paid to date", "AFN 120,000.00"),
    ], G, total=("Balance", "AFN 225,320.00"))
    els += e
    els += _spec(cx, ox, oy, cw,
                 "No approval. Draft POs show Place order instead of Receive goods. "
                 "Balance is DERIVED from finance_payables. Cancel is hidden once a posted receipt exists — use a debit note.")
    return els


# ══════════════════════════════════════════════════════════════════
#  D. RECEIVING
# ══════════════════════════════════════════════════════════════════

def _d1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D1.  Receipts list", "Procurement", g,
                                     sub_active="Receipts (GRN)")
    e, y = page_header(cx, cy, cw, "Receipts (GRN)",
                       actions=[("Export", "ghost"), ("Receive goods", "primary")],
                       subtitle="Posted receipts cannot be edited — void only", g=G)
    els += e
    e, y = _sheet_bar(cx, y, cw, G, "Search GRN, PO or supplier…")
    els += e
    els += filter_chips(cx, y, ["All", "Draft", "Posted", "Void"], 0, G)
    y += 42
    e, y = table(cx, y, cw,
                 ["GRN #", "PO #", "Supplier", "Date", "Lines", "Landed AFN", "New SKUs", "Status"],
                 [["GRN26-0008", "PO26-000012", "Istanbul Bridal Co.", "18 Sep", "4", "107,068",
                   ("2", VIOLET), ("Draft", MUTED)],
                  ["GRN26-0007", "PO26-000012", "Istanbul Bridal Co.", "09 Sep", "2", "94,116",
                   "0", ("Posted", OK)],
                  ["GRN26-0006", "PO26-000015", "Kabul Textile Traders", "14 Sep", "5", "148,000",
                   "0", ("Posted", OK)],
                  ["GRN26-0005", "PO26-000008", "Istanbul Bridal Co.", "16 Aug", "5", "241,400",
                   "0", ("Posted", OK)]],
                 G, row_h=42, sheet=True,
                 widths=[1.15, 1.15, 1.7, 0.9, 0.6, 1.1, 0.9, 0.9])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Receive goods opens the D2 drawer over this list. "
                 "You cannot type a receive qty higher than remaining on the PO — the input is capped.")
    return els


def _d2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D2.  Receive goods — drawer over the list",
                                     "Procurement", g, sub_active="Receipts (GRN)")
    els += _receipts_backdrop(cx, cy, cw, G)
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Receive goods · GRN26-0008",
                            side="right", width=680,
                            subtitle="Against PO26-000012 · Istanbul Bridal Co. · draft — stock has not moved",
                            g=G)
    els += de
    half = (fw - 16) / 2
    e, _ = select(fx, fy, half, "Purchase order", "PO26-000012 · Istanbul Bridal", G, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Warehouse", "Main store — Kabul", G, True)
    els += e
    e, _ = field(fx, fy, half, "Received date", "18 Sep 2026", G, True)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Supplier invoice no.", "IST-2026-4471", G)
    els += e
    els.append(text(fx, fy, f"PO currency USD · rate {RATE} — costs below post in AFN",
                    11, MUTED, width=fw, g=G))
    fy += 20
    e, fy = table(fx, fy, fw,
                  ["Item", "Left", "Recv now", "Unit cost", "Landed"],
                  [["White A-Line Gown", "2", "2", "13,172", ("14,499", ACCENT)],
                   ["Ivory Ball Gown", "2", "2", "17,088", ("18,810", ACCENT)],
                   [("Chantilly Veil · NEW", VIOLET), "12", "12", "1,994", ("2,195", ACCENT)],
                   [("Pearl Hair Comb · NEW", VIOLET), "20", "20", "641", ("706", ACCENT)]],
                  G, row_h=36, widths=[2.1, 0.6, 0.8, 0.95, 0.9])
    els += e
    els += note(fx, fy, fw,
                "Recv now cannot exceed Left. Two NEW lines need a name, category and prices (D3) before Post.",
                VIOLET, G)
    fy += 58
    e, fy = field(fx, fy, fw, "Shipping & customs AFN — split automatically by line value",
                  "9,800.00", G)
    els += e
    e, fy = money_row(fx, fy, fw, [
        ("Goods", "AFN 97,268"),
        ("Shipping & customs", "AFN 9,800"),
    ], G, total=("Landed → inventory", "AFN 107,068"))
    els += e
    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, 140, 44, "Save draft", "secondary", G)
    els += btn(fx + fw - 160, by, 160, 44, "Post receipt", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "Post: procurement_receipts + items (landed_unit_cost stored) → stock_in at landed cost → "
                 "WAC recompute → open finance_payables. Over-receipt is blocked by the qty cap — no extra approval.")
    return els


def _d3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D3.  New item on receipt — drawer",
                                     "Procurement", g, sub_active="Receipts (GRN)")
    els += _receipts_backdrop(cx, cy, cw, G)
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New item — line 3",
                            side="right", width=470,
                            subtitle="Free-text PO line “Chantilly Veil (ivory)” · SKU is issued on post",
                            g=G)
    els += de
    half = (fw - 16) / 2
    e, fy = field(fx, fy, fw, "Item name", "Chantilly Veil (ivory)", G, True)
    els += e
    e, _ = select(fx, fy, half, "Main category", "Accessories", G, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Sub category", "Veils", G, True)
    els += e
    e, _ = select(fx, fy, half, "Size", "One size", G)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Colour", "Ivory", G)
    els += e
    e, _ = field(fx, fy, half, "Sale price AFN", "4,500.00", G)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Rental price AFN", "1,200.00", G)
    els += e
    els.append(rect(fx, fy, fw, 78, strokeColor=HAIRLINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=G))
    els.append(text(fx + 16, fy + 12, "SKU preview — generated on post · barcode and QR follow from it",
                    11, MUTED, width=fw - 32, g=G))
    c, _ = chip(fx + 16, fy + 36, "AC-VL-0308", VIOLET, g=G, size=13)
    els += c
    fy += 92
    els += note(fx, fy, fw, "Landed unit cost 2,194.92 is locked from the GRN line.", ACCENT, G)
    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, half, 44, "Back", "secondary", G)
    els += btn(fx + half + 16, by, half, 44, "Save & continue", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "Runs ON POST for every PO line whose inventory_item_id IS NULL. "
                 "INSERT inventory_items then back-fill the PO line. Cancelling the drawer cancels the whole post.")
    return els


def _d4(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D4.  Receipt posted — stock, cost & payable",
                                     "Procurement", g, sub_active="Receipts (GRN)")
    e, y = page_header(cx, cy, cw, "GRN26-0008 posted",
                       actions=[("View stock ledger", "secondary"), ("Void receipt", "danger")],
                       subtitle="PO26-000012 · Istanbul Bridal Co. · 18 Sep 2026 14:22 by Ahmad Zaki", g=G)
    els += e
    els.append(rect(cx, y, cw, 56, strokeColor=OK, backgroundColor=OK_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 20, y + 18,
                    f"{ICON['check']}  36 units in · landed AFN 107,068 · 2 new SKUs · payable AP26-0042 opened",
                    14, OK, width=cw - 40, g=G))
    y += 72
    e, y = table(cx, y, cw,
                 ["Txn #", "Item · SKU", "Type", "Qty", "Landed unit", "Value AFN", "WAC after"],
                 [["TRN26-000418", "White A-Line Gown · BD-AL-0114", ("stock_in", OK), "+2",
                   "14,499.00", "28,998.00", "14,071.14"],
                  ["TRN26-000419", "Ivory Ball Gown · BD-BG-0077", ("stock_in", OK), "+2",
                   "18,810.00", "37,620.00", "18,444.00"],
                  ["TRN26-000420", "Chantilly Veil · AC-VL-0308", ("stock_in", OK), "+12",
                   "2,194.92", "26,339.00", ("new · 2,194.92", VIOLET)],
                  ["TRN26-000421", "Pearl Hair Comb · AC-HC-0309", ("stock_in", OK), "+20",
                   "705.55", "14,111.00", ("new · 705.55", VIOLET)]],
                 G, row_h=40, sheet=True,
                 widths=[1.25, 2.4, 0.9, 0.55, 1.15, 1.1, 1.4])
    els += e
    tw = (cw - 24) / 2
    els += _panel(cx, y, tw, 140, "New items created", G)
    e, _ = _kvr(cx + 16, y + 44, tw - 32, [
        ("Chantilly Veil (ivory)", ("AC-VL-0308", VIOLET)),
        ("Pearl Hair Comb", ("AC-HC-0309", VIOLET)),
        ("Opening WAC", "= landed unit cost"),
    ], G, step=26)
    els += e
    els += _panel(cx + tw + 24, y, tw, 140, "Payable opened", G, ROSE_BG, ROSE)
    e, _ = _kvr(cx + tw + 40, y + 44, tw - 32, [
        ("Payable #", ("AP26-0042", ROSE)),
        ("Amount", "AFN 107,068.00"),
        ("Due", "Net 30 · 18 Oct 2026"),
    ], G, step=26)
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Confirmation of one atomic post. Posted receipts are IMMUTABLE — Void writes reversing stock and a reversing payable. Never Edit.",
                 OK)
    return els


# ══════════════════════════════════════════════════════════════════
#  E. PAY & RETURN
# ══════════════════════════════════════════════════════════════════

def _e1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "E1.  Pay supplier — drawer",
                                     "Procurement", g, sub_active="Suppliers")
    e, y = page_header(cx, cy, cw, "Istanbul Bridal Co.",
                       actions=[("Record payment", "primary")],
                       subtitle="SUP26-0001 · A/P balance AFN 332,388.00", g=G)
    els += e
    e, _ = table(cx, y, cw - 500,
                 ["Payable #", "PO #", "Due", "Balance"],
                 [["AP26-0039", "PO26-000012", "09 Oct", ("225,320", ROSE)],
                  ["AP26-0042", "PO26-000012", "18 Oct", ("107,068", ROSE)]],
                 G, row_h=42, sheet=True, widths=[1.2, 1.2, 0.9, 1.1])
    els += e
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Pay supplier",
                            side="right", width=460,
                            subtitle="SPAY26-0015 · Istanbul Bridal Co.", g=G)
    els += de
    e, fy = field(fx, fy, fw, "Amount AFN", "80,000.00", G, True)
    els += e
    e, fy = select(fx, fy, fw, "Pay from account", "Cash drawer — Main branch", G, True)
    els += e
    e, fy = select(fx, fy, fw, "Payment method", "Cash", G, True)
    els += e
    e, fy = field(fx, fy, fw, "Paid at", "20 Sep 2026 11:40", G, True)
    els += e
    els += _lab(fx, fy, "ALLOCATE TO OPEN PAYABLES", G)
    fy += 18
    e, fy = table(fx, fy, fw, ["", "Payable", "Balance", "Allocate"],
                  [[("✓", ACCENT), "AP26-0039", "225,320", ("50,000", ACCENT)],
                   [("✓", ACCENT), "AP26-0042", "107,068", ("30,000", ACCENT)]],
                  G, row_h=36, widths=[0.4, 1.2, 1.1, 1.1])
    els += e
    e, fy = money_row(fx, fy, fw, [
        ("Payment", "AFN 80,000"),
        ("Allocated", ("AFN 80,000", OK)),
    ], G, total=("A/P after", "AFN 252,388"))
    els += e
    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, fw, 44, "Post payment", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "INSERT procurement_supplier_payments + finance_transactions OUT, then reduce each allocated payable. "
                 "Unallocated money cannot post.")
    return els


def _e2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "E2.  Supplier return — drawer",
                                     "Procurement", g, sub_active="Receipts (GRN)")
    els += _receipts_backdrop(cx, cy, cw, G)
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Supplier return · DN26-0003",
                            side="right", width=560,
                            subtitle="Against GRN26-0008 · Istanbul Bridal Co.", g=G)
    els += de
    e, fy = select(fx, fy, fw, "Reason", "Faulty — damaged beading", G, True)
    els += e
    e, fy = table(fx, fy, fw, ["", "Item", "Return", "Credit AFN"],
                  [[("☐", FAINT), "White A-Line Gown", "0", "0.00"],
                   [("✓", ACCENT), "Ivory Ball Gown", ("1", ACCENT), ("18,810", ROSE)]],
                  G, row_h=38, widths=[0.35, 2.2, 0.7, 1.1])
    els += e
    e, fy = textarea(fx, fy, fw, "Note", "Beading torn — supplier agreed credit, WhatsApp Elif 21 Sep.",
                     G, rows=2)
    els += e
    els += _panel(fx, fy, fw, 96, "On post", G)
    els.append(text(fx + 16, fy + 44,
                    "Stock out −1 at landed cost 18,810  ·  payable AP26-0042  107,068 → 88,258",
                    12, MUTED, width=fw - 32, g=G))
    by = oy + TITLE_H + DESK_H - 68
    half = (fw - 16) / 2
    els += btn(fx, by, half, 44, "Cancel", "secondary", G)
    els += btn(fx + half + 16, by, half, 44, "Post debit note", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "INSERT procurement_returns + stock_out at landed cost + reduce finance_payables. "
                 "Never edits the original receipt.")
    return els


# ══════════════════════════════════════════════════════════════════
#  F. REPORTS
# ══════════════════════════════════════════════════════════════════

def _report_tiles(x, y, w, active, g):
    tiles = [("Purchase register", ICON["receipt"], "Spend by supplier"),
             ("Stock-in report", ICON["inventory"], "Every unit that came in"),
             ("Supplier aging", ICON["ledger"], "A/P buckets")]
    n = len(tiles)
    tw = (w - 16 * (n - 1)) / n
    els = []
    for i, (name, icon, sub) in enumerate(tiles):
        on = i == active
        tx = x + i * (tw + 16)
        els.append(rect(tx, y, tw, 72, strokeColor=ACCENT if on else HAIRLINE,
                        backgroundColor=ACCENT_BG if on else BG, strokeWidth=2 if on else 1, groupIds=g))
        els.append(text(tx + 14, y + 12, icon, 14, ACCENT if on else MUTED, g=g))
        els.append(text(tx + 14, y + 34, name, 13, ACCENT if on else INK, width=tw - 28, g=g))
        els.append(text(tx + 14, y + 52, sub, 11, MUTED, width=tw - 28, g=g))
    return els, y + 88


def _f1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F1.  Purchase register", "Procurement", g,
                                     sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Procurement reports",
                       actions=[("Export CSV", "secondary"), ("Print", "ghost")],
                       subtitle="All figures in AFN at each document's rate snapshot", g=G)
    els += e
    e, y = _report_tiles(cx, y, cw, 0, G)
    els += e
    colw, gap = 266, 24
    e, y2 = field(cx, y, colw, "From", "01 Sep 2026", G, True)
    els += e
    e, _ = field(cx + colw + gap, y, colw, "To", "30 Sep 2026", G, True)
    els += e
    e, _ = select(cx + 2 * (colw + gap), y, colw, "Supplier", "All suppliers", G)
    els += e
    e, _ = select(cx + 3 * (colw + gap), y, colw, "Status", "All except draft", G)
    els += e
    y = y2
    lw = 560
    e, _ = bar_chart(cx, y, lw, 180, "Purchase spend by supplier · AFN", [
        ("Istanbul", 1.0, "345k"), ("Dubai", 0.59, "203k"), ("Kabul", 0.43, "148k"),
        ("Herat", 0.25, "86k")], G)
    els += e
    els += _panel(cx + lw + 24, y, cw - lw - 24, 180, "Period totals", G)
    e, _ = money_row(cx + lw + 40, y + 48, cw - lw - 56, [
        ("Ordered", "AFN 782,640"),
        ("Received (landed)", "AFN 601,668"),
        ("Paid", "AFN 268,000"),
    ], G, total=("Outstanding A/P", "AFN 514,640"))
    els += e
    y += 196
    e, y = table(cx, y, cw,
                 ["PO #", "Supplier", "Date", "Total AFN", "Received", "Paid AFN", "Balance", "Status"],
                 [["PO26-000012", "Istanbul Bridal Co.", "04 Sep", "345,320", ("60%", WARN),
                   "120,000", ("225,320", ROSE), ("Partial", WARN)],
                  ["PO26-000013", "Dubai Fashion House", "07 Sep", "202,920", ("0%", MUTED),
                   "0", ("202,920", ROSE), ("Ordered", INFO)],
                  ["PO26-000015", "Kabul Textile Traders", "09 Sep", "148,000", ("100%", OK),
                   "148,000", "0", ("Received", OK)],
                  [("TOTAL", INK), "", "", ("782,640", INK), "", ("268,000", INK),
                   ("514,640", ROSE), ""]],
                 G, row_h=36, sheet=True,
                 widths=[1.15, 1.7, 0.8, 1.1, 0.85, 1.05, 1.1, 0.9])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Purchase register = POs in the period × exchange_rate. Received value uses landed_unit_cost so it ties to the stock-in report.")
    return els


def _f2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F2.  Stock-in report — by source",
                                     "Procurement", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Stock-in report",
                       actions=[("Export CSV", "secondary")],
                       subtitle="01–30 Sept 2026 · every positive stock movement", g=G)
    els += e
    e, y = _report_tiles(cx, y, cw, 1, G)
    els += e
    els += filter_chips(cx, y, ["All sources", "Purchase receipt", "Manual", "Sale return",
                                "Rental return", "Transfer in"], 0, G)
    y += 42
    lw = 500
    e, _ = bar_chart(cx, y, lw, 176, "Stock-in value by source · AFN", [
        ("Purchase", 1.0, "413k"), ("Manual", 0.23, "96k"), ("Sale ret.", 0.13, "53k"),
        ("Rental ret.", 0.2, "84k"), ("Transfer", 0.08, "32k")], G)
    els += e
    e, _ = table(cx + lw + 24, y, cw - lw - 24,
                 ["Source", "Txns", "Qty", "Value AFN"],
                 [["Purchase receipt", "6", "48", ("412,600", OK)],
                  ["Manual entry", "3", "12", "96,400"],
                  ["Sale return", "4", "4", "52,800"],
                  ["Rental return", "9", "9", "84,200"],
                  [("TOTAL", INK), ("24", INK), ("79", INK), ("678,000", INK)]],
                 G, row_h=32, widths=[1.7, 0.6, 0.6, 1.1])
    els += e
    y += 192
    e, y = table(cx, y, cw,
                 ["Date", "Txn #", "Source", "Document", "Item · SKU", "Qty", "Value AFN"],
                 [["18 Sep", "TRN26-000418", ("Purchase", OK), "GRN26-0008",
                   "White A-Line Gown · BD-AL-0114", "+2", "28,998"],
                  ["16 Sep", "TRN26-000411", ("Manual", VIOLET), "MSE26-0011",
                   "Satin Gloves · AC-GL-0045", "+10", "4,800"],
                  ["14 Sep", "TRN26-000402", ("Sale return", WARN), "SR26-0004",
                   "Blush Bridesmaid · BD-BM-0231", "+1", "6,840"],
                  ["12 Sep", "TRN26-000396", ("Rental return", INFO), "SO26-000017",
                   "Ivory Ball Gown · BD-BG-0077", "+1", "18,200"]],
                 G, row_h=36, sheet=True,
                 widths=[0.7, 1.2, 1.15, 1.1, 2.3, 0.5, 1.0])
    els += e
    els += note(cx, y, cw,
                "Opening 4,812,000 + in 678,000 − out 486,300 = closing 5,003,700 · variance 0.00 ✓", INFO, G)
    els += _spec(cx, ox, oy, cw,
                 "inventory_stock_transactions WHERE quantity > 0, grouped by reference_type. "
                 "Purchase rows valued at landed_unit_cost so this ties to F1.")
    return els


def _f3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F3.  Supplier ledger & aging",
                                     "Procurement", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Supplier ledger & aging",
                       actions=[("Export CSV", "secondary")],
                       subtitle="As at 30 Sept 2026 · buckets from finance_payables.due_date", g=G)
    els += e
    e, y = _report_tiles(cx, y, cw, 2, G)
    els += e
    e, y = table(cx, y, cw,
                 ["Supplier", "Open docs", "Current", "1–30 days", "31–60 days", "61–90", "Total A/P"],
                 [["Istanbul Bridal Co.", "2", "107,068", ("225,320", WARN), "0", "0", ("332,388", ROSE)],
                  ["Dubai Fashion House", "1", "202,920", "0", "0", "0", ("202,920", ROSE)],
                  ["Kabul Textile Traders", "2", "0", "0", ("88,000", DANGER), ("30,000", DANGER),
                   ("118,000", DANGER)],
                  [("TOTAL", INK), ("6", INK), ("309,988", INK), ("225,320", INK),
                   ("88,000", DANGER), ("30,000", DANGER), ("745,308", ROSE)]],
                 G, row_h=40, sheet=True,
                 widths=[1.8, 0.8, 1.1, 1.1, 1.1, 0.9, 1.2])
    els += e
    hw = (cw - 24) / 2
    els += _lab(cx, y, "PO FULFILMENT", G)
    e, _ = table(cx, y + 20, hw, ["PO #", "Ordered", "Received", "Fill %", "Late"],
                 [["PO26-000012", "65", "39", ("60%", WARN), "0"],
                  ["PO26-000013", "22", "0", ("0%", MUTED), "0"],
                  ["PO26-000015", "31", "31", ("100%", OK), ("6 d", DANGER)]],
                 G, row_h=36, sheet=True, widths=[1.3, 0.8, 0.9, 0.8, 0.8])
    els += e
    els += _lab(cx + hw + 24, y, "PRICE TREND — White A-Line Gown", G)
    e, _ = table(cx + hw + 24, y + 20, hw, ["GRN", "Date", "Landed", "Δ"],
                 [["GRN26-0005", "16 Aug", "13,010", ("+4.3%", WARN)],
                  ["GRN26-0007", "09 Sep", "13,860", ("+6.5%", WARN)],
                  ["GRN26-0008", "18 Sep", ("14,499", ACCENT), ("+4.6%", DANGER)]],
                 G, row_h=36, sheet=True, widths=[1.2, 0.9, 1.1, 0.8])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Aging from finance_payables only — this report and Finance A/P cannot disagree. "
                 "Fulfilment uses recomputed quantity_received.")
    return els


GROUPS = [
    ("DASHBOARD", [_a1]),
    ("SUPPLIERS", [_b1, _b2, _b3, _b4, _b5, _b6, _b7, _b8, _b9]),
    ("PURCHASE ORDERS", [_c1, _c2, _c3]),
    ("RECEIVING", [_d1, _d2, _d3, _d4]),
    ("PAY & RETURN", [_e1, _e2]),
    ("REPORTS", [_f1, _f2, _f3]),
]


def desktop():
    els = board_title(0, -230, "BOMS Desktop — Procurement",
                      "Read top to bottom: A Dashboard · B Suppliers (list → drawers → the six profile tabs) · "
                      "C Purchase orders · D Receiving · E Pay & return · F Reports.\n"
                      "No PO approval · every create/edit is a drawer over its list · language switcher shows English / دری / پښتو only · "
                      "qty to receive is capped at remaining.\n"
                      "Landed cost = unit + share of shipping · A/P lives in finance_payables · posted receipts are immutable")
    els += grouped_board(GROUPS, DESK_COLS, colors=SECTION_COLORS)
    return els


# ══════════════════════════════════════════════════════════════════
#  MOBILE
# ══════════════════════════════════════════════════════════════════

def _mnote(ox, oy, body, color=ACCENT):
    return note(ox, oy + TITLE_H + PHONE_H + 16, PHONE_W, body, color)


def _m1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "A1. Procurement hub", g, "More")
    e, y = phone_header(cx, cy, cw, "Procurement", right=ICON["search"], g=G)
    els += e
    e, y = stat_row(cx, y, cw, [("Open POs", "5", INK, None, ICON["truck"]),
                                ("Awaiting", "3", WARN, None, ICON["clock"])], h=80, g=G)
    els += e
    e, y = stat_row(cx, y, cw, [("A/P AFN", "745,308", ROSE, None, ICON["ledger"]),
                                ("Spend MTD", "782,640", INK, None, ICON["chart"])], h=80, g=G)
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000012 · Istanbul Bridal",
                                 "Expected 18 Sep · AFN 345,320",
                                 "Received 60%"], G, badge=("Partial", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000015 · Kabul Textile",
                                 "Expected 14 Sep · AFN 148,000",
                                 "Delivery overdue 6 days"], G, badge=("Late", DANGER))
    els += e
    els += fab(cx + cw, oy + TITLE_H + PHONE_H - 138, f"{ICON['add']} New PO", G)
    els += _mnote(ox, oy, "Read only. FAB opens the new-PO sheet. Tap a PO → C3.")
    return els


def _m2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B1. Suppliers", g, "More")
    e, y = phone_header(cx, cy, cw, "Suppliers", left=ICON["back"], right=ICON["filter"], g=G)
    els += e
    els += search_bar(cx, y, cw, "Search suppliers…", G)
    y += 52
    els += filter_chips(cx, y, ["All", "Active", "A/P due"], 0, G)
    y += 42
    for name, meta, bal, badge in [
        ("Istanbul Bridal Co.", "SUP26-0001 · USD · Net 30", "A/P AFN 332,388", ("3 POs", INFO)),
        ("Dubai Fashion House", "SUP26-0002 · USD · Net 15", "A/P AFN 202,920", ("1 PO", INFO)),
        ("Kabul Textile Traders", "SUP26-0003 · AFN · Net 7", "A/P AFN 118,000 overdue", ("Late", DANGER)),
        ("Herat Silk House", "SUP26-0004 · AFN · Cash", "A/P AFN 0.00", ("Active", OK)),
    ]:
        e, y = list_card(cx, y, cw, [name, meta, bal], G, badge=badge)
        els += e
    els += fab(cx + cw, oy + TITLE_H + PHONE_H - 138, f"{ICON['add']} New supplier", G)
    els += _mnote(ox, oy, "FAB opens the same drawer as desktop B2 (bottom sheet on the phone).")
    return els


def _m3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B4. Supplier profile", g, "More")
    e, y = phone_header(cx, cy, cw, "Istanbul Bridal", left=ICON["back"], right=ICON["settings"], g=G)
    els += e
    c, xx = chip(cx, y, "Active", OK, g=G)
    els += c
    c, xx = chip(xx, y, "USD @ 71.20", INFO, g=G)
    els += c
    y += 36
    els += _panel(cx, y, cw, 100, "A/P", G)
    e, _ = money_row(cx + 16, y + 40, cw - 32, [("Current", "107,068"), ("1–30 days", "225,320")],
                     G, total=("Owed", "332,388"))
    els += e
    y += 116
    e, y = tabs(cx, y, cw, ["Orders", "Receipts", "Payments"], 0, G)
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000012 · 04 Sep", "AFN 345,320 · received 60%"], G,
                     badge=("Partial", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000008 · 02 Aug", "AFN 241,400 · received 100%"], G,
                     badge=("Closed", MUTED))
    els += e
    els += btn(cx, y + 4, (cw - 12) / 2, 44, "New PO", "primary", G)
    els += btn(cx + (cw + 12) / 2, y + 4, (cw - 12) / 2, 44, "Pay", "secondary", G)
    els += _mnote(ox, oy, "Items supplied + price history stay on desktop B8 / B9.")
    return els


def _m4(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C2. New PO (sheet)", g, "More")
    e, y = phone_header(cx, cy, cw, "New purchase order", left=ICON["back"], g=G)
    els += e
    half = (cw - 12) / 2
    e, y = select(cx, y, cw, "Supplier", "Istanbul Bridal Co. (USD)", G, True)
    els += e
    e, _ = field(cx, y, half, "Order date", "12 Sep 2026", G, True)
    els += e
    e, y = field(cx + half + 12, y, half, "Expected", "26 Sep 2026", G)
    els += e
    e, y = list_card(cx, y, cw, ["White A-Line Gown", "6 × USD 185.00", "USD 1,110.00"], G,
                     badge=("Existing", INFO))
    els += e
    e, y = list_card(cx, y, cw, ["Chantilly Veil (ivory)", "12 × USD 28.00 · no SKU yet",
                                 "USD 336.00"], G, badge=("NEW", VIOLET))
    els += e
    e, y = money_row(cx, y, cw, [("Subtotal", "USD 2,586"), ("Shipping", "USD 138")],
                     G, total=("Total · AFN 194,011", "USD 2,724"))
    els += e
    els += btn(cx, y, half, 44, "Save draft", "secondary", G)
    els += btn(cx + half + 12, y, half, 44, "Place order", "primary", G)
    els += _mnote(ox, oy, "No Submit for approval — Place order writes status='ordered'.")
    return els


def _m5(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C3. PO detail", g, "More")
    e, y = phone_header(cx, cy, cw, "PO26-000012", left=ICON["back"], right=ICON["print"], g=G)
    els += e
    e, y = timeline(cx, y, cw, [("Draft", "done"), ("Ordered", "done"),
                                ("Partial", "current"), ("Paid", "todo")], G)
    els += e
    e, y = money_row(cx, y, cw, [("PO total", "AFN 345,320"), ("Paid", "AFN 120,000")],
                     G, total=("Balance", "AFN 225,320"))
    els += e
    e, y = list_card(cx, y, cw, ["White A-Line Gown", "ord 6 · recv 4 · remaining 2"], G,
                     badge=("Partial", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["Chantilly Veil (ivory)", "ord 12 · recv 0 · SKU on receipt"], G,
                     badge=("Pending", VIOLET))
    els += e
    els += btn(cx, y, cw, 46, "Receive goods", "primary", G)
    els += _mnote(ox, oy, "No approval stamp. Receive opens the D2 sheet.")
    return els


def _m6(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "D2. Receive goods", g, "More")
    e, y = phone_header(cx, cy, cw, "Receive · GRN26-0008", left=ICON["back"], g=G)
    els += e
    e, y = list_card(cx, y, cw, ["White A-Line Gown", "left 2 · recv now 2",
                                 ("landed 14,499", ACCENT, 11.5)], G, badge=("2 left", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["Chantilly Veil · NEW", "left 12 · recv now 12",
                                 ("landed 2,195", ACCENT, 11.5)], G, badge=("SKU?", VIOLET))
    els += e
    e, y = field(cx, y, cw, "Shipping & customs AFN", "9,800.00", G)
    els += e
    e, y = money_row(cx, y, cw, [("Goods", "AFN 97,268"), ("Shipping", "AFN 9,800")],
                     G, total=("Landed → stock", "AFN 107,068"))
    els += e
    els += btn(cx, y, cw, 46, "Post receipt", "primary", G)
    els += _mnote(ox, oy, "Recv now cannot exceed remaining. NEW lines open D3 before post.")
    return els


def _m7(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "E1. Pay supplier", g, "More")
    e, y = phone_header(cx, cy, cw, "Pay supplier", left=ICON["back"], g=G)
    els += e
    e, y = select(cx, y, cw, "Supplier", "Istanbul Bridal Co.", G, True)
    els += e
    e, y = list_card(cx, y, cw, ["✓  AP26-0039 · PO26-000012",
                                 "Balance 225,320 · allocate 50,000"], G, badge=("Part", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["✓  AP26-0042 · PO26-000012",
                                 "Balance 107,068 · allocate 30,000"], G, badge=("Part", WARN))
    els += e
    half = (cw - 12) / 2
    e, _ = field(cx, y, half, "Amount AFN", "80,000.00", G, True)
    els += e
    e, y = select(cx + half + 12, y, half, "Method", "Cash", G, True)
    els += e
    e, y = money_row(cx, y, cw, [("Allocated", "AFN 80,000")], G, total=("A/P after", "AFN 252,388"))
    els += e
    els += btn(cx, y, cw, 46, "Post payment", "primary", G)
    els += _mnote(ox, oy, "Payment must allocate to named payables — no unallocated cash.")
    return els


def _m8(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "F2. Stock-in report", g, "More")
    e, y = phone_header(cx, cy, cw, "Stock-in report", left=ICON["back"], right=ICON["export"], g=G)
    els += e
    els += filter_chips(cx, y, ["Sept 2026", "All sources"], 0, G)
    y += 44
    e, y = bar_chart(cx, y, cw, 168, "Stock-in value by source · AFN", [
        ("Purch.", 1.0, "413k"), ("Manual", 0.23, "96k"), ("Sale ret", 0.13, "53k"),
        ("Rent ret", 0.2, "84k")], G)
    els += e
    e, y = table(cx, y, cw, ["Source", "Qty", "Value AFN"],
                 [["Purchase receipt", "48", ("412,600", OK)],
                  ["Manual entry", "12", "96,400"],
                  [("TOTAL", INK), ("79", INK), ("678,000", INK)]],
                 G, row_h=32, widths=[1.7, 0.6, 1.1])
    els += e
    els += _mnote(ox, oy, "Purchase rows valued at landed cost so this ties to the register.", INFO)
    return els


MOBILE_SCREENS = [_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8]


def mobile():
    els = board_title(0, -150, "BOMS Mobile — Procurement",
                      "Same order as desktop: hub → suppliers → PO (no approval) → receive → pay → stock-in report.")
    for i, fn in enumerate(MOBILE_SCREENS):
        ox, oy = grid_pos(i, PHONE_COLS, PHONE_W, PHONE_H)
        els += fn(ox, oy)
    els += flow_arrows(len(MOBILE_SCREENS), PHONE_COLS, PHONE_W, PHONE_H)
    return els
