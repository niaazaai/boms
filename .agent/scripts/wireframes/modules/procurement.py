#!/usr/bin/env python3
"""BOMS — Procurement module wireframes (desktop + mobile).

Draws the CORRECTED procurement model:
  • header other_cost allocated pro-rata by line value at receipt time →
    landed_unit_cost = unit_cost + allocated_other_cost / qty  (this is what posts)
  • receiving creates missing inventory_items and back-fills the PO line
  • over-receipt blocked unless explicitly approved
  • A/P lives in finance_payables only (PO balance is a derived display)
  • posted receipts are immutable — Void writes reversing rows
  • PO approval records approved_by / approved_at on draft → ordered
  • supplier returns (debit notes) → stock_out + reduce A/P
  • costing = Weighted Average Cost
"""

from __future__ import annotations

from dsl import *  # noqa: F401,F403

# ── Board geometry ────────────────────────────────────────────────
COLS = 4
D_ROW_GAP = 360          # extra room for the per-screen spec notes
M_COLS = 6
M_ROW_GAP = 300

SECTIONS = ["SUPPLIERS", "PURCHASE ORDERS", "RECEIVING & PAYMENT", "RETURNS & REPORTS"]
M_SECTIONS = ["PROCUREMENT — MOBILE", "PAYMENT & REPORTS"]

RATE = "USD @ 71.20 AFN"


# ── Local composition helpers (built from dsl primitives only) ────

def panel(x, y, w, h, title, gl, sub=None):
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=gl)]
    if title:
        els.append(text(x + 16, y + 14, title, 13, INK, width=w - 32, g=gl))
    if sub:
        els.append(text(x + 16, y + 33, sub, 11, MUTED, width=w - 32, g=gl))
    return els


def sub_head(x, y, w, label, gl, right=None, color=INK):
    els = [text(x, y, label, 14, color, width=w - 120, g=gl)]
    if right:
        els.append(text(x + w - 160, y + 2, right, 12, ACCENT, "right", 160, gl))
    return els, y + 26


def kv(x, y, w, pairs, gl, size=12, step=22):
    """Label left / value right rows inside a panel."""
    els, yy = [], y
    for lab, val in pairs:
        col = INK
        if isinstance(val, tuple):
            val, col = val
        els.append(text(x, yy, lab, size, MUTED, width=w * 0.55, g=gl))
        els.append(text(x + w * 0.45, yy, val, size, col, "right", w * 0.55, gl))
        yy += step
    return els, yy


def note_under(ox, oy, body, color=ACCENT, w=DESK_W):
    return note(ox, oy + TITLE_H + DESK_H + 20, w, body, color)


def m_note_under(ox, oy, body, color=ACCENT, w=470):
    return note(ox, oy + TITLE_H + PHONE_H + 18, w, body, color)


def win(ox, oy):
    """Full browser-window interior — used as the dim region for drawers/modals."""
    return ox + 1, oy + TITLE_H + 35, DESK_W - 2, DESK_H - 36


# ── Shared data ───────────────────────────────────────────────────

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
    ["PO26-000008", "Istanbul Bridal Co.", "02 Aug", "16 Aug", "5", "241,400", ("100%", OK),
     "241,400", "0.00", ("Closed", MUTED)],
]

# GRN26-0008 — receiving against PO26-000012.
#   line value Σ = 97,268 · other_cost 9,800 allocated pro-rata by line value
#   landed Σ = 107,068
GRN_LINES = [
    ["1 · White A-Line Gown", "6", "4", "2", "13,172.00", "2,654.00", ("14,499.00", ACCENT), "28,998.00"],
    ["2 · Ivory Ball Gown", "4", "2", "2", "17,088.00", "3,444.00", ("18,810.00", ACCENT), "37,620.00"],
    ["3 · Chantilly Veil · NEW", "12", "0", "12", "1,994.00", "2,411.00", ("2,194.92", ACCENT), "26,339.00"],
    ["4 · Pearl Hair Comb · NEW", "20", "0", "20", "641.00", "1,291.00", ("705.55", ACCENT), "14,111.00"],
]

GRN_COLS = ["Line / item", "Ord.", "Already", "Recv now", "Unit cost", "Alloc. other",
            "Landed unit", "Line value"]
GRN_W = [2.2, 0.7, 0.95, 1.0, 1.15, 1.2, 1.2, 1.15]


def grn_body(cx, cy, cw, gl, over=False):
    """Receiving table + allocation panel. Shared by screens 8, 9 and 10."""
    els = []
    colw, gap = 266, 24
    e, y = select(cx, cy, colw, "Purchase order *", "PO26-000012 · Istanbul Bridal", gl, True)
    els += e
    e, _ = select(cx + colw + gap, cy, colw, "Receive into warehouse *", "Main store — Kabul", gl, True)
    els += e
    e, _ = field(cx + 2 * (colw + gap), cy, colw, "Received date *", "18 Sep 2026", gl, True)
    els += e
    e, _ = field(cx + 3 * (colw + gap), cy, colw, "Supplier invoice no.", "IST-2026-4471", gl)
    els += e

    els.append(text(cx, y + 2, f"{ICON['globe']}  PO currency USD · rate snapshot {RATE} (taken on order date) — "
                               "all costs below posted in AFN", 11.5, MUTED, width=cw, g=gl))
    y += 24

    rows = [list(r) for r in GRN_LINES]
    if over:
        rows[0][3] = ("4  ⚠", DANGER)
        rows[0][7] = ("57,996.00", DANGER)
    e, y = table(cx, y, cw, GRN_COLS, rows, gl, row_h=42, widths=GRN_W)
    els += e

    # allocation + totals
    pw = 560
    els += panel(cx, y, pw, 126, "Landed cost allocation", gl,
                 "Header other cost is split pro-rata by line value at post time")
    e, _ = kv(cx + 16, y + 56, pw - 32, [
        ("Goods value (Σ line value)", "AFN  97,268.00"),
        ("Header other cost — freight + customs", "AFN   9,800.00"),
        ("Allocated to lines (pro-rata by value)", ("AFN   9,800.00", OK)),
    ], gl)
    els += e
    e, _ = money_row(cx + pw + 24, y + 8, cw - pw - 24, [
        ("Goods value", "AFN 97,268.00"),
        ("Other cost allocated", "AFN 9,800.00"),
        ("Landed cost → inventory", "AFN 107,068.00"),
    ], gl, total=("Payable to supplier", "AFN 107,068.00"))
    els += e
    return els, y + 142


# ══════════════════════════════════════════════════════════════════
#  DESKTOP
# ══════════════════════════════════════════════════════════════════

def d1(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "1. Procurement hub", "Procurement", g,
                                     sub_active="Purchase orders")
    e, y = page_header(cx, cy, cw, "Procurement",
                       [("＋ New purchase order", "primary"), ("Receive goods", "secondary"),
                        ("＋ Supplier", "secondary")],
                       "Main branch · September 2026 · base currency AFN", gl)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Open POs", "5", INK, "3 ordered · 2 draft", ICON["truck"]),
        ("Awaiting receipt", "3", WARN, "1 delivery overdue", ICON["clock"]),
        ("Received this month", "6", OK, "GRNs posted", ICON["receipt"]),
        ("Total A/P", "745,308", ROSE, "AFN · finance_payables", ICON["ledger"]),
        ("Overdue A/P", "118,000", DANGER, "Kabul Textile Traders", ICON["alert"]),
        ("Spend MTD", "782,640", INK, "+18% vs Aug", ICON["chart"]),
    ], g=gl)
    els += e

    lw, rx, rw = 700, cx + 724, 412
    e, ly = sub_head(cx, y, lw, "Open purchase orders", gl, "View all →")
    els += e
    e, ly = table(cx, ly, lw, ["PO #", "Supplier", "Expected", "Total AFN", "Recv", "Balance", "Status"],
                  [r[:1] + r[1:2] + r[3:4] + r[5:7] + r[8:10] for r in PO_ROWS[:5]],
                  gl, row_h=42, widths=[1.1, 1.8, 1.0, 1.1, 0.6, 1.1, 0.9])
    els += e
    e, ly = bar_chart(cx, ly + 6, lw, 196, "Purchase spend by month · AFN", [
        ("May", 0.34, "268k"), ("Jun", 0.51, "402k"), ("Jul", 0.43, "340k"),
        ("Aug", 0.85, "664k"), ("Sep", 1.0, "783k")], gl)
    els += e

    els += panel(rx, y, rw, 122, "Quick actions", gl)
    bw = (rw - 44) / 2
    els += btn(rx + 16, y + 44, bw, 40, "New PO", "primary", gl)
    els += btn(rx + 28 + bw, y + 44, bw, 40, "Receive goods", "secondary", gl)
    els += btn(rx + 16, y + 92, bw, 40, "Pay supplier", "secondary", gl)
    els += btn(rx + 28 + bw, y + 92, bw, 40, "Reports", "secondary", gl)
    ry = y + 138
    e, ry = sub_head(rx, ry, rw, "Upcoming deliveries", gl)
    els += e
    e, ry = table(rx, ry, rw, ["Expected", "PO # · supplier", "Lines"], [
        [("14 Sep · overdue", DANGER), "PO26-000015 · Kabul Textile", "5"],
        ["18 Sep", "PO26-000012 · Istanbul Bridal", "6"],
        ["21 Sep", "PO26-000013 · Dubai Fashion", "4"],
    ], gl, row_h=40, widths=[1.15, 2.0, 0.6])
    els += e
    e, ry = sub_head(rx, ry + 4, rw, "Overdue payables", gl, "A/P →")
    els += e
    e, ry = table(rx, ry, rw, ["Payable #", "Supplier", "Balance"], [
        ["AP26-0031", "Kabul Textile", ("88,000", DANGER)],
        ["AP26-0028", "Kabul Textile", ("30,000", DANGER)],
    ], gl, row_h=38, widths=[1.1, 1.3, 0.9])
    els += e

    els += note_under(ox, oy,
        "READ ONLY — no writes. Open POs = procurement_purchase_orders.status IN (draft, ordered, partial_received).\n"
        "Total A/P = SUM(finance_payables.balance_amount) WHERE status IN (open, partial) — NEVER from purchase_orders.balance_amount (derived cache only).\n"
        "Received this month = COUNT(procurement_receipts WHERE status='posted'). Spend MTD = SUM(total_amount × exchange_rate) for POs ordered this month.\n"
        "Overdue = finance_payables.due_date < today AND balance_amount > 0.")
    return els


def d2(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "2. Suppliers list", "Procurement", g,
                                     sub_active="Suppliers")
    e, y = page_header(cx, cy, cw, "Suppliers",
                       [("＋ New supplier", "primary"), ("Export", "secondary")],
                       "6 suppliers · 2 with overdue balances", gl)
    els += e
    els += search_bar(cx, y, 520, "Search name, code, phone or contact person…", gl)
    els += filter_chips(cx + 540, y + 5, ["All", "Active", "Inactive", "Has open PO", "Overdue A/P"], 0, gl)
    y += 56
    e, y = table(cx, y, cw,
                 ["Code", "Name", "Contact person", "Phone", "Curr.", "Terms", "Open POs",
                  "A/P balance AFN", "Status"],
                 SUPPLIER_ROWS, gl, row_h=46,
                 widths=[0.95, 1.55, 1.3, 1.25, 0.55, 0.75, 0.75, 1.15, 0.8])
    els += e
    e, y = pagination(cx, y, cw, "1–6 of 6 suppliers", gl)
    els += e
    els += note(cx, y + 6, cw,
                "A/P balance is read from finance_payables (SUM balance_amount per supplier) — procurement_suppliers stores no balance column.",
                INFO, gl)

    els += note_under(ox, oy,
        "READS procurement_suppliers (tenant scoped) LEFT JOIN finance_payables for the balance column and procurement_purchase_orders for the open-PO count.\n"
        "Row click → supplier detail. Status toggle writes procurement_suppliers.status ('active' | 'inactive') + updated_by / updated_at; inactive suppliers cannot be chosen on a new PO.\n"
        "Export streams the same query to CSV — no state change.")
    return els


def d3(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "3. Supplier detail", "Procurement", g,
                                     sub_active="Suppliers")
    e, y = page_header(cx, cy, cw, "Istanbul Bridal Co.",
                       [("＋ New PO", "primary"), ("Record payment", "secondary"), ("Edit", "secondary")],
                       "SUP26-0001 · Active · USD · Net 30 · supplier since Feb 2026", gl)
    els += e

    pw, rx = 340, cx + 364
    rw = cw - 364
    els += panel(cx, y, pw, 250, "Profile", gl)
    e, _ = kv(cx + 16, y + 48, pw - 32, [
        ("Contact person", "Elif Demir"),
        ("Phone", "+90 532 441 8820"),
        ("Email", "elif@istanbulbridal.com"),
        ("Address", "Nişantaşı, Istanbul, TR"),
        ("Payment term", "Net 30"),
        ("Currency", ("USD · " + RATE, INFO)),
        ("Created by", "Ahmad Zaki · 12 Feb 2026"),
    ], gl, step=26)
    els += e
    els += panel(cx, y + 266, pw, 212, "A/P summary — finance_payables", gl)
    e, _ = money_row(cx + 16, y + 306, pw - 32, [
        ("Open payables (2)", "AFN 332,388.00"),
        ("Current (not due)", "AFN 107,068.00"),
        ("1–30 days", "AFN 225,320.00"),
        ("Overdue 30+", "AFN 0.00"),
    ], gl, total=("Balance owed", "AFN 332,388.00"))
    els += e

    e, ry = tabs(rx, y, rw, ["Purchase orders", "Receipts (GRN)", "Payments", "Items supplied",
                             "Price history"], 0, gl)
    els += e
    e, ry = table(rx, ry, rw, ["PO #", "Order date", "Total AFN", "Recv", "Paid", "Balance", "Status"],
                  [["PO26-000012", "04 Sep 2026", "345,320", ("60%", WARN), "120,000", ("225,320", ROSE), ("Partial", WARN)],
                   ["PO26-000008", "02 Aug 2026", "241,400", ("100%", OK), "241,400", "0.00", ("Closed", MUTED)],
                   ["PO26-000004", "19 Jun 2026", "198,700", ("100%", OK), "198,700", "0.00", ("Closed", MUTED)]],
                  gl, row_h=42, widths=[1.2, 1.2, 1.1, 0.7, 1.0, 1.1, 0.9])
    els += e
    e, ry = sub_head(rx, ry + 4, rw, "Price history — White A-Line Gown (BD-AL-0114)", gl, "All items →")
    els += e
    e, ry = table(rx, ry, rw, ["Document", "Date", "Qty", "Unit cost", "Landed unit", "Change"],
                  [["PO26-000004 · GRN26-0002", "21 Jun 2026", "4", "USD 172.00", "12,470.00", ("—", FAINT)],
                   ["PO26-000008 · GRN26-0005", "16 Aug 2026", "6", "USD 178.00", "13,010.00", ("+4.3%", WARN)],
                   ["PO26-000012 · GRN26-0007", "09 Sep 2026", "4", "USD 185.00", "13,860.00", ("+6.5%", WARN)],
                   ["PO26-000012 · GRN26-0008", "18 Sep 2026", "2", "USD 185.00", ("14,499.00", ACCENT), ("+4.6%", DANGER)]],
                  gl, row_h=40, widths=[1.7, 1.1, 0.55, 1.0, 1.0, 0.8])
    els += e

    els += note_under(ox, oy,
        "READS procurement_suppliers + procurement_purchase_orders + procurement_receipts + procurement_supplier_payments + finance_payables.\n"
        "Price history is derived from procurement_receipt_items (unit_cost and landed_unit_cost per inventory_item_id), newest last — it is what drives the WAC recalculation.\n"
        "A/P aging buckets come from finance_payables.due_date vs today. The supplier row itself never stores a balance.")
    return els


def d4(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "4. Add / edit supplier — drawer", "Procurement", g,
                                     sub_active="Suppliers")
    # dimmed background list
    e, y = page_header(cx, cy, cw, "Suppliers", [("＋ New supplier", "primary")], None, gl)
    els += e
    els += search_bar(cx, y, 520, "Search suppliers…", gl)
    e, _ = table(cx, y + 56, cw, ["Code", "Name", "Contact person", "Phone", "Curr.", "Terms", "Status"],
                 [r[:5] + r[5:6] + r[8:9] for r in SUPPLIER_ROWS[:5]], gl, row_h=46,
                 widths=[1.0, 1.6, 1.3, 1.3, 0.6, 0.8, 0.8])
    els += e

    dox, doy, dcw, dch = win(ox, oy)
    e, fx, fy, fw = drawer(dox, doy, dcw, dch, "New supplier",
                           subtitle="Drawer opens from the RIGHT in LTR · from the LEFT in RTL (Dari / Pashto)",
                           width=460, g=gl)
    els += e
    half = (fw - 16) / 2
    e, fy = field(fx, fy, fw, "Supplier name", "Istanbul Bridal Co.", gl, True)
    els += e
    e, _ = field(fx, fy, half, "Supplier code", "SUP26-0007 (auto)", gl)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Status", "Active", gl)
    els += e
    e, _ = field(fx, fy, half, "Contact person", "Elif Demir", gl)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Phone", "+90 532 441 8820", gl, True)
    els += e
    e, fy = field(fx, fy, fw, "Email", "elif@istanbulbridal.com", gl)
    els += e
    e, fy = textarea(fx, fy, fw, "Address", "Nişantaşı Mah. No 44, Istanbul, Türkiye", gl, rows=2)
    els += e
    e, _ = select(fx, fy, half, "Payment term", "Net 30", gl, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Currency", "USD", gl, True)
    els += e
    e, fy = textarea(fx, fy, fw, "Note", "e.g. ships via Kabul customs broker", gl, rows=2)
    els += e
    els += note(fx, fy, fw,
                "Opening A/P is NOT entered here — create a manual\nfinance_payables row instead.", INFO, gl)
    els += btn(fx, doy + dch - 72, half, 44, "Cancel", "secondary", gl)
    els += btn(fx + half + 16, doy + dch - 72, half, 44, "Save supplier", "primary", gl)

    els += note_under(ox, oy,
        "INSERT / UPDATE procurement_suppliers (tenant_id, supplier_code, name, contact_person, phone, email, address, payment_term_id, currency_id, status, note, created_by / updated_by).\n"
        "supplier_code is generated server-side (SUP26-nnnn) and is unique per tenant; name is required. Currency drives the PO default and the exchange_rate snapshot taken at PO time.\n"
        "No balance is written — opening A/P is a manual finance_payables row so the ledger stays the single source of truth (defect D4).")
    return els


def d5(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "5. Purchase orders list", "Procurement", g,
                                     sub_active="Purchase orders")
    e, y = page_header(cx, cy, cw, "Purchase orders",
                       [("＋ New PO", "primary"), ("Export", "secondary")],
                       "September 2026 · all branches", gl)
    els += e
    els += search_bar(cx, y, 440, "Search PO number, supplier or item…", gl)
    els += filter_chips(cx + 460, y + 5,
                        ["All", "Draft", "Ordered", "Partial", "Received", "Cancelled"], 0, gl)
    y += 56
    e, y = table(cx, y, cw,
                 ["PO #", "Supplier", "Date", "Expected", "Lines", "Total AFN", "Received",
                  "Paid", "Balance", "Status"],
                 PO_ROWS, gl, row_h=44,
                 widths=[1.15, 1.55, 0.8, 0.85, 0.6, 1.05, 0.85, 0.95, 1.0, 0.95])
    els += e
    e, y = pagination(cx, y, cw, "1–7 of 23 purchase orders", gl)
    els += e
    els += note(cx, y + 4, cw,
                "Received % = SUM(quantity_received) / SUM(quantity_ordered) over procurement_purchase_order_items · Balance is the derived display of finance_payables.",
                INFO, gl)

    els += note_under(ox, oy,
        "READS procurement_purchase_orders JOIN procurement_suppliers, with line aggregates from procurement_purchase_order_items and A/P from finance_payables.\n"
        "quantity_received is RECOMPUTED from procurement_receipt_items (never incremented in place), so the % column cannot drift from the receipts (defect D3).\n"
        "Status chips filter status enum(draft, ordered, partial_received, received, cancelled). A PO that has any posted receipt can no longer be cancelled — use a supplier return instead.")
    return els


def d6(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "6. Create purchase order", "Procurement", g,
                                     sub_active="Purchase orders")
    e, y = page_header(cx, cy, cw, "New purchase order",
                       [("Submit for approval", "primary"), ("Save draft", "secondary"),
                        ("Cancel", "ghost")],
                       "Draft · PO26-000016 · created by Ahmad Zaki · 12 Sep 2026", gl)
    els += e
    colw, gap = 266, 24
    e, y2 = select(cx, y, colw, "Supplier", "Istanbul Bridal Co. (USD)", gl, True)
    els += e
    e, _ = select(cx + colw + gap, y, colw, "Branch", "Main branch — Kabul", gl, True)
    els += e
    e, _ = select(cx + 2 * (colw + gap), y, colw, "Receive into warehouse", "Main store", gl, True)
    els += e
    e, _ = field(cx + 3 * (colw + gap), y, colw, "Currency & rate snapshot", "USD @ 71.20", gl, True)
    els += e
    y = y2
    e, y2 = field(cx, y, colw, "Order date", "12 Sep 2026", gl, True)
    els += e
    e, _ = field(cx + colw + gap, y, colw, "Expected delivery", "26 Sep 2026", gl)
    els += e
    e, _ = select(cx + 2 * (colw + gap), y, colw, "Payment term", "Net 30 — due 12 Oct 2026", gl)
    els += e
    e, _ = field(cx + 3 * (colw + gap), y, colw, "Supplier reference", "e.g. quote IST-Q-1182", gl)
    els += e
    y = y2

    e, y = sub_head(cx, y, cw, "Lines", gl, "Existing item OR free-text new item")
    els += e
    e, y = table(cx, y, cw,
                 ["#", "Item — existing SKU or new name", "Source", "Qty", "Unit cost USD",
                  "Line total USD", "Line total AFN", ""],
                 [["1", "White A-Line Gown · BD-AL-0114", ("Existing item", INFO), "6", "185.00",
                   "1,110.00", "79,032.00", ("✕", FAINT)],
                  ["2", "Ivory Ball Gown · BD-BG-0077", ("Existing item", INFO), "4", "240.00",
                   "960.00", "68,352.00", ("✕", FAINT)],
                  ["3", "Chantilly Veil (ivory)", ("NEW — no SKU yet", VIOLET), "12", "28.00",
                   "336.00", "23,923.20", ("✕", FAINT)],
                  ["4", "Pearl Hair Comb", ("NEW — no SKU yet", VIOLET), "20", "9.00",
                   "180.00", "12,816.00", ("✕", FAINT)]],
                 gl, row_h=42, widths=[0.35, 2.6, 1.3, 0.6, 1.1, 1.15, 1.2, 0.4])
    els += e
    els.append(rect(cx, y, cw, 44, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=gl))
    els.append(text(cx + 16, y + 14, f"{ICON['add']}  Add line — search an existing item, or type a new "
                                     "dress name to create it at receipt", 12.5, MUTED, width=cw - 32, g=gl))
    y += 58

    pw = 560
    els += panel(cx, y, pw, 150, "Header other cost", gl,
                 "Shipping / customs — allocated pro-rata to lines when the GRN posts")
    e, _ = field(cx + 16, y + 56, 250, "Other cost (USD)", "137.64", gl)
    els += e
    e, _ = select(cx + 286, y + 56, 250, "Allocation basis", "Pro-rata by line value", gl, True)
    els += e
    els.append(text(cx + 16, y + 124, "Locked basis — landed_unit_cost = unit_cost + allocated_other_cost / qty",
                    11, ACCENT, width=pw - 32, g=gl))
    e, _ = money_row(cx + pw + 24, y, cw - pw - 24, [
        ("Subtotal (4 lines)", "USD 2,586.00"),
        ("Discount", "USD 0.00"),
        ("Other cost — shipping & customs", "USD 137.64"),
        ("Tax", "USD 0.00"),
    ], gl, total=("PO total · AFN 194,010.53", "USD 2,723.64"))
    els += e

    els += note_under(ox, oy,
        "Save draft → INSERT procurement_purchase_orders (status='draft', exchange_rate snapshot) + procurement_purchase_order_items.\n"
        "A line with an existing item sets inventory_item_id; a free-text line leaves inventory_item_id NULL and keeps item_name only — the GRN creates the item and back-fills this id (defect D2).\n"
        "Header other_cost is stored ONCE on the PO header; line other_cost is never entered by hand. Allocation happens at receipt, not here (defect D1).\n"
        "A draft PO touches NO stock and NO finance rows. Submit for approval → screen 7.")
    return els


def d7(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "7. PO detail — approval & fulfilment", "Procurement", g,
                                     sub_active="Purchase orders")
    e, y = page_header(cx, cy, cw, "PO26-000012",
                       [("Receive goods", "primary"), ("Record payment", "secondary"),
                        ("Print", "ghost")],
                       "Istanbul Bridal Co. · ordered 04 Sep 2026 · USD @ 71.20 AFN · expected 18 Sep 2026", gl)
    els += e
    e, y = timeline(cx, y, cw, [("Draft", "done"), ("Ordered — approved", "done"),
                                ("Partially received", "current"), ("Received", "todo"),
                                ("Closed — paid", "todo")], gl)
    els += e
    els += note(cx, y - 2, cw,
                "Approved by Ahmad Zaki (Owner) on 04 Sep 2026 09:12 — written to approved_by / approved_at on the draft → ordered transition.",
                OK, gl)
    y += 46

    e, y = table(cx, y, cw,
                 ["Line", "SKU", "Ordered", "Received", "Remaining", "Unit cost USD",
                  "Landed unit AFN", "Line total AFN", "Status"],
                 [["White A-Line Gown", "BD-AL-0114", "6", "4", ("2", WARN), "185.00", "13,860.00",
                   "79,032.00", ("Partial", WARN)],
                  ["Ivory Ball Gown", "BD-BG-0077", "4", "2", ("2", WARN), "240.00", "18,120.00",
                   "68,352.00", ("Partial", WARN)],
                  ["Chantilly Veil (ivory)", ("— on receipt", VIOLET), "12", "0", ("12", DANGER),
                   "28.00", ("— on receipt", FAINT), "23,923.20", ("Pending", MUTED)],
                  ["Pearl Hair Comb", ("— on receipt", VIOLET), "20", "0", ("20", DANGER), "9.00",
                   ("— on receipt", FAINT), "12,816.00", ("Pending", MUTED)]],
                 gl, row_h=42, widths=[1.9, 1.15, 0.7, 0.8, 0.9, 1.1, 1.25, 1.2, 0.85])
    els += e

    hw = (cw - 24) / 2
    e, ly = sub_head(cx, y, hw, "Receipts (GRN)", gl)
    els += e
    e, _ = table(cx, ly, hw, ["GRN #", "Date", "Lines", "Landed value", "Status"],
                 [["GRN26-0007", "09 Sep 2026", "2", "94,116.00", ("Posted", OK)],
                  ["GRN26-0008", "18 Sep 2026", "4", "107,068.00", ("Draft", MUTED)]],
                 gl, row_h=38, widths=[1.1, 1.1, 0.6, 1.1, 0.8])
    els += e
    e, ry = sub_head(cx + hw + 24, y, hw, "Payments & A/P", gl, "finance_payables")
    els += e
    e, ry = table(cx + hw + 24, ry, hw, ["Doc #", "Date", "Amount AFN", "Type"],
                  [["AP26-0039", "09 Sep 2026", "94,116.00", ("Payable opened", ROSE)],
                   ["SPAY26-0014", "12 Sep 2026", "120,000.00", ("Payment out", OK)]],
                  gl, row_h=38, widths=[1.2, 1.1, 1.1, 1.2])
    els += e
    e, _ = money_row(cx + hw + 24, ry + 4, hw, [
        ("PO total", "AFN 345,320.00"),
        ("Paid to date", "AFN 120,000.00"),
    ], gl, total=("Balance (derived from A/P)", "AFN 225,320.00"))
    els += e

    els += note_under(ox, oy,
        "READS procurement_purchase_orders + _items + procurement_receipts + procurement_supplier_payments + finance_payables.\n"
        "Approve (draft → ordered) UPDATEs status, approved_by, approved_at — permission procurement.purchase_order.approve (defect D8). Only ordered / partial_received POs can be received.\n"
        "Balance shown is DERIVED: SUM(finance_payables.balance_amount) for this PO. purchase_orders.balance_amount is a cache refreshed in the same transaction, never the source (defect D4).\n"
        "Cancel is disabled because posted receipts exist — the correction path is a supplier return / debit note (screen 13).")
    return els


def d8(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "8. Receive goods (GRN) — landed cost", "Procurement", g,
                                     sub_active="Receipts (GRN)")
    e, y = page_header(cx, cy, cw, "Receive goods · GRN26-0008",
                       [("Post receipt", "primary"), ("Save draft", "secondary"), ("Cancel", "ghost")],
                       "Against PO26-000012 · Istanbul Bridal Co. · draft — nothing has moved yet", gl)
    els += e
    e, y = grn_body(cx, y, cw, gl)
    els += e
    els += note(cx, y, cw,
                "2 free-text lines have no SKU — posting opens the guided new-item form (screen 10) and writes the new inventory_items id back onto the PO line.",
                VIOLET, gl)

    els += note_under(ox, oy,
        "Post receipt (one transaction): INSERT procurement_receipts (status='posted') + procurement_receipt_items storing quantity_received, unit_cost, allocated_other_cost AND landed_unit_cost (auditable — defect D1).\n"
        "Allocation: allocated_other_cost(line) = header other_cost × line_value / Σ line_value; landed_unit_cost = unit_cost + allocated_other_cost / qty. That number — not unit_cost — posts to the ledger.\n"
        "Then: inventory_stock_transactions type='stock_in', quantity=+recv, unit_cost=landed_unit_cost, reference_type='procurement_receipt'; recompute inventory_items WAC; recompute PO quantity_received; open finance_payables.\n"
        "Guard: receiving now > ordered − already received is BLOCKED unless over_receipt_approved_by is set (screen 9, defect D3).")
    return els


def d9(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "9. Over-receipt blocked — approval required",
                                     "Procurement", g, sub_active="Receipts (GRN)")
    e, y = page_header(cx, cy, cw, "Receive goods · GRN26-0008",
                       [("Post receipt", "primary"), ("Save draft", "secondary")],
                       "Line 1 receives 4 but only 2 remain on PO26-000012", gl)
    els += e
    e, _ = grn_body(cx, y, cw, gl, over=True)
    els += e

    mox, moy, mcw, mch = win(ox, oy)
    mw, mh = 560, 360
    mx, my = mox + (mcw - mw) / 2, moy + (mch - mh) / 2
    els += modal(mox, moy, mcw, mch, "Over-receipt blocked",
                 "Line 1 · White A-Line Gown\nOrdered 6 · already received 4 · remaining 2 · receiving now 4.\n"
                 "This would receive 2 units more than ordered.\nPosting is blocked until an approver is recorded on the receipt.",
                 w=mw, h=mh,
                 actions=[("Cancel", "secondary"), ("Reduce to 2", "secondary"),
                          ("Approve over-receipt", "danger")], g=gl)
    els.append(rect(mx, my, 7, mh, strokeColor=DANGER, backgroundColor=DANGER, strokeWidth=1, groupIds=gl))
    els.append(text(mx + mw - 60, my + 22, ICON["alert"], 20, DANGER, g=gl))
    els.append(rect(mx + 24, my + 150, mw - 48, 78, strokeColor=DANGER, backgroundColor=DANGER_BG,
                    strokeWidth=1, groupIds=gl))
    els.append(mono(mx + 40, my + 166, "CHECK quantity_received <= quantity_ordered\n"
                                       "        OR over_receipt_approved_by IS NOT NULL",
                    12, DANGER, g=gl))
    e, _ = select(mx + 24, my + 242, mw - 48, "Over-receipt approved by (required to proceed)",
                  "…select an approver with procurement.approve", gl, True)
    els += e

    els += note_under(ox, oy,
        "VALIDATION, not a warning. Server rejects the post unless procurement_receipts.over_receipt_approved_by (+ approved_at, reason) is set by a user holding procurement.purchase_order.approve.\n"
        "Approving writes the approver onto the RECEIPT, posts the extra units at the same landed_unit_cost, and leaves quantity_received > quantity_ordered on the PO line — visible on the fulfilment report.\n"
        "'Reduce to 2' simply rewrites the draft receipt line. Nothing has touched inventory_stock_transactions or finance_payables at this point (defect D3).", DANGER)
    return els


def d10(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "10. GRN · create new item (free-text line)",
                                     "Procurement", g, sub_active="Receipts (GRN)")
    e, y = page_header(cx, cy, cw, "Receive goods · GRN26-0008",
                       [("Post receipt", "primary"), ("Save draft", "secondary")],
                       "Line 3 has no SKU — complete the item before posting", gl)
    els += e
    e, _ = grn_body(cx, y, cw, gl)
    els += e

    dox, doy, dcw, dch = win(ox, oy)
    e, fx, fy, fw = drawer(dox, doy, dcw, dch, "New item — line 3",
                           subtitle="Free-text PO line “Chantilly Veil (ivory)” · SKU is generated when the GRN posts",
                           width=470, g=gl)
    els += e
    half = (fw - 16) / 2
    e, fy = field(fx, fy, fw, "Item name", "Chantilly Veil (ivory)", gl, True)
    els += e
    e, _ = select(fx, fy, half, "Main category", "Accessories", gl, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Sub category", "Veils", gl, True)
    els += e
    e, _ = select(fx, fy, half, "Item type", "Veil", gl, True)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Purpose", "Sale + Rental", gl, True)
    els += e
    e, _ = select(fx, fy, half, "Size", "One size", gl)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Colour", "Ivory", gl)
    els += e
    e, _ = field(fx, fy, half, "Sale price AFN", "4,500.00", gl, True)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Rental price AFN", "1,200.00", gl)
    els += e
    e, _ = field(fx, fy, half, "Rental deposit AFN", "2,000.00", gl)
    els += e
    e, fy = field(fx + half + 16, fy, half, "Landed unit cost", "2,194.92 (locked)", gl)
    els += e
    els += panel(fx, fy, fw, 78, None, gl)
    els.append(text(fx + 16, fy + 14, "SKU preview — generated on post", 11, MUTED, width=fw - 32, g=gl))
    c, _ = chip(fx + 16, fy + 36, "AC-VL-0308", VIOLET, g=gl, size=13)
    els += c
    els.append(text(fx + 140, fy + 40, "category · type · running no.", 11, FAINT, width=fw - 160, g=gl))
    els += btn(fx, doy + dch - 72, half, 44, "Back", "secondary", gl)
    els += btn(fx + half + 16, doy + dch - 72, half, 44, "Save & continue", "primary", gl)

    els += note_under(ox, oy,
        "This form runs ON POST for every PO line whose inventory_item_id IS NULL. Order inside the one transaction: INSERT inventory_items (sku, names, category, size, colour, purpose, prices, cost=landed_unit_cost, status='active')\n"
        "→ write the new id onto procurement_receipt_items.inventory_item_id AND back onto procurement_purchase_order_items.inventory_item_id → then post the stock_in row (defect D2).\n"
        "SKU is server-generated and unique per tenant. Opening WAC for the new item = landed_unit_cost. Cancelling the drawer cancels the whole post — no half-created items.", VIOLET)
    return els


def d11(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "11. GRN posted — stock, cost & payable",
                                     "Procurement", g, sub_active="Receipts (GRN)")
    e, y = page_header(cx, cy, cw, "GRN26-0008 posted",
                       [("Print GRN", "secondary"), ("View stock ledger", "secondary"),
                        ("Void receipt", "danger")],
                       "PO26-000012 · Istanbul Bridal Co. · posted 18 Sep 2026 14:22 by Ahmad Zaki", gl)
    els += e
    els.append(rect(cx, y, cw, 64, strokeColor=OK, backgroundColor=OK_BG, strokeWidth=1, groupIds=gl))
    els.append(text(cx + 20, y + 22, f"{ICON['check']}  Receipt posted — 36 units in · landed value AFN 107,068.00 "
                                     "· 2 new SKUs created · payable AP26-0042 opened",
                    14, OK, width=cw - 40, g=gl))
    y += 82

    e, y = sub_head(cx, y, cw, "Stock transactions created — inventory_stock_transactions", gl,
                    "reference_type = procurement_receipt")
    els += e
    e, y = table(cx, y, cw,
                 ["Txn #", "Item · SKU", "Type", "Warehouse", "Qty", "Unit cost (landed)",
                  "Value AFN", "WAC before → after"],
                 [["TRN26-000418", "White A-Line Gown · BD-AL-0114", ("stock_in", OK), "Main store",
                   "+2", "14,499.00", "28,998.00", "13,900.00 → 14,071.14"],
                  ["TRN26-000419", "Ivory Ball Gown · BD-BG-0077", ("stock_in", OK), "Main store",
                   "+2", "18,810.00", "37,620.00", "18,200.00 → 18,444.00"],
                  ["TRN26-000420", "Chantilly Veil · AC-VL-0308", ("stock_in", OK), "Main store",
                   "+12", "2,194.92", "26,339.00", ("new → 2,194.92", VIOLET)],
                  ["TRN26-000421", "Pearl Hair Comb · AC-HC-0309", ("stock_in", OK), "Main store",
                   "+20", "705.55", "14,111.00", ("new → 705.55", VIOLET)]],
                 gl, row_h=42, widths=[1.25, 2.3, 0.85, 1.0, 0.55, 1.25, 1.1, 1.6])
    els += e

    tw = (cw - 24) / 2
    els += panel(cx, y, tw, 176, "New items created", gl, "inventory_items rows written before the stock_in")
    e, _ = kv(cx + 16, y + 58, tw - 32, [
        ("Chantilly Veil (ivory)", ("AC-VL-0308", VIOLET)),
        ("Pearl Hair Comb", ("AC-HC-0309", VIOLET)),
        ("PO lines back-filled", ("2 · inventory_item_id set", OK)),
        ("Opening WAC", "= landed unit cost"),
    ], gl, step=26)
    els += e
    els += panel(cx + tw + 24, y, tw, 176, "Payable opened — finance_payables", gl,
                 "A/P is created here, not on the purchase order")
    e, _ = kv(cx + tw + 40, y + 58, tw - 32, [
        ("Payable #", ("AP26-0042", ROSE)),
        ("Amount", "AFN 107,068.00"),
        ("Terms · due", "Net 30 · 18 Oct 2026"),
        ("Supplier A/P balance", ("AFN 332,388.00", ROSE)),
    ], gl, step=26)
    els += e
    y += 190
    els += note(cx, y, cw,
                "Posted receipts are IMMUTABLE — there is no “Edit posted”. Void writes reversing stock transactions and a reversing payable, both linked to this GRN.",
                DANGER, gl)

    els += note_under(ox, oy,
        "Confirmation of one atomic post: procurement_receipts.status='posted' · procurement_receipt_items (landed_unit_cost stored) · inventory_items (2 created + WAC recomputed for all 4) ·\n"
        "inventory_stock_transactions × 4 (stock_in, unit_cost = landed) · finance_payables AP26-0042 opened · procurement_purchase_order_items.quantity_received recomputed · PO status → partial_received.\n"
        "Weighted Average Cost: new_wac = (on_hand_qty × old_wac + recv_qty × landed_unit_cost) / (on_hand_qty + recv_qty).\n"
        "VOID (defect D6) → reversing inventory_stock_transactions (negative, same landed cost), reversing finance_payables row, receipt status='void'. Never an in-place edit, never a delete.", OK)
    return els


def d12(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "12. Pay supplier", "Procurement", g,
                                     sub_active="Suppliers")
    e, y = page_header(cx, cy, cw, "Pay supplier",
                       [("Post payment", "primary"), ("Cancel", "secondary")],
                       "SPAY26-0015 · Istanbul Bridal Co. · A/P balance AFN 332,388.00", gl)
    els += e
    lw = 700
    rx, rw = cx + 724, cw - 724
    e, ly = sub_head(cx, y, lw, "Open payables — allocate the payment", gl, "finance_payables")
    els += e
    e, ly = table(cx, ly, lw,
                  ["", "Payable #", "PO #", "Issued", "Due", "Original", "Balance", "Allocate AFN"],
                  [[("✓", ACCENT), "AP26-0039", "PO26-000012", "09 Sep", "09 Oct", "94,116.00",
                    "225,320.00", ("50,000.00", ACCENT)],
                   [("✓", ACCENT), "AP26-0042", "PO26-000012", "18 Sep", "18 Oct", "107,068.00",
                    "107,068.00", ("30,000.00", ACCENT)],
                   [("☐", FAINT), "AP26-0044", "PO26-000017", "20 Sep", "20 Oct", "62,400.00",
                    "62,400.00", ("0.00", FAINT)]],
                  gl, row_h=44, widths=[0.35, 1.2, 1.2, 0.85, 0.85, 1.1, 1.1, 1.2])
    els += e
    e, ly = money_row(cx + lw - 380, ly, 380, [
        ("Payment amount", "AFN 80,000.00"),
        ("Allocated", ("AFN 80,000.00", OK)),
        ("Unallocated", ("AFN 0.00", MUTED)),
    ], gl, total=("Supplier A/P after posting", "AFN 252,388.00"))
    els += e
    els += note(cx, ly + 6, lw,
                "Unallocated money is not allowed to post — every payment settles named payables so A/P never drifts.",
                INFO, gl)

    e, ry = field(rx, y, rw, "Amount", "80,000.00", gl, True)
    els += e
    e, ry = select(rx, ry, rw, "Currency & rate", "AFN @ 1.000000", gl, True)
    els += e
    e, ry = select(rx, ry, rw, "Pay from account", "Cash drawer — Main branch", gl, True)
    els += e
    e, ry = select(rx, ry, rw, "Payment method", "Cash", gl, True)
    els += e
    e, ry = field(rx, ry, rw, "Paid at", "20 Sep 2026 11:40", gl, True)
    els += e
    e, ry = field(rx, ry, rw, "Reference no.", "RCPT-IST-8841", gl)
    els += e
    e, ry = textarea(rx, ry, rw, "Note", "Part payment against Sept deliveries", gl, rows=2)
    els += e
    els += panel(rx, ry, rw, 92, "Account after posting", gl)
    e, _ = kv(rx + 16, ry + 44, rw - 32, [
        ("Cash drawer balance", ("AFN 318,600 → 238,600", WARN)),
    ], gl)
    els += e

    els += note_under(ox, oy,
        "Post payment (one transaction): INSERT procurement_supplier_payments (payment_number, supplier_id, amount, currency + exchange_rate, payment_method_id, finance_account_id, paid_at, reference_no)\n"
        "→ INSERT finance_transactions (money OUT, posted) and store its id on the payment row so every money movement has exactly one ledger row (defect E2)\n"
        "→ UPDATE each allocated finance_payables.paid_amount / balance_amount / status (open → partial → paid) → refresh the cached procurement_purchase_orders.paid_amount, balance_amount, payment_status.\n"
        "finance_accounts balance stays derived (opening_balance + Σ posted finance_transactions); the displayed figure is the cached column refreshed in the same transaction.")
    return els


def d13(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "13. Supplier return · debit note", "Procurement", g,
                                     sub_active="Receipts (GRN)")
    e, y = page_header(cx, cy, cw, "Supplier return · DN26-0003",
                       [("Post debit note", "primary"), ("Save draft", "secondary")],
                       "Istanbul Bridal Co. · against GRN26-0008 · 22 Sep 2026", gl)
    els += e
    lw = 748
    rx, rw = cx + 772, cw - 772
    colw = (lw - 24) / 2
    e, y2 = select(cx, y, colw, "Receipt (GRN)", "GRN26-0008 · 18 Sep 2026", gl, True)
    els += e
    e, _ = select(cx + colw + 24, y, colw, "Reason", "Faulty — damaged beading", gl, True)
    els += e
    e, ly = sub_head(cx, y2, lw, "Received lines — choose what goes back", gl)
    els += e
    e, ly = table(cx, ly, lw,
                  ["", "Item · SKU", "Received", "Returnable", "Return qty", "Landed unit", "Credit AFN"],
                  [[("☐", FAINT), "White A-Line Gown · BD-AL-0114", "2", "2", ("0", FAINT),
                    "14,499.00", ("0.00", FAINT)],
                   [("✓", ACCENT), "Ivory Ball Gown · BD-BG-0077", "2", "2", ("1", ACCENT),
                    "18,810.00", ("18,810.00", ROSE)],
                   [("☐", FAINT), "Chantilly Veil · AC-VL-0308", "12", "12", ("0", FAINT),
                    "2,194.92", ("0.00", FAINT)],
                   [("☐", FAINT), "Pearl Hair Comb · AC-HC-0309", "20", "20", ("0", FAINT),
                    "705.55", ("0.00", FAINT)]],
                  gl, row_h=42, widths=[0.35, 2.4, 0.8, 0.85, 0.9, 1.0, 1.0])
    els += e
    e, ly = textarea(cx, ly, lw, "Reason detail (printed on the debit note)",
                     "Beading torn on bodice — supplier agreed credit on 21 Sep, ref WhatsApp Elif.", gl, rows=2)
    els += e
    els += panel(cx, ly, lw, 132, "Effect on posting", gl)
    hw2 = (lw - 48) / 2
    e, _ = kv(cx + 16, ly + 46, hw2, [
        ("Stock", ("stock_out −1 · BD-BG-0077", DANGER)),
        ("Value out", "AFN 18,810.00 at landed cost"),
        ("WAC", "unchanged — issue at current WAC"),
    ], gl, step=24)
    els += e
    e, _ = kv(cx + 32 + hw2, ly + 46, hw2, [
        ("Payable", ("AP26-0042 reduced", ROSE)),
        ("Balance", "107,068.00 → 88,258.00"),
        ("Ledger", "reversing finance_transactions row"),
    ], gl, step=24)
    els += e

    e, ry = sub_head(rx, y, rw, "Previous returns", gl)
    els += e
    els += empty_state(rx, ry, rw, 300, ICON["truck"], "No returns yet",
                       "Istanbul Bridal Co. has no posted\ndebit notes in the last 12 months.",
                       "New debit note", gl)
    els += panel(rx, ry + 316, rw, 200, "Rules", gl)
    els.append(text(rx + 16, ry + 348,
                    "• Only lines from a POSTED receipt\n  can be returned.\n"
                    "• Return qty ≤ received qty minus\n  quantity already returned.\n"
                    "• Credit is always at landed unit\n  cost — never at the raw unit cost.\n"
                    "• Posting is irreversible; correct it\n  with a second debit note.",
                    12, MUTED, width=rw - 32, g=gl))

    els += note_under(ox, oy,
        "Post debit note (one transaction): INSERT procurement_returns + return items (receipt_item_id, inventory_item_id, quantity, landed_unit_cost, reason) ·\n"
        "inventory_stock_transactions type='stock_out', quantity=−1, unit_cost = landed_unit_cost, reference_type='procurement_return' ·\n"
        "UPDATE finance_payables (AP26-0042 original 107,068.00 → 88,258.00) + reversing finance_transactions row · refresh the PO balance cache (defect D7).\n"
        "A return NEVER edits the original receipt — posted receipts stay immutable.", ROSE)
    return els


def _report_tiles(x, y, w, active, gl):
    tiles = [("Purchase register", ICON["receipt"], "PO spend by supplier & period"),
             ("Stock-in report", ICON["inventory"], "Every stock-in by source"),
             ("Supplier ledger & aging", ICON["ledger"], "A/P buckets per supplier"),
             ("PO fulfilment", ICON["truck"], "Ordered vs received vs late"),
             ("Price history", ICON["chart"], "Unit & landed cost per item")]
    n = len(tiles)
    tw = (w - 19 * (n - 1)) / n
    els = []
    for i, (name, icon, sub) in enumerate(tiles):
        on = i == active
        tx = x + i * (tw + 19)
        els.append(rect(tx, y, tw, 84, strokeColor=ACCENT if on else HAIRLINE,
                        backgroundColor=ACCENT_BG if on else BG, strokeWidth=2 if on else 1, groupIds=gl))
        els.append(text(tx + 14, y + 13, icon, 14, ACCENT if on else MUTED, g=gl))
        els.append(text(tx + 14, y + 36, name, 12.5, ACCENT if on else INK, width=tw - 28, g=gl))
        els.append(text(tx + 14, y + 56, sub, 10.5, MUTED, width=tw - 28, g=gl))
    return els, y + 100


def d14(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "14. Reports hub · Purchase register", "Procurement", g,
                                     sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Procurement reports",
                       [("Export CSV", "secondary"), ("Print", "ghost")],
                       "All figures in AFN at the rate snapshot of each document", gl)
    els += e
    e, y = _report_tiles(cx, y, cw, 0, gl)
    els += e
    colw, gap = 266, 24
    e, y2 = field(cx, y, colw, "From", "01 Sep 2026", gl, True)
    els += e
    e, _ = field(cx + colw + gap, y, colw, "To", "30 Sep 2026", gl, True)
    els += e
    e, _ = select(cx + 2 * (colw + gap), y, colw, "Supplier", "All suppliers", gl)
    els += e
    e, _ = select(cx + 3 * (colw + gap), y, colw, "Status", "All except draft", gl)
    els += e
    y = y2

    lw = 560
    e, _ = bar_chart(cx, y, lw, 200, "Purchase spend by supplier · AFN", [
        ("Istanbul", 1.0, "345k"), ("Dubai", 0.59, "203k"), ("Kabul", 0.43, "148k"),
        ("Herat", 0.25, "86k")], gl)
    els += e
    els += panel(cx + lw + 24, y, cw - lw - 24, 200, "Period totals", gl,
                 "01–30 Sept 2026 · 4 purchase orders")
    e, _ = money_row(cx + lw + 40, y + 56, cw - lw - 56, [
        ("Ordered value", "AFN 782,640.00"),
        ("Received value (landed)", "AFN 601,668.00"),
        ("Paid to suppliers", "AFN 268,000.00"),
    ], gl, total=("Outstanding A/P", "AFN 514,640.00"))
    els += e
    y += 216
    e, y = table(cx, y, cw,
                 ["PO #", "Supplier", "Date", "Items", "Total AFN", "Received", "Paid AFN",
                  "Balance AFN", "Status"],
                 [["PO26-000012", "Istanbul Bridal Co.", "04 Sep", "6", "345,320.00", ("60%", WARN),
                   "120,000.00", ("225,320.00", ROSE), ("Partial", WARN)],
                  ["PO26-000013", "Dubai Fashion House", "07 Sep", "4", "202,920.00", ("0%", MUTED),
                   "0.00", ("202,920.00", ROSE), ("Ordered", INFO)],
                  ["PO26-000015", "Kabul Textile Traders", "09 Sep", "5", "148,000.00", ("100%", OK),
                   "148,000.00", "0.00", ("Received", OK)],
                  ["PO26-000014", "Herat Silk House", "11 Sep", "3", "86,400.00", ("—", FAINT),
                   "0.00", ("86,400.00", MUTED), ("Draft", MUTED)],
                  [("TOTAL · 4 POs", INK), "", "", ("18", INK), ("782,640.00", INK), "",
                   ("268,000.00", INK), ("514,640.00", ROSE), ""]],
                 gl, row_h=40, widths=[1.2, 1.7, 0.8, 0.6, 1.15, 0.9, 1.15, 1.2, 0.9])
    els += e

    els += note_under(ox, oy,
        "Purchase register = procurement_purchase_orders JOIN _items JOIN procurement_suppliers, filtered on order_date BETWEEN from AND to, values × exchange_rate.\n"
        "Received value is taken from procurement_receipt_items.landed_unit_cost × quantity_received — it is the SAME number that hit inventory, so the register reconciles to the stock-in report.\n"
        "Paid / balance come from finance_payables + procurement_supplier_payments, never from cached PO columns. Drafts are excluded from spend by default.\n"
        "Export CSV runs the identical query; the tiles switch report without losing the period filter.")
    return els


def d15(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "15. Stock-in report — by source", "Procurement", g,
                                     sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Stock-in report",
                       [("Export CSV", "secondary"), ("Print", "ghost")],
                       "01–30 Sept 2026 · all warehouses · every positive stock movement, grouped by source", gl)
    els += e
    e, y = _report_tiles(cx, y, cw, 1, gl)
    els += e
    els += filter_chips(cx, y, ["All sources", "Purchase receipt", "Manual entry", "Sale return",
                                "Rental return", "Transfer in"], 0, gl)
    y += 44

    lw = 520
    e, _ = bar_chart(cx, y, lw, 196, "Stock-in value by source · AFN", [
        ("Purchase", 1.0, "413k"), ("Manual", 0.23, "96k"), ("Sale ret.", 0.13, "53k"),
        ("Rental ret.", 0.2, "84k"), ("Transfer", 0.08, "32k")], gl)
    els += e
    e, _ = table(cx + lw + 24, y, cw - lw - 24,
                 ["Source", "Ref. type", "Txns", "Qty in", "Value AFN", "% value"],
                 [["Purchase receipt", "procurement_receipt", "6", "48", ("412,600.00", OK), "60.9%"],
                  ["Manual entry", "manual_entry", "3", "12", "96,400.00", "14.2%"],
                  ["Sale return restock", "sales_return", "4", "4", "52,800.00", "7.8%"],
                  ["Rental return", "rental_return", "9", "9", "84,200.00", "12.4%"],
                  ["Transfer in", "transfer", "2", "6", "32,000.00", "4.7%"],
                  [("TOTAL", INK), "", ("24", INK), ("79", INK), ("678,000.00", INK), ("100%", INK)]],
                 gl, row_h=32, widths=[1.6, 1.5, 0.6, 0.7, 1.1, 0.75])
    els += e
    y += 212

    e, y = table(cx, y, cw,
                 ["Date", "Txn #", "Source", "Source document", "Item · SKU", "Warehouse",
                  "Qty", "Unit cost", "Value AFN"],
                 [["18 Sep", "TRN26-000418", ("Purchase receipt", OK), ("GRN26-0008 →", INFO),
                   "White A-Line Gown · BD-AL-0114", "Main store", "+2", "14,499.00", "28,998.00"],
                  ["18 Sep", "TRN26-000420", ("Purchase receipt", OK), ("GRN26-0008 →", INFO),
                   "Chantilly Veil · AC-VL-0308", "Main store", "+12", "2,194.92", "26,339.00"],
                  ["16 Sep", "TRN26-000411", ("Manual entry", VIOLET), ("MSE26-0011 →", INFO),
                   "Satin Gloves · AC-GL-0045", "Main store", "+10", "480.00", "4,800.00"],
                  ["14 Sep", "TRN26-000402", ("Sale return", WARN), ("SR26-0004 →", INFO),
                   "Blush Bridesmaid · BD-BM-0231", "Main store", "+1", "6,840.00", "6,840.00"],
                  ["12 Sep", "TRN26-000396", ("Rental return", INFO), ("RRN26-0021 →", INFO),
                   "Ivory Ball Gown · BD-BG-0077", "Rental rack", "+1", "18,200.00", "18,200.00"],
                  ["09 Sep", "TRN26-000388", ("Transfer in", MUTED), ("TRF26-0006 →", INFO),
                   "Chantilly Veil · AC-VL-0308", "Herat branch", "+4", "2,194.92", "8,779.68"]],
                 gl, row_h=36, widths=[0.7, 1.25, 1.25, 1.25, 2.3, 1.0, 0.5, 1.0, 1.05])
    els += e
    els += note(cx, y, cw,
                "RECONCILIATION — opening stock value 01 Sep 4,812,000.00 + stock-ins 678,000.00 − stock-outs 486,300.00 = closing 5,003,700.00 · "
                "Σ stock-in rows = inventory increase · variance AFN 0.00  ✓", INFO, gl)

    els += note_under(ox, oy,
        "THE report the brief asked for. Source = inventory_stock_transactions WHERE quantity > 0 AND type IN (stock_in, transfer_in, rent_return, adjustment+), grouped by reference_type.\n"
        "Value = quantity × unit_cost × exchange_rate — for purchase rows unit_cost IS the landed_unit_cost stored on procurement_receipt_items, so this report ties exactly to the purchase register.\n"
        "Source document deep-links to GRN / manual entry / sales return / rental return / transfer. Voided receipts appear as their reversing negative rows, so the totals self-correct.\n"
        "Reconciliation line proves Σ stock-ins − Σ stock-outs = closing − opening valuation; a non-zero variance means someone mutated stock outside the ledger (defect D5).", INFO)
    return els


def d16(i):
    ox, oy = grid_pos(i, COLS, row_gap=D_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "16. Supplier ledger & aging · fulfilment · price history",
                                     "Procurement", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Supplier ledger & aging",
                       [("Export CSV", "secondary"), ("Print", "ghost")],
                       "As at 30 Sept 2026 · A/P buckets from finance_payables.due_date", gl)
    els += e
    e, y = _report_tiles(cx, y, cw, 2, gl)
    els += e
    e, y = table(cx, y, cw,
                 ["Supplier", "Open docs", "Current", "1–30 days", "31–60 days", "61–90 days",
                  "90+ days", "Total A/P AFN"],
                 [["Istanbul Bridal Co.", "2", "107,068.00", ("225,320.00", WARN), "0.00", "0.00",
                   "0.00", ("332,388.00", ROSE)],
                  ["Dubai Fashion House", "1", "202,920.00", "0.00", "0.00", "0.00", "0.00",
                   ("202,920.00", ROSE)],
                  ["Kabul Textile Traders", "2", "0.00", "0.00", ("88,000.00", DANGER),
                   ("30,000.00", DANGER), "0.00", ("118,000.00", DANGER)],
                  ["Mashhad Veil Supply", "1", "0.00", ("92,000.00", WARN), "0.00", "0.00", "0.00",
                   ("92,000.00", ROSE)],
                  [("TOTAL", INK), ("6", INK), ("309,988.00", INK), ("317,320.00", INK),
                   ("88,000.00", DANGER), ("30,000.00", DANGER), ("0.00", INK), ("745,308.00", ROSE)]],
                 gl, row_h=40, widths=[1.8, 0.8, 1.1, 1.1, 1.1, 1.1, 1.0, 1.25])
    els += e

    hw = (cw - 24) / 2
    e, ly = sub_head(cx, y + 4, hw, "PO fulfilment — ordered vs received", gl, "late = expected < today")
    els += e
    e, _ = table(cx, ly, hw, ["PO #", "Ordered", "Received", "Fill %", "Days late", "Status"],
                 [["PO26-000012", "65", "39", ("60%", WARN), ("0", MUTED), ("Partial", WARN)],
                  ["PO26-000013", "22", "0", ("0%", MUTED), ("0", MUTED), ("Ordered", INFO)],
                  ["PO26-000015", "31", "31", ("100%", OK), ("6", DANGER), ("Received late", DANGER)],
                  ["PO26-000010", "18", "18", ("100%", OK), ("0", MUTED), ("Closed", MUTED)]],
                 gl, row_h=38, widths=[1.3, 0.8, 0.9, 0.8, 0.9, 1.2])
    els += e
    e, ry = sub_head(cx + hw + 24, y + 4, hw, "Price history — White A-Line Gown", gl, "BD-AL-0114")
    els += e
    e, _ = table(cx + hw + 24, ry, hw,
                 ["GRN #", "Date", "Qty", "Unit cost", "Landed unit", "Δ"],
                 [["GRN26-0002", "21 Jun", "4", "12,212.00", "12,470.00", ("—", FAINT)],
                  ["GRN26-0005", "16 Aug", "6", "12,638.00", "13,010.00", ("+4.3%", WARN)],
                  ["GRN26-0007", "09 Sep", "4", "13,172.00", "13,860.00", ("+6.5%", WARN)],
                  ["GRN26-0008", "18 Sep", "2", "13,172.00", ("14,499.00", ACCENT), ("+4.6%", DANGER)]],
                 gl, row_h=38, widths=[1.2, 0.8, 0.55, 1.05, 1.1, 0.7])
    els += e

    els += note_under(ox, oy,
        "Aging: buckets = today − finance_payables.due_date for rows WHERE status IN (open, partial); the ledger is the only A/P source, so this report and the Finance A/P pillar cannot disagree (defect D4).\n"
        "Fulfilment: SUM(quantity_ordered) vs recomputed SUM(quantity_received) per PO, plus days late = received_date − expected_date. Over-receipts (fill > 100%) are flagged with their approver.\n"
        "Price history: procurement_receipt_items per inventory_item_id ordered by received_date — raw unit_cost AND landed_unit_cost side by side; the landed column is what moved the weighted average cost.")
    return els


D_SCREENS = [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16]


def desktop() -> list:
    els = board_title(0, -270, "BOMS Desktop — Procurement",
                      "Suppliers → PO → approval → GRN with landed-cost allocation → weighted average cost → finance_payables → payment → supplier returns → "
                      "procurement & stock-in reports · AFN base, USD POs at a rate snapshot · September 2026")
    for r, lab in enumerate(SECTIONS):
        els += section_label(0, r * (DESK_H + D_ROW_GAP) - 66, lab)
    for i, fn in enumerate(D_SCREENS):
        els += fn(i)
    els += flow_arrows(len(D_SCREENS), COLS, row_gap=D_ROW_GAP)
    return els


# ══════════════════════════════════════════════════════════════════
#  MOBILE
# ══════════════════════════════════════════════════════════════════

def m1(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "1. Procurement hub", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "Procurement", right=ICON["search"], g=gl)
    els += e
    e, y = stat_row(cx, y, cw, [("Open POs", "5", INK, None, ICON["truck"]),
                                ("Awaiting receipt", "3", WARN, None, ICON["clock"])], h=80, g=gl)
    els += e
    e, y = stat_row(cx, y, cw, [("Total A/P AFN", "745,308", ROSE, None, ICON["ledger"]),
                                ("Spend MTD AFN", "782,640", INK, None, ICON["chart"])], h=80, g=gl)
    els += e
    e, y = sub_head(cx, y, cw, "Open purchase orders", gl, "All →")
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000012 · Istanbul Bridal",
                                 "Expected 18 Sep · 6 lines · AFN 345,320",
                                 "Received 60% · balance 225,320"], gl, badge=("Partial", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000013 · Dubai Fashion",
                                 "Expected 21 Sep · 4 lines · AFN 202,920",
                                 "Received 0% · balance 202,920"], gl, badge=("Ordered", INFO))
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000015 · Kabul Textile",
                                 "Expected 14 Sep · 5 lines · AFN 148,000",
                                 "Delivery overdue 6 days"], gl, badge=("Late", DANGER))
    els += e
    els.append(rect(cx, y, cw, 46, strokeColor=DANGER, backgroundColor=DANGER_BG, strokeWidth=1,
                    groupIds=gl))
    els.append(text(cx + 14, y + 15, f"{ICON['alert']}  Overdue A/P  AFN 118,000  →", 12.5, DANGER,
                    width=cw - 28, g=gl))
    els += fab(cx + cw, oy + TITLE_H + PHONE_H - 138, f"{ICON['add']} New PO", gl)

    els += m_note_under(ox, oy,
        "Read only. KPIs from procurement_purchase_orders +\n"
        "finance_payables (A/P is NEVER read from the PO row).\n"
        "Tap a PO → mobile screen 5. FAB → screen 4.")
    return els


def m2(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "2. Suppliers", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "Suppliers", left=ICON["back"], right=ICON["filter"], g=gl)
    els += e
    els += search_bar(cx, y, cw, "Search suppliers…", gl)
    y += 52
    els += filter_chips(cx, y, ["All", "Active", "A/P due"], 0, gl)
    y += 42
    for name, meta, bal, badge in [
        ("Istanbul Bridal Co.", "SUP26-0001 · USD · Net 30", "A/P AFN 332,388", ("3 POs", INFO)),
        ("Dubai Fashion House", "SUP26-0002 · USD · Net 15", "A/P AFN 202,920", ("1 PO", INFO)),
        ("Kabul Textile Traders", "SUP26-0003 · AFN · Net 7", "A/P AFN 118,000 overdue", ("Late", DANGER)),
        ("Herat Silk House", "SUP26-0004 · AFN · Cash", "A/P AFN 0.00", ("Active", OK)),
        ("Mashhad Veil Supply", "SUP26-0005 · AFN · Net 30", "A/P AFN 92,000", ("Active", OK)),
    ]:
        e, y = list_card(cx, y, cw, [name, meta, bal], gl, badge=badge)
        els += e
    els += fab(cx + cw, oy + TITLE_H + PHONE_H - 138, f"{ICON['add']} New supplier", gl)

    els += m_note_under(ox, oy,
        "READS procurement_suppliers; the balance line is\n"
        "SUM(finance_payables.balance_amount) per supplier.\n"
        "FAB opens the same drawer form as desktop screen 4\n"
        "(slides from the LEFT when the tenant is RTL).")
    return els


def m3(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "3. Supplier detail", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "Istanbul Bridal", left=ICON["back"], right=ICON["settings"], g=gl)
    els += e
    c, xx = chip(cx, y, "Active", OK, g=gl)
    els += c
    c, xx = chip(xx, y, "USD @ 71.20", INFO, g=gl)
    els += c
    c, xx = chip(xx, y, "Net 30", MUTED, g=gl)
    els += c
    y += 34
    els += panel(cx, y, cw, 104, "Contact", gl)
    e, _ = kv(cx + 16, y + 40, cw - 32, [("Elif Demir", "+90 532 441 8820"),
                                         ("Email", "elif@istanbulbridal.com")], gl, step=24)
    els += e
    y += 118
    els += panel(cx, y, cw, 118, "A/P — finance_payables", gl)
    e, _ = money_row(cx + 16, y + 42, cw - 32, [("Current", "AFN 107,068"),
                                                ("1–30 days", "AFN 225,320")], gl,
                     total=("Owed", "AFN 332,388"))
    els += e
    y += 132
    e, y = tabs(cx, y, cw, ["Purchase orders", "Receipts", "Payments"], 0, gl)
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000012 · 04 Sep", "AFN 345,320 · received 60%"], gl,
                     badge=("Partial", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["PO26-000008 · 02 Aug", "AFN 241,400 · received 100%"], gl,
                     badge=("Closed", MUTED))
    els += e
    els += btn(cx, y + 4, (cw - 12) / 2, 44, "New PO", "primary", gl)
    els += btn(cx + (cw + 12) / 2, y + 4, (cw - 12) / 2, 44, "Pay", "secondary", gl)

    els += m_note_under(ox, oy,
        "READS procurement_suppliers, _purchase_orders,\n"
        "_receipts, _supplier_payments, finance_payables.\n"
        "Items supplied + price history live on desktop only —\n"
        "mobile keeps the three action-oriented tabs.")
    return els


def m4(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "4. Create PO", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "New purchase order", left=ICON["back"], g=gl)
    els += e
    half = (cw - 12) / 2
    e, y = select(cx, y, cw, "Supplier", "Istanbul Bridal Co. (USD)", gl, True)
    els += e
    e, _ = field(cx, y, half, "Order date", "12 Sep 2026", gl, True)
    els += e
    e, y = field(cx + half + 12, y, half, "Expected", "26 Sep 2026", gl)
    els += e
    e, _ = select(cx, y, half, "Warehouse", "Main store", gl, True)
    els += e
    e, y = field(cx + half + 12, y, half, "Rate", "71.20", gl, True)
    els += e
    e, y = sub_head(cx, y, cw, "Lines (4)", gl, "Add →")
    els += e
    for nm, meta, tot, badge in [
        ("White A-Line Gown", "BD-AL-0114 · 6 × USD 185.00", "USD 1,110.00", ("Existing", INFO)),
        ("Chantilly Veil (ivory)", "no SKU · 12 × USD 28.00", "USD 336.00", ("NEW", VIOLET)),
    ]:
        e, y = list_card(cx, y, cw, [nm, meta, tot], gl, badge=badge)
        els += e
    els.append(rect(cx, y, cw, 42, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=gl))
    els.append(text(cx + 14, y + 13, f"{ICON['add']}  Add line — item or new name", 12.5, MUTED,
                    width=cw - 28, g=gl))
    y += 54
    e, y = money_row(cx, y, cw, [("Subtotal", "USD 2,586.00"),
                                 ("Other cost (shipping)", "USD 137.64")], gl,
                     total=("Total · AFN 194,010", "USD 2,723.64"))
    els += e
    els += btn(cx, y, half, 44, "Save draft", "secondary", gl)
    els += btn(cx + half + 12, y, half, 44, "Submit", "primary", gl)

    els += m_note_under(ox, oy,
        "INSERT procurement_purchase_orders (status='draft',\n"
        "exchange_rate snapshot) + _purchase_order_items.\n"
        "NEW lines keep inventory_item_id NULL — the GRN creates\n"
        "the item. Header other_cost is allocated at receipt, not now.")
    return els


def m5(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "5. PO detail", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "PO26-000012", left=ICON["back"], right=ICON["print"], g=gl)
    els += e
    els.append(text(cx, y - 4, "Istanbul Bridal Co. · ordered 04 Sep · USD @ 71.20", 11.5, MUTED,
                    width=cw, g=gl))
    y += 18
    e, y = timeline(cx, y, cw, [("Draft", "done"), ("Ordered", "done"), ("Partial", "current"),
                                ("Received", "todo"), ("Closed", "todo")], gl)
    els += e
    els.append(text(cx, y - 6, "Approved by Ahmad Zaki · 04 Sep 09:12", 11, OK, width=cw, g=gl))
    y += 16
    e, y = money_row(cx, y, cw, [("PO total", "AFN 345,320"), ("Paid", "AFN 120,000")], gl,
                     total=("Balance (A/P)", "AFN 225,320"))
    els += e
    e, y = sub_head(cx, y, cw, "Lines", gl, "4 of 6 received")
    els += e
    for nm, meta, badge in [
        ("White A-Line Gown", "ord 6 · recv 4 · remaining 2", ("Partial", WARN)),
        ("Chantilly Veil (ivory)", "ord 12 · recv 0 · SKU on receipt", ("Pending", VIOLET)),
    ]:
        e, y = list_card(cx, y, cw, [nm, meta], gl, badge=badge)
        els += e
    e, y = list_card(cx, y, cw, ["GRN26-0007 · posted 09 Sep", "Landed value AFN 94,116"], gl,
                     badge=("Posted", OK))
    els += e
    els += btn(cx, y, cw, 46, "Receive goods", "primary", gl)

    els += m_note_under(ox, oy,
        "Approve (draft → ordered) writes approved_by /\n"
        "approved_at. Only ordered / partial POs can be received.\n"
        "Balance is DERIVED from finance_payables. Cancel is hidden\n"
        "once a posted receipt exists — use a debit note instead.")
    return els


def m6(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "6. Receive goods", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "Receive · GRN26-0008", left=ICON["back"], g=gl)
    els += e
    half = (cw - 12) / 2
    e, _ = select(cx, y, half, "Warehouse", "Main store", gl, True)
    els += e
    e, y = field(cx + half + 12, y, half, "Date", "18 Sep 2026", gl, True)
    els += e
    e, y = sub_head(cx, y, cw, "Receiving now", gl, "4 lines")
    els += e
    for nm, l1, l2, badge in [
        ("White A-Line Gown", "ord 6 · already 4 · now 2", "13,172 + 1,327 alloc = 14,499 landed",
         ("2 left", WARN)),
        ("Chantilly Veil · NEW", "ord 12 · already 0 · now 12", "1,994 + 200.92 = 2,194.92 landed",
         ("SKU?", VIOLET)),
        ("Pearl Hair Comb · NEW", "ord 20 · already 0 · now 20", "641 + 64.55 = 705.55 landed",
         ("SKU?", VIOLET)),
    ]:
        e, y = list_card(cx, y, cw, [nm, l1, (l2, ACCENT, 11.5)], gl, badge=badge)
        els += e
    e, y = field(cx, y, cw, "Header other cost — freight & customs (AFN)", "9,800.00", gl)
    els += e
    els.append(text(cx, y - 6, "Allocated pro-rata by line value at post time", 11, ACCENT,
                    width=cw, g=gl))
    y += 14
    e, y = money_row(cx, y, cw, [("Goods value", "AFN 97,268"), ("Other cost", "AFN 9,800")], gl,
                     total=("Landed → inventory", "AFN 107,068"))
    els += e
    els += btn(cx, y, cw, 46, "Post receipt", "primary", gl)

    els += m_note_under(ox, oy,
        "Post: procurement_receipts + _receipt_items (landed_unit_cost\n"
        "stored) → create missing inventory_items & back-fill the PO\n"
        "line → inventory_stock_transactions stock_in at LANDED cost →\n"
        "recompute WAC → open finance_payables. Over-receipt blocked.")
    return els


def m7(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "7. Pay supplier", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "Pay supplier", left=ICON["back"], g=gl)
    els += e
    e, y = select(cx, y, cw, "Supplier", "Istanbul Bridal Co.", gl, True)
    els += e
    e, y = sub_head(cx, y, cw, "Open payables", gl, "allocate")
    els += e
    e, y = list_card(cx, y, cw, ["✓  AP26-0039 · PO26-000012",
                                 "Balance 225,320 · due 09 Oct",
                                 "Allocate AFN 50,000"], gl, badge=("Part", WARN))
    els += e
    e, y = list_card(cx, y, cw, ["✓  AP26-0042 · PO26-000012",
                                 "Balance 107,068 · due 18 Oct",
                                 "Allocate AFN 30,000"], gl, badge=("Part", WARN))
    els += e
    half = (cw - 12) / 2
    e, _ = field(cx, y, half, "Amount AFN", "80,000.00", gl, True)
    els += e
    e, y = select(cx + half + 12, y, half, "Method", "Cash", gl, True)
    els += e
    e, y = select(cx, y, cw, "Pay from account", "Cash drawer — Main branch", gl, True)
    els += e
    e, y = money_row(cx, y, cw, [("Allocated", "AFN 80,000"), ("Unallocated", "AFN 0")], gl,
                     total=("A/P after", "AFN 252,388"))
    els += e
    els += btn(cx, y, cw, 46, "Post payment", "primary", gl)

    els += m_note_under(ox, oy,
        "INSERT procurement_supplier_payments + finance_transactions\n"
        "(money OUT) with the ledger id stored on the payment row →\n"
        "update each allocated finance_payables balance/status →\n"
        "refresh the cached PO paid_amount / payment_status.")
    return els


def m8(i):
    ox, oy = grid_pos(i, M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    g = nid(); gl = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "8. Stock-in report", g, active_tab="More")
    e, y = phone_header(cx, cy, cw, "Stock-in report", left=ICON["back"], right=ICON["export"], g=gl)
    els += e
    els += filter_chips(cx, y, ["Sept 2026", "All sources", "All WH"], 0, gl)
    y += 44
    e, y = bar_chart(cx, y, cw, 184, "Stock-in value by source · AFN", [
        ("Purch.", 1.0, "413k"), ("Manual", 0.23, "96k"), ("Sale ret", 0.13, "53k"),
        ("Rent ret", 0.2, "84k"), ("Transfer", 0.08, "32k")], gl)
    els += e
    e, y = table(cx, y, cw, ["Source", "Qty", "Value AFN"],
                 [["Purchase receipt", "48", ("412,600", OK)],
                  ["Manual entry", "12", "96,400"],
                  ["Sale return restock", "4", "52,800"],
                  ["Rental return", "9", "84,200"],
                  ["Transfer in", "6", "32,000"],
                  [("TOTAL · 24 txns", INK), ("79", INK), ("678,000", INK)]],
                 gl, row_h=32, widths=[1.7, 0.6, 1.1])
    els += e
    els += note(cx, y, cw,
                "Opening 4,812,000 + in 678,000 − out 486,300\n= closing 5,003,700 · variance 0.00 ✓", INFO, gl)

    els += m_note_under(ox, oy,
        "inventory_stock_transactions WHERE quantity > 0 in the period,\n"
        "grouped by reference_type. Purchase rows are valued at the\n"
        "landed_unit_cost stored on procurement_receipt_items, so this\n"
        "ties to the purchase register. Tap a row → the source document.", INFO)
    return els


M_SCREENS = [m1, m2, m3, m4, m5, m6, m7, m8]


def mobile() -> list:
    els = board_title(0, -190, "BOMS Mobile — Procurement",
                      "Hub → suppliers → PO → receive with visible landed cost → pay → stock-in report · "
                      "AFN base with USD rate snapshot · September 2026")
    for r, lab in enumerate(M_SECTIONS):
        els += section_label(0, r * (PHONE_H + M_ROW_GAP) - 56, lab)
    for i, fn in enumerate(M_SCREENS):
        els += fn(i)
    els += flow_arrows(len(M_SCREENS), M_COLS, PHONE_W, PHONE_H, row_gap=M_ROW_GAP)
    return els
