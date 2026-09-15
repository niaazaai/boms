#!/usr/bin/env python3
"""BOMS — Sales module wireframes (desktop + mobile).

READING ORDER — one heading per row, same pattern as Inventory / Procurement:

    A. DASHBOARD     A1
    B. COUNTER       B1 ticket · B2 register-customer drawer · B3 printed slip
    C. ORDERS        C1 list · C2 detail · C3 scan-return drawer
    D. RETURNS       D1 scan sale-return · D2 posted
    E. CUSTOMERS     E1 list · E2 new drawer · E3 profile
    F. REPORTS       F1 summary · F2 rental performance · F3 deposits

The counter is one screen, not a wizard:

    1. Search the customer by phone. Missing → register in a drawer.
       Walk-in is fine for a sale-only ticket.
    2. Scan or search items. Each line has Rent | Sell and a price input
       pre-filled with the catalogue price — staff may type a higher amount.
    3. Collect, then print the slip. Barcode + QR of the order number sit at
       the foot of the slip so the next visit is a scan, not a search.
    4. Return: scan the slip (or the garment), take any remaining money,
       put the dress back in stock.

Rules:
  • line_type (sale | rental) is authoritative; header badge is derived.
  • A rental line requires a named customer.
  • Deposits are a liability, never income.
  • Every create / edit is a drawer over its list.
  • Language switcher shows the language name only.
"""

from __future__ import annotations

from dsl import *  # noqa: F401,F403

DESK_COLS = 4
PHONE_COLS = 6

SECTION_COLORS = {
    "DASHBOARD": ACCENT,
    "COUNTER": ROSE,
    "ORDERS": INFO,
    "RETURNS": WARN,
    "CUSTOMERS": VIOLET,
    "REPORTS": OK,
}

LW, GAP, RW = 704, 24, 408


# ── local compositions ────────────────────────────────────────────

def _lab(x, y, s, g, color=MUTED, size=11.5):
    return [text(x, y, s, size, color, g=g)]


def _panel(x, y, w, h, title=None, g=None, bg=BG, color=HAIRLINE):
    g = g or []
    els = [rect(x, y, w, h, strokeColor=color, backgroundColor=bg, strokeWidth=1, groupIds=g)]
    if title:
        els.append(text(x + 16, y + 14, title, 12, MUTED if color == HAIRLINE else color,
                        width=w - 32, g=g))
    return els


def _kv(x, y, w, label, value, g, color=INK, size=13):
    return [text(x, y, label, 12, MUTED, width=w * 0.55, g=g),
            text(x + w * 0.45, y - 1, value, size, color, "right", w * 0.55, g=g)]


def _spec(cx, ox, oy, cw, body, color=ACCENT):
    return note(cx, oy + TITLE_H + DESK_H - 92, cw, body, color)


def _sheet_bar(cx, y, cw, g, search="Search…"):
    els = search_bar(cx, y, 440, search, g)
    els += btn(cx + 456, y, 130, 40, f"{ICON['filter']}  Filters", "secondary", g)
    els += btn(cx + cw - 150, y, 150, 40, "Columns ▾", "secondary", g)
    return els, y + 52


def _chiprow(x, y, items, g):
    els, xx = [], x
    for lab, col in items:
        e, xx = chip(xx, y, lab, col, g=g)
        els += e
    return els, xx


def _toggle_rent_sell(x, y, w, mode, g):
    """Rent | Sell segmented control. mode 0 = rent, 1 = sell."""
    els = [rect(x, y, w, 28, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=g)]
    sw = w / 2
    for i, lab in enumerate(["Rent", "Sell"]):
        on = i == mode
        col = ACCENT if i == 0 else INFO
        if on:
            els.append(rect(x + i * sw + 2, y + 2, sw - 4, 24, strokeColor=col,
                            backgroundColor=ACCENT_BG if i == 0 else INFO_BG,
                            strokeWidth=1, groupIds=g))
        els.append(text(x + i * sw, y + 6, lab, 11, col if on else MUTED, "center", sw, g))
    return els


def _price_input(x, y, w, value, g, label="Price AFN"):
    els = [rect(x, y, w, 28, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
           text(x + 8, y + 6, value, 12, INK, width=w - 16, g=g)]
    return els


def _orders_backdrop(cx, cy, cw, g):
    els, y = page_header(cx, cy, cw, "Orders",
                         actions=[("＋ New ticket", "primary")],
                         subtitle="Today · Main branch", g=g)
    els += search_bar(cx, y, 400, "Order # · name · phone…", g)
    e, _ = table(cx, y + 52, cw,
                 ["Order #", "Customer", "Type", "Total", "Status"],
                 [["SO26-000019", "Sara Ahmadi", ("Mixed", VIOLET), "16,000", ("Confirmed", INFO)],
                  ["SO26-000018", "Walk-in", ("Sale", INFO), "12,600", ("Completed", OK)],
                  ["SO26-000017", "Maryam Noori", ("Rental", ACCENT), "9,000", ("Out", ACCENT)]],
                 g, row_h=40, sheet=True, widths=[1.2, 1.5, 0.9, 0.9, 1.0])
    els += e
    return els


def _customers_backdrop(cx, cy, cw, g):
    els, y = page_header(cx, cy, cw, "Customers",
                         actions=[("＋ New customer", "primary")],
                         subtitle="412 customers", g=g)
    els += search_bar(cx, y, 400, "Search by phone — 0700 12 34 56", g)
    e, _ = table(cx, y + 52, cw,
                 ["Code", "Name", "Phone", "Wedding", "Balance"],
                 [["CUS26-0117", "Sara Ahmadi", "0700 12 34 56", "28 Sep", ("9,200", WARN)],
                  ["CUS26-0094", "Maryam Noori", "0700 12 34 57", "16 Sep", ("4,500", WARN)],
                  ["CUS26-0088", "Fatima Rahimi", "0700 12 34 58", "12 Sep", "0"]],
                 g, row_h=40, sheet=True, widths=[1.1, 1.4, 1.3, 1.0, 0.9])
    els += e
    return els


def _report_card(x, y, w, h, icon, title, desc, g, on=False):
    return [
        rect(x, y, w, h, strokeColor=ACCENT if on else HAIRLINE,
             backgroundColor=ACCENT_BG if on else BG, strokeWidth=2 if on else 1, groupIds=g),
        text(x + 14, y + 13, icon, 15, ACCENT, g=g),
        text(x + 14, y + 40, title, 12.5, INK, width=w - 28, g=g),
        text(x + 14, y + 60, desc, 10.5, MUTED, width=w - 28, g=g),
    ]


def _sticky(x, y, w, label, value, cta, g, sub=None):
    els = [rect(x, y, w, 76, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=g),
           text(x + 14, y + 11, label, 10.5, MUTED, width=w - 160, g=g),
           text(x + 14, y + 28, value, 18, INK, width=w - 160, g=g)]
    if sub:
        els.append(text(x + 14, y + 54, sub, 10, VIOLET, width=w - 160, g=g))
    els += btn(x + w - 148, y + 18, 134, 42, cta, "primary", g)
    return els


# ══════════════════════════════════════════════════════════════════
#  A. DASHBOARD
# ══════════════════════════════════════════════════════════════════

def _a1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "A1.  Sales dashboard", "Sales", g, sub_active="Counter")
    e, y = page_header(cx, cy, cw, "Sales",
                       actions=[("Scan return", "secondary"), ("＋ New ticket", "primary")],
                       subtitle="Sat 12 Sept 2026 · Main branch · AFN", g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Today revenue", "84,500", INK, "sale + rental, no deposits", ICON["cash"]),
        ("Open tickets", "12", INK, "4 draft · 8 confirmed", ICON["receipt"]),
        ("Due back today", "3", ACCENT, "scan to return", ICON["clock"]),
        ("Overdue returns", "2", DANGER, "late fee accruing", ICON["alert"]),
        ("Deposits held", "145,000", VIOLET, "liability, not revenue", ICON["reserve"]),
        ("Unpaid A/R", "62,300", WARN, "finance_receivables", ICON["ledger"]),
    ], g=G)
    els += e
    els += note(cx, y, cw,
                "Deposits held is a LIABILITY tile — it is not part of Today revenue. "
                "＋ New ticket opens the counter. Scan return opens the C3 drawer.", VIOLET, G)
    y += 70

    els += _lab(cx, y, f"{ICON['calendar']}  TODAY — PICKUPS & RETURNS", G)
    e, _ = table(cx, y + 22, LW,
                 ["Time", "Order", "Customer", "Item", "Action"],
                 [["09:30", "SO26-000014", "Sara Ahmadi", "White A-Line Gown", ("Pick up", ACCENT)],
                  ["11:00", "SO26-000015", "Maryam Noori", "Gold Ball Gown", ("Pick up", ACCENT)],
                  ["14:00", "SO26-000011", "Fatima Rahimi", "Ivory Mermaid Gown", ("Return · scan", INFO)],
                  ["16:30", "SO26-000012", "Zahra Sadat", "Chantilly Veil", ("Return · scan", INFO)],
                  ["—", "SO26-000009", "Nasrin Amiri", "Rose Evening Gown", ("Overdue 2 d", DANGER)]],
                 G, row_h=38, sheet=True, widths=[0.7, 1.25, 1.3, 1.7, 1.15])
    els += e

    rx = cx + LW + GAP
    els += _lab(rx, y, f"{ICON['receipt']}  RECENT TICKETS", G)
    e, _ = table(rx, y + 22, RW,
                 ["Order", "Type", "Total", "Status"],
                 [["SO26-000018", ("Sale", INFO), "12,700", ("Paid", OK)],
                  ["SO26-000017", ("Rental", ACCENT), "9,000", ("Out", ACCENT)],
                  ["SO26-000016", ("Mixed", VIOLET), "15,200", ("Confirmed", INFO)],
                  ["SO26-000015", ("Rental", ACCENT), "11,500", ("Confirmed", INFO)],
                  ["SO26-000013", ("Sale", INFO), "3,400", ("Partial", WARN)]],
                 G, row_h=38, sheet=True, widths=[1.25, 0.95, 0.85, 1.0])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "READS ONLY. Revenue = Σ sales_order_items.line_total (sale + rental). "
                 "Deposits held = Σ finance_customer_deposits status='held'. "
                 "Due back = status='out' AND rental_end_date = today.")
    return els


# ══════════════════════════════════════════════════════════════════
#  B. COUNTER
# ══════════════════════════════════════════════════════════════════

def _b1(ox, oy):
    """The whole sale/rent flow on one screen."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B1.  Counter — one ticket, rent or sell per line",
                                     "Sales", g, sub_active="Counter")
    e, y = page_header(cx, cy, cw, "New ticket · SO26-000020",
                       actions=[("Clear", "ghost"), ("Print slip", "secondary"),
                                ("Collect & finish", "primary")],
                       subtitle="Walk-in or named customer · scan items · switch Rent / Sell · price is editable",
                       g=G)
    els += e

    # customer strip
    els += _panel(cx, y, cw, 88, None, G)
    els += search_bar(cx + 16, y + 20, 420, f"{ICON['search']}  Phone — 0700 12 34 56", G)
    els += btn(cx + 452, y + 24, 150, 36, "＋ Register", "secondary", G)
    els += btn(cx + 614, y + 24, 140, 36, "Walk-in", "ghost", G)
    c, _ = chip(cx + 780, y + 30, "Sara Ahmadi · 0700 12 34 56 · CUS26-0117", OK, g=G)
    els += c
    els.append(text(cx + 16, y + 64,
                    "Found by phone. No match → Register (B2 drawer). Walk-in is allowed until a Rent line is added.",
                    11, MUTED, width=cw - 32, g=G))
    y += 104

    els += search_bar(cx, y, LW, f"{ICON['tag']}  Scan barcode or search SKU / name…", G)
    ly = y + 52

    # cart header
    els.append(rect(cx, ly, LW, 36, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=G))
    for lab, xx, ww in [("Item", 12, 220), ("Rent / Sell", 250, 120), ("Price AFN", 390, 110),
                        ("Qty", 520, 50), ("Line total", 590, 100)]:
        els.append(text(cx + xx, ly + 10, lab, 11, MUTED, width=ww, g=G))
    ly += 36

    cart = [
        ("White A-Line Gown  ·  ADF26-0042", 0, "9,500", "1", "9,500", "catalogue 9,500 · deposit 5,000"),
        ("Chantilly Veil  ·  ADF26-0118", 1, "3,500", "1", "3,500", "catalogue 3,500"),
        ("Pearl Hair Comb  ·  ADF26-0206", 1, "1,400", "2", "2,800", "catalogue 1,200 · staff typed 1,400"),
    ]
    for name, mode, price, qty, total, hint in cart:
        els.append(rect(cx, ly, LW, 56, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 12, ly + 8, name, 13, INK, width=230, g=G))
        els.append(text(cx + 12, ly + 30, hint, 10.5, MUTED, width=230, g=G))
        els += _toggle_rent_sell(cx + 250, ly + 14, 120, mode, G)
        els += _price_input(cx + 390, ly + 14, 110, price, G)
        els.append(rect(cx + 520, ly + 14, 50, 28, strokeColor=LINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 520, ly + 20, qty, 12, INK, "center", 50, G))
        els.append(text(cx + 590, ly + 18, total, 13, INK, "right", 90, G))
        ly += 56

    els.append(rect(cx, ly, LW, 40, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=G))
    els.append(text(cx + 16, ly + 12, f"{ICON['add']}  Scan the next item, or search by name",
                    12.5, MUTED, width=LW - 32, g=G))
    ly += 52
    e, _ = _chiprow(cx, ly, [("1 rental line", ACCENT), ("2 sale lines", INFO),
                             ("Named customer required", WARN)], G)
    els += e

    # right — totals + pay
    rx, ry = cx + LW + GAP, y
    els += _panel(rx, ry, RW, 168, None, G)
    e, _ = money_row(rx + 16, ry + 16, RW - 32, [
        ("Sale lines", "6,300 AFN"),
        ("Rental lines", "9,500 AFN"),
        ("Deposit (liability)", ("5,000 AFN", VIOLET)),
    ], G, total=("Collect now", "20,800 AFN"))
    els += e
    ry += 184

    e, ry = field(rx, ry, RW, "Rental window (only if a Rent line exists)", "24 → 28 Sep 2026", G)
    els += e
    e, ry = select(rx, ry, RW, "Pay from", "Cash · Main drawer (CASH-01)", G, True)
    els += e
    e, ry = field(rx, ry, RW, "Amount received", "20,800", G, True)
    els += e
    els += note(rx, ry, RW,
                "5,000 of this is deposit — held, not revenue.\nStaff may type a higher price on any line.",
                VIOLET, G)
    ry += 66
    els += btn(rx, ry, RW, 48, "Collect & print slip", "primary", G)

    els += _spec(cx, ox, oy, cw,
                 "WRITES sales_orders + sales_order_items (line_type per row, unit_price as typed). "
                 "Rent lines → inventory_reservations + finance_customer_deposits. "
                 "Sale lines → sale_out. Walk-in blocked if any line_type='rental'.")
    return els


def _b2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B2.  Register customer — drawer over the counter",
                                     "Sales", g, sub_active="Counter")
    # dimmed counter behind
    e, y = page_header(cx, cy, cw, "New ticket · SO26-000020",
                       actions=[("Collect & finish", "primary")],
                       subtitle="No customer matches 0700 99 88 77", g=G)
    els += e
    els += search_bar(cx, y, 420, "0700 99 88 77", G)
    els += empty_state(cx, y + 56, LW, 160, ICON["customers"],
                       "No customer matches this phone",
                       "Register them now — the cart stays open.", None, G)

    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Register customer",
                            side="right", width=440,
                            subtitle="Name + phone is enough · the cart is not lost", g=G)
    els += de
    half = (fw - 16) / 2
    e, fy = field(fx, fy, fw, "Full name", "Sara Ahmadi", G, True)
    els += e
    e, fy = field(fx, fy, fw, "Phone", "0700 99 88 77", G, True)
    els += e
    e, _ = field(fx, fy, half, "Wedding date", "28 Sep 2026", G)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Gender", "Female", G)
    els += e
    e, fy = field(fx, fy, fw, "Customer code", "CUS26-0118  (auto)", G)
    els += e
    e, fy = textarea(fx, fy, fw, "Note", "Bride · referred by Maryam Noori", G, rows=2)
    els += e
    els += note(fx, fy, fw, "Phone is unique per tenant. Duplicate numbers are blocked.", ACCENT, G)
    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, half, 44, "Cancel", "secondary", G)
    els += btn(fx + half + 16, by, half, 44, "Save & use", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "INSERT sales_customers (customer_code auto). The counter keeps the cart. "
                 "Walk-in writes nothing — customer_id stays NULL until a rental line forces a name.")
    return els


def _b3(ox, oy):
    """Printed slip with barcode + QR for later return."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B3.  Printed slip — barcode & QR for the return",
                                     "Sales", g, sub_active="Counter")
    e, y = page_header(cx, cy, cw, "Ticket printed · SO26-000020",
                       actions=[("New ticket", "primary")],
                       subtitle="Hand this slip to the customer · scan it when the dress comes back", g=G)
    els += e

    # receipt paper
    slip_w = 360
    sx = cx + 40
    sh = 620
    els.append(rect(sx, y, slip_w, sh, strokeColor=INK, backgroundColor=BG, strokeWidth=2, groupIds=G))
    els.append(text(sx, y + 16, "AL DUBAI BRIDAL", 16, INK, "center", slip_w, G))
    els.append(text(sx, y + 38, "Main branch · Kabul", 11, MUTED, "center", slip_w, G))
    els.append(text(sx, y + 56, "SO26-000020  ·  12 Sep 2026 14:22", 12, INK, "center", slip_w, G))
    els.append(text(sx, y + 76, "Sara Ahmadi  ·  0700 12 34 56", 12, MUTED, "center", slip_w, G))
    e, xx = _chiprow(sx + 70, y + 98, [("Mixed", VIOLET), ("Paid", OK)], G)
    els += e

    lines_y = y + 132
    for name, kind, amt in [
        ("White A-Line Gown", "RENT  24–28 Sep", "9,500"),
        ("Chantilly Veil", "SALE", "3,500"),
        ("Pearl Hair Comb × 2", "SALE", "2,800"),
    ]:
        els.append(text(sx + 20, lines_y, name, 12, INK, width=220, g=G))
        els.append(text(sx + 20, lines_y + 16, kind, 10.5, ACCENT if "RENT" in kind else INFO,
                        width=220, g=G))
        els.append(text(sx + slip_w - 90, lines_y, amt, 12, INK, "right", 70, G))
        lines_y += 40

    els.append(line(sx + 20, lines_y, slip_w - 40, LINE, G))
    lines_y += 12
    for lab, amt, col in [("Sale", "6,300", INK), ("Rental", "9,500", ACCENT),
                          ("Deposit held", "5,000", VIOLET), ("Collected", "20,800", INK)]:
        els.append(text(sx + 20, lines_y, lab, 12, MUTED, width=180, g=G))
        els.append(text(sx + slip_w - 90, lines_y, amt, 12, col, "right", 70, G))
        lines_y += 20

    els.append(text(sx + 20, lines_y + 8, "Bring this slip (or the garment tag) to return.",
                    11, MUTED, width=slip_w - 40, g=G))
    e, _ = barcode(sx + 24, lines_y + 36, slip_w - 120, 70, "SO26-000020", G)
    els += e
    e, _ = qr(sx + slip_w - 92, lines_y + 32, 72, "SO26-000020", G, caption="scan")
    els += e
    els.append(text(sx, y + sh - 28, "Thank you  ·  aldubai.af", 11, MUTED, "center", slip_w, G))

    # right — what happens next
    rx = cx + slip_w + 80
    RWW = cw - slip_w - 80
    els += _panel(rx, y, RWW, 200, "WHAT THE CODES DO", G, SOFT2)
    els.append(text(rx + 18, y + 44,
                    "Both the barcode and the QR carry the order number SO26-000020. "
                    "One scan at the returns desk opens the ticket — no phone search, no typing.",
                    13, INK, width=RWW - 36, g=G))
    els.append(text(rx + 18, y + 120,
                    "Garment tags still carry the SKU barcode (from Inventory). "
                    "Scan the slip to find the ticket, then scan the dress to check it in.",
                    13, MUTED, width=RWW - 36, g=G))

    els += _panel(rx, y + 220, RWW, 220, "NEXT VISIT", G)
    for i, t in enumerate([
            "1  Scan this slip → ticket opens (C3).",
            "2  Scan the gown → line marked returned.",
            "3  Collect remaining balance or refund the deposit.",
            "4  Stock goes back. Cleaning buffer blocks the next booking."]):
        els.append(text(rx + 18, y + 256 + i * 36, t, 13, INK, width=RWW - 36, g=G))

    els += btn(rx, y + 460, RWW, 48, f"{ICON['print']}  Reprint slip", "secondary", G)

    els += _spec(cx, ox, oy, cw,
                 "The slip is a print of the posted sales_order. Payload of both codes = order_number. "
                 "SKU barcodes on the garment still resolve inventory_items — used at step 2 of the return.")
    return els


# ══════════════════════════════════════════════════════════════════
#  C. ORDERS
# ══════════════════════════════════════════════════════════════════

def _c1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C1.  Orders list", "Sales", g, sub_active="Orders")
    e, y = page_header(cx, cy, cw, "Orders",
                       actions=[("Export", "ghost"), ("＋ New ticket", "primary")], g=G)
    els += e
    e, y = tabs(cx, y, cw, ["All  (124)", "Sale  (57)", "Rental  (58)", "Mixed  (9)"], 0, G)
    els += e
    e, y = _sheet_bar(cx, y, cw, G, "Search order # · customer name · phone…")
    els += e
    els += filter_chips(cx, y, ["Any status", "Draft", "Confirmed", "Out", "Returned", "Completed", "Overdue"], 0, G)
    y += 42
    e, y = table(cx, y, cw,
                 ["Order #", "Customer", "Type", "Dates", "Total", "Paid",
                  "Deposit held", "Balance", "Status"],
                 [["SO26-000019", "Sara Ahmadi", ("Mixed", VIOLET), "10–14 Sep", "15,200",
                   "6,000", ("8,000", VIOLET), ("9,200", WARN), ("Confirmed", INFO)],
                  ["SO26-000018", "Walk-in", ("Sale", INFO), "12 Sep", "12,700",
                   "12,700", "—", "0", ("Completed", OK)],
                  ["SO26-000017", "Maryam Noori", ("Rental", ACCENT), "12–16 Sep", "9,000",
                   "4,500", ("6,000", VIOLET), ("4,500", WARN), ("Out", ACCENT)],
                  ["SO26-000016", "Fatima Rahimi", ("Mixed", VIOLET), "08–12 Sep", "18,400",
                   "18,400", ("10,000", VIOLET), "0", ("Returned", INFO)],
                  ["SO26-000014", "Nasrin Amiri", ("Rental", ACCENT), "09–12 Sep", "8,500",
                   "8,500", ("6,000", VIOLET), "0", ("Out", DANGER)],
                  ["SO26-000013", "Walk-in", ("Sale", INFO), "09 Sep", "3,400",
                   "1,400", "—", ("2,000", WARN), ("Confirmed", INFO)]],
                 G, row_h=40, sheet=True,
                 widths=[1.15, 1.3, 0.85, 1.0, 0.85, 0.8, 1.0, 0.85, 1.0])
    els += e
    e, y = pagination(cx, y, cw, "1–6 of 124 orders", G)
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Type badge is DERIVED from line_type mix. Deposit held is the liability, shown apart from Paid. "
                 "＋ New ticket jumps to the counter. This page has no form.")
    return els


def _c2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C2.  Order detail", "Sales", g, sub_active="Orders")
    e, y = page_header(cx, cy, cw, "SO26-000017",
                       actions=[("Print slip", "ghost"), ("Collect", "secondary"),
                                ("Scan return", "primary")],
                       subtitle="Maryam Noori · 0700 12 34 56 · 12–16 Sep 2026", g=G)
    els += e
    e, _ = _chiprow(cx, y - 2, [("Rental", ACCENT), ("Out", ACCENT), ("Overdue 2 days", DANGER),
                                ("Deposit held 6,000", VIOLET)], G)
    els += e
    y += 36
    e, y = timeline(cx, y, cw, [
        ("Draft", "done"), ("Confirmed", "done"), ("Out", "current"),
        ("Returned", "todo"), ("Done", "todo"),
    ], G)
    els += e

    e, ly = table(cx, y, LW,
                  ["Item", "SKU", "Line", "Days", "Price", "Total", "Deposit"],
                  [["Ivory Mermaid Gown", "ADF26-0091", ("Rental", ACCENT), "4", "1,350",
                    "5,400", ("6,000", VIOLET)],
                   ["Chantilly Veil", "ADF26-0118", ("Rental", ACCENT), "4", "900",
                    "3,600", "—"]],
                  G, row_h=40, sheet=True, widths=[1.7, 1.15, 0.85, 0.5, 0.8, 0.8, 0.85])
    els += e
    els += _lab(cx, ly + 4, "SCAN THE SLIP OR THE GOWN TO RETURN — opens C3", G, ACCENT)

    rx = cx + LW + GAP
    els += _panel(rx, y, RW, 148, f"{ICON['reserve']}  DEPOSIT — LIABILITY", G, VIOLET_BG, VIOLET)
    els += _kv(rx + 16, y + 48, RW - 32, "Held now", "6,000 AFN", G, VIOLET, 16)
    els += _kv(rx + 16, y + 78, RW - 32, "Settled on return", "apply / refund", G, MUTED, 12)
    els += _kv(rx + 16, y + 108, RW - 32, "Never income until forfeited", "0 forfeited", G, MUTED, 12)

    els += _panel(rx, y + 164, RW, 160, None, G)
    e, _ = money_row(rx + 16, y + 180, RW - 32, [
        ("Rental", "9,000 AFN"),
        ("Paid", "4,500 AFN"),
        ("Late fee accruing", "2,000 AFN"),
        ("Deposit held", "6,000 AFN"),
    ], G, total=("Balance → A/R", "6,500 AFN"))
    els += e
    els += btn(rx, y + 340, RW, 46, f"{ICON['scan']}  Scan return", "primary", G)

    els += _spec(cx, ox, oy, cw,
                 "READS sales_orders + items + finance_customer_deposits + finance_receivables. "
                 "Scan return opens C3 over this page. Sale-only tickets show Sale return instead.")
    return els


def _c3(ox, oy):
    """Scan slip → take money → return to stock."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C3.  Scan return — drawer over the order",
                                     "Sales", g, sub_active="Orders")
    els += _orders_backdrop(cx, cy, cw, G)

    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Scan return · SO26-000017",
                            side="right", width=520,
                            subtitle="Scan the slip or the garment · collect · put back in stock", g=G)
    els += de
    e, fy = field(fx, fy, fw, f"{ICON['scan']}  Scan slip / barcode / QR", "SO26-000017", G, True)
    els += e
    els.append(text(fx, fy - 8, "Maryam Noori · Ivory Mermaid Gown · due 16 Sep · 2 days late",
                    11.5, DANGER, width=fw, g=G))
    fy += 16
    els += _lab(fx, fy, "CONDITION", G)
    fy += 18
    els += filter_chips(fx, fy, ["Good", "Needs cleaning", "Damaged", "Lost"], 1, G)
    fy += 44
    e, fy = table(fx, fy, fw, ["Item", "Line", "Action"],
                  [["Ivory Mermaid Gown", ("Rental", ACCENT), ("Return to stock", OK)],
                   ["Chantilly Veil", ("Rental", ACCENT), ("Return to stock", OK)]],
                  G, row_h=36, widths=[1.8, 0.9, 1.3])
    els += e

    els += _panel(fx, fy, fw, 88, None, G, WARN_BG, WARN)
    e, _ = money_row(fx + 14, fy + 12, fw - 28, [
        ("Late fee  2 × 1,000", "2,000 AFN"),
        ("Waive", "− 500 · loyal customer"),
    ], G, total=("Late fee charged", "1,500 AFN"))
    els += e
    fy += 100

    els += _panel(fx, fy, fw, 110, "DEPOSIT 6,000 — SETTLE", G, VIOLET_BG, VIOLET)
    els += _kv(fx + 14, fy + 44, fw - 28, "Apply to balance", "1,500 AFN", G, ACCENT, 13)
    els += _kv(fx + 14, fy + 68, fw - 28, "Refund to customer", "4,500 AFN", G, OK, 13)
    fy += 122
    e, fy = select(fx, fy, fw, "Pay / refund from", "Cash · Main drawer (CASH-01)", G, True)
    els += e

    by = oy + TITLE_H + DESK_H - 68
    half = (fw - 16) / 2
    els += btn(fx, by, half, 44, "Cancel", "secondary", G)
    els += btn(fx + half + 16, by, half, 44, "Confirm return", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "WRITES status='returned', rent_return stock rows, deposit applied/refunded. "
                 "Only a forfeited slice ever becomes income. Damaged/Lost opens a claim instead of restocking.")
    return els


# ══════════════════════════════════════════════════════════════════
#  D. RETURNS (sold goods)
# ══════════════════════════════════════════════════════════════════

def _d1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D1.  Sale return — scan the slip",
                                     "Sales", g, sub_active="Returns")
    e, y = page_header(cx, cy, cw, "Returns",
                       actions=[("＋ Sale return", "primary")],
                       subtitle="Sold goods only · rentals come back through Scan return on the order", g=G)
    els += e
    e, y = _sheet_bar(cx, y, cw, G, "Scan slip barcode / QR, or search order #…")
    els += e
    els += note(cx, y, cw,
                "A rental coming back is not this screen — open the order and Scan return (C3). "
                "This list is for goods that were SOLD.", INFO, G)
    y += 70
    e, y = table(cx, y, cw,
                 ["Return #", "Against", "Customer", "Date", "Lines", "Refund AFN", "Restock", "Status"],
                 [["RET26-0006", "SO26-000018", "Walk-in", "14 Sep", "2", "4,600", ("Yes", OK), ("Posted", OK)],
                  ["RET26-0005", "SO26-000013", "Walk-in", "11 Sep", "1", "900", ("No", MUTED), ("Posted", OK)],
                  ["RET26-0004", "SO26-000006", "Sara Ahmadi", "04 Sep", "1", "3,500", ("Yes", OK), ("Posted", OK)]],
                 G, row_h=42, sheet=True,
                 widths=[1.15, 1.15, 1.3, 0.9, 0.6, 1.1, 0.8, 0.85])
    els += e

    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Sale return · RET26-0007",
                            side="right", width=520,
                            subtitle="Against SO26-000018 · Walk-in · sold 12 Sep", g=G)
    els += de
    e, fy = field(fx, fy, fw, f"{ICON['scan']}  Scan slip", "SO26-000018", G, True)
    els += e
    e, fy = table(fx, fy, fw, ["", "Item", "Sold", "Return", "Refund"],
                  [[("☑", ACCENT), "Chantilly Veil", "1", "1", "3,500"],
                   [("☑", ACCENT), "Pearl Hair Comb", "2", "1", "1,200"],
                   [("☐", FAINT), "Ivory Clutch", "1", "0", "—"]],
                  G, row_h=36, widths=[0.35, 1.6, 0.55, 0.7, 0.8])
    els += e
    e, fy = select(fx, fy, fw, "Reason", "Customer change of mind", G, True)
    els += e
    e, fy = select(fx, fy, fw, "Condition", "Good — restock", G)
    els += e
    e, fy = money_row(fx, fy, fw, [
        ("Lines", "4,700 AFN"),
        ("Discount share", "− 100 AFN"),
    ], G, total=("Refund due", "4,600 AFN"))
    els += e
    by = oy + TITLE_H + DESK_H - 68
    half = (fw - 16) / 2
    els += btn(fx, by, half, 44, "Cancel", "secondary", G)
    els += btn(fx + half + 16, by, half, 44, "Post & refund", "primary", G)
    els += _spec(cx, ox, oy, 520,
                 "WRITES sales_sale_returns. Restock → sale_return_in. Refund → finance_transactions OUT. "
                 "Does not touch deposits or reservations.")
    return els


def _d2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D2.  Sale return posted",
                                     "Sales", g, sub_active="Returns")
    e, y = page_header(cx, cy, cw, "RET26-0006 posted",
                       actions=[("Print credit note", "secondary")],
                       subtitle="Against SO26-000018 · Walk-in · 14 Sep 2026 11:08", g=G)
    els += e
    els.append(rect(cx, y, cw, 56, strokeColor=OK, backgroundColor=OK_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 20, y + 18,
                    f"{ICON['check']}  2 lines restocked · refund 4,600 AFN cash · COGS reversed 2,450 AFN",
                    14, OK, width=cw - 40, g=G))
    y += 72
    e, y = table(cx, y, cw,
                 ["Item", "SKU", "Qty back", "Refund", "Stock effect"],
                 [["Chantilly Veil", "ADF26-0042", "+1", "3,500", ("sale_return_in", OK)],
                  ["Pearl Hair Comb", "ADF26-0118", "+1", "1,200", ("sale_return_in", OK)]],
                 G, row_h=42, sheet=True, widths=[1.8, 1.2, 0.9, 0.9, 1.4])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Posted returns are immutable. Correct with another return, never an edit. "
                 "Order payment_status → partially_refunded.", OK)
    return els


# ══════════════════════════════════════════════════════════════════
#  E. CUSTOMERS
# ══════════════════════════════════════════════════════════════════

def _e1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "E1.  Customers list", "Sales", g, sub_active="Customers")
    e, y = page_header(cx, cy, cw, "Customers",
                       actions=[("Export", "ghost"), ("＋ New customer", "primary")], g=G)
    els += e
    e, y = _sheet_bar(cx, y, cw, G, "Search by phone — 0700 12 34 56")
    els += e
    els += filter_chips(cx, y, ["All", "Has open balance", "Deposit held", "Wedding this month", "Inactive"], 0, G)
    y += 42
    e, y = stat_row(cx, y, cw, [
        ("Customers", "412", INK, "+9 this month", ICON["customers"]),
        ("With open A/R", "23", WARN, "62,300 AFN", ICON["ledger"]),
        ("Deposits held", "18", VIOLET, "145,000 AFN", ICON["reserve"]),
        ("Weddings this month", "31", ROSE, "peak season", ICON["calendar"]),
    ], 88, 14, G)
    els += e
    e, y = table(cx, y, cw,
                 ["Code", "Name", "Phone", "Wedding date", "Orders", "Lifetime",
                  "Deposit held", "Balance"],
                 [["CUS26-0117", "Sara Ahmadi", "0700 12 34 56", "28 Sep 2026", "4",
                   "48,900", ("8,000", VIOLET), ("9,200", WARN)],
                  ["CUS26-0094", "Maryam Noori", "0700 12 34 57", "16 Sep 2026", "3",
                   "27,500", ("6,000", VIOLET), ("4,500", WARN)],
                  ["CUS26-0088", "Fatima Rahimi", "0700 12 34 58", "12 Sep 2026", "6",
                   "71,200", "—", "0"],
                  ["CUS26-0072", "Zahra Sadat", "0700 55 44 33", "05 Oct 2026", "2",
                   "19,300", ("8,000", VIOLET), ("6,500", WARN)],
                  ["CUS26-0061", "Nasrin Amiri", "0700 77 66 55", "02 Sep 2026", "5",
                   "58,400", ("6,000", VIOLET), ("26,000", DANGER)]],
                 G, row_h=40, sheet=True,
                 widths=[1.05, 1.3, 1.2, 1.1, 0.6, 0.95, 1.0, 0.85])
    els += e
    e, y = pagination(cx, y, cw, "1–5 of 412 customers", G)
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Indexed on tenant_id + phone. Lifetime value excludes deposits. "
                 "Walk-in tickets have customer_id NULL and appear in no row. ＋ New customer opens E2.")
    return els


def _e2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "E2.  New customer — drawer over the list",
                                     "Sales", g, sub_active="Customers")
    els += _customers_backdrop(cx, cy, cw, G)
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New customer",
                            side="right", width=440,
                            subtitle="Name + phone required · everything else optional", g=G)
    els += de
    half = (fw - 16) / 2
    e, fy = field(fx, fy, fw, "Full name", "Laila Karimi", G, True)
    els += e
    e, fy = field(fx, fy, fw, "Phone", "0700 88 99 00", G, True)
    els += e
    e, _ = field(fx, fy, half, "Wedding date", "22 Oct 2026", G)
    els += e
    e, fy = select(fx + half + 16, fy, half, "Gender", "Female", G)
    els += e
    e, fy = field(fx, fy, fw, "Address", "Shahr-e Naw, Kabul", G)
    els += e
    e, fy = field(fx, fy, fw, "Customer code", "CUS26-0120  (auto)", G)
    els += e
    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, half, 44, "Cancel", "secondary", G)
    els += btn(fx + half + 16, by, half, 44, "Save customer", "primary", G)
    els += _spec(cx, ox, oy, 560,
                 "INSERT sales_customers. Duplicate phone is blocked. This drawer is also used from the counter (B2).")
    return els


def _e3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "E3.  Customer profile", "Sales", g, sub_active="Customers")
    e, y = page_header(cx, cy, cw, "Sara Ahmadi",
                       actions=[("Statement", "ghost"), ("＋ New ticket", "primary")],
                       subtitle="CUS26-0117 · 0700 12 34 56 · customer since Mar 2026", g=G)
    els += e

    els += _panel(cx, y, RW, 250, f"{ICON['user']}  PROFILE", G)
    py = y + 42
    for lab, val, col in [("Phone", "0700 12 34 56", INK),
                          ("Wedding date", "28 Sep 2026  (16 days)", ROSE),
                          ("Gender", "Female", MUTED),
                          ("Branch", "Main branch", MUTED),
                          ("Address", "Shahr-e Naw, Kabul", MUTED),
                          ("Status", "Active", OK)]:
        els += _kv(cx + 16, py, RW - 32, lab, val, G, col, 13)
        py += 32
    y2 = y + 266
    els += _panel(cx, y2, RW, 150, "DEPOSIT & A/R", G, VIOLET_BG, VIOLET)
    els += _kv(cx + 16, y2 + 44, RW - 32, "Deposits held", "8,000 AFN", G, VIOLET, 15)
    els += _kv(cx + 16, y2 + 74, RW - 32, "Open A/R", "9,200 AFN", G, DANGER, 13)
    els += _kv(cx + 16, y2 + 104, RW - 32, "Lifetime revenue", "48,900 AFN", G, INK, 13)

    rx = cx + RW + GAP
    e, ry = tabs(rx, y, LW, ["Orders", "Deposits", "Payments", "Notes"], 0, G)
    els += e
    e, ry = table(rx, ry, LW,
                  ["Order #", "Date", "Type", "Total", "Deposit", "Balance", "Status"],
                  [["SO26-000019", "12 Sep", ("Mixed", VIOLET), "16,000",
                    ("14,000 held", VIOLET), ("9,200", WARN), ("Confirmed", INFO)],
                   ["SO26-000010", "02 Aug", ("Rental", ACCENT), "9,400",
                    ("8,000 refunded", MUTED), "0", ("Completed", OK)],
                   ["SO26-000006", "19 Jun", ("Sale", INFO), "12,700", "—", "0", ("Completed", OK)]],
                  G, row_h=40, sheet=True, widths=[1.15, 0.8, 0.85, 0.85, 1.35, 0.85, 1.0])
    els += e
    els += _lab(rx, ry + 4, "DEPOSIT MOVEMENTS — only forfeited rows are income", G, VIOLET)
    e, _ = table(rx, ry + 26, LW,
                 ["Date", "Order", "Event", "Amount", "Status"],
                 [["12 Sep", "SO26-000019", "Deposit taken", ("+ 14,000", VIOLET), ("held", VIOLET)],
                  ["12 Aug", "SO26-000010", "Clean return", ("− 8,000", MUTED), ("refunded", MUTED)],
                  ["09 May", "SO26-000002", "Late 2 days", ("− 1,500", WARN), ("forfeited", WARN)]],
                 G, row_h=36, sheet=True, widths=[0.8, 1.2, 1.4, 1.0, 1.0])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "READS sales_customers + orders + finance_customer_deposits + finance_receivables. "
                 "ONLY forfeited deposits appear in Income.", VIOLET)
    return els


# ══════════════════════════════════════════════════════════════════
#  F. REPORTS
# ══════════════════════════════════════════════════════════════════

def _f_tiles(cx, y, cw, g, active):
    cards = [(ICON["chart"], "Sales Summary", "Revenue, margin, by day"),
             (ICON["rental"], "Rental Performance", "Utilisation & damage"),
             (ICON["reserve"], "Deposits & Refunds", "Liability movement")]
    ccw = (cw - 14 * 2) / 3
    els = []
    for i, (ic, t, d) in enumerate(cards):
        els += _report_card(cx + i * (ccw + 14), y, ccw, 84, ic, t, d, g, on=(i == active))
    return els, y + 100


def _f1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F1.  Sales summary", "Sales", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Sales reports",
                       actions=[("Export CSV", "secondary"), ("Print", "ghost")],
                       subtitle="01–12 Sept 2026 · Main branch · AFN", g=G)
    els += e
    e, y = _f_tiles(cx, y, cw, G, 0)
    els += e
    e, y2 = field(cx, y, 180, "From", "01 Sep 2026", G)
    els += e
    e2, _ = field(cx + 196, y, 180, "To", "12 Sep 2026", G)
    els += e2
    e2, _ = select(cx + 392, y, 200, "Branch", "Main branch", G)
    els += e2
    els += btn(cx + 608, y + 18, 120, 40, "Run report", "primary", G)
    y = y2
    e, y = stat_row(cx, y, cw, [
        ("Revenue — total", "612,400", INK, "12 days", ICON["cash"]),
        ("Sale lines", "268,900", INFO, "44%", ICON["tag"]),
        ("Rental lines", "343,500", ACCENT, "56%", ICON["rental"]),
        ("COGS + amortisation", "247,100", WARN, "sale + per-use", ICON["ledger"]),
        ("Gross margin", "365,300", OK, "59.6%", ICON["chart"]),
        ("Deposits held (not revenue)", "145,000", VIOLET, "liability", ICON["reserve"]),
    ], 88, 14, G)
    els += e
    BW = 668
    e, _ = bar_chart(cx, y, BW, 220, "Revenue by day — sale vs rental (AFN, thousands)",
                     [("01", 0.42, "38"), ("04", 0.71, "64"), ("05", 0.86, "77"),
                      ("06", 0.94, "85"), ("09", 0.66, "59"), ("10", 0.78, "70"),
                      ("11", 0.62, "56"), ("12", 0.94, "85")], G)
    els += e
    rx = cx + BW + GAP
    RWW = cw - BW - GAP
    e, ry = table(rx, y, RWW, ["Category", "Qty", "Revenue", "Margin"],
                  [["Gowns — rental", "48", "286,400", ("62%", OK)],
                   ["Gowns — sale", "9", "184,200", ("41%", OK)],
                   ["Veils", "37", "63,900", ("55%", OK)],
                   ["Accessories", "62", "20,800", ("49%", WARN)]],
                  G, row_h=36, sheet=True, widths=[1.6, 0.55, 1.0, 0.8])
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Split by line_type so a mixed ticket feeds both columns. Revenue excludes deposits and refunds. "
                 "Rental cost = purchase_cost ÷ expected_uses.")
    return els


def _f2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F2.  Rental performance", "Sales", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Rental performance",
                       actions=[("Export CSV", "secondary")],
                       subtitle="Per dress · 01 Jan – 12 Sept 2026 · Main branch", g=G)
    els += e
    e, y = _f_tiles(cx, y, cw, G, 1)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Rentable dresses", "186", INK, "142 rented ≥1×", ICON["dress"]),
        ("Rentals completed", "428", INK, "avg 4.2 days", ICON["rental"]),
        ("Rental revenue", "1,284,600", ACCENT, "YTD", ICON["cash"]),
        ("Fleet utilisation", "38%", WARN, "target 50%", ICON["chart"]),
        ("Late returns", "31", WARN, "7.2%", ICON["clock"]),
        ("Damage / loss", "6", DANGER, "4 damage · 2 loss", ICON["alert"]),
    ], 88, 14, G)
    els += e
    e, y = table(cx, y, cw,
                 ["Dress", "SKU", "Times rented", "Revenue", "Utilisation", "Late", "Claims", "Amortised"],
                 [["White A-Line Gown", "ADF26-0042", "27", "189,000", ("71%", OK), "3", ("0", OK), ("84%", OK)],
                  ["Gold Ball Gown", "ADF26-0077", "22", "121,000", ("58%", OK), "2", ("1 damage", WARN), ("66%", OK)],
                  ["Ivory Mermaid Gown", "ADF26-0091", "19", "102,600", ("49%", WARN), "4", ("0", OK), ("51%", WARN)],
                  ["Rose Evening Gown", "ADF26-0176", "9", "43,200", ("24%", DANGER), "2", ("1 loss", DANGER),
                   ("written off", DANGER)],
                  ["Blush Tulle Gown", "ADF26-0198", "2", "8,800", ("5%", DANGER), "0", ("0", OK), ("6%", DANGER)]],
                 G, row_h=36, sheet=True,
                 widths=[1.8, 1.1, 1.0, 1.0, 1.0, 0.7, 1.0, 1.1])
    els += e
    e, _ = bar_chart(cx, y, cw, 160, "Utilisation % — top dresses (days out ÷ days available)",
                     [("0042", 0.71, "71%"), ("0077", 0.58, "58%"), ("0091", 0.49, "49%"),
                      ("0104", 0.36, "36%"), ("0176", 0.24, "24%"), ("0198", 0.05, "5%")], G)
    els += e
    els += _spec(cx, ox, oy, cw,
                 "Utilisation excludes the cleaning buffer. Idle gowns are the sell-off list. "
                 "Amortised % = accumulated per-use COGS ÷ purchase_cost.", ACCENT)
    return els


def _f3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F3.  Deposits & refunds", "Sales", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Deposits & refunds",
                       actions=[("Export CSV", "secondary")],
                       subtitle="Liability movement · 01–12 Sept 2026 · never mixed into revenue", g=G)
    els += e
    e, y = _f_tiles(cx, y, cw, G, 2)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Taken this period", "86,000", VIOLET, "cash IN · liability ↑", ICON["reserve"]),
        ("Refunded", "42,000", OK, "cash OUT · liability ↓", ICON["money_out"]),
        ("Applied to balance", "18,500", ACCENT, "cleared A/R", ICON["ledger"]),
        ("Forfeited → income", "3,000", WARN, "the only income slice", ICON["cash"]),
        ("Still held", "145,000", VIOLET, "open rentals", ICON["lock"]),
        ("Sale refunds", "4,600", INFO, "contra-revenue", ICON["receipt"]),
    ], 88, 14, G)
    els += e
    e, y = table(cx, y, cw,
                 ["Date", "Order", "Customer", "Event", "Amount", "Status", "Finance effect"],
                 [["12 Sep", "SO26-000019", "Sara Ahmadi", "Deposit taken", ("+ 14,000", VIOLET),
                   ("held", VIOLET), "Cash IN · liability ↑"],
                  ["12 Sep", "SO26-000017", "Maryam Noori", "Deposit taken", ("+ 6,000", VIOLET),
                   ("held", VIOLET), "Cash IN · liability ↑"],
                  ["11 Sep", "SO26-000012", "Zahra Sadat", "Clean return", ("− 8,000", MUTED),
                   ("refunded", MUTED), "Cash OUT · liability ↓"],
                  ["10 Sep", "SO26-000009", "Nasrin Amiri", "Late 2 days", ("− 1,500", WARN),
                   ("forfeited", WARN), "Income ↑ (only here)"],
                  ["14 Sep", "SO26-000018", "Walk-in", "Sale return", ("− 4,600", INFO),
                   ("refunded", INFO), "Contra-revenue"]],
                 G, row_h=38, sheet=True,
                 widths=[0.75, 1.15, 1.2, 1.2, 1.0, 0.95, 1.6])
    els += e
    els += note(cx, y, cw,
                "Reconciliation  held_start 122,000 + taken 86,000 − refunded 42,000 − applied 18,500 − forfeited 3,000 "
                "= held_end 144,500 ≈ 145,000  ✓", VIOLET, G)
    els += _spec(cx, ox, oy, cw,
                 "finance_customer_deposits movements + sales_sale_returns refunds. "
                 "The forfeited column is the only one that hits Income. Sale refunds are contra-revenue, not an expense.",
                 VIOLET)
    return els


GROUPS = [
    ("DASHBOARD", [_a1]),
    ("COUNTER", [_b1, _b2, _b3]),
    ("ORDERS", [_c1, _c2, _c3]),
    ("RETURNS", [_d1, _d2]),
    ("CUSTOMERS", [_e1, _e2, _e3]),
    ("REPORTS", [_f1, _f2, _f3]),
]


def desktop():
    els = board_title(0, -230, "BOMS Desktop — Sales",
                      "Read top to bottom: A Dashboard · B Counter (one ticket, Rent/Sell per line, printed slip) · "
                      "C Orders · D Sale returns · E Customers · F Reports.\n"
                      "Walk-in or phone search · register in a drawer · price input defaults to catalogue, staff may type higher · "
                      "slip ends with barcode + QR of the order number.\n"
                      "Return = scan slip → collect/refund → stock back. Deposits are a liability. Every create/edit is a drawer.")
    els += grouped_board(GROUPS, DESK_COLS, colors=SECTION_COLORS)
    return els


# ══════════════════════════════════════════════════════════════════
#  MOBILE
# ══════════════════════════════════════════════════════════════════

def _mnote(ox, oy, body, color=ACCENT):
    return note(ox, oy + TITLE_H + PHONE_H + 16, PHONE_W, body, color)


def _m1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "A1. Sales hub", g, "Sales")
    e, y = phone_header(cx, cy, cw, "Sales", right=ICON["search"], g=G)
    els += e
    els.append(text(cx, y - 8, "Sat 12 Sept · Main branch", 11, MUTED, width=cw, g=G))
    y += 12
    els += btn(cx, y, cw, 56, f"{ICON['sales']}  New ticket", "primary", G)
    y += 68
    kw = (cw - 10) / 2
    els += kpi_card(cx, y, kw, 78, "Today revenue", "84,500", INK, None, ICON["cash"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Due back", "3", ACCENT, None, ICON["clock"], G)
    y += 88
    els += kpi_card(cx, y, kw, 78, "Deposits held", "145,000", VIOLET, None, ICON["reserve"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Overdue", "2", DANGER, None, ICON["alert"], G)
    y += 96
    els += _lab(cx, y, "DUE BACK TODAY — TAP TO SCAN", G)
    y += 20
    e, y = list_card(cx, y, cw,
                     [("Ivory Mermaid Gown", INK, 13.5),
                      ("SO26-000011 · Fatima Rahimi", MUTED, 11),
                      ("Due 14:00 · deposit 6,000 held", VIOLET, 11)], G, badge=("Out", ACCENT))
    els += e
    e, y = list_card(cx, y, cw,
                     [("Rose Evening Gown", INK, 13.5),
                      ("SO26-000009 · Nasrin Amiri", MUTED, 11),
                      ("Due 10 Sep · late fee accruing", DANGER, 11)], G, badge=("2 d late", DANGER))
    els += e
    els += _mnote(ox, oy, "New ticket → counter. Tap a due-back row → scan return.")
    return els


def _m2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B1. Counter", g, "Sales")
    e, y = phone_header(cx, cy, cw, "New ticket", left=ICON["back"], g=G)
    els += e
    els += search_bar(cx, y, cw, "Phone — 0700 12 34 56", G)
    y += 50
    e, y = list_card(cx, y, cw,
                     [("Sara Ahmadi", INK, 13.5),
                      ("0700 12 34 56 · CUS26-0117", MUTED, 11)], G, badge=("Use", OK))
    els += e
    els += search_bar(cx, y, cw, f"{ICON['tag']}  Scan item…", G)
    y += 50

    for name, mode, price, total in [
        ("White A-Line Gown", 0, "9,500", "9,500"),
        ("Chantilly Veil", 1, "3,500", "3,500"),
    ]:
        els.append(rect(cx, y, cw, 70, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 12, y + 8, name, 13, INK, width=cw - 90, g=G))
        els += _toggle_rent_sell(cx + 12, y + 32, 120, mode, G)
        els += _price_input(cx + 144, y + 32, 90, price, G)
        els.append(text(cx + cw - 78, y + 34, total, 13, INK, "right", 66, G))
        y += 78

    sy = oy + TITLE_H + PHONE_H - 72 - 82
    els += _sticky(cx, sy, cw, "Collect now (incl. deposit 5,000)", "20,800 AFN", "Collect", G)
    els += _mnote(ox, oy, "Rent/Sell per line. Price input defaults to catalogue, staff may type higher.")
    return els


def _m3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B2. Register customer", g, "Sales")
    e, y = phone_header(cx, cy, cw, "Register customer", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y - 8, "No match for 0700 99 88 77 · cart kept", 11, MUTED, width=cw, g=G))
    y += 12
    e, y = field(cx, y, cw, "Full name", "Sara Ahmadi", G, True)
    els += e
    e, y = field(cx, y, cw, "Phone", "0700 99 88 77", G, True)
    els += e
    e, y = field(cx, y, cw, "Wedding date", "28 Sep 2026", G)
    els += e
    els += btn(cx, y + 8, cw, 48, "Save & use", "primary", G)
    els += _mnote(ox, oy, "INSERT sales_customers. Returns to the counter with the cart intact.")
    return els


def _m4(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B3. Printed slip", g, "Sales")
    e, y = phone_header(cx, cy, cw, "Slip · SO26-000020", left=ICON["back"], right=ICON["print"], g=G)
    els += e
    els.append(text(cx, y, "Sara Ahmadi · Mixed · paid", 12, MUTED, width=cw, g=G))
    y += 24
    for name, kind, amt in [("White A-Line Gown", "RENT 24–28 Sep", "9,500"),
                            ("Chantilly Veil", "SALE", "3,500")]:
        els.append(text(cx, y, name, 13, INK, width=cw - 80, g=G))
        els.append(text(cx, y + 18, kind, 11, ACCENT if "RENT" in kind else INFO, width=cw - 80, g=G))
        els.append(text(cx + cw - 70, y, amt, 13, INK, "right", 70, G))
        y += 44
    e, y = money_row(cx, y, cw, [("Deposit held", "5,000"), ("Collected", "20,800")], G)
    els += e
    e, _ = barcode(cx, y, cw - 88, 64, "SO26-000020", G)
    els += e
    e, _ = qr(cx + cw - 80, y, 72, "SO26-000020", G)
    els += e
    y += 90
    els.append(text(cx, y, "Scan this slip to return the dress.", 11.5, MUTED, width=cw, g=G))
    els += _mnote(ox, oy, "Both codes carry SO26-000020. Next visit starts with a scan.")
    return els


def _m5(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C3. Scan return", g, "Sales")
    e, y = phone_header(cx, cy, cw, "Scan return", left=ICON["back"], g=G)
    els += e
    e, y = field(cx, y, cw, f"{ICON['scan']}  Scan slip or garment", "SO26-000017", G, True)
    els += e
    e, y = list_card(cx, y, cw,
                     [("Ivory Mermaid Gown", INK, 13.5),
                      ("Maryam Noori · 2 days late", DANGER, 11),
                      ("deposit 6,000 held", VIOLET, 11)], G, badge=("Out", ACCENT))
    els += e
    els += filter_chips(cx, y, ["Good", "Needs cleaning"], 1, G)
    y += 42
    els += _panel(cx, y, cw, 120, None, G, VIOLET_BG, VIOLET)
    els += _kv(cx + 14, y + 16, cw - 28, "Late fee charged", "1,500 AFN", G, DANGER, 13)
    els += _kv(cx + 14, y + 44, cw - 28, "Deposit → balance", "1,500 AFN", G, ACCENT, 12)
    els += _kv(cx + 14, y + 70, cw - 28, "Refund to customer", "4,500 AFN", G, OK, 12)
    y += 132
    els += btn(cx, y, cw, 48, "Confirm return", "primary", G)
    els += _mnote(ox, oy, "rent_return + deposit settle + optional cash. Stock is back.")
    return els


def _m6(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C1. Orders", g, "Sales")
    e, y = phone_header(cx, cy, cw, "Orders", left=ICON["back"], right=ICON["filter"], g=G)
    els += e
    els += search_bar(cx, y, cw, "Order # · name · phone…", G)
    y += 50
    els += filter_chips(cx, y, ["All", "Sale", "Rental", "Mixed"], 0, G)
    y += 42
    for lines, badge in [
        ([("SO26-000019 · Sara Ahmadi", INK, 13.5),
          ("Mixed · 16,000 · dep 14,000 held", VIOLET, 11)], ("Confirmed", INFO)),
        ([("SO26-000018 · Walk-in", INK, 13.5),
          ("Sale · 12,600 · paid in full", OK, 11)], ("Completed", OK)),
        ([("SO26-000017 · Maryam Noori", INK, 13.5),
          ("Rental · overdue 2 d · dep 6,000", DANGER, 11)], ("Out", DANGER)),
    ]:
        e, y = list_card(cx, y, cw, lines, G, badge=badge)
        els += e
    els += fab(cx + cw, oy + TITLE_H + PHONE_H - 140, "＋  New ticket", G)
    els += _mnote(ox, oy, "Type is derived from the lines. FAB opens the counter.")
    return els


def _m7(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "D1. Sale return", g, "Sales")
    e, y = phone_header(cx, cy, cw, "Sale return", left=ICON["back"], g=G)
    els += e
    e, y = field(cx, y, cw, f"{ICON['scan']}  Scan slip", "SO26-000018", G, True)
    els += e
    els += note(cx, y, cw, "Sold goods only. Rentals return via Scan return.", INFO, G)
    y += 62
    for mark, name, meta, qty in [
        ("☑", "Chantilly Veil", "sold 1 · 3,500", "1"),
        ("☑", "Pearl Hair Comb", "sold 2 · 1,200", "1"),
        ("☐", "Ivory Clutch Bag", "sold 1 · 6,000", "0"),
    ]:
        els.append(rect(cx, y, cw, 56, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 12, y + 18, mark, 15, ACCENT if mark == "☑" else FAINT, g=G))
        els.append(text(cx + 36, y + 10, name, 13, INK if mark == "☑" else MUTED, width=cw - 120, g=G))
        els.append(text(cx + 36, y + 30, meta, 11, MUTED, width=cw - 120, g=G))
        y += 64
    sy = oy + TITLE_H + PHONE_H - 72 - 82
    els += _sticky(cx, sy, cw, "Refund · Cash", "4,600 AFN", "Post", G)
    els += _mnote(ox, oy, "Restock → sale_return_in. Refund is contra-revenue.", INFO)
    return els


def _m8(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "F1. Sales summary", g, "Sales")
    e, y = phone_header(cx, cy, cw, "Sales summary", left=ICON["back"], right=ICON["export"], g=G)
    els += e
    els.append(text(cx, y - 6, "01 – 12 Sept · Main branch · AFN", 11, MUTED, width=cw, g=G))
    y += 10
    kw = (cw - 10) / 2
    els += kpi_card(cx, y, kw, 78, "Revenue", "612,400", INK, None, ICON["cash"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Margin", "59.6%", OK, None, ICON["chart"], G)
    y += 88
    els += kpi_card(cx, y, kw, 78, "Sale lines", "268,900", INFO, None, ICON["tag"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Rental lines", "343,500", ACCENT, None, ICON["rental"], G)
    y += 96
    els += note(cx, y, cw, "Deposits held 145,000 AFN are a liability — excluded.", VIOLET, G)
    y += 66
    e, y = bar_chart(cx, y, cw, 160, "Revenue by day (AFN thousands)",
                     [("05", 0.77, "77"), ("06", 0.85, "85"), ("09", 0.59, "59"),
                      ("10", 0.70, "70"), ("12", 0.85, "85")], G)
    els += e
    els += _mnote(ox, oy, "Split by line_type. Mixed tickets feed both columns.")
    return els


MOBILE_SCREENS = [_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8]


def mobile():
    els = board_title(0, -150, "BOMS Mobile — Sales",
                      "Counter-first: phone search, Rent/Sell per line, print slip with barcode + QR, scan to return.")
    for i, fn in enumerate(MOBILE_SCREENS):
        ox, oy = grid_pos(i, PHONE_COLS, PHONE_W, PHONE_H)
        els += fn(ox, oy)
    els += flow_arrows(len(MOBILE_SCREENS), PHONE_COLS, PHONE_W, PHONE_H)
    return els
