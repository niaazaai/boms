#!/usr/bin/env python3
"""BOMS wireframes — SALES module (rent + sell bridal clothing).

Draws the *corrected* data model, not the original spec:

  • Deposits are a LIABILITY (finance_customer_deposits), never Income.
  • One order may mix `sale` and `rental` lines — `line_type` is authoritative,
    the header badge (Sale / Rental / Mixed) is derived.
  • Walk-in allowed for sale lines; rentals always need a named customer.
  • Rental lifecycle: draft → confirmed → out → returned → completed.
  • Late fee computed on "Mark returned", waivable with a reason.
  • Lost / damaged → sales_rental_claims (separate doc, not a "return").
  • Sale return (sales_sale_returns) ≠ rental return.
  • A/R lives in finance_receivables; order balance is derived display only.
  • Availability respects a cleaning buffer after return.

Exports: desktop() -> list, mobile() -> list
"""

from dsl import *

# ── placement constants ───────────────────────────────────────────
DESK_COLS = 4
PHONE_COLS = 6
DESK_NOTE_Y = TITLE_H + DESK_H + 16     # note strip under a desktop frame
PHONE_NOTE_Y = TITLE_H + PHONE_H + 14   # note strip under a phone frame

# two-column desktop content split (content width = 1136)
LW, GAP, RW = 704, 24, 408


# ── small local compositions (rect / text only) ───────────────────

def _h(x, y, label, g=None, size=13, color=INK):
    """Inline section heading inside a screen."""
    return [text(x, y, label, size, color, g=g or [])]


def _panel(x, y, w, h, title=None, color=HAIRLINE, bg=BG, g=None):
    g = g or []
    els = [rect(x, y, w, h, strokeColor=color, backgroundColor=bg,
                strokeWidth=1, groupIds=g)]
    if title:
        els.append(text(x + 16, y + 14, title, 12,
                        MUTED if color == HAIRLINE else color, width=w - 32, g=g))
    return els


def _kv(x, y, w, label, value, g=None, vcolor=INK, vsize=13):
    g = g or []
    return [
        text(x, y, label, 12, MUTED, width=w * 0.55, g=g),
        text(x + w * 0.45, y - 1, value, vsize, vcolor, "right", w * 0.55, g=g),
    ]


def _chiprow(x, y, items, g=None):
    """items = [(label, color)] → (elements, next_x)"""
    els, xx = [], x
    for lab, col in items:
        e, xx = chip(xx, y, lab, col, g=g)
        els += e
    return els, xx


def _radio(x, y, w, label, sub, on=False, g=None, color=ACCENT):
    """Selectable option row."""
    g = g or []
    els = [rect(x, y, w, 52, strokeColor=color if on else LINE,
                backgroundColor=ACCENT_BG if on else BG, strokeWidth=2 if on else 1,
                groupIds=g),
           base("ellipse", x + 14, y + 16, 18, 18, strokeColor=color if on else LINE,
                backgroundColor=color if on else BG, strokeWidth=1, groupIds=g),
           text(x + 42, y + 9, label, 13, INK, width=w - 60, g=g),
           text(x + 42, y + 28, sub, 11, MUTED, width=w - 60, g=g)]
    if on:
        els.append(text(x + 14, y + 19, ICON["check"], 10, "#ffffff", "center", 18, g))
    return els, y + 60


def _toggle(x, y, w, label, sub, on=True, g=None):
    g = g or []
    col = OK if on else LINE
    els = [text(x, y, label, 13, INK, width=w - 80, g=g),
           text(x, y + 20, sub, 11, MUTED, width=w - 80, g=g),
           rect(x + w - 56, y, 52, 28, strokeColor=col,
                backgroundColor=OK_BG if on else SOFT, strokeWidth=1, groupIds=g),
           base("ellipse", x + w - (28 if on else 54), y + 3, 22, 22, strokeColor=col,
                backgroundColor=col if on else BG, strokeWidth=1, groupIds=g)]
    return els, y + 46


def _report_card(x, y, w, h, icon, title, desc, g=None):
    g = g or []
    return [
        rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
        text(x + 14, y + 13, icon, 15, ACCENT, g=g),
        text(x + 14, y + 40, title, 12.5, INK, width=w - 28, g=g),
        text(x + 14, y + 60, desc, 10.5, MUTED, width=w - 28, g=g),
    ]


def _sticky(x, y, w, label, value, cta, g=None, sub=None):
    """Mobile sticky bottom total bar."""
    g = g or []
    els = [rect(x, y, w, 76, strokeColor=HAIRLINE, backgroundColor=SOFT,
                strokeWidth=1, groupIds=g),
           text(x + 14, y + 11, label, 10.5, MUTED, width=w - 160, g=g),
           text(x + 14, y + 28, value, 18, INK, width=w - 160, g=g)]
    if sub:
        els.append(text(x + 14, y + 54, sub, 10, VIOLET, width=w - 160, g=g))
    els += btn(x + w - 148, y + 18, 134, 42, cta, "primary", g)
    return els


def _seg(x, y, w, labels, active=0, g=None):
    """Segmented control (mobile period picker)."""
    g = g or []
    els = [rect(x, y, w, 34, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1, groupIds=g)]
    sw = w / len(labels)
    for i, lab in enumerate(labels):
        if i == active:
            els.append(rect(x + i * sw + 3, y + 3, sw - 6, 28, strokeColor=ACCENT,
                            backgroundColor=BG, strokeWidth=1, groupIds=g))
        els.append(text(x + i * sw, y + 9, lab, 11.5, ACCENT if i == active else MUTED,
                        "center", sw, g))
    return els, y + 44


# ══════════════════════════════════════════════════════════════════
#  DESKTOP — 16 screens × 4 columns
# ══════════════════════════════════════════════════════════════════

def desktop():
    els = board_title(
        0, -150, "BOMS Desktop — Sales",
        "Rent + sell bridal clothing · corrected model: deposits are a liability, "
        "mixed sale/rental orders, rental claims ≠ sale returns, A/R lives in finance_receivables · "
        "currency AFN · Sept 2026")

    rows = [
        (0, "ORDER CAPTURE"),
        (1, "RENTAL CHECKOUT, AVAILABILITY & PAYMENT"),
        (2, "RENTAL LIFECYCLE, CLAIMS & RETURNS"),
        (3, "CUSTOMERS & REPORTS"),
    ]
    for r, label in rows:
        _, ry = grid_pos(r * DESK_COLS, DESK_COLS)
        els += section_label(0, ry - 62, label)

    for i, fn in enumerate([_d01, _d02, _d03, _d04, _d05, _d06, _d07, _d08,
                            _d09, _d10, _d11, _d12, _d13, _d14, _d15, _d16]):
        ox, oy = grid_pos(i, DESK_COLS)
        els += fn(ox, oy)

    els += flow_arrows(16, DESK_COLS)
    return els


def _dnote(ox, oy, content, color=ACCENT):
    return note(ox, oy + DESK_NOTE_Y, DESK_W, content, color)


# ── 1. Sales hub ──────────────────────────────────────────────────
def _d01(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "1. Sales hub", "Sales", g, sub_active="Orders")
    G = [g]

    e, y = page_header(cx, cy, cw, "Sales",
                       [("＋ New Sale", "primary"), ("⏱️ New Rental", "accent")],
                       "Sat 12 Sept 2026 · Main branch · Al Dubai Bridal · AFN", G)
    els += e

    e, y = stat_row(cx, y, cw, [
        ("Today revenue (excl. deposits)", "84,500", INK, "+12% vs yesterday", ICON["cash"]),
        ("Open orders", "12", INK, "4 draft · 8 confirmed", ICON["receipt"]),
        ("Due back today", "3", ACCENT, "pickups 2 · returns 3", ICON["clock"]),
        ("Overdue returns", "2", DANGER, "late fee accruing", ICON["alert"]),
        ("Deposits held (liability)", "145,000", VIOLET, "18 open rentals", ICON["reserve"]),
        ("Unpaid A/R", "62,300", WARN, "finance_receivables", ICON["ledger"]),
    ], g=G)
    els += e

    els += note(cx, y, cw,
                "Deposits held is a LIABILITY tile — it is NOT part of Today revenue. "
                "Revenue = Σ sale lines + Σ rental lines only.", VIOLET, G)
    y += 74

    # left — today's schedule
    els += _h(cx, y, f"{ICON['calendar']}  Today · pickups & returns", G)
    e, _ = table(cx, y + 26, LW,
                 ["Time", "Order", "Customer", "Item", "Action"],
                 [["09:30", "SO26-000014", "Sara Ahmadi", "White A-Line Gown", ("Pick up", ACCENT)],
                  ["11:00", "SO26-000015", "Maryam Noori", "Gold Ball Gown", ("Pick up", ACCENT)],
                  ["14:00", "SO26-000011", "Fatima Rahimi", "Ivory Mermaid Gown", ("Return due", INFO)],
                  ["16:30", "SO26-000012", "Zahra Sadat", "Chantilly Veil", ("Return due", INFO)],
                  ["—", "SO26-000009", "Nasrin Amiri", "Rose Evening Gown", ("Overdue 2 d", DANGER)],
                  ["—", "SO26-000007", "Laila Karimi", "Gold Ball Gown", ("Overdue 1 d", DANGER)]],
                 G, widths=[0.7, 1.25, 1.3, 1.7, 1.05])
    els += e

    # right — recent orders
    rx = cx + LW + GAP
    els += _h(rx, y, f"{ICON['receipt']}  Recent orders", G)
    e, _ = table(rx, y + 26, RW,
                 ["Order", "Type", "Total", "Status"],
                 [["SO26-000018", ("Sale", INFO), "12,700", ("Paid", OK)],
                  ["SO26-000017", ("Rental", ACCENT), "9,000", ("Out", ACCENT)],
                  ["SO26-000016", ("Mixed", VIOLET), "15,200", ("Confirmed", INFO)],
                  ["SO26-000015", ("Rental", ACCENT), "11,500", ("Confirmed", INFO)],
                  ["SO26-000014", ("Rental", ACCENT), "8,500", ("Out", ACCENT)],
                  ["SO26-000013", ("Sale", INFO), "3,400", ("Partial", WARN)]],
                 G, widths=[1.25, 0.95, 0.85, 1.0])
    els += e

    els += _dnote(ox, oy,
                  "READS ONLY. Revenue KPI = Σ sales_order_items.line_total for the day (sale + rental lines).\n"
                  "Deposits held = Σ finance_customer_deposits.status='held' — a liability tile, never summed into revenue.\n"
                  "Due back today = sales_orders WHERE status='out' AND rental_end_date = today. Overdue = rental_end_date < today.\n"
                  "Unpaid A/R = Σ finance_receivables.balance_amount WHERE status IN ('open','partial') — never sales_orders.balance_amount.")
    return els


# ── 2. Orders list ────────────────────────────────────────────────
def _d02(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "2. Orders list", "Sales", g, sub_active="Orders")
    G = [g]

    e, y = page_header(cx, cy, cw, "Orders",
                       [("⬇ Export", "secondary"), ("＋ New Sale", "primary"),
                        ("⏱️ New Rental", "accent")], None, G)
    els += e
    e, y = tabs(cx, y, cw, ["All  (124)", "Sale  (57)", "Rental  (58)", "Mixed  (9)"], 0, G)
    els += e

    els += search_bar(cx, y, 420, "Search order # · customer name · phone…", G)
    els += filter_chips(cx + 440, y + 5, ["Any status", "Draft", "Confirmed", "Out",
                                          "Returned", "Completed", "Overdue"], 0, G)
    y += 56

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
                  ["SO26-000015", "Zahra Sadat", ("Rental", ACCENT), "13–17 Sep", "11,500",
                   "5,000", ("8,000", VIOLET), ("6,500", WARN), ("Confirmed", INFO)],
                  ["SO26-000014", "Nasrin Amiri", ("Rental", ACCENT), "09–12 Sep", "8,500",
                   "8,500", ("6,000", VIOLET), "0", ("Out", DANGER)],
                  ["SO26-000013", "Walk-in", ("Sale", INFO), "09 Sep", "3,400",
                   "1,400", "—", ("2,000", WARN), ("Confirmed", INFO)],
                  ["SO26-000012", "Laila Karimi", ("Rental", ACCENT), "05–08 Sep", "9,800",
                   "9,800", ("—  refunded", MUTED), "0", ("Completed", OK)]],
                 G, widths=[1.2, 1.3, 0.85, 1.0, 0.85, 0.8, 1.0, 0.85, 1.0])
    els += e
    e, y = pagination(cx, y, cw - 80, "1–8 of 124 orders", G)
    els += e

    els += _dnote(ox, oy,
                  "READS sales_orders + derived columns. Type badge = DERIVED order_kind from sales_order_items.line_type\n"
                  "(all sale → Sale · all rental → Rental · both → Mixed). The header never contradicts its lines.\n"
                  "Deposit held column = Σ finance_customer_deposits WHERE sales_order_id = order AND status='held' — shown\n"
                  "SEPARATELY from Paid, because a deposit is not payment toward the total. Balance is a display value\n"
                  "recomputed from payments; the authoritative A/R row lives in finance_receivables.")
    return els


# ── 3. New order — customer step ──────────────────────────────────
def _d03(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "3. New order · customer step", "Sales", g,
                                     sub_active="Orders")
    G = [g]
    DW = 420
    LWW = cw - DW - 32

    e, y = page_header(cx, cy, LWW, "New order", [("Cancel", "ghost")],
                       "Step 1 of 3 — who is this order for?", G)
    els += e
    e, y = timeline(cx, y, LWW, [("Customer", "current"), ("Items", "todo"),
                                 ("Payment", "todo")], G)
    els += e
    y += 10

    els += search_bar(cx, y, LWW, "0700 99 88 77", G)
    y += 56

    els += empty_state(cx, y, LWW, 196, ICON["customers"],
                       "No customer matches 0700 99 88 77",
                       "Search by phone (primary key for counter staff), name or customer code.",
                       None, G)
    y += 212

    els += btn(cx, y, (LWW - 16) / 2, 52, "＋ Create customer  (opens quick form →)", "primary", G)
    els += btn(cx + (LWW - 16) / 2 + 16, y, (LWW - 16) / 2, 52,
               "🛒 Continue as Walk-in", "secondary", G)
    y += 66

    els += note(cx, y, LWW,
                "Walk-in is allowed for SALE lines only — sales_orders.customer_id stays NULL.\n"
                "The moment a RENTAL line is added the order demands a named customer:\n"
                "you must know who is holding the dress and who owes the deposit back.",
                WARN, G)

    # quick-create drawer
    e, fx, fy, fw = drawer(cx, cy - 20, cw, ch + 20, "Quick create customer",
                           subtitle="sales_customers · minimum fields for the counter", g=G)
    els += e
    e, fy = field(fx, fy, fw, "Full name", "Sara Ahmadi", G, required=True)
    els += e
    e, fy = field(fx, fy, (fw - 16) / 2, "Phone", "0700 12 34 56", G, required=True)
    els += e
    e2, _ = field(fx + (fw - 16) / 2 + 16, fy - 68, (fw - 16) / 2, "Alt phone", "…optional", G)
    els += e2
    e, fy = field(fx, fy, (fw - 16) / 2, "Wedding date", "28 Sep 2026", G)
    els += e
    e2, _ = select(fx + (fw - 16) / 2 + 16, fy - 68, (fw - 16) / 2, "Gender", "Female", G)
    els += e2
    e, fy = field(fx, fy, fw, "Customer code", "CUS26-0117  (auto)", G)
    els += e
    e, fy = textarea(fx, fy, fw, "Note", "Bride · referred by Maryam Noori", G, rows=2)
    els += e
    els += note(fx, fy, fw, "Saves to sales_customers.\nPhone is indexed (tenant_id, phone).", ACCENT, G)
    els += btn(fx, fy + 76, fw, 46, "Save & use customer", "primary", G)

    els += _dnote(ox, oy,
                  "WRITES sales_customers on quick-create (customer_code auto CUS26-####, indexed on tenant_id+phone).\n"
                  "Walk-in path writes NOTHING here — sales_orders.customer_id is NULLABLE and stays NULL.\n"
                  "Guard: adding any sales_order_items row with line_type='rental' blocks save while customer_id IS NULL.")
    return els


# ── 4. New sale checkout ──────────────────────────────────────────
def _d04(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "4. New sale checkout", "Sales", g,
                                     sub_active="Orders")
    G = [g]

    e, y = page_header(cx, cy, cw, "New sale · SO26-000019",
                       [("Save draft", "secondary"), ("Confirm & collect", "primary")],
                       "Walk-in customer · Main branch · 12 Sept 2026 · AFN", G)
    els += e
    e, y = timeline(cx, y, cw, [("Customer", "done"), ("Items", "current"),
                                ("Payment", "todo")], G)
    els += e
    y += 8

    els += search_bar(cx, y, LW, f"{ICON['tag']}  Scan barcode or search SKU / item name…", G)
    els += btn(cx + LW - 132, y + 4, 124, 32, "＋ Add manually", "secondary", G)
    ly = y + 56

    e, ly = table(cx, ly, LW,
                  ["Item", "SKU", "Line type", "Qty", "Unit price", "Disc", "Line total"],
                  [["Chantilly Veil", "ADF26-0042", ("Sale", INFO), "1", "3,500", "0", "3,500"],
                   ["Pearl Hair Comb", "ADF26-0118", ("Sale", INFO), "2", "1,200", "0", "2,400"],
                   ["Satin Bridal Gloves", "ADF26-0206", ("Sale", INFO), "1", "900", "100", "800"],
                   ["Ivory Clutch Bag", "ADF26-0311", ("Sale", INFO), "1", "6,000", "0", "6,000"]],
                  G, widths=[1.9, 1.2, 0.95, 0.5, 0.95, 0.6, 0.95])
    els += e

    els += note(cx, ly, LW,
                "Every line carries line_type. Add a rental line here and the header badge flips to Mixed\n"
                "and the order starts demanding a named customer + a rental window.", INFO, G)
    ly += 62
    e, ly = field(cx, ly, (LW - 16) / 2, "Order discount", "0", G)
    els += e
    e2, _ = select(cx + (LW - 16) / 2 + 16, ly - 68, (LW - 16) / 2, "Salesperson", "Ahmad Zaki", G)
    els += e2

    # right — totals + payment split
    rx = cx + LW + GAP
    ry = y
    els += _panel(rx, ry, RW, 226, None, HAIRLINE, BG, G)
    e, _ = money_row(rx + 18, ry + 20, RW - 36,
                     [("Subtotal (4 sale lines)", "12,700 AFN"),
                      ("Order discount", "− 100 AFN"),
                      ("Tax", "0 AFN"),
                      ("Other charges", "0 AFN"),
                      ("Deposit (liability)", "n/a — no rental lines")],
                     G, total=("Total due", "12,600 AFN"))
    els += e
    ry += 244

    els += _h(rx, ry, f"{ICON['cash']}  Payment split", G)
    ry += 26
    e, ry2 = select(rx, ry, RW, "Method", "Cash", G)
    els += e
    e, ry2 = select(rx, ry2, RW, "Finance account", "Main cash drawer (CASH-01)", G)
    els += e
    e, ry2 = field(rx, ry2, RW, "Amount received", "12,600", G)
    els += e
    els += btn(rx, ry2, RW, 46, "＋ Add second payment method", "secondary", G)
    ry2 += 58
    e, _ = money_row(rx, ry2, RW, [("Paid now", "12,600 AFN"), ("Change", "0 AFN")],
                     G, total=("Balance → A/R", "0 AFN"))
    els += e

    els += _dnote(ox, oy,
                  "WRITES sales_orders (order_kind DERIVED = 'sale', customer_id NULL for walk-in) + sales_order_items\n"
                  "(line_type='sale', unit_cost_snapshot frozen for COGS) + sales_order_payments (payment_type='full').\n"
                  "Confirm → inventory_stock_transactions type='sale_out' (qty leaves stock permanently).\n"
                  "Payment → finance_transactions IN against finance_accounts. Any residual balance → finance_receivables.\n"
                  "NO deposit rows: deposits only exist for rental lines.")
    return els


# ── 5. New rental checkout ────────────────────────────────────────
def _d05(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "5. New rental checkout", "Sales", g,
                                     sub_active="Rentals")
    G = [g]

    e, y = page_header(cx, cy, cw, "New rental · SO26-000020",
                       [("Save draft", "secondary"), ("Check availability", "secondary"),
                        ("Confirm & reserve", "primary")],
                       "Sara Ahmadi · 0700 12 34 56 · wedding 28 Sep 2026", G)
    els += e

    fwd = (LW - 48) / 4
    e, y2 = field(cx, y, fwd, "Event date", "26 Sep 2026", G, required=True)
    els += e
    e2, _ = field(cx + fwd + 16, y, fwd, "Rental start", "24 Sep 2026", G, required=True)
    els += e2
    e2, _ = field(cx + 2 * (fwd + 16), y, fwd, "Rental end (due back)", "28 Sep 2026", G, required=True)
    els += e2
    e2, _ = field(cx + 3 * (fwd + 16), y, fwd, "Cleaning buffer", "2 days (tenant setting)", G)
    els += e2
    y = y2

    e, xx = _chiprow(cx, y, [("✓ Available 24–28 Sep", OK),
                             ("Blocked until 30 Sep (cleaning)", VIOLET),
                             ("5 rental days", INFO)], G)
    els += e
    y += 40

    e, ly = table(cx, y, LW,
                  ["Item", "SKU", "Line", "Days", "Rate/day", "Line total", "Deposit", "Late/day"],
                  [["White A-Line Gown", "ADF26-0042", ("Rental", ACCENT), "5", "1,400",
                    "7,000", ("8,000", VIOLET), "800"],
                   ["Gold Ball Gown", "ADF26-0077", ("Rental", ACCENT), "5", "1,100",
                    "5,500", ("6,000", VIOLET), "700"],
                   ["Chantilly Veil", "ADF26-0118", ("Sale", INFO), "—", "3,500",
                    "3,500", "—", "—"]],
                  G, widths=[1.75, 1.15, 0.85, 0.5, 0.85, 0.9, 0.85, 0.7])
    els += e

    els += note(cx, ly, LW,
                "Line 3 is a SALE line on a rental order → header badge becomes Mixed. The veil is sold and leaves\n"
                "stock permanently; the two gowns are reserved and come back. One document, two economics.", VIOLET, G)
    ly += 62
    e, _ = textarea(cx, ly, LW, "Fitting / alteration note",
                    "Hem shortened 4 cm · bring shoes to fitting on 20 Sep", G, rows=2)
    els += e

    # right — calendar + money
    rx = cx + LW + GAP
    e, ry = calendar_grid(rx, y - 58, RW, 250,
                          "September 2026 · White A-Line Gown availability",
                          {5: DANGER, 6: DANGER, 7: DANGER, 12: WARN, 13: WARN,
                           24: ACCENT, 25: ACCENT, 26: ACCENT, 27: ACCENT, 28: ACCENT,
                           29: OK, 30: OK}, G)
    els += e
    e, xx = _chiprow(rx, ry - 6, [("This booking", ACCENT), ("Booked", DANGER),
                                  ("Cleaning", OK)], G)
    els += e
    ry += 30

    els += _panel(rx, ry, RW, 148, None, HAIRLINE, BG, G)
    e, _ = money_row(rx + 18, ry + 18, RW - 36,
                     [("Rental lines (2)", "12,500 AFN"),
                      ("Sale lines (1)", "3,500 AFN"),
                      ("Discount", "0 AFN")],
                     G, total=("Revenue total", "16,000 AFN"))
    els += e
    ry += 164

    els += _panel(rx, ry, RW, 132, f"{ICON['reserve']}  DEPOSIT — LIABILITY, NOT REVENUE",
                  VIOLET, VIOLET_BG, G)
    els += _kv(rx + 18, ry + 44, RW - 36, "Deposit required (Σ per line)", "14,000 AFN", G, VIOLET, 15)
    els += _kv(rx + 18, ry + 72, RW - 36, "Collect now", "14,000 AFN", G, INK)
    els += _kv(rx + 18, ry + 98, RW - 36, "Returned to customer on clean return", "14,000 AFN", G, MUTED, 12)

    els += _dnote(ox, oy,
                  "WRITES sales_orders (rental_start_date, rental_end_date, event_date; order_kind DERIVED='mixed')\n"
                  "+ sales_order_items with per-line deposit_amount, rental dates and late_fee_per_day snapshot.\n"
                  "Confirm → inventory_reservations (one row PER sales_order_item_id, not per order) for rental lines;\n"
                  "sale lines instead hit inventory_stock_transactions type='sale_out'. Availability window =\n"
                  "rental_start … rental_end + tenant cleaning_buffer_days. Deposit → finance_customer_deposits status='held'.",
                  VIOLET)
    return els


# ── 6. Rental availability conflict ───────────────────────────────
def _d06(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "6. Rental availability conflict", "Sales", g,
                                     sub_active="Rentals")
    G = [g]

    e, y = page_header(cx, cy, cw, "New rental · SO26-000020",
                       [("Save draft", "secondary"), ("Confirm & reserve", "primary")],
                       "Sara Ahmadi · 24–28 Sep 2026", G)
    els += e
    e, ly = table(cx, y + 10, cw,
                  ["Item", "SKU", "Line", "Days", "Rate/day", "Line total", "Deposit", "Status"],
                  [["White A-Line Gown", "ADF26-0042", ("Rental", ACCENT), "5", "1,400",
                    "7,000", ("8,000", VIOLET), ("⚠ Conflict", DANGER)],
                   ["Gold Ball Gown", "ADF26-0077", ("Rental", ACCENT), "5", "1,100",
                    "5,500", ("6,000", VIOLET), ("✓ Available", OK)]],
                  G, widths=[1.75, 1.15, 0.85, 0.5, 0.85, 0.9, 0.85, 1.0])
    els += e

    # modal
    MW, MH = 700, 468
    mx, my = cx + (cw - MW) / 2, cy + (ch - MH) / 2 - 20
    els += modal(cx, cy - 26, cw, ch + 26,
                 "⚠  Booking conflict — White A-Line Gown",
                 "ADF26-0042 is already reserved for part of 24–28 Sep 2026.",
                 MW, MH,
                 [("Change dates", "secondary"), ("Join waitlist", "secondary"),
                  ("Swap to alternative", "danger")], G)

    bx, by = mx + 24, my + 96
    els += _panel(bx, by, MW - 48, 108, None, DANGER, DANGER_BG, G)
    els += [text(bx + 16, by + 14, "Clashing booking", 11, DANGER, width=300, g=G),
            text(bx + 16, by + 34, "SO26-000015 · Zahra Sadat · 0700 55 44 33", 13, INK,
                 width=MW - 100, g=G),
            text(bx + 16, by + 56, "Out 23 Sep → due back 27 Sep · +2 days cleaning buffer → free 29 Sep",
                 12, DANGER, width=MW - 100, g=G),
            text(bx + 16, by + 78, "Overlap with your window: 24, 25, 26, 27 Sep", 12, MUTED,
                 width=MW - 100, g=G)]
    by += 124

    els += _h(bx, by, "Suggested alternatives — same size, same window", G, 12, MUTED)
    e, _ = table(bx, by + 20, MW - 48,
                 ["Dress", "SKU", "Size", "Rate/day", "Free 24–28 Sep"],
                 [["Ivory Mermaid Gown", "ADF26-0091", "38", "1,350", ("✓ Available", OK)],
                  ["Pearl Empire Gown", "ADF26-0104", "38", "1,250", ("✓ Available", OK)],
                  ["White A-Line Gown", "ADF26-0143", "40", "1,400", ("✓ Available", OK)]],
                 G, widths=[1.8, 1.1, 0.55, 0.9, 1.1], row_h=38, zebra=False)
    els += e

    els += _dnote(ox, oy,
                  "READS inventory_reservations JOIN sales_orders. A dress is unavailable when the requested window\n"
                  "overlaps [rental_start_date, rental_end_date + cleaning_buffer_days] of any reservation whose order\n"
                  "status IN ('confirmed','out') — the buffer is part of the block, not a suggestion.\n"
                  "No write happens until the clash is resolved: Confirm is refused rather than double-booking the gown.",
                  DANGER)
    return els


# ── 7. Collect payment drawer ─────────────────────────────────────
def _d07(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "7. Collect payment drawer", "Sales", g,
                                     sub_active="Orders")
    G = [g]

    e, y = page_header(cx, cy, cw - 460, "SO26-000019 · Sara Ahmadi",
                       [("Collect payment", "primary")],
                       "Mixed order · 24–28 Sep 2026 · Confirmed", G)
    els += e
    e, _ = table(cx, y + 8, cw - 460,
                 ["Item", "Line", "Total"],
                 [["White A-Line Gown", ("Rental", ACCENT), "7,000"],
                  ["Gold Ball Gown", ("Rental", ACCENT), "5,500"],
                  ["Chantilly Veil", ("Sale", INFO), "3,500"]],
                 G, widths=[2.0, 0.9, 0.8])
    els += e

    e, fx, fy, fw = drawer(cx, cy - 20, cw, ch + 20, "Collect payment",
                           subtitle="SO26-000019 · Sara Ahmadi · AFN", g=G)
    els += e

    e, fy = select(fx, fy, fw, "Payment type", "Deposit  (refundable — liability)", G, required=True)
    els += e
    els += note(fx, fy - 4, fw,
                "deposit → finance_customer_deposits (status 'held') + Cash IN.\n"
                "It does NOT reduce the order balance and NEVER posts to Income.",
                VIOLET, G)
    fy += 62
    e, fy = field(fx, fy, fw, "Amount", "14,000", G, required=True)
    els += e
    e, fy = select(fx, fy, (fw - 16) / 2, "Method", "Cash", G, required=True)
    els += e
    e2, _ = field(fx + (fw - 16) / 2 + 16, fy - 68, (fw - 16) / 2, "Reference no.", "…optional", G)
    els += e2
    e, fy = select(fx, fy, fw, "Finance account", "Main cash drawer (CASH-01)", G, required=True)
    els += e
    e, fy = field(fx, fy, fw, "Paid at", "12 Sep 2026  ·  14:22", G)
    els += e

    els += _panel(fx, fy, fw, 176, "RESULTING POSITION", HAIRLINE, SOFT2, G)
    e, _ = money_row(fx + 16, fy + 40, fw - 32,
                     [("Order total (revenue)", "16,000 AFN"),
                      ("Paid toward total", "6,000 AFN"),
                      ("Deposit held (liability)", "14,000 AFN"),
                      ("Balance → finance_receivables", "10,000 AFN")],
                     G)
    els += e
    fy += 192
    els += btn(fx, fy, fw, 48, "Record payment", "primary", G)

    els += _dnote(ox, oy,
                  "WRITES sales_order_payments (payment_type ∈ deposit | installment | full | refund | late_fee)\n"
                  "+ finance_transactions IN against the chosen finance_accounts row (link is mandatory — no orphan cash).\n"
                  "payment_type='deposit' → finance_customer_deposits (status='held'); it is a LIABILITY: it never touches\n"
                  "Income and never reduces the order balance. installment/full → reduces finance_receivables.balance_amount\n"
                  "and the derived sales_orders.paid_amount / balance_amount display columns.",
                  VIOLET)
    return els


# ── 8. Order detail · Sale ────────────────────────────────────────
def _d08(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "8. Order detail · Sale", "Sales", g,
                                     sub_active="Orders")
    G = [g]

    e, y = page_header(cx, cy, cw, "SO26-000018",
                       [("🖨 Print receipt", "secondary"), ("Sale return", "secondary"),
                        ("Void", "danger")],
                       "Walk-in customer · 12 Sept 2026 · Main branch", G)
    els += e
    e, _ = _chiprow(cx, y - 4, [("Sale", INFO), ("Completed", OK), ("Paid in full", OK),
                                ("No deposit — sale only", MUTED), ("Cashier: Ahmad Zaki", MUTED)], G)
    els += e
    y += 40

    els += _h(cx, y, f"{ICON['receipt']}  Lines", G)
    e, ly = table(cx, y + 26, LW,
                  ["Item", "SKU", "Line", "Qty", "Unit price", "Cost snap.", "Line total"],
                  [["Chantilly Veil", "ADF26-0042", ("Sale", INFO), "1", "3,500", "1,900", "3,500"],
                   ["Pearl Hair Comb", "ADF26-0118", ("Sale", INFO), "2", "1,200", "550", "2,400"],
                   ["Satin Bridal Gloves", "ADF26-0206", ("Sale", INFO), "1", "900", "380", "800"],
                   ["Ivory Clutch Bag", "ADF26-0311", ("Sale", INFO), "1", "6,000", "3,100", "6,000"]],
                  G, widths=[1.85, 1.15, 0.85, 0.5, 0.95, 0.95, 0.95])
    els += e

    els += _h(cx, ly + 8, f"{ICON['cash']}  Payments", G)
    e, ly = table(cx, ly + 34, LW,
                  ["Payment #", "Date", "Type", "Method", "Account", "Amount"],
                  [["PAY26-0061", "12 Sep 14:20", ("full", INFO), "Cash", "CASH-01", "8,000"],
                   ["PAY26-0062", "12 Sep 14:21", ("installment", INFO), "Card", "BANK-AZ-01", "4,600"]],
                  G, widths=[1.15, 1.15, 0.95, 0.75, 1.0, 0.8], row_h=40)
    els += e

    els += note(cx, ly, LW,
                "No deposit row exists for this order — deposits belong to rental lines only.\n"
                "COGS = Σ qty × unit_cost_snapshot = 6,530 AFN, frozen at sale time.", INFO, G)

    rx = cx + LW + GAP
    ry = y
    els += _panel(rx, ry, RW, 208, None, HAIRLINE, BG, G)
    e, _ = money_row(rx + 18, ry + 20, RW - 36,
                     [("Subtotal", "12,700 AFN"), ("Discount", "− 100 AFN"),
                      ("Tax", "0 AFN"), ("Paid toward total", "12,600 AFN"),
                      ("Deposit held", "— (not a rental)")],
                     G, total=("Balance", "0 AFN"))
    els += e
    ry += 226
    els += _panel(rx, ry, RW, 116, "GROSS MARGIN (this order)", HAIRLINE, SOFT2, G)
    els += _kv(rx + 18, ry + 44, RW - 36, "Revenue", "12,600 AFN", G)
    els += _kv(rx + 18, ry + 68, RW - 36, "COGS (cost snapshots)", "− 6,530 AFN", G)
    els += _kv(rx + 18, ry + 92, RW - 36, "Margin", "6,070 AFN  (48%)", G, OK, 14)
    ry += 132
    els += _h(rx, ry, "Actions", G, 12, MUTED)
    els += btn(rx, ry + 22, RW, 44, "🖨  Print / share receipt", "secondary", G)
    els += btn(rx, ry + 74, RW, 44, "↩  Sale return (refund + restock)", "secondary", G)
    els += btn(rx, ry + 126, RW, 44, "✕  Void order (reverse everything)", "danger", G)

    els += _dnote(ox, oy,
                  "READS sales_orders + sales_order_items + sales_order_payments. Balance is DERIVED from payments;\n"
                  "the authoritative open amount is finance_receivables (here closed, so nothing is open).\n"
                  "'Sale return' opens sales_sale_returns — the SOLD-goods document (refund + optional restock).\n"
                  "It is a different document from a rental return and from sales_rental_claims. Never label both 'return'.\n"
                  "'Void' on a completed order writes reversing rows: inventory_stock_transactions, finance_transactions, A/R.",
                  INFO)
    return els


# ── 9. Order detail · Rental ──────────────────────────────────────
def _d09(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "9. Order detail · Rental", "Sales", g,
                                     sub_active="Rentals")
    G = [g]

    e, y = page_header(cx, cy, cw, "SO26-000017",
                       [("Collect payment", "secondary"), ("Raise claim", "danger"),
                        ("Mark returned", "primary")],
                       "Maryam Noori · 0700 12 34 56 · wedding 16 Sept 2026", G)
    els += e
    e, _ = _chiprow(cx, y - 4, [("Rental", ACCENT), ("Out", ACCENT), ("Overdue 2 days", DANGER),
                                ("Deposit held 6,000", VIOLET), ("Balance 4,500", WARN)], G)
    els += e
    y += 42

    e, y = timeline(cx, y, cw, [("draft", "done"), ("confirmed", "done"), ("out", "current"),
                                ("returned", "todo"), ("completed", "todo")], G)
    els += e
    y += 10

    els += _panel(cx, y, LW, 108, "RENTAL WINDOW", HAIRLINE, SOFT2, G)
    qw = (LW - 36) / 4
    for i, (lab, val, col) in enumerate([
            ("Event date", "16 Sep 2026", INK), ("Out on", "12 Sep 2026", INK),
            ("Due back", "16 Sep 2026", DANGER), ("Today", "18 Sep → 2 days late", DANGER)]):
        els += [text(cx + 18 + i * qw, y + 42, lab, 11, MUTED, width=qw - 12, g=G),
                text(cx + 18 + i * qw, y + 62, val, 13, col, width=qw - 12, g=G)]
    els.append(text(cx + 18, y + 86, "Available again 20 Sep 2026 after the 2-day cleaning buffer",
                    11, VIOLET, width=LW - 36, g=G))
    y += 124

    e, ly = table(cx, y, LW,
                  ["Item", "SKU", "Line", "Days", "Rate/day", "Line total", "Deposit", "Late/day"],
                  [["Ivory Mermaid Gown", "ADF26-0091", ("Rental", ACCENT), "4", "1,350",
                    "5,400", ("6,000", VIOLET), "800"],
                   ["Chantilly Veil", "ADF26-0118", ("Rental", ACCENT), "4", "900",
                    "3,600", ("—", MUTED), "200"]],
                  G, widths=[1.75, 1.15, 0.85, 0.5, 0.85, 0.9, 0.85, 0.7])
    els += e

    els += _panel(cx, ly, LW, 102, f"{ICON['photo']}  CONDITION ON DISPATCH", HAIRLINE, BG, G)
    for i in range(4):
        els.append(rect(cx + 18 + i * 68, ly + 36, 58, 48, strokeColor=HAIRLINE,
                        backgroundColor=SOFT, strokeWidth=1, groupIds=G))
        els.append(text(cx + 18 + i * 68, ly + 54, ICON["dress"], 14, FAINT, "center", 58, G))
    els.append(text(cx + 300, ly + 40, "Checked out as: Good · no marks · zip intact",
                    12.5, INK, width=LW - 320, g=G))
    els.append(text(cx + 300, ly + 62, "Signed by Maryam Noori · staff Ahmad Zaki · 12 Sep 09:34",
                    11, MUTED, width=LW - 320, g=G))

    rx = cx + LW + GAP
    ry = y
    els += _panel(rx, ry, RW, 160, f"{ICON['reserve']}  DEPOSIT — LIABILITY", VIOLET, VIOLET_BG, G)
    els += _kv(rx + 18, ry + 44, RW - 36, "Deposit required", "6,000 AFN", G, INK)
    els += _kv(rx + 18, ry + 70, RW - 36, "Deposit held now", "6,000 AFN", G, VIOLET, 15)
    els += _kv(rx + 18, ry + 98, RW - 36, "Applied / forfeited", "0 AFN", G, MUTED, 12)
    els.append(text(rx + 18, ry + 122, "Settled on Mark returned — apply, forfeit or refund",
                    11, VIOLET, width=RW - 36, g=G))
    ry += 176

    els += _panel(rx, ry, RW, 168, None, HAIRLINE, BG, G)
    e, _ = money_row(rx + 18, ry + 18, RW - 36,
                     [("Rental revenue", "9,000 AFN"),
                      ("Paid toward total", "4,500 AFN"),
                      ("Late fee (accruing)", "2,000 AFN"),
                      ("Deposit held (separate)", "6,000 AFN")],
                     G, total=("Balance → A/R", "6,500 AFN"))
    els += e
    ry += 184
    els += btn(rx, ry, RW, 46, "✓  Mark returned", "primary", G)
    els += btn(rx, ry + 54, RW, 44, "⚠  Raise rental claim (damage / loss)", "danger", G)

    els += _dnote(ox, oy,
                  "READS sales_orders (status, rental_start_date, rental_end_date, actual_return_date) + items + payments\n"
                  "+ finance_customer_deposits (held) + finance_receivables (the real A/R). Lifecycle transitions:\n"
                  "confirmed → inventory_reservations created; 'Mark out' → inventory_stock_transactions type='rent_out';\n"
                  "'Mark returned' → type='rent_return' + reservation released + cleaning buffer applied; then 'completed'.\n"
                  "Deposit held is displayed SEPARATELY from Paid toward total — they are different money.",
                  ACCENT)
    return els


# ── 10. Mark returned ─────────────────────────────────────────────
def _d10(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "10. Mark returned (rental)", "Sales", g,
                                     sub_active="Rentals")
    G = [g]

    e, y = page_header(cx, cy, cw, "Mark returned · SO26-000017",
                       [("Cancel", "ghost"), ("Confirm return", "primary")],
                       "Maryam Noori · Ivory Mermaid Gown + Chantilly Veil · due back 16 Sep 2026", G)
    els += e

    els += _h(cx, y, "1 · Condition on return", G)
    y += 26
    ow = (LW - 36) / 4
    for i, (lab, sub, on) in enumerate([
            ("Good", "straight back to stock", False),
            ("Needs cleaning", "buffer +2 days", True),
            ("Damaged", "→ opens rental claim", False),
            ("Lost", "→ claim + write-off", False)]):
        col = {0: OK, 1: ACCENT, 2: WARN, 3: DANGER}[i]
        e, _ = _radio(cx + i * (ow + 12), y, ow, lab, sub, on, G, col)
        els += e
    y += 68
    e, y = textarea(cx, y, LW, "Return note", "Light make-up mark on collar — sent to cleaner", G, rows=2)
    els += e

    els += _h(cx, y, "2 · Late fee (computed, waivable)", G)
    y += 26
    els += _panel(cx, y, LW, 196, None, WARN, WARN_BG, G)
    e, _ = money_row(cx + 18, y + 18, LW - 36,
                     [("Rental end (due back)", "16 Sep 2026"),
                      ("Actual return date", "18 Sep 2026"),
                      ("late_days = max(0, actual − end)", "2 days"),
                      ("Σ line late fee/day  (800 + 200)", "1,000 AFN/day"),
                      ("Computed late fee  =  2 × 1,000", "2,000 AFN")], G)
    els += e
    e2, _ = field(cx + 18, y + 150, (LW - 52) / 2, "Waive amount", "500", G)
    els += e2
    e2, _ = field(cx + 18 + (LW - 52) / 2 + 16, y + 150, (LW - 52) / 2,
                  "Waive reason (required if waived)", "Loyal customer — 4th rental", G)
    els += e2
    y += 226
    els += _kv(cx, y, LW, "Late fee charged after waiver  (2,000 − 500)", "1,500 AFN", G, DANGER, 15)

    # right — deposit settlement
    rx = cx + LW + GAP
    ry = cy + 64
    els += _panel(rx, ry, RW, 92, f"{ICON['reserve']}  DEPOSIT SETTLEMENT", VIOLET, VIOLET_BG, G)
    els += _kv(rx + 18, ry + 44, RW - 36, "Deposit held", "6,000 AFN", G, VIOLET, 16)
    els.append(text(rx + 18, ry + 68, "Split the held amount across the three outcomes below",
                    11, VIOLET, width=RW - 36, g=G))
    ry += 106

    e, ry = _radio(rx, ry, RW, "Apply to balance  —  1,500 AFN",
                   "Reduces finance_receivables · becomes revenue collected", True, G, ACCENT)
    els += e
    e, ry = _radio(rx, ry, RW, "Forfeit  —  0 AFN",
                   "Only a forfeited deposit becomes INCOME", False, G, WARN)
    els += e
    e, ry = _radio(rx, ry, RW, "Refund to customer  —  4,500 AFN",
                   "Cash OUT · liability cleared · not an expense", True, G, OK)
    els += e
    ry += 6

    els += _panel(rx, ry, RW, 168, None, HAIRLINE, BG, G)
    e, _ = money_row(rx + 18, ry + 18, RW - 36,
                     [("Rental revenue", "9,000 AFN"),
                      ("Late fee charged", "1,500 AFN"),
                      ("Paid so far", "− 4,500 AFN"),
                      ("Deposit applied", "− 1,500 AFN")],
                     G, total=("Remaining balance", "4,500 AFN"))
    els += e
    ry += 184
    els += btn(rx, ry, RW, 48, "✓  Confirm return & settle deposit", "primary", G)

    els += _dnote(ox, oy,
                  "WRITES sales_orders: status='returned', actual_return_date, late_days, late_fee_amount=2,000,\n"
                  "late_fee_waived_amount=500 + waiver reason, return_condition='needs_cleaning'.\n"
                  "inventory_stock_transactions type='rent_return' (qty back) · inventory_reservations released ·\n"
                  "availability blocked until actual_return_date + cleaning_buffer_days.\n"
                  "finance_customer_deposits: 1,500 applied → finance_receivables, 4,500 refunded → finance_transactions OUT,\n"
                  "0 forfeited. ONLY the forfeited slice ever posts to Income. Condition 'damaged'/'lost' opens sales_rental_claims instead.",
                  VIOLET)
    return els


# ── 11. Rental claim ──────────────────────────────────────────────
def _d11(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "11. Rental claim (damage / loss)", "Sales", g,
                                     sub_active="Rentals")
    G = [g]

    e, y = page_header(cx, cy, cw, "Rental claim · CLM26-0004",
                       [("Cancel", "ghost"), ("Post claim", "danger")],
                       "SO26-000014 · Nasrin Amiri · Rose Evening Gown ADF26-0176", G)
    els += e
    e, _ = _chiprow(cx, y - 4, [("Claim — not a return", DANGER), ("Rental", ACCENT),
                                ("Deposit held 6,000", VIOLET)], G)
    els += e
    y += 42

    els += note(cx, y, cw,
                "A lost or destroyed dress is NOT a return: nothing comes back to stock. This document charges the "
                "customer, consumes the deposit and writes the asset off. Sale returns and rental returns are separate documents.",
                DANGER, G)
    y += 62

    e, y2 = select(cx, y, (LW - 16) / 2, "Claim type", "Loss — dress not returned", G, required=True)
    els += e
    e2, _ = field(cx + (LW - 16) / 2 + 16, y, (LW - 16) / 2, "Claim date", "20 Sep 2026", G, required=True)
    els += e2
    y = y2

    e, ly = table(cx, y, LW,
                  ["Item", "SKU", "Qty", "Replacement value", "Assessed charge"],
                  [["Rose Evening Gown", "ADF26-0176", "1", "40,000", ("32,000", DANGER)],
                   ["Matching Veil", "ADF26-0182", "1", "4,000", ("0  (returned)", MUTED)]],
                  G, widths=[1.9, 1.2, 0.55, 1.2, 1.2])
    els += e
    e, ly = textarea(cx, ly, LW, "Assessment note",
                     "Customer reports dress lost in transit after the event. Depreciated replacement "
                     "value agreed at 80% · photos and WhatsApp confirmation on file.", G, rows=3)
    els += e

    els += _panel(cx, ly, LW, 116, f"{ICON['dispose']}  LINKED INVENTORY WRITE-OFF", DANGER, DANGER_BG, G)
    els += [text(cx + 18, ly + 44, "DSP26-0011 · Rose Evening Gown ADF26-0176 · qty 1",
                 13, INK, width=LW - 220, g=G),
            text(cx + 18, ly + 66, "reason='lost' · book value 26,400 AFN → written off on post",
                 11.5, DANGER, width=LW - 220, g=G),
            text(cx + 18, ly + 88, "Stock cannot stay on hand for a dress that no longer exists.",
                 11, MUTED, width=LW - 220, g=G)]
    els += btn(cx + LW - 186, ly + 54, 168, 40, "Open disposal →", "secondary", G)

    rx = cx + LW + GAP
    ry = cy + 64
    els += _panel(rx, ry, RW, 236, None, HAIRLINE, BG, G)
    e, _ = money_row(rx + 18, ry + 20, RW - 36,
                     [("Assessed charge", "32,000 AFN"),
                      ("Outstanding rental balance", "0 AFN"),
                      ("Deposit held", "6,000 AFN"),
                      ("Deposit applied to claim", "− 6,000 AFN"),
                      ("Deposit refunded", "0 AFN"),
                      ("Already paid", "0 AFN")],
                     G, total=("Balance → A/R", "26,000 AFN"))
    els += e
    ry += 254

    els += _panel(rx, ry, RW, 132, "WHERE THE MONEY LANDS", HAIRLINE, SOFT2, G)
    els += _kv(rx + 18, ry + 42, RW - 36, "Income — claim charge", "32,000 AFN", G, OK)
    els += _kv(rx + 18, ry + 66, RW - 36, "Liability cleared — deposit", "6,000 AFN", G, VIOLET)
    els += _kv(rx + 18, ry + 90, RW - 36, "Loss on write-off", "26,400 AFN", G, DANGER)
    els += _kv(rx + 18, ry + 112, RW - 36, "Net effect", "+ 5,600 AFN", G, OK, 12)
    ry += 148

    e, ry = select(rx, ry, RW, "Collect now?", "No — invoice to A/R, due 30 Sep", G)
    els += e
    els += btn(rx, ry, RW, 48, "Post claim & write off stock", "danger", G)

    els += _dnote(ox, oy,
                  "WRITES sales_rental_claims (claim_type ∈ damage | loss | late, charge_amount, deposit_applied,\n"
                  "balance_to_ar, sales_order_id, sales_order_item_id) — a document in its own right, NOT sales_sale_returns.\n"
                  "finance_customer_deposits 6,000 → status='applied' (liability cleared, not income).\n"
                  "Remaining 26,000 → finance_receivables (open). Charge → finance_transactions Income.\n"
                  "For claim_type='loss': linked inventory_disposals row + inventory_stock_transactions type='disposal'.",
                  DANGER)
    return els


# ── 12. Sale return ───────────────────────────────────────────────
def _d12(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "12. Sale return (sold goods)", "Sales", g,
                                     sub_active="Returns")
    G = [g]

    e, y = page_header(cx, cy, cw, "Sale return · RET26-0006",
                       [("Cancel", "ghost"), ("Post return", "primary")],
                       "Against SO26-000018 · Walk-in customer · sold 12 Sep 2026", G)
    els += e
    e, _ = _chiprow(cx, y - 4, [("Sale return", INFO), ("Sold goods only", MUTED),
                                ("Not a rental return", DANGER)], G)
    els += e
    y += 42

    els += note(cx, y, cw,
                "This document refunds and (optionally) restocks goods that were SOLD. Rental returns are an order "
                "lifecycle transition (screen 10) and lost/damaged rentals are claims (screen 11). Three different things.",
                INFO, G)
    y += 62

    els += _h(cx, y, "Select lines to return", G)
    e, ly = table(cx, y + 26, LW,
                  ["", "Item", "SKU", "Sold qty", "Return qty", "Unit price", "Refund"],
                  [[("☑", ACCENT), "Chantilly Veil", "ADF26-0042", "1", "1", "3,500", "3,500"],
                   [("☑", ACCENT), "Pearl Hair Comb", "ADF26-0118", "2", "1", "1,200", "1,200"],
                   [("☐", FAINT), ("Satin Bridal Gloves", MUTED), ("ADF26-0206", MUTED),
                    ("1", MUTED), ("0", MUTED), ("900", MUTED), ("—", MUTED)],
                   [("☐", FAINT), ("Ivory Clutch Bag", MUTED), ("ADF26-0311", MUTED),
                    ("1", MUTED), ("0", MUTED), ("6,000", MUTED), ("—", MUTED)]],
                  G, widths=[0.32, 1.8, 1.15, 0.7, 0.8, 0.85, 0.85])
    els += e

    e, ly2 = select(cx, ly, (LW - 16) / 2, "Reason", "Customer change of mind", G, required=True)
    els += e
    e2, _ = select(cx + (LW - 16) / 2 + 16, ly, (LW - 16) / 2, "Condition received", "Good — resaleable", G)
    els += e2
    ly = ly2
    e, ly = textarea(cx, ly, LW, "Note", "Veil unworn, tags attached. Comb opened but undamaged.", G, rows=2)
    els += e

    rx = cx + LW + GAP
    ry = cy + 64
    els += _panel(rx, ry, RW, 124, "RESTOCK", HAIRLINE, BG, G)
    e, _ = _toggle(rx + 18, ry + 44, RW - 36, "Restock returned goods",
                   "Good condition → back to sellable stock", True, G)
    els += e
    els.append(text(rx + 18, ry + 96, "Unusable condition → disposal instead of restock",
                    11, MUTED, width=RW - 36, g=G))
    ry += 140

    els += _panel(rx, ry, RW, 200, None, HAIRLINE, BG, G)
    e, _ = money_row(rx + 18, ry + 20, RW - 36,
                     [("Lines returned (2)", "4,700 AFN"),
                      ("Original discount share", "− 100 AFN"),
                      ("Restocking fee", "0 AFN"),
                      ("COGS reversed", "2,450 AFN")],
                     G, total=("Refund due", "4,600 AFN"))
    els += e
    ry += 218
    e, ry = select(rx, ry, RW, "Refund method", "Cash — Main cash drawer (CASH-01)", G, required=True)
    els += e
    els += note(rx, ry, RW,
                "Order becomes 'partially_refunded' —\nnot 'paid', not 'refunded'.", INFO, G)
    ry += 62
    els += btn(rx, ry, RW, 48, "Post return & refund 4,600 AFN", "primary", G)

    els += _dnote(ox, oy,
                  "WRITES sales_sale_returns (return_number RET26-####, reason, restock, refund_amount, status='posted')\n"
                  "+ sales_sale_return_items (sales_order_item_id, quantity, condition).\n"
                  "restock=true → inventory_stock_transactions type='sale_return_in'; condition='unusable' → disposal instead.\n"
                  "Refund → finance_transactions OUT (contra-revenue, NOT an expense) + COGS reversal for the returned qty.\n"
                  "Order payment_status → 'partially_refunded'. NOTHING here touches deposits or inventory_reservations.",
                  INFO)
    return els


# ── 13. Customers list ────────────────────────────────────────────
def _d13(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "13. Customers list", "Sales", g,
                                     sub_active="Customers")
    G = [g]

    e, y = page_header(cx, cy, cw, "Customers",
                       [("⬇ Export", "secondary"), ("＋ New customer", "primary")], None, G)
    els += e

    els += search_bar(cx, y, 420, "Search by phone — 0700 12 34 56", G)
    els += filter_chips(cx + 440, y + 5, ["All", "Has open balance", "Deposit held",
                                          "Wedding this month", "Inactive"], 0, G)
    y += 56

    e, y = stat_row(cx, y, cw, [
        ("Customers", "412", INK, "+9 this month", ICON["customers"]),
        ("With open A/R", "23", WARN, "62,300 AFN", ICON["ledger"]),
        ("Deposits held", "18", VIOLET, "145,000 AFN", ICON["reserve"]),
        ("Weddings this month", "31", ROSE, "peak season", ICON["calendar"]),
    ], 88, 14, G)
    els += e

    e, y = table(cx, y, cw,
                 ["Code", "Name", "Phone", "Wedding date", "Orders", "Lifetime value",
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
                   "58,400", ("6,000", VIOLET), ("26,000", DANGER)],
                  ["CUS26-0043", "Laila Karimi", "0700 88 99 00", "22 Aug 2026", "7",
                   "92,600", "—", "0"]],
                 G, widths=[1.05, 1.3, 1.2, 1.1, 0.6, 1.05, 0.95, 0.85])
    els += e
    e, y = pagination(cx, y, cw - 80, "1–6 of 412 customers", G)
    els += e

    els += _dnote(ox, oy,
                  "READS sales_customers (indexed on tenant_id + phone — phone is how counter staff actually search).\n"
                  "Lifetime value = Σ sales_orders.total_amount for completed orders, EXCLUDING deposits.\n"
                  "Deposit held = Σ finance_customer_deposits status='held' · Balance = Σ finance_receivables.balance_amount.\n"
                  "Walk-in sale orders have customer_id NULL and appear in no customer row — that is correct, not a bug.")
    return els


# ── 14. Customer detail ───────────────────────────────────────────
def _d14(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "14. Customer detail", "Sales", g,
                                     sub_active="Customers")
    G = [g]

    e, y = page_header(cx, cy, cw, "Sara Ahmadi",
                       [("🖨 Statement", "secondary"), ("＋ New rental", "accent"),
                        ("＋ New sale", "primary")],
                       "CUS26-0117 · 0700 12 34 56 · customer since Mar 2026", G)
    els += e

    # left profile
    els += _panel(cx, y, RW, 268, f"{ICON['user']}  PROFILE", HAIRLINE, BG, G)
    py = y + 42
    for lab, val, col in [("Phone", "0700 12 34 56", INK),
                          ("Alt phone", "0700 12 34 59", MUTED),
                          ("Wedding date", "28 Sep 2026  (16 days)", ROSE),
                          ("Gender", "Female", MUTED),
                          ("Branch", "Main branch", MUTED),
                          ("Payment term", "Net 15", MUTED),
                          ("Address", "Shahr-e Naw, Kabul", MUTED),
                          ("Status", "Active", OK)]:
        els += _kv(cx + 18, py, RW - 36, lab, val, G, col, 12.5)
        py += 26
    y2 = y + 284

    els += _panel(cx, y2, RW, 162, f"{ICON['reserve']}  DEPOSIT & A/R LEDGER", VIOLET, VIOLET_BG, G)
    els += _kv(cx + 18, y2 + 44, RW - 36, "Deposits held (liability)", "8,000 AFN", G, VIOLET, 15)
    els += _kv(cx + 18, y2 + 72, RW - 36, "Deposits applied lifetime", "12,500 AFN", G, INK, 12.5)
    els += _kv(cx + 18, y2 + 96, RW - 36, "Deposits forfeited → income", "1,500 AFN", G, WARN, 12.5)
    els += _kv(cx + 18, y2 + 120, RW - 36, "Deposits refunded", "22,000 AFN", G, MUTED, 12.5)
    els += _kv(cx + 18, y2 + 144, RW - 36, "Open A/R (finance_receivables)", "9,200 AFN", G, DANGER, 13)
    y2 += 178

    els += _panel(cx, y2, RW, 118, "LIFETIME", HAIRLINE, SOFT2, G)
    els += _kv(cx + 18, y2 + 42, RW - 36, "Orders", "4  (2 rental · 1 sale · 1 mixed)", G, INK, 12.5)
    els += _kv(cx + 18, y2 + 66, RW - 36, "Revenue", "48,900 AFN", G, INK, 12.5)
    els += _kv(cx + 18, y2 + 90, RW - 36, "Late returns / claims", "1 late · 0 claims", G, WARN, 12.5)

    # right — history
    rx = cx + RW + GAP
    e, ry = tabs(rx, y - 10, LW, ["Order history", "Deposits", "Payments", "Notes"], 0, G)
    els += e
    e, ry = table(rx, ry, LW,
                  ["Order #", "Date", "Type", "Window", "Total", "Deposit", "Balance", "Status"],
                  [["SO26-000019", "12 Sep", ("Mixed", VIOLET), "24–28 Sep", "16,000",
                    ("14,000 held", VIOLET), ("9,200", WARN), ("Confirmed", INFO)],
                   ["SO26-000010", "02 Aug", ("Rental", ACCENT), "08–12 Aug", "9,400",
                    ("8,000 refunded", MUTED), "0", ("Completed", OK)],
                   ["SO26-000006", "19 Jun", ("Sale", INFO), "19 Jun", "12,700",
                    "—", "0", ("Completed", OK)],
                   ["SO26-000002", "04 May", ("Rental", ACCENT), "06–09 May", "10,800",
                    ("6,000 · 1,500 forfeit", WARN), "0", ("Completed", OK)]],
                  G, widths=[1.15, 0.75, 0.85, 1.0, 0.85, 1.45, 0.85, 1.0])
    els += e

    els += _h(rx, ry + 6, f"{ICON['ledger']}  Deposit movements", G)
    e, ry = table(rx, ry + 32, LW,
                  ["Date", "Order", "Event", "Amount", "Status", "Finance effect"],
                  [["12 Sep", "SO26-000019", "Deposit taken", ("+ 14,000", VIOLET), ("held", VIOLET),
                    "Cash IN · liability ↑"],
                   ["12 Aug", "SO26-000010", "Clean return", ("− 8,000", MUTED), ("refunded", MUTED),
                    "Cash OUT · liability ↓"],
                   ["09 May", "SO26-000002", "Late 2 days", ("− 1,500", WARN), ("forfeited", WARN),
                    "Income ↑ (only here)"],
                   ["09 May", "SO26-000002", "Remainder back", ("− 4,500", MUTED), ("refunded", MUTED),
                    "Cash OUT · liability ↓"]],
                  G, widths=[0.7, 1.2, 1.25, 0.9, 0.9, 1.6], row_h=40)
    els += e

    els += _dnote(ox, oy,
                  "READS sales_customers + sales_orders + sales_order_payments + finance_customer_deposits + finance_receivables.\n"
                  "The deposit ledger is the audit trail for the liability: held → applied | forfeited | refunded.\n"
                  "ONLY the 'forfeited' rows ever appear in Income. 'held' is money the shop is holding, not money it earned.\n"
                  "Balance column is display-only; the authoritative open amount is the finance_receivables row per order.",
                  VIOLET)
    return els


# ── 15. Sales reports hub + Sales Summary ─────────────────────────
def _d15(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "15. Sales reports · Sales Summary", "Sales", g,
                                     sub_active="Reports")
    G = [g]

    e, y = page_header(cx, cy, cw, "Sales reports",
                       [("⬇ Export CSV", "secondary"), ("🖨 Print", "secondary")],
                       "Six reports · period 01–12 Sept 2026 · Main branch · AFN", G)
    els += e

    cards = [(ICON["chart"], "Sales Summary", "Revenue, margin, by day"),
             (ICON["tag"], "Sales by Item", "Item / category mix"),
             (ICON["rental"], "Rental Performance", "Utilisation & damage"),
             (ICON["ledger"], "Customer Ledger", "Balances per customer"),
             (ICON["user"], "Staff Sales", "Cashier performance"),
             (ICON["reserve"], "Deposits & Refunds", "Liability movement")]
    ccw = (cw - 14 * 5) / 6
    for i, (ic, t, d) in enumerate(cards):
        els += _report_card(cx + i * (ccw + 14), y, ccw, 92, ic, t, d, G)
    y += 112

    e, y2 = field(cx, y, 180, "From", "01 Sep 2026", G)
    els += e
    e2, _ = field(cx + 196, y, 180, "To", "12 Sep 2026", G)
    els += e2
    e2, _ = select(cx + 392, y, 200, "Group by", "Day", G)
    els += e2
    e2, _ = select(cx + 608, y, 200, "Branch", "Main branch", G)
    els += e2
    els += btn(cx + 824, y + 18, 120, 40, "Run report", "primary", G)
    y = y2

    e, y = stat_row(cx, y, cw, [
        ("Revenue — total", "612,400", INK, "12 days", ICON["cash"]),
        ("Revenue — sale lines", "268,900", INFO, "44% of revenue", ICON["tag"]),
        ("Revenue — rental lines", "343,500", ACCENT, "56% of revenue", ICON["rental"]),
        ("COGS + rental amortisation", "247,100", WARN, "sale COGS + per-use", ICON["ledger"]),
        ("Gross margin", "365,300", OK, "59.6%", ICON["chart"]),
        ("Deposits held (NOT revenue)", "145,000", VIOLET, "liability, excluded", ICON["reserve"]),
    ], 88, 14, G)
    els += e

    BW = 668
    e, _ = bar_chart(cx, y, BW, 248, "Revenue by day — sale vs rental (AFN, thousands)",
                     [("01", 0.42, "38"), ("02", 0.55, "49"), ("03", 0.38, "34"),
                      ("04", 0.71, "64"), ("05", 0.86, "77"), ("06", 0.94, "85"),
                      ("07", 0.30, "27"), ("08", 0.58, "52"), ("09", 0.66, "59"),
                      ("10", 0.78, "70"), ("11", 0.62, "56"), ("12", 0.94, "85")], G)
    els += e

    rx = cx + BW + GAP
    RWW = cw - BW - GAP
    e, ry = table(rx, y, RWW,
                  ["Category", "Qty", "Revenue", "Margin %"],
                  [["Bridal gowns — rental", "48", "286,400", ("62%", OK)],
                   ["Bridal gowns — sale", "9", "184,200", ("41%", OK)],
                   ["Veils & headpieces", "37", "63,900", ("55%", OK)],
                   ["Evening gowns — rental", "14", "57,100", ("58%", OK)],
                   ["Accessories", "62", "20,800", ("49%", WARN)]],
                  G, widths=[1.8, 0.55, 1.0, 0.85], row_h=40)
    els += e

    els += _panel(rx, ry + 4, RWW, 118, "PERIOD MARGIN", HAIRLINE, SOFT2, G)
    els += _kv(rx + 18, ry + 46, RWW - 36, "Revenue", "612,400 AFN", G)
    els += _kv(rx + 18, ry + 70, RWW - 36, "− COGS & rental amortisation", "247,100 AFN", G, WARN)
    els += _kv(rx + 18, ry + 94, RWW - 36, "Gross margin", "365,300 AFN  ·  59.6%", G, OK, 14)

    els += _dnote(ox, oy,
                  "READS sales_order_items JOIN sales_orders over the period, split by line_type — this is why line_type\n"
                  "must be authoritative: a mixed order contributes to BOTH the sale and the rental column.\n"
                  "Revenue EXCLUDES deposits entirely (finance_customer_deposits is a liability) and excludes refunds.\n"
                  "Sale COGS = Σ qty × unit_cost_snapshot. Rental cost = per-use amortisation (purchase_cost ÷ expected_uses),\n"
                  "so a 40,000 AFN gown is expensed gradually instead of on its first rental or never.")
    return els


# ── 16. Rental performance report ─────────────────────────────────
def _d16(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = desk_shell(ox, oy, "16. Rental performance report", "Sales", g,
                                     sub_active="Reports")
    G = [g]

    e, y = page_header(cx, cy, cw, "Rental performance",
                       [("⬇ Export CSV", "secondary"), ("🖨 Print", "secondary")],
                       "Per dress · 01 Jan – 12 Sept 2026 · Main branch · AFN", G)
    els += e

    e, y2 = field(cx, y, 180, "From", "01 Jan 2026", G)
    els += e
    e2, _ = field(cx + 196, y, 180, "To", "12 Sep 2026", G)
    els += e2
    e2, _ = select(cx + 392, y, 220, "Category", "All rentable items", G)
    els += e2
    e2, _ = select(cx + 628, y, 200, "Sort by", "Utilisation %", G)
    els += e2
    els += btn(cx + 844, y + 18, 120, 40, "Run report", "primary", G)
    y = y2
    els += filter_chips(cx, y - 6, ["All", "Top performers", "Idle > 60 days",
                                    "Damage incidents", "Fully amortised"], 0, G)
    y += 40

    e, y = stat_row(cx, y, cw, [
        ("Rentable dresses", "186", INK, "142 rented ≥1×", ICON["dress"]),
        ("Rentals completed", "428", INK, "avg 4.2 days", ICON["rental"]),
        ("Rental revenue", "1,284,600", ACCENT, "YTD", ICON["cash"]),
        ("Fleet utilisation", "38%", WARN, "target 50%", ICON["chart"]),
        ("Late returns", "31", WARN, "7.2% of rentals", ICON["clock"]),
        ("Damage / loss claims", "6", DANGER, "4 damage · 2 loss", ICON["alert"]),
    ], 88, 14, G)
    els += e

    e, y = table(cx, y, cw,
                 ["Dress", "SKU", "Times rented", "Revenue", "Utilisation", "Avg days",
                  "Late returns", "Claims", "Amortised"],
                 [["White A-Line Gown", "ADF26-0042", "27", "189,000", ("71%", OK), "4.6",
                   "3", ("0", OK), ("84%", OK)],
                  ["Gold Ball Gown", "ADF26-0077", "22", "121,000", ("58%", OK), "4.1",
                   "2", ("1 damage", WARN), ("66%", OK)],
                  ["Ivory Mermaid Gown", "ADF26-0091", "19", "102,600", ("49%", WARN), "4.0",
                   "4", ("0", OK), ("51%", WARN)],
                  ["Pearl Empire Gown", "ADF26-0104", "14", "70,000", ("36%", WARN), "3.8",
                   "1", ("0", OK), ("38%", WARN)],
                  ["Rose Evening Gown", "ADF26-0176", "9", "43,200", ("24%", DANGER), "3.4",
                   "2", ("1 loss", DANGER), ("— written off", DANGER)],
                  ["Blush Tulle Gown", "ADF26-0198", "2", "8,800", ("5%", DANGER), "3.0",
                   "0", ("0", OK), ("6%", DANGER)]],
                 G, widths=[1.85, 1.1, 0.9, 0.95, 0.9, 0.72, 0.9, 0.95, 1.0], row_h=38)
    els += e

    BW = 668
    e, _ = bar_chart(cx, y, BW, 196, "Utilisation % — top dresses (days out ÷ days available)",
                     [("0042", 0.71, "71%"), ("0077", 0.58, "58%"), ("0091", 0.49, "49%"),
                      ("0104", 0.36, "36%"), ("0176", 0.24, "24%"), ("0198", 0.05, "5%")], G)
    els += e

    rx = cx + BW + GAP
    RWW = cw - BW - GAP
    els += _panel(rx, y, RWW, 196, "WHAT THIS REPORT ANSWERS", HAIRLINE, SOFT2, G)
    for i, t in enumerate([
            "Which gowns earn their purchase cost back?",
            "Which sit idle and should be sold off?",
            "Utilisation % = days out ÷ days available,",
            "   where days available excludes the",
            "   cleaning buffer after each return.",
            "Late returns and claims flag dresses that",
            "   cost more than they earn."]):
        els.append(text(rx + 18, y + 44 + i * 22, t, 12,
                        MUTED if i > 1 else INK, width=RWW - 36, g=G))

    els += _dnote(ox, oy,
                  "READS sales_order_items WHERE line_type='rental' JOIN sales_orders (status IN 'returned','completed')\n"
                  "GROUP BY inventory_item_id. Times rented = COUNT(lines). Avg days = AVG(rental_end − rental_start).\n"
                  "Utilisation % = Σ rental days ÷ (days in period − days blocked by cleaning buffer − days disposed).\n"
                  "Late returns = COUNT(actual_return_date > rental_end_date). Claims = sales_rental_claims by item.\n"
                  "Amortised % = accumulated per-use rental COGS ÷ purchase_cost — shows the asset being consumed.",
                  ACCENT)
    return els


# ══════════════════════════════════════════════════════════════════
#  MOBILE — 10 screens × 6 columns
# ══════════════════════════════════════════════════════════════════

def mobile():
    els = board_title(
        0, -150, "BOMS Mobile — Sales",
        "Counter-first: phone search, two-tap checkout, rental return with deposit settlement · "
        "deposits shown as liability everywhere · AFN · Sept 2026")

    for r, label in [(0, "SELL & RENT AT THE COUNTER"), (1, "LIFECYCLE, RETURNS & REPORTING")]:
        _, ry = grid_pos(r * PHONE_COLS, PHONE_COLS, PHONE_W, PHONE_H)
        els += section_label(0, ry - 62, label)

    for i, fn in enumerate([_m01, _m02, _m03, _m04, _m05,
                            _m06, _m07, _m08, _m09, _m10]):
        ox, oy = grid_pos(i, PHONE_COLS, PHONE_W, PHONE_H)
        els += fn(ox, oy)

    els += flow_arrows(10, PHONE_COLS, PHONE_W, PHONE_H)
    return els


def _mnote(ox, oy, content, color=ACCENT):
    return note(ox, oy + PHONE_NOTE_Y, PHONE_W, content, color)


# ── M1. Sales hub ─────────────────────────────────────────────────
def _m01(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M1. Sales hub", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "Sales", right=ICON["search"], g=G)
    els += e
    els.append(text(cx, y - 8, "Sat 12 Sept · Main branch", 11, MUTED, width=cw, g=G))
    y += 12

    bw = (cw - 12) / 2
    els += btn(cx, y, bw, 64, "🛒  New Sale", "primary", G)
    els += btn(cx + bw + 12, y, bw, 64, "⏱️  New Rental", "accent", G)
    y += 78

    kw = (cw - 10) / 2
    els += kpi_card(cx, y, kw, 78, "Today revenue", "84,500", INK, None, ICON["cash"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Open orders", "12", INK, None, ICON["receipt"], G)
    y += 88
    els += kpi_card(cx, y, kw, 78, "Deposits held", "145,000", VIOLET, None, ICON["reserve"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Overdue returns", "2", DANGER, None, ICON["alert"], G)
    y += 88

    els += note(cx, y, cw, "Deposits held is a liability —\nnot part of today revenue.", VIOLET, G)
    y += 66

    els += _h(cx, y, f"{ICON['clock']}  Due back today", G, 13)
    y += 24
    e, y = list_card(cx, y, cw,
                     [("Ivory Mermaid Gown", INK, 13.5),
                      ("SO26-000011 · Fatima Rahimi", MUTED, 11),
                      ("Due 14:00 · deposit 6,000 held", VIOLET, 11)],
                     G, badge=("Out", ACCENT))
    els += e
    e, y = list_card(cx, y, cw,
                     [("Rose Evening Gown", INK, 13.5),
                      ("SO26-000009 · Nasrin Amiri", MUTED, 11),
                      ("Due 10 Sep · late fee accruing", DANGER, 11)],
                     G, badge=("2 d late", DANGER))
    els += e

    els += _mnote(ox, oy,
                  "Revenue = Σ sales_order_items.line_total (sale + rental).\n"
                  "Deposits held = Σ finance_customer_deposits status='held'.\n"
                  "Due back = sales_orders status='out' AND rental_end_date ≤ today.")
    return els


# ── M2. Orders list ───────────────────────────────────────────────
def _m02(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M2. Orders list", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "Orders", left=ICON["back"], right=ICON["filter"], g=G)
    els += e
    els += search_bar(cx, y, cw, "Order # · name · phone…", G)
    y += 50
    els += filter_chips(cx, y, ["All", "Sale", "Rental", "Mixed"], 0, G)
    y += 42

    for lines, badge in [
        ([("SO26-000019 · Sara Ahmadi", INK, 13.5),
          ("Mixed · 24–28 Sep · 16,000 AFN", MUTED, 11),
          ("Deposit 14,000 held · bal 9,200", VIOLET, 11)], ("Confirmed", INFO)),
        ([("SO26-000018 · Walk-in", INK, 13.5),
          ("Sale · 12 Sep · 12,600 AFN", MUTED, 11),
          ("Paid in full · no deposit", OK, 11)], ("Completed", OK)),
        ([("SO26-000017 · Maryam Noori", INK, 13.5),
          ("Rental · 12–16 Sep · 9,000 AFN", MUTED, 11),
          ("Deposit 6,000 held · bal 4,500", VIOLET, 11)], ("Out", ACCENT)),
        ([("SO26-000014 · Nasrin Amiri", INK, 13.5),
          ("Rental · 09–12 Sep · 8,500 AFN", MUTED, 11),
          ("Overdue 2 days · fee 2,000", DANGER, 11)], ("Late", DANGER)),
        ([("SO26-000013 · Walk-in", INK, 13.5),
          ("Sale · 09 Sep · 3,400 AFN", MUTED, 11),
          ("Balance 2,000 → A/R", WARN, 11)], ("Partial", WARN)),
    ]:
        e, y = list_card(cx, y, cw, lines, G, badge=badge)
        els += e

    els += fab(cx + cw, oy + TITLE_H + PHONE_H - 140, "＋  New order", G)

    els += _mnote(ox, oy,
                  "READS sales_orders. Type badge DERIVED from line_type mix.\n"
                  "Deposit line is the liability, shown apart from the balance.\n"
                  "Balance display only — real A/R is finance_receivables.")
    return els


# ── M3. Customer pick ─────────────────────────────────────────────
def _m03(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M3. Customer pick", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "Who is it for?", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y - 8, "Step 1 of 3 · search by phone", 11, MUTED, width=cw, g=G))
    y += 14

    els += search_bar(cx, y, cw, "0700 12 34", G)
    y += 50

    els += _h(cx, y, "2 matches", G, 12, MUTED)
    y += 22
    e, y = list_card(cx, y, cw,
                     [("Sara Ahmadi", INK, 14),
                      ("0700 12 34 56 · CUS26-0117", MUTED, 11),
                      ("Wedding 28 Sep · 4 orders", ROSE, 11)],
                     G, badge=("Bal 9,200", WARN))
    els += e
    e, y = list_card(cx, y, cw,
                     [("Maryam Noori", INK, 14),
                      ("0700 12 34 57 · CUS26-0094", MUTED, 11),
                      ("Wedding 16 Sep · 3 orders", ROSE, 11)],
                     G, badge=("Dep 6,000", VIOLET))
    els += e
    y += 8

    els += btn(cx, y, cw, 50, "＋  Create new customer", "secondary", G)
    y += 60
    els += btn(cx, y, cw, 50, "🛒  Continue as Walk-in", "secondary", G)
    y += 62

    els += note(cx, y, cw,
                "Walk-in is for SALE lines only.\nAdd a rental line and a named\ncustomer becomes required.",
                WARN, G)

    els += _mnote(ox, oy,
                  "READS sales_customers by (tenant_id, phone) index.\n"
                  "Walk-in → sales_orders.customer_id stays NULL (nullable).\n"
                  "Any line_type='rental' blocks save while customer_id IS NULL.", WARN)
    return els


# ── M4. New sale checkout ─────────────────────────────────────────
def _m04(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M4. New sale checkout", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "New sale", left=ICON["back"], right=ICON["add"], g=G)
    els += e
    els.append(text(cx, y - 8, "SO26-000019 · Walk-in customer", 11, MUTED, width=cw, g=G))
    y += 14

    els += search_bar(cx, y, cw, f"{ICON['tag']}  Scan barcode or search SKU…", G)
    y += 52

    for name, meta, total in [
        ("Chantilly Veil", "ADF26-0042 · Sale · 1 × 3,500", "3,500"),
        ("Pearl Hair Comb", "ADF26-0118 · Sale · 2 × 1,200", "2,400"),
        ("Satin Bridal Gloves", "ADF26-0206 · Sale · 1 × 900 − 100", "800"),
        ("Ivory Clutch Bag", "ADF26-0311 · Sale · 1 × 6,000", "6,000"),
    ]:
        els.append(rect(cx, y, cw, 58, strokeColor=HAIRLINE, backgroundColor=BG,
                        strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 12, name, 13.5, INK, width=cw - 110, g=G))
        els.append(text(cx + 14, y + 32, meta, 11, MUTED, width=cw - 110, g=G))
        els.append(text(cx + cw - 104, y + 20, total + " AFN", 13, INK, "right", 90, G))
        y += 66

    e, _ = _chiprow(cx, y, [("4 sale lines", INFO), ("No deposit", MUTED)], G)
    els += e
    y += 34
    els += note(cx, y, cw, "Add a rental line here and this\norder becomes Mixed.", INFO, G)

    sy = oy + TITLE_H + PHONE_H - 72 - 82
    els += _sticky(cx, sy, cw, "Total due (4 lines)", "12,600 AFN", "Collect", G)

    els += _mnote(ox, oy,
                  "WRITES sales_orders (order_kind derived 'sale') + sales_order_items\n"
                  "line_type='sale' with unit_cost_snapshot for COGS.\n"
                  "Confirm → inventory_stock_transactions type='sale_out'.", INFO)
    return els


# ── M5. New rental checkout ───────────────────────────────────────
def _m05(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M5. New rental checkout", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "New rental", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y - 8, "SO26-000020 · Sara Ahmadi · 0700 12 34 56", 11, MUTED,
                    width=cw, g=G))
    y += 16

    e, y2 = field(cx, y, cw, "Event date", "26 Sep 2026", G, required=True)
    els += e
    hw = (cw - 12) / 2
    e, y3 = field(cx, y2, hw, "Rental start", "24 Sep 2026", G, required=True)
    els += e
    e2, _ = field(cx + hw + 12, y2, hw, "Rental end", "28 Sep 2026", G, required=True)
    els += e2
    y = y3

    e, _ = _chiprow(cx, y, [("✓ Available", OK), ("5 days", INFO), ("+2 d cleaning", VIOLET)], G)
    els += e
    y += 36

    for name, meta, total, dep in [
        ("White A-Line Gown", "ADF26-0042 · 5 d × 1,400", "7,000", "8,000"),
        ("Gold Ball Gown", "ADF26-0077 · 5 d × 1,100", "5,500", "6,000"),
        ("Chantilly Veil", "ADF26-0118 · Sale · 1 × 3,500", "3,500", "—"),
    ]:
        els.append(rect(cx, y, cw, 64, strokeColor=HAIRLINE, backgroundColor=BG,
                        strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, name, 13.5, INK, width=cw - 110, g=G))
        els.append(text(cx + 14, y + 29, meta, 11, MUTED, width=cw - 110, g=G))
        els.append(text(cx + 14, y + 46, f"deposit {dep}", 11, VIOLET, width=cw - 110, g=G))
        els.append(text(cx + cw - 104, y + 22, total + " AFN", 13, INK, "right", 90, G))
        y += 72

    els += _panel(cx, y, cw, 84, None, VIOLET, VIOLET_BG, G)
    els += _kv(cx + 14, y + 14, cw - 28, "Revenue total", "16,000 AFN", G, INK, 13)
    els += _kv(cx + 14, y + 40, cw - 28, "Deposit (liability)", "14,000 AFN", G, VIOLET, 14)
    els.append(text(cx + 14, y + 62, "Refundable — never income", 10.5, VIOLET, width=cw - 28, g=G))

    sy = oy + TITLE_H + PHONE_H - 72 - 82
    els += _sticky(cx, sy, cw, "Collect now (revenue + deposit)", "30,000 AFN", "Reserve", G,
                   "of which 14,000 is deposit")

    els += _mnote(ox, oy,
                  "WRITES sales_orders rental window + items with per-line deposit_amount.\n"
                  "Reserve → inventory_reservations per sales_order_item_id.\n"
                  "Deposit → finance_customer_deposits status='held' (never Income).", VIOLET)
    return els


# ── M6. Collect payment sheet ─────────────────────────────────────
def _m06(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M6. Collect payment sheet", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "SO26-000019", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y - 8, "Sara Ahmadi · Mixed · 24–28 Sep", 11, MUTED, width=cw, g=G))
    e, _ = list_card(cx, y + 16, cw,
                     [("Order total", INK, 13.5), ("16,000 AFN · paid 6,000", MUTED, 11)],
                     G, badge=("Confirmed", INFO))
    els += e

    # scrim + bottom sheet
    els.append(rect(ox + 2, oy + TITLE_H + 2, PHONE_W - 4, PHONE_H - 4,
                    strokeColor="transparent", backgroundColor="#0f172a",
                    strokeWidth=0, opacity=35, groupIds=G))
    sh = 566
    sy = oy + TITLE_H + PHONE_H - sh - 2
    els.append(rect(ox + 2, sy, PHONE_W - 4, sh, strokeColor=LINE, backgroundColor=BG,
                    strokeWidth=2, groupIds=G))
    els.append(rect(ox + PHONE_W / 2 - 22, sy + 10, 44, 5, strokeColor=LINE,
                    backgroundColor=LINE, strokeWidth=1, groupIds=G))
    sx, sw = ox + 20, PHONE_W - 40
    els.append(text(sx, sy + 26, "Collect payment", 17, INK, width=sw, g=G))
    els.append(text(sx + sw - 20, sy + 26, ICON["cross"], 14, MUTED, g=G))
    fy = sy + 62

    e, fy = select(sx, fy, sw, "Payment type", "Deposit (refundable)", G, required=True)
    els += e
    els += note(sx, fy - 4, sw,
                "Liability — does not reduce the\norder balance, never Income.", VIOLET, G)
    fy += 58
    e, fy = field(sx, fy, sw, "Amount", "14,000", G, required=True)
    els += e
    hw = (sw - 12) / 2
    e, fy2 = select(sx, fy, hw, "Method", "Cash", G, required=True)
    els += e
    e2, _ = select(sx + hw + 12, fy, hw, "Account", "CASH-01", G, required=True)
    els += e2
    fy = fy2

    els += _panel(sx, fy, sw, 104, None, HAIRLINE, SOFT2, G)
    e, _ = money_row(sx + 14, fy + 14, sw - 28,
                     [("Paid toward total", "6,000 AFN"),
                      ("Deposit held after", "14,000 AFN"),
                      ("Balance → A/R", "10,000 AFN")], G)
    els += e
    fy += 118
    els += btn(sx, fy, sw, 50, "Record payment", "primary", G)

    els += _mnote(ox, oy,
                  "WRITES sales_order_payments + finance_transactions IN on finance_accounts.\n"
                  "payment_type='deposit' → finance_customer_deposits status='held'.\n"
                  "installment/full → reduces finance_receivables.balance_amount.", VIOLET)
    return els


# ── M7. Order detail · rental ─────────────────────────────────────
def _m07(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M7. Order detail · rental", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "SO26-000017", left=ICON["back"], right=ICON["print"], g=G)
    els += e
    els.append(text(cx, y - 8, "Maryam Noori · 0700 12 34 56", 11, MUTED, width=cw, g=G))
    y += 14

    e, _ = _chiprow(cx, y, [("Rental", ACCENT), ("Out", ACCENT), ("2 d late", DANGER)], G)
    els += e
    y += 34

    e, y = timeline(cx, y, cw, [("draft", "done"), ("confirmed", "done"), ("out", "current"),
                                ("returned", "todo"), ("done", "todo")], G)
    els += e
    y += 4

    els += _panel(cx, y, cw, 96, None, HAIRLINE, SOFT2, G)
    els += _kv(cx + 14, y + 14, cw - 28, "Out on", "12 Sep 2026", G, INK, 12.5)
    els += _kv(cx + 14, y + 38, cw - 28, "Due back", "16 Sep 2026", G, DANGER, 12.5)
    els += _kv(cx + 14, y + 62, cw - 28, "Free again", "20 Sep (after cleaning)", G, VIOLET, 12)
    y += 108

    e, y = list_card(cx, y, cw,
                     [("Ivory Mermaid Gown", INK, 13.5),
                      ("ADF26-0091 · 4 d × 1,350 = 5,400", MUTED, 11),
                      ("deposit 6,000 · late 800/day", VIOLET, 11)], G)
    els += e

    els += _panel(cx, y, cw, 106, None, VIOLET, VIOLET_BG, G)
    els += _kv(cx + 14, y + 14, cw - 28, "Rental revenue", "9,000 AFN", G, INK, 12.5)
    els += _kv(cx + 14, y + 38, cw - 28, "Paid toward total", "4,500 AFN", G, INK, 12.5)
    els += _kv(cx + 14, y + 62, cw - 28, "Deposit held (liability)", "6,000 AFN", G, VIOLET, 13)
    els += _kv(cx + 14, y + 86, cw - 28, "Balance → A/R", "4,500 AFN", G, WARN, 12.5)
    y += 118

    els += btn(cx, y, cw, 48, "✓  Mark returned", "primary", G)
    els += btn(cx, y + 56, (cw - 12) / 2, 44, "⚠ Claim", "danger", G)
    els += btn(cx + (cw - 12) / 2 + 12, y + 56, (cw - 12) / 2, 44, "💵 Collect", "secondary", G)

    els += _mnote(ox, oy,
                  "READS sales_orders + items + finance_customer_deposits + finance_receivables.\n"
                  "Mark out → stock txn 'rent_out' · Mark returned → 'rent_return' + release.\n"
                  "Deposit held is displayed apart from Paid — different money.")
    return els


# ── M8. Mark returned ─────────────────────────────────────────────
def _m08(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M8. Mark returned", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "Mark returned", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y - 8, "SO26-000017 · Ivory Mermaid Gown", 11, MUTED, width=cw, g=G))
    y += 14

    els += _h(cx, y, "Condition", G, 12, MUTED)
    y += 20
    els += filter_chips(cx, y, ["Good", "Needs cleaning"], 1, G)
    y += 38
    els += filter_chips(cx, y, ["Damaged → claim", "Lost → claim"], -1, G)
    y += 44

    els += _panel(cx, y, cw, 124, None, WARN, WARN_BG, G)
    e, _ = money_row(cx + 14, y + 14, cw - 28,
                     [("Due back", "16 Sep 2026"),
                      ("Returned", "18 Sep 2026"),
                      ("late_days", "2"),
                      ("Late fee  2 × 1,000/day", "2,000 AFN")], G)
    els += e
    y += 136

    e, y = field(cx, y, cw, "Waive late fee (reason required)", "500 · loyal customer", G)
    els += e

    els += _panel(cx, y, cw, 132, None, VIOLET, VIOLET_BG, G)
    els.append(text(cx + 14, y + 12, "DEPOSIT SETTLEMENT · 6,000 held", 11, VIOLET,
                    width=cw - 28, g=G))
    els += _kv(cx + 14, y + 36, cw - 28, "Apply to balance", "1,500 AFN", G, ACCENT, 12.5)
    els += _kv(cx + 14, y + 60, cw - 28, "Forfeit → income", "0 AFN", G, WARN, 12.5)
    els += _kv(cx + 14, y + 84, cw - 28, "Refund to customer", "4,500 AFN", G, OK, 12.5)
    els += _kv(cx + 14, y + 108, cw - 28, "Remaining balance", "4,500 AFN", G, DANGER, 12.5)

    sy = oy + TITLE_H + PHONE_H - 72 - 82
    els += _sticky(cx, sy, cw, "Late fee charged (after waiver)", "1,500 AFN", "Confirm", G)

    els += _mnote(ox, oy,
                  "WRITES sales_orders status='returned', actual_return_date, late_days,\n"
                  "late_fee_amount + late_fee_waived_amount + reason · stock 'rent_return' ·\n"
                  "finance_customer_deposits applied / forfeited / refunded. Only forfeit = Income.",
                  VIOLET)
    return els


# ── M9. Sale return ───────────────────────────────────────────────
def _m09(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M9. Sale return", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "Sale return", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y - 8, "RET26-0006 against SO26-000018", 11, MUTED, width=cw, g=G))
    y += 14

    els += note(cx, y, cw, "Sold goods only. Rental returns\nand claims are other documents.", INFO, G)
    y += 62

    els += _h(cx, y, "Select lines & quantity", G, 12, MUTED)
    y += 20
    for mark, name, meta, qty, col in [
        ("☑", "Chantilly Veil", "ADF26-0042 · sold 1 · 3,500", "1", ACCENT),
        ("☑", "Pearl Hair Comb", "ADF26-0118 · sold 2 · 1,200", "1", ACCENT),
        ("☐", "Ivory Clutch Bag", "ADF26-0311 · sold 1 · 6,000", "0", FAINT),
    ]:
        els.append(rect(cx, y, cw, 58, strokeColor=HAIRLINE, backgroundColor=BG,
                        strokeWidth=1, groupIds=G))
        els.append(text(cx + 12, y + 20, mark, 15, col, g=G))
        els.append(text(cx + 36, y + 12, name, 13.5, INK if mark == "☑" else MUTED,
                        width=cw - 130, g=G))
        els.append(text(cx + 36, y + 32, meta, 11, MUTED, width=cw - 130, g=G))
        els.append(rect(cx + cw - 92, y + 14, 80, 30, strokeColor=LINE,
                        backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + cw - 92, y + 21, f"−   {qty}   ＋", 11, MUTED, "center", 80, G))
        y += 66

    e, y = select(cx, y, cw, "Reason", "Customer change of mind", G, required=True)
    els += e
    e, y = _toggle(cx, y, cw, "Restock to sellable stock",
                   "Good condition · else disposal", True, G)
    els += e

    els += _panel(cx, y, cw, 86, None, HAIRLINE, SOFT2, G)
    els += _kv(cx + 14, y + 14, cw - 28, "Lines returned (2)", "4,700 AFN", G, INK, 12.5)
    els += _kv(cx + 14, y + 38, cw - 28, "Discount share", "− 100 AFN", G, MUTED, 12.5)
    els += _kv(cx + 14, y + 62, cw - 28, "Refund due", "4,600 AFN", G, DANGER, 13)

    sy = oy + TITLE_H + PHONE_H - 72 - 82
    els += _sticky(cx, sy, cw, "Refund · Cash CASH-01", "4,600 AFN", "Post", G)

    els += _mnote(ox, oy,
                  "WRITES sales_sale_returns + sales_sale_return_items.\n"
                  "restock → inventory_stock_transactions 'sale_return_in' · else disposal.\n"
                  "Refund → finance_transactions OUT (contra-revenue) + COGS reversal.", INFO)
    return els


# ── M10. Sales summary report ─────────────────────────────────────
def _m10(ox, oy):
    g = nid()
    els, cx, cy, cw, ch = phone_shell(ox, oy, "M10. Sales summary report", g, "Sales")
    G = [g]

    e, y = phone_header(cx, cy, cw, "Sales summary", left=ICON["back"], right=ICON["export"], g=G)
    els += e
    e, y = _seg(cx, y, cw, ["Today", "Week", "Month", "Custom"], 2, G)
    els += e
    els.append(text(cx, y - 10, "01 – 12 Sept 2026 · Main branch · AFN", 11, MUTED, width=cw, g=G))
    y += 8

    kw = (cw - 10) / 2
    els += kpi_card(cx, y, kw, 78, "Revenue", "612,400", INK, None, ICON["cash"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Gross margin", "59.6%", OK, None, ICON["chart"], G)
    y += 88
    els += kpi_card(cx, y, kw, 78, "Sale lines", "268,900", INFO, None, ICON["tag"], G)
    els += kpi_card(cx + kw + 10, y, kw, 78, "Rental lines", "343,500", ACCENT, None, ICON["rental"], G)
    y += 88

    els += note(cx, y, cw, "Deposits held 145,000 AFN are a\nliability and excluded from revenue.", VIOLET, G)
    y += 66

    e, y = bar_chart(cx, y, cw, 168, "Revenue by day (AFN thousands)",
                     [("04", 0.64, "64"), ("05", 0.77, "77"), ("06", 0.85, "85"),
                      ("07", 0.27, "27"), ("08", 0.52, "52"), ("09", 0.59, "59"),
                      ("10", 0.70, "70"), ("11", 0.56, "56"), ("12", 0.85, "85")], G)
    els += e

    e, y = table(cx, y, cw, ["Category", "Revenue", "Margin"],
                 [["Gowns — rental", "286,400", ("62%", OK)],
                  ["Gowns — sale", "184,200", ("41%", OK)],
                  ["Veils & accessories", "84,700", ("54%", OK)]],
                 G, widths=[1.5, 1.0, 0.75], row_h=36)
    els += e

    els += _mnote(ox, oy,
                  "READS sales_order_items split by line_type — a mixed order feeds both.\n"
                  "Revenue excludes deposits and refunds. Sale COGS = unit_cost_snapshot;\n"
                  "rental cost = per-use amortisation (purchase_cost ÷ expected_uses).")
    return els
