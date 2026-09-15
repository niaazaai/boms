#!/usr/bin/env python3
"""BOMS — Finance module wireframes (desktop + mobile).

Draws the CORRECTED money model:
  • 5 pillars: Cash & banks · Income · Expenses · A/P · A/R
  • + a 6th tile: Customer deposits HELD — a liability sitting inside cash
  • Deposits are never income (ADR-003)
  • COGS has its own ledger with TWO kinds (ADR-002):
        sale_cogs           = WAC of a dress that was sold
        rental_amortisation = acquisition_cost / expected_rental_uses per rental
  • Account balances are DERIVED; the cached column is reconciled
  • Void = a reversing entry, never a delete
  • Every money movement has exactly one finance_transactions row
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


def _pillar(x, y, w, h, n, title, value, sub, color, icon, g):
    """A numbered pillar card."""
    els = [rect(x, y, w, h, strokeColor=color, backgroundColor=BG, strokeWidth=2, groupIds=g),
           rect(x, y, w, 4, strokeColor=color, backgroundColor=color, strokeWidth=1, groupIds=g),
           text(x + 16, y + 18, f"{icon}  PILLAR {n}", 10, color, width=w - 32, g=g),
           text(x + 16, y + 38, title, 12.5, MUTED, width=w - 32, g=g),
           text(x + 16, y + 60, value, 23, color, width=w - 32, g=g)]
    if sub:
        els.append(text(x + 16, y + h - 26, sub, 10.5, MUTED, width=w - 32, g=g))
    return els


def _stmt(x, y, w, rows, g):
    """Profit & loss statement block. rows = (indent, label, value, color, bold)"""
    els, yy = [], y
    for ind, lab, val, col, bold in rows:
        if lab == "---":
            els.append(line(x, yy + 6, w, LINE, g))
            yy += 16
            continue
        els.append(text(x + ind * 18, yy, lab, 14 if bold else 12.5,
                        INK if bold else MUTED, width=w * 0.62, g=g))
        els.append(text(x + w * 0.62, yy, val, 15 if bold else 12.5, col, "right", w * 0.38, g=g))
        yy += 26 if bold else 23
    return els, yy


# ══════════════════════════════════════════════════════════════════
#  DESKTOP
# ══════════════════════════════════════════════════════════════════

def _d1(ox, oy):
    """Finance dashboard — the 5 pillars."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "1. Finance dashboard — the five pillars",
                                     "Finance", g, sub_active="Dashboard")
    e, y = page_header(cx, cy, cw, "Finance",
                       actions=[("⬇ Export", "ghost"), ("＋ Add expense", "primary")],
                       subtitle="Am I making money? · 12 Sep 2026 · Main branch · AFN",
                       g=G)
    els += e
    els += filter_chips(cx, y - 6, ["Today", "This week", "This month", "Custom"], 0, G)
    e, _ = _sel(cx + 420, y - 24, 200, "Branch", "All branches", G)
    els += e
    y += 44

    pw = (cw - 5 * 14) / 6
    pillars = [
        (1, "Cash & banks", "412,000", "3 accounts", ACCENT, ICON["cash"]),
        (2, "Income", "118,500", "today, posted only", OK, ICON["money_in"]),
        (3, "Expenses", "34,200", "today, posted only", DANGER, ICON["money_out"]),
        (4, "Accounts payable", "252,388", "we owe 4 suppliers", WARN, ICON["suppliers"]),
        (5, "Accounts receivable", "86,400", "11 customers owe us", INFO, ICON["customers"]),
    ]
    for i, (n, t, v, s, c, ic) in enumerate(pillars):
        els += _pillar(cx + i * (pw + 14), y, pw, 128, n, t, v, s, c, ic, G)
    # 6th tile — the liability
    lx = cx + 5 * (pw + 14)
    els.append(rect(lx, y, pw, 128, strokeColor=VIOLET, backgroundColor=VIOLET_BG, strokeWidth=2, groupIds=G))
    els.append(rect(lx, y, pw, 4, strokeColor=VIOLET, backgroundColor=VIOLET, strokeWidth=1, groupIds=G))
    els.append(text(lx + 16, y + 18, f"{ICON['lock']}  LIABILITY", 10, VIOLET, width=pw - 32, g=G))
    els.append(text(lx + 16, y + 38, "Deposits held", 12.5, MUTED, width=pw - 32, g=G))
    els.append(text(lx + 16, y + 60, "68,000", 23, VIOLET, width=pw - 32, g=G))
    els.append(text(lx + 16, y + 102, "not your money", 10.5, VIOLET, width=pw - 32, g=G))
    y += 150

    # hero: net profit + cash split
    HW = cw * 0.46
    els.append(rect(cx, y, HW, 214, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=2, groupIds=G))
    els.append(text(cx + 24, y + 20, "NET PROFIT TODAY", 11, ACCENT, width=HW - 48, g=G))
    els.append(text(cx + 24, y + 42, "AFN 61,180", 40, ACCENT, width=HW - 48, g=G))
    e, _ = _stmt(cx + 24, y + 98, HW - 48, [
        (0, "Revenue", "118,500", INK, False),
        (0, "− COGS (sale)", "16,420", DANGER, False),
        (0, "− COGS (rental amortisation)", "6,700", DANGER, False),
        (0, "---", "", INK, False),
        (0, "Gross profit", "95,380", OK, True),
        (0, "− Operating expenses", "34,200", DANGER, False),
        (0, "---", "", INK, False),
        (0, "Net profit", "61,180", ACCENT, True),
    ], G)
    els += e

    # cash split panel
    rx = cx + HW + 20
    RW = cw * 0.28
    els.append(rect(rx, y, RW, 214, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
    els.append(text(rx + 20, y + 18, "HOW MUCH OF THE CASH IS YOURS?", 10.5, MUTED, width=RW - 40, g=G))
    e, _ = _stmt(rx + 20, y + 48, RW - 40, [
        (0, "Cash & banks", "412,000", INK, False),
        (0, "− Customer deposits held", "68,000", VIOLET, False),
        (0, "---", "", INK, False),
        (0, "Your cash", "344,000", ACCENT, True),
    ], G)
    els += e
    els += note(rx + 20, y + 152, RW - 40,
                "A rental deposit is the customer's money,\nheld as security. It sits in the drawer but\nit is a liability, never income.", VIOLET, G)

    # alerts
    ax = rx + RW + 20
    AW = cw - HW - RW - 40
    els += _lab(ax, y, "NEEDS ATTENTION", G, DANGER)
    e, _ = table(ax, y + 20, AW, ["", "Item", "Amount"],
                 [[("⚠", DANGER), "A/R overdue 30+ days", ("24,600", DANGER)],
                  [("⚠", WARN), "A/P due this week", ("88,000", WARN)],
                  [("⚠", WARN), "3 deposits unsettled 14+ d", ("18,000", WARN)],
                  [("⚠", INFO), "Cash Drawer not reconciled", ("—", MUTED)]],
                 G, row_h=44, widths=[0.25, 1.7, 0.8])
    els += e
    y += 234
    e, _ = bar_chart(cx, y, cw * 0.46, 190, "Income vs expenses — last 7 days (AFN '000)",
                     [("Sat", 0.55, "72"), ("Sun", 0.68, "88"), ("Mon", 0.42, "54"),
                      ("Tue", 0.80, "104"), ("Wed", 0.61, "79"), ("Thu", 0.91, "118"),
                      ("Fri", 0.34, "44")], G, OK)
    els += e
    els += note(cx + cw * 0.46 + 20, y, cw - cw * 0.46 - 20,
                "Read-only dashboard. Reads finance_accounts + finance_transactions (posted only) for cash, finance_categories for the income/expense split,\n"
                "finance_cogs_entries for BOTH cogs lines, finance_payables / finance_receivables for pillars 4 and 5, and finance_customer_deposits for the liability tile.\n"
                "Every figure filters on business_date (ADR-011), not created_at — a sale rung up after midnight belongs to the correct trading day.\n"
                "Deposits are excluded from Income by construction: their finance_transactions rows carry is_deposit_movement = true and no income category.",
                ACCENT, G)
    return els


def _d2(ox, oy):
    """Period comparison."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "2. Dashboard — period comparison",
                                     "Finance", g, sub_active="Dashboard")
    e, y = page_header(cx, cy, cw, "Performance",
                       actions=[("⬇ Export", "ghost")],
                       subtitle="September 2026 vs August 2026 · all branches",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Revenue", "AFN 2.41M", OK, "+18% vs Aug", ICON["money_in"]),
        ("COGS", "AFN 684k", DANGER, "+11% vs Aug", ICON["inventory"]),
        ("Gross profit", "AFN 1.73M", ACCENT, "+21% vs Aug", ICON["chart"]),
        ("Expenses", "AFN 612k", DANGER, "+4% vs Aug", ICON["money_out"]),
        ("Net profit", "AFN 1.11M", ACCENT, "+32% vs Aug", ICON["cash"]),
        ("Margin", "46.2%", OK, "+4.1 pts", ICON["star"]),
    ], h=92, gap=12, g=G)
    els += e
    e, _ = bar_chart(cx, y, cw * 0.48, 250, "Revenue by week (AFN '000)",
                     [("W1", 0.52, "480"), ("W2", 0.66, "610"), ("W3", 0.81, "748"),
                      ("W4", 0.62, "572")], G, OK)
    els += e
    e, _ = table(cx + cw * 0.50, y, cw * 0.24, ["Top income", "AFN"],
                 [["Rental fees", "1,284,000"], ["Dress sales", "986,000"],
                  ["Late fees", "84,500"], ["Forfeited deposits", "38,000"],
                  ["Other income", "17,500"]], G, row_h=42, widths=[1.5, 1])
    els += e
    e, _ = table(cx + cw * 0.76, y, cw * 0.24, ["Top expense", "AFN"],
                 [["Salaries", "248,000"], ["Shop rent", "180,000"],
                  ["Dry cleaning", "86,400"], ["Marketing", "54,000"],
                  ["Utilities", "43,600"]], G, row_h=42, widths=[1.5, 1])
    els += e
    els += note(cx, y + 268, cw,
                "Comparison reads finance_daily_summaries where fresh, falling back to a live query when is_stale = true. The snapshot is a CACHE, never a source of truth —\n"
                "a back-dated expense flips is_stale on every covered date so the figure is recomputed rather than silently served stale.",
                ACCENT, G)
    return els


def _d3(ox, oy):
    """Cash & banks."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "3. Pillar 1 — cash & bank accounts",
                                     "Finance", g, sub_active="Cash & banks")
    e, y = page_header(cx, cy, cw, "Cash & banks",
                       actions=[("Transfer", "secondary"), ("＋ New account", "primary")],
                       subtitle="Balance is derived from posted transactions; the cached column is reconciled nightly",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Total cash & banks", "AFN 412,000", ACCENT, "3 active accounts", ICON["cash"]),
        ("Deposits held (liability)", "AFN 68,000", VIOLET, "inside the total above", ICON["lock"]),
        ("Your cash", "AFN 344,000", OK, "free to use", ICON["check"]),
        ("Reconciliation", "1 mismatch", DANGER, "Cash Drawer −200", ICON["alert"]),
    ], h=88, gap=14, g=G)
    els += e
    e, y2 = table(cx, y, cw,
                  ["Code", "Account", "Type", "Currency", "Opening", "In", "Out", "Computed", "Cached", "Status"],
                  [["CASH-MAIN", "Cash Drawer", "cash", "AFN", "50,000", ("+486,200", OK), ("−398,400", DANGER), "137,800", ("138,000", DANGER), ("⚠ mismatch", DANGER)],
                   ["BANK-AZIZI", "Azizi Bank", "bank", "AFN", "120,000", ("+412,000", OK), ("−296,800", DANGER), "235,200", "235,200", ("✓ matched", OK)],
                   ["WALLET-HP", "HesabPay wallet", "wallet", "AFN", "0", ("+64,500", OK), ("−25,500", DANGER), "39,000", "39,000", ("✓ matched", OK)],
                   [("TOTAL", INK), "", "", "AFN", "170,000", ("+962,700", OK), ("−720,700", DANGER), ("412,000", ACCENT), "412,200", ""]],
                  G, row_h=46, widths=[0.95, 1.35, 0.6, 0.66, 0.8, 0.9, 0.9, 0.85, 0.85, 0.95])
    els += e
    els += note(cx, y2 + 8, cw * 0.62,
                "TRUTH = finance_accounts.opening_balance + Σ posted finance_transactions (signed by direction).\n"
                "finance_accounts.cached_balance is a performance cache refreshed inside the posting transaction. A nightly job compares the two;\n"
                "a difference raises a platform_notifications row of kind 'reconcile_mismatch' — visible here as the red chip. The v1 spec stored\n"
                "current_balance as the only value, so a single failed write desynchronised the account permanently with nothing to detect it.",
                ACCENT, G)
    els += btn(cx + cw - 220, y2 + 20, 220, 40, "Recompute from ledger", "secondary", G)
    return els


def _d4(ox, oy):
    """Account statement."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "4. Account statement — running balance",
                                     "Finance", g, sub_active="Cash & banks")
    e, y = page_header(cx, cy, cw, "Cash Drawer  ·  CASH-MAIN",
                       actions=[("🖨 Print", "ghost"), ("⬇ Export CSV", "secondary")],
                       subtitle="AFN · 01 Sep – 12 Sep 2026 · opening 50,000",
                       g=G)
    els += e
    els += search_bar(cx, y, 320, "Reference / counterparty", G)
    els += filter_chips(cx + 336, y + 5, ["All", "In", "Out", "Deposits"], 0, G)
    y += 56
    e, y2 = table(cx, y, cw,
                  ["Date", "Txn #", "Description", "Source document", "In", "Out", "Balance"],
                  [["01 Sep", "—", "Opening balance", "—", "", "", "50,000.00"],
                   ["03 Sep", "FIN26-000411", "Sale — Maryam Noori", "SO26-000012", ("+96,000", OK), "", "146,000.00"],
                   ["04 Sep", "FIN26-000418", ("Rental deposit — Sara Ahmadi", VIOLET), "SO26-000019", ("+20,000", VIOLET), "", "166,000.00"],
                   ["05 Sep", "FIN26-000423", "Shop rent — September", "EXP26-0031", "", ("−180,000", DANGER), "−14,000.00"],
                   ["06 Sep", "FIN26-000431", "Transfer from Azizi Bank", "FTR26-0007", ("+200,000", OK), "", "186,000.00"],
                   ["09 Sep", "FIN26-000442", "Rental fee — Fatima Rahimi", "SO26-000014", ("+18,000", OK), "", "204,000.00"],
                   ["10 Sep", "FIN26-000448", "Supplier payment — Istanbul Bridal", "SPAY26-0014", "", ("−80,000", DANGER), "124,000.00"],
                   ["11 Sep", "FIN26-000455", ("Deposit refund — Zainab Karimi", VIOLET), "SO26-000009", "", ("−12,000", VIOLET), "112,000.00"],
                   ["12 Sep", "FIN26-000461", "Dry cleaning — Sept batch", "EXP26-0038", "", ("−18,200", DANGER), "93,800.00"],
                   ["12 Sep", "FIN26-000463", "Sale — walk-in veil", "SO26-000022", ("+44,000", OK), "", ("137,800.00", ACCENT)]],
                  G, row_h=40, widths=[0.62, 1.15, 1.9, 1.15, 0.72, 0.72, 0.9])
    els += e
    els += note(cx, y2 + 6, cw,
                "Every row links to the document that caused it — there is no way to move money without a source document. Deposit rows are tinted:\n"
                "they change cash but carry is_deposit_movement = true and no income category, so they never reach the Income pillar or the P&L.",
                ACCENT, G)
    return els


def _d5(ox, oy):
    """Add expense — the highest-frequency screen."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "5. Add expense — fast entry",
                                     "Finance", g, sub_active="Expenses")
    e, y = page_header(cx, cy, cw, "Expenses",
                       actions=[("⬇ Export", "ghost"), ("＋ Add expense", "primary")],
                       subtitle="Under 30 seconds — the most-used manual screen in the system",
                       g=G)
    els += e
    e, _ = table(cx, y, cw * 0.54, ["Date", "Category", "Vendor", "Amount", "Account"],
                 [["12 Sep", "Dry cleaning", "Kabul Laundry", "18,200", "Cash Drawer"],
                  ["11 Sep", "Transport", "—", "3,400", "Cash Drawer"],
                  ["10 Sep", "Marketing", "Insta ads", "12,000", "HesabPay"],
                  ["05 Sep", "Shop rent", "Landlord", "180,000", "Azizi Bank"]],
                 G, row_h=42, widths=[0.7, 1.2, 1.2, 0.9, 1.1])
    els += e
    de, fx, fy, fw = drawer(cx, cy - 20, cw, ch, "Add expense", "right", 460,
                            "Drawer opens from the right in English, left in Dari and Pashto", G)
    els += de
    els += _lab(fx, fy, "RECENT CATEGORIES — TAP TO FILL", G)
    els += filter_chips(fx, fy + 20, ["Dry cleaning", "Transport", "Salaries"], 0, G)
    yy = fy + 68
    e, yy = _sel(fx, yy, fw, "Category", "Dry cleaning", G, True)
    els += e
    e, yy = _inp(fx, yy, fw * 0.55 - 8, "Amount", "18,200.00", G, True)
    els += e
    e, _ = _sel(fx + fw * 0.55 + 8, yy - 64, fw * 0.45 - 8, "Currency", "AFN", G, True)
    els += e
    e, yy = _sel(fx, yy, fw, "Pay from account", "Cash Drawer — AFN 137,800", G, True)
    els += e
    e, yy = _sel(fx, yy, fw, "Payment method", "Cash", G, True)
    els += e
    e, yy = _inp(fx, yy, fw * 0.55 - 8, "Date", "12 Sep 2026", G, True)
    els += e
    e, _ = _inp(fx + fw * 0.55 + 8, yy - 64, fw * 0.45 - 8, "Vendor", "Kabul Laundry", G)
    els += e
    e, yy = textarea(fx, yy, fw, "Note", "September rental gown batch — 14 dresses", G, 2)
    els += e
    els.append(rect(fx, yy, fw, 62, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=G))
    els.append(text(fx, yy + 22, f"{ICON['photo']}   ＋ Attach receipt photo", 12.5, ACCENT, "center", fw, G))
    els += btn(fx, yy + 78, fw, 44, "Save expense", "primary", G)
    els += note(fx, yy + 132, fw,
                "POST writes finance_expenses AND exactly one\nfinance_transactions row (direction=out), linked by\nfinance_transaction_id. Account balance recomputes.\nPhotos → platform_attachments (many per expense).", ACCENT, G)
    return els


def _d6(ox, oy):
    """Unified ledger with a voided pair."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "6. Unified ledger — every money movement",
                                     "Finance", g, sub_active="Dashboard")
    e, y = page_header(cx, cy, cw, "Transaction ledger",
                       actions=[("⬇ Export CSV", "secondary")],
                       subtitle="finance_transactions — one row for every movement, whatever created it",
                       g=G)
    els += e
    els += search_bar(cx, y, 320, "Txn # / reference / counterparty", G)
    els += filter_chips(cx + 336, y + 5, ["All", "In", "Out", "Deposits", "Voided"], 0, G)
    y += 56
    e, y2 = table(cx, y, cw,
                  ["Txn #", "Date", "Dir", "Amount", "Base (AFN)", "Account", "Category", "Counterparty", "Source", "Status"],
                  [["FIN26-000463", "12 Sep", ("in", OK), "44,000 AFN", "44,000", "Cash Drawer", "dress_sale", "Walk-in", "SO26-000022", ("posted", OK)],
                   ["FIN26-000461", "12 Sep", ("out", DANGER), "18,200 AFN", "18,200", "Cash Drawer", "dry_cleaning", "Kabul Laundry", "EXP26-0038", ("posted", OK)],
                   ["FIN26-000455", "11 Sep", ("out", VIOLET), "12,000 AFN", "12,000", "Cash Drawer", ("— deposit —", VIOLET), "Zainab Karimi", "SO26-000009", ("posted", OK)],
                   ["FIN26-000448", "10 Sep", ("out", DANGER), "1,135 USD", "80,000", "Cash Drawer", "—", "Istanbul Bridal", "SPAY26-0014", ("posted", OK)],
                   ["FIN26-000442", "09 Sep", ("in", OK), "18,000 AFN", "18,000", "Cash Drawer", "rental_fee", "Fatima Rahimi", "SO26-000014", ("posted", OK)],
                   [("FIN26-000437", MUTED), "08 Sep", ("in", MUTED), ("22,000 AFN", MUTED), ("22,000", MUTED), ("Cash Drawer", MUTED), ("dress_sale", MUTED), ("Nargis A.", MUTED), ("SO26-000011", MUTED), ("✕ void", DANGER)],
                   [("FIN26-000438", INFO), "08 Sep", ("out", INFO), ("22,000 AFN", INFO), ("22,000", INFO), ("Cash Drawer", INFO), ("dress_sale", INFO), ("Nargis A.", INFO), ("reverses 000437", INFO), ("reversal", INFO)],
                   ["FIN26-000431", "06 Sep", ("in", OK), "200,000 AFN", "200,000", "Cash Drawer", "—", "Internal", "FTR26-0007", ("posted", OK)]],
                  G, row_h=40, widths=[1.1, 0.6, 0.42, 0.92, 0.78, 0.95, 0.95, 0.95, 1.05, 0.72])
    els += e
    els += note(cx, y2 + 6, cw * 0.60,
                "THE REVERSAL PAIR (rows 6 and 7) is how correction works everywhere in BOMS.\n"
                "FIN26-000437 was posted in error. Voiding it does NOT edit or delete the row — it inserts\n"
                "FIN26-000438, a mirrored row with reverses_id pointing at the original, and flips the\n"
                "original's status to 'void'. Both stay visible forever; the balance nets to zero.",
                INFO, G)
    els += note(cx + cw * 0.62, y2 + 6, cw * 0.38,
                "Every row carries amount + exchange_rate + amount_base.\n"
                "The USD supplier payment shows 1,135 USD and 80,000 AFN:\n"
                "the rate was snapshotted at posting, so editing today's rate\n"
                "never restates history.", VIOLET, G)
    return els


def _d7(ox, oy):
    """Void modal."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "7. Void a transaction — reversing entry",
                                     "Finance", g, sub_active="Dashboard")
    e, y = page_header(cx, cy, cw, "Transaction ledger", subtitle="FIN26-000437 selected", g=G)
    els += e
    e, _ = table(cx, y, cw, ["Txn #", "Date", "Dir", "Amount", "Account", "Source", "Status"],
                 [["FIN26-000437", "08 Sep", "in", "22,000 AFN", "Cash Drawer", "SO26-000011", "posted"],
                  ["FIN26-000436", "08 Sep", "in", "12,000 AFN", "Cash Drawer", "SO26-000010", "posted"]],
                 G, row_h=42, widths=[1.1, 0.7, 0.5, 1, 1.1, 1.1, 0.8])
    els += e
    els += modal(cx, cy - 20, cw, ch, "Void FIN26-000437?",
                 "This does not delete anything.\n\n"
                 "A new reversing row FIN26-000438 will be created for −22,000 AFN,\n"
                 "linked by reverses_id. FIN26-000437 will be marked 'void'.\n"
                 "Both rows stay in the ledger permanently.\n\n"
                 "Effects: Cash Drawer −22,000 · Income −22,000 · A/R for\n"
                 "SO26-000011 reopened at 22,000 · the sale's COGS entry reversed.",
                 w=580, h=330,
                 actions=[("Cancel", "secondary"), ("Void & reverse", "danger")], g=G)
    els += note(cx, oy + 790, cw,
                "Void is the ONLY correction mechanism for posted documents (ADR-005) — it applies identically to stock transactions, receipts, orders, payments and expenses.\n"
                "A void_reason is mandatory and is written to audit_logs alongside the user and timestamp. Nothing in BOMS is ever edited after posting, and nothing is ever deleted.",
                DANGER, G)
    return els


def _d8(ox, oy):
    """Accounts payable + aging."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "8. Pillar 4 — accounts payable & aging",
                                     "Finance", g, sub_active="A/P")
    e, y = page_header(cx, cy, cw, "Accounts payable",
                       actions=[("⬇ Export", "ghost"), ("Pay supplier", "primary")],
                       subtitle="What we owe · finance_payables is the single source of this number",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Total A/P", "AFN 252,388", WARN, "4 suppliers · 7 invoices", ICON["suppliers"]),
        ("Current", "AFN 94,000", OK, "not yet due", ICON["check"]),
        ("1–30 days", "AFN 88,388", WARN, "due soon", ICON["clock"]),
        ("31–60 days", "AFN 46,000", DANGER, "chase", ICON["alert"]),
        ("60+ days", "AFN 24,000", DANGER, "overdue", ICON["alert"]),
    ], h=88, gap=14, g=G)
    els += e
    e, y2 = table(cx, y, cw,
                  ["Payable", "Supplier", "PO / GRN", "Issued", "Due", "Original", "Paid", "Balance", "Age", "Status", ""],
                  [["AP26-0022", "Istanbul Bridal Co.", "PO26-000012", "12 Sep", "12 Oct", "246,404", "80,000", ("166,404", WARN), ("0 d", OK), ("partial", WARN), "Pay"],
                   ["AP26-0019", "Dubai Fashion House", "PO26-000009", "28 Aug", "27 Sep", "46,000", "0", ("46,000", WARN), ("16 d", WARN), ("open", WARN), "Pay"],
                   ["AP26-0014", "Kabul Textile Traders", "PO26-000006", "02 Aug", "01 Sep", "24,000", "0", ("24,000", DANGER), ("42 d", DANGER), ("overdue", DANGER), "Pay"],
                   ["AP26-0011", "Herat Silk House", "PO26-000004", "18 Jul", "17 Aug", "15,984", "0", ("15,984", DANGER), ("57 d", DANGER), ("overdue", DANGER), "Pay"],
                   [("TOTAL", INK), "", "", "", "", "332,388", "80,000", ("252,388", WARN), "", "", ""]],
                  G, row_h=44, widths=[0.85, 1.5, 1.05, 0.6, 0.6, 0.85, 0.7, 0.85, 0.5, 0.75, 0.45])
    els += e
    els += note(cx, y2 + 8, cw,
                "A/P is opened by procurement_receipts on post and reduced by procurement_supplier_payments and procurement_returns.\n"
                "procurement_purchase_orders.cached_balance_amount mirrors this for display and is NEVER summed for the pillar — in v1 both tables held the number\n"
                "with no reconciliation, so the dashboard and the PO list were guaranteed to drift apart. Aging buckets come from due_date vs the current business_date.",
                ACCENT, G)
    return els


def _d9(ox, oy):
    """Accounts receivable + aging."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "9. Pillar 5 — accounts receivable & aging",
                                     "Finance", g, sub_active="A/R")
    e, y = page_header(cx, cy, cw, "Accounts receivable",
                       actions=[("⬇ Export", "ghost"), ("Collect payment", "primary")],
                       subtitle="What customers owe us · finance_receivables is the single source",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Total A/R", "AFN 86,400", INFO, "11 customers", ICON["customers"]),
        ("Current", "AFN 42,300", OK, "not yet due", ICON["check"]),
        ("1–30 days", "AFN 19,500", WARN, "follow up", ICON["clock"]),
        ("31–60 days", "AFN 14,600", DANGER, "chase", ICON["alert"]),
        ("60+ days", "AFN 10,000", DANGER, "at risk", ICON["alert"]),
    ], h=88, gap=14, g=G)
    els += e
    e, y2 = table(cx, y, cw,
                  ["Receivable", "Customer", "Phone", "Order", "Issued", "Due", "Original", "Paid", "Balance", "Age", ""],
                  [["AR26-0041", "Sara Ahmadi", "0700 12 34 56", "SO26-000019", "12 Sep", "26 Sep", "31,500", "20,000", ("11,500", OK), ("0 d", OK), "Collect"],
                   ["AR26-0038", "Maryam Noori", "0700 88 21 09", "SO26-000012", "03 Sep", "17 Sep", "96,000", "65,700", ("30,300", OK), ("0 d", OK), "Collect"],
                   ["AR26-0033", "Fatima Rahimi", "0700 45 67 12", "SO26-000014", "26 Aug", "09 Sep", "24,500", "10,000", ("14,500", WARN), ("3 d", WARN), "Collect"],
                   ["AR26-0029", "Zainab Karimi", "0700 33 90 44", ("CLM26-0003 damage", VIOLET), "12 Aug", "26 Aug", "20,100", "5,500", ("14,600", DANGER), ("17 d", DANGER), "Collect"],
                   ["AR26-0021", "Nargis Amini", "0700 71 05 88", "SO26-000004", "02 Jul", "16 Jul", "15,500", "0", ("15,500", DANGER), ("58 d", DANGER), "Collect"],
                   [("TOTAL", INK), "", "", "", "", "", "187,600", "101,200", ("86,400", INFO), "", ""]],
                  G, row_h=44, widths=[0.85, 1.25, 1.1, 1.25, 0.6, 0.6, 0.78, 0.7, 0.8, 0.5, 0.62])
    els += e
    els += note(cx, y2 + 8, cw,
                "A/R opens when an order completes with a balance, or when a rental claim (damage / loss / late) charges a customer beyond their deposit — row 4 shows exactly that case.\n"
                "sales_orders.cached_balance_amount mirrors this for display only. Collecting posts a finance_transactions IN, reduces the receivable, and updates the order's cache.",
                ACCENT, G)
    return els


def _d10(ox, oy):
    """Collect / pay drawer with allocation."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "10. Collect payment — allocate across invoices",
                                     "Finance", g, sub_active="A/R")
    e, y = page_header(cx, cy, cw, "Accounts receivable", subtitle="Maryam Noori selected", g=G)
    els += e
    e, _ = table(cx, y, cw * 0.5, ["Receivable", "Order", "Balance", "Age"],
                 [["AR26-0038", "SO26-000012", "30,300", "0 d"],
                  ["AR26-0026", "SO26-000007", "12,000", "22 d"]],
                 G, row_h=42, widths=[1, 1.1, 0.8, 0.5])
    els += e
    de, fx, fy, fw = drawer(cx, cy - 20, cw, ch, "Collect from Maryam Noori", "right", 460,
                            "0700 88 21 09 · 2 open receivables · AFN 42,300", G)
    els += de
    yy = fy
    e, yy = _inp(fx, yy, fw * 0.55 - 8, "Amount received", "35,000.00", G, True)
    els += e
    e, _ = _sel(fx + fw * 0.55 + 8, yy - 64, fw * 0.45 - 8, "Currency", "AFN", G, True)
    els += e
    e, yy = _sel(fx, yy, fw, "Deposit into account", "Cash Drawer", G, True)
    els += e
    e, yy = _sel(fx, yy, fw, "Payment method", "Cash", G, True)
    els += e
    els += _lab(fx, yy, "ALLOCATE ACROSS RECEIVABLES", G)
    e, yy2 = table(fx, yy + 20, fw, ["Receivable", "Balance", "Apply"],
                   [["AR26-0026 (oldest)", "12,000", ("12,000", ACCENT)],
                    ["AR26-0038", "30,300", ("23,000", ACCENT)]],
                   G, row_h=42, widths=[1.5, 0.8, 0.8])
    els += e
    e, yy3 = money_row(fx, yy2 + 6, fw,
                       [("Received", "35,000.00"), ("Allocated", ("35,000.00", OK)),
                        ("Unallocated", ("0.00", MUTED))],
                       G, total=("Remaining A/R after", "AFN 7,300.00"))
    els += e
    els += btn(fx, yy3 + 8, fw, 44, "Post collection", "primary", G)
    els += note(fx, yy3 + 62, fw,
                "Oldest-first allocation is the default and is editable.\nPOST writes one finance_transactions IN, reduces each\nallocated finance_receivables row, and refreshes the\ncached balance on the linked sales_orders.", ACCENT, G)
    return els


def _d11(ox, oy):
    """Profit & loss."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "11. Profit & loss statement",
                                     "Finance", g, sub_active="P&L")
    e, y = page_header(cx, cy, cw, "Profit & loss",
                       actions=[("🖨 Print", "ghost"), ("⬇ Export", "secondary")],
                       subtitle="01 – 30 September 2026 · all branches · AFN",
                       g=G)
    els += e
    e, _ = _sel(cx, y, 200, "Period", "This month", G)
    els += e
    e, _ = _sel(cx + 216, y, 200, "Branch", "All branches", G)
    els += e
    e, _ = _sel(cx + 432, y, 200, "Compare with", "Last month", G)
    els += e
    els += btn(cx + 648, y + 18, 110, 38, "Run", "primary", G)
    y += 92
    SW = cw * 0.54
    els.append(rect(cx, y, SW, 452, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 24, y + 18, "STATEMENT", 11, MUTED, width=SW - 48, g=G))
    els.append(text(cx + SW - 160, y + 18, "Sept 2026        vs Aug", 10.5, MUTED, "right", 140, G))
    e, _ = _stmt(cx + 24, y + 48, SW - 48, [
        (0, "REVENUE", "", INK, True),
        (1, "Rental fees", "1,284,000", INK, False),
        (1, "Dress sales", "986,000", INK, False),
        (1, "Late fees", "84,500", INK, False),
        (1, "Forfeited deposits", "38,000", VIOLET, False),
        (1, "Other income", "17,500", INK, False),
        (0, "---", "", INK, False),
        (0, "Total revenue", "2,410,000", OK, True),
        (0, "", "", INK, False),
        (0, "COST OF GOODS SOLD", "", INK, True),
        (1, "Sale COGS — weighted avg cost of dresses sold", "492,000", DANGER, False),
        (1, "Rental amortisation — cost per use", "192,000", VIOLET, False),
        (0, "---", "", INK, False),
        (0, "Total COGS", "684,000", DANGER, True),
        (0, "---", "", INK, False),
        (0, "GROSS PROFIT", "1,726,000", OK, True),
        (0, "", "", INK, False),
        (0, "OPERATING EXPENSES", "", INK, True),
        (1, "Salaries", "248,000", DANGER, False),
        (1, "Shop rent", "180,000", DANGER, False),
        (1, "Dry cleaning", "86,400", DANGER, False),
        (1, "Marketing", "54,000", DANGER, False),
        (1, "Utilities & transport", "43,600", DANGER, False),
        (0, "---", "", INK, False),
        (0, "Total expenses", "612,000", DANGER, True),
        (0, "---", "", INK, False),
        (0, "NET PROFIT", "1,114,000", ACCENT, True),
    ], G)
    els += e
    rx = cx + SW + 24
    RW = cw - SW - 24
    e, _ = bar_chart(rx, y, RW, 250, "Revenue → net profit (AFN '000)",
                     [("Revenue", 1.0, "2,410"), ("− COGS", 0.28, "684"),
                      ("Gross", 0.72, "1,726"), ("− Expenses", 0.25, "612"),
                      ("Net", 0.46, "1,114")], G, ACCENT)
    els += e
    e, _ = table(rx, y + 266, RW, ["Margin", "Sept", "Aug"],
                 [["Gross margin", ("71.6%", OK), "68.9%"],
                  ["Net margin", ("46.2%", OK), "42.1%"],
                  ["COGS ratio", "28.4%", "31.1%"],
                  ["Expense ratio", "25.4%", "26.8%"]],
                 G, row_h=42, widths=[1.4, 0.8, 0.8])
    els += e
    els += note(rx, y + 470, RW,
                "RENTAL AMORTISATION (ADR-002) is the line the v1 spec\n"
                "had no home for. A rented dress is not consumed, so it\n"
                "carries acquisition_cost ÷ expected_rental_uses per rental,\n"
                "accumulated until the dress has paid for itself.\n"
                "Without it, rental margin looks like 100% forever.", VIOLET, G)
    els += note(cx, y + 466, SW,
                "Reads finance_transactions (by category kind) for revenue and expenses, and finance_cogs_entries for BOTH COGS lines.\n"
                "Deposits appear only as 'forfeited deposits' — money the shop actually kept. Deposits still held are a liability and never enter this statement.",
                ACCENT, G)
    return els


def _d12(ox, oy):
    """Customer deposits register."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "12. Customer deposits held — liability register",
                                     "Finance", g, sub_active="Dashboard")
    e, y = page_header(cx, cy, cw, "Customer deposits",
                       actions=[("⬇ Export", "ghost")],
                       subtitle="Security money held against rentals — inside cash, but not the shop's money",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Currently held", "AFN 68,000", VIOLET, "14 open rentals", ICON["lock"]),
        ("Applied to balances", "AFN 142,000", OK, "this month", ICON["check"]),
        ("Forfeited → income", "AFN 38,000", WARN, "damage & late", ICON["alert"]),
        ("Refunded", "AFN 96,500", INFO, "this month", ICON["money_out"]),
        ("Unsettled 14+ days", "AFN 18,000", DANGER, "3 rentals", ICON["clock"]),
    ], h=88, gap=14, g=G)
    els += e
    e, y2 = table(cx, y, cw,
                  ["Deposit", "Order", "Customer", "Taken", "Applied", "Forfeited", "Refunded", "Still held", "Status"],
                  [["DEP26-0041", "SO26-000019", "Sara Ahmadi", "20,000", "0", "0", "0", ("20,000", VIOLET), ("held", VIOLET)],
                   ["DEP26-0040", "SO26-000021", "Maryam Noori", "24,000", "0", "0", "0", ("24,000", VIOLET), ("held", VIOLET)],
                   ["DEP26-0038", "SO26-000018", "Fatima Rahimi", "12,000", "0", "0", "0", ("12,000", VIOLET), ("held", VIOLET)],
                   ["DEP26-0036", "SO26-000016", "Nasrin Hakimi", "12,000", "0", "0", "0", ("12,000", VIOLET), ("held", VIOLET)],
                   ["DEP26-0033", "SO26-000014", "Zainab Karimi", "20,000", "8,000", ("12,000", WARN), "0", ("0", MUTED), ("settled", OK)],
                   ["DEP26-0029", "SO26-000009", "Nargis Amini", "12,000", "0", "0", ("12,000", INFO), ("0", MUTED), ("settled", OK)],
                   [("TOTALS", INK), "", "", "100,000", "8,000", "12,000", "12,000", ("68,000", VIOLET), ""]],
                  G, row_h=42, widths=[0.95, 1.15, 1.25, 0.75, 0.75, 0.82, 0.8, 0.85, 0.75])
    els += e
    els += note(cx, y2 + 8, cw * 0.58,
                "held = taken − applied − forfeited − refunded, and the TOTALS row reconciles exactly to the\n"
                "'Deposits held' tile on the dashboard and to the cash split on the Cash & banks screen.\n"
                "Row 5 is a damage case: 12,000 of a 20,000 deposit was forfeited (→ INCOME, appears in the\n"
                "P&L as 'forfeited deposits') and 8,000 was applied to the final rental balance.",
                VIOLET, G)
    els += note(cx + cw * 0.60, y2 + 8, cw * 0.40,
                "Why this matters: in v1 a deposit was posted straight to\n"
                "Income. A day with ten bookings showed a large profit that\n"
                "partly had to be handed back — the single number the owner\n"
                "trusts most was systematically overstated.", DANGER, G)
    return els


# ══════════════════════════════════════════════════════════════════
#  MOBILE
# ══════════════════════════════════════════════════════════════════

def _m1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "1. Finance dashboard", g, "Finance")
    e, y = phone_header(cx, cy, cw, "Finance", right=ICON["calendar"], g=G)
    els += e
    els += filter_chips(cx, y, ["Today", "Week", "Month"], 0, G)
    y += 44
    els.append(rect(cx, y, cw, 104, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=2, groupIds=G))
    els.append(text(cx + 16, y + 14, "NET PROFIT TODAY", 10, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 34, "AFN 61,180", 32, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 78, "revenue 118,500 − cogs 23,120 − expenses 34,200", 9.5, ACCENT, width=cw - 32, g=G))
    y += 120
    for i, (n, t, v, c, ic) in enumerate([
            (1, "Cash & banks", "412,000", ACCENT, ICON["cash"]),
            (2, "Income", "118,500", OK, ICON["money_in"]),
            (3, "Expenses", "34,200", DANGER, ICON["money_out"]),
            (4, "A/P — we owe", "252,388", WARN, ICON["suppliers"]),
            (5, "A/R — owed to us", "86,400", INFO, ICON["customers"])]):
        els.append(rect(cx, y, cw, 56, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(rect(cx, y, 4, 56, strokeColor=c, backgroundColor=c, strokeWidth=1, groupIds=G))
        els.append(text(cx + 16, y + 10, f"{ic}  PILLAR {n}", 9, c, width=cw - 130, g=G))
        els.append(text(cx + 16, y + 28, t, 12.5, INK, width=cw - 130, g=G))
        els.append(text(cx + cw - 130, y + 18, f"AFN {v}", 15, c, "right", 116, G))
        y += 62
    els.append(rect(cx, y, cw, 62, strokeColor=VIOLET, backgroundColor=VIOLET_BG, strokeWidth=2, groupIds=G))
    els.append(text(cx + 16, y + 10, f"{ICON['lock']}  DEPOSITS HELD — NOT YOUR MONEY", 9, VIOLET, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 26, "AFN 68,000", 17, VIOLET, width=cw - 150, g=G))
    els.append(text(cx + cw - 150, y + 30, "your cash 344,000", 10, VIOLET, "right", 136, G))
    return els


def _m2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "2. Add expense", g, "Finance", show_nav=False)
    els.append(rect(ox + 1, oy + TITLE_H + 110, PHONE_W - 2, PHONE_H - 110, strokeColor=LINE,
                    backgroundColor=BG, strokeWidth=2, groupIds=G))
    sy = oy + TITLE_H + 128
    els.append(text(cx, sy, "Add expense", 19, INK, width=cw - 40, g=G))
    els.append(text(cx + cw - 20, sy + 2, ICON["cross"], 15, MUTED, g=G))
    y = sy + 34
    els.append(text(cx, y, "RECENT — TAP TO FILL", 9.5, MUTED, width=cw, g=G))
    els += filter_chips(cx, y + 16, ["Dry cleaning", "Transport"], 0, G)
    y += 60
    for lab, val, req in [("Category", "Dry cleaning", True), ("Amount (AFN)", "18,200.00", True),
                          ("Pay from", "Cash Drawer", True), ("Method", "Cash", True),
                          ("Date", "12 Sep 2026", True), ("Vendor", "Kabul Laundry", False)]:
        e, y = _inp(cx, y, cw, lab, val, G, req, 34)
        els += e
    els.append(rect(cx, y, cw, 52, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=G))
    els.append(text(cx, y + 18, f"{ICON['photo']}  ＋ Attach receipt", 12, ACCENT, "center", cw, G))
    els += btn(cx, y + 64, cw, 46, "Save expense", "primary", G)
    return els


def _m3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "3. Cash & banks", g, "Finance")
    e, y = phone_header(cx, cy, cw, "Cash & banks", right="＋", g=G)
    els += e
    els.append(rect(cx, y, cw, 86, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 16, y + 12, "TOTAL", 10, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 30, "AFN 412,000", 24, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 62, "− 68,000 deposits held = 344,000 yours", 10, VIOLET, width=cw - 32, g=G))
    y += 102
    for code, nm, typ, bal, st, col in [("CASH-MAIN", "Cash Drawer", "cash", "137,800", "⚠ mismatch −200", DANGER),
                                        ("BANK-AZIZI", "Azizi Bank", "bank", "235,200", "✓ reconciled", OK),
                                        ("WALLET-HP", "HesabPay", "wallet", "39,000", "✓ reconciled", OK)]:
        els.append(rect(cx, y, cw, 70, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, nm, 13.5, INK, width=cw - 130, g=G))
        els.append(text(cx + 14, y + 30, f"{code} · {typ}", 10.5, MUTED, width=cw - 130, g=G))
        els.append(text(cx + 14, y + 48, st, 10, col, width=cw - 130, g=G))
        els.append(text(cx + cw - 128, y + 24, f"AFN {bal}", 15, INK, "right", 114, G))
        y += 78
    els += btn(cx, y + 6, cw, 44, "Transfer between accounts", "secondary", G)
    return els


def _m4(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "4. Ledger", g, "Finance")
    e, y = phone_header(cx, cy, cw, "Ledger", right=ICON["filter"], g=G)
    els += e
    els += filter_chips(cx, y, ["All", "In", "Out", "Deposits"], 0, G)
    y += 44
    rows = [("Sale — walk-in veil", "SO26-000022 · 12 Sep", "+44,000", OK),
            ("Dry cleaning", "EXP26-0038 · 12 Sep", "−18,200", DANGER),
            ("Deposit refund — Zainab", "SO26-000009 · 11 Sep", "−12,000", VIOLET),
            ("Supplier — Istanbul Bridal", "SPAY26-0014 · 10 Sep", "−80,000", DANGER),
            ("Rental fee — Fatima", "SO26-000014 · 09 Sep", "+18,000", OK),
            ("Sale — voided", "FIN26-000437 · void", "22,000", MUTED)]
    for desc, ref, amt, col in rows:
        els.append(rect(cx, y, cw, 62, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 12, desc, 12.5, INK, width=cw - 120, g=G))
        els.append(text(cx + 14, y + 32, ref, 10.5, MUTED, width=cw - 120, g=G))
        els.append(text(cx + cw - 118, y + 22, amt, 15, col, "right", 104, G))
        y += 70
    return els


def _m5(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "5. A/P & A/R", g, "Finance")
    e, y = phone_header(cx, cy, cw, "Owed", g=G)
    els += e
    els += filter_chips(cx, y, ["We owe (A/P)", "Owed to us"], 0, G)
    y += 46
    els.append(rect(cx, y, cw, 72, strokeColor=WARN, backgroundColor=WARN_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 16, y + 12, "TOTAL A/P", 10, WARN, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 30, "AFN 252,388", 22, WARN, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 56, "current 94,000 · overdue 39,984", 9.5, WARN, width=cw - 32, g=G))
    y += 88
    for sup, ref, bal, age, col in [("Istanbul Bridal Co.", "AP26-0022 · due 12 Oct", "166,404", "0 d", OK),
                                    ("Dubai Fashion House", "AP26-0019 · due 27 Sep", "46,000", "16 d", WARN),
                                    ("Kabul Textile Traders", "AP26-0014 · overdue", "24,000", "42 d", DANGER),
                                    ("Herat Silk House", "AP26-0011 · overdue", "15,984", "57 d", DANGER)]:
        els.append(rect(cx, y, cw, 70, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, sup, 12.5, INK, width=cw - 120, g=G))
        els.append(text(cx + 14, y + 30, ref, 10.5, MUTED, width=cw - 120, g=G))
        els.append(text(cx + 14, y + 48, age, 10, col, width=cw - 120, g=G))
        els.append(text(cx + cw - 118, y + 16, f"AFN {bal}", 13.5, col, "right", 104, G))
        els.append(text(cx + cw - 78, y + 42, "Pay →", 11.5, ACCENT, "right", 64, G))
        y += 78
    return els


def _m6(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "6. Profit & loss", g, "Finance")
    e, y = phone_header(cx, cy, cw, "Profit & loss", right=ICON["export"], g=G)
    els += e
    els.append(text(cx, y, "September 2026 · all branches", 11, MUTED, width=cw, g=G))
    y += 24
    els.append(rect(cx, y, cw, 78, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=2, groupIds=G))
    els.append(text(cx + 16, y + 12, "NET PROFIT", 10, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 30, "AFN 1,114,000", 26, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 60, "net margin 46.2%  ·  +32% vs August", 9.5, ACCENT, width=cw - 32, g=G))
    y += 94
    e, y = _stmt(cx, y, cw, [
        (0, "Revenue", "2,410,000", OK, True),
        (1, "Rental fees", "1,284,000", MUTED, False),
        (1, "Dress sales", "986,000", MUTED, False),
        (1, "Late fees", "84,500", MUTED, False),
        (1, "Forfeited deposits", "38,000", VIOLET, False),
        (1, "Other", "17,500", MUTED, False),
        (0, "---", "", INK, False),
        (0, "COGS", "684,000", DANGER, True),
        (1, "Sale COGS", "492,000", MUTED, False),
        (1, "Rental amortisation", "192,000", VIOLET, False),
        (0, "---", "", INK, False),
        (0, "Gross profit", "1,726,000", OK, True),
        (0, "Expenses", "612,000", DANGER, True),
        (0, "---", "", INK, False),
        (0, "NET PROFIT", "1,114,000", ACCENT, True),
    ], G)
    els += e
    els += note(cx, y + 6, cw, "Rental amortisation = cost ÷ expected uses\nper rental. Without it rental margin would\nlook like 100% forever.", VIOLET, G)
    return els


def _m7(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "7. Deposits held", g, "Finance")
    e, y = phone_header(cx, cy, cw, "Deposits held", left=ICON["back"], g=G)
    els += e
    els.append(rect(cx, y, cw, 80, strokeColor=VIOLET, backgroundColor=VIOLET_BG, strokeWidth=2, groupIds=G))
    els.append(text(cx + 16, y + 12, f"{ICON['lock']}  CURRENTLY HELD — A LIABILITY", 9.5, VIOLET, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 30, "AFN 68,000", 26, VIOLET, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 62, "across 14 open rentals", 10, VIOLET, width=cw - 32, g=G))
    y += 96
    for cust, order, amt, days, col in [("Sara Ahmadi", "SO26-000019 · 19–21 Sep", "20,000", "held 1 d", VIOLET),
                                        ("Maryam Noori", "SO26-000021 · 24–26 Sep", "24,000", "held 0 d", VIOLET),
                                        ("Fatima Rahimi", "SO26-000018 · 14–16 Sep", "12,000", "held 16 d", DANGER),
                                        ("Nasrin Hakimi", "SO26-000016 · 08–10 Sep", "12,000", "held 22 d", DANGER)]:
        els.append(rect(cx, y, cw, 68, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, cust, 12.5, INK, width=cw - 110, g=G))
        els.append(text(cx + 14, y + 29, order, 10.5, MUTED, width=cw - 110, g=G))
        els.append(text(cx + 14, y + 46, days, 10, col, width=cw - 110, g=G))
        els.append(text(cx + cw - 108, y + 24, f"AFN {amt}", 13.5, VIOLET, "right", 94, G))
        y += 76
    els += note(cx, y + 4, cw, "Settle on return: apply to the balance,\nforfeit for damage (→ income), or refund.", VIOLET, G)
    return els


def _m8(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "8. Empty state", g, "Finance")
    e, y = phone_header(cx, cy, cw, "Expenses", right=ICON["filter"], g=G)
    els += e
    els += filter_chips(cx, y, ["Today", "Week", "Month"], 0, G)
    y += 46
    els += empty_state(cx, y, cw, 300, ICON["receipt"], "No expenses today",
                       "Nothing recorded for 12 Sep 2026.\nAdd one as soon as you spend —\nit takes about 20 seconds.",
                       "＋ Add expense", G)
    return els


# ══════════════════════════════════════════════════════════════════

def desktop():
    els = board_title(0, -170, "BOMS Desktop — Finance",
                      "Five pillars + the deposits liability · deposits are never income · COGS has two kinds "
                      "(sale + rental amortisation) · balances derived · void = reversing entry")
    screens = [_d1, _d2, _d3, _d4, _d5, _d6, _d7, _d8, _d9, _d10, _d11, _d12]
    labels = {0: "PILLARS & DASHBOARD", 4: "PILLARS 2 & 3 — MONEY IN / OUT",
              8: "PILLARS 4 & 5 — A/P & A/R", 11: "PROFIT & LOSS"}
    for i, fn in enumerate(screens):
        ox, oy = grid_pos(i, DESK_COLS)
        if i in labels:
            els += section_label(ox, oy - 74, labels[i])
        els += fn(ox, oy)
    els += flow_arrows(len(screens), DESK_COLS)
    return els


def mobile():
    els = board_title(0, -150, "BOMS Mobile — Finance",
                      "Owner's daily answer: am I making money? · add expense in 20 seconds · deposits shown as a liability")
    screens = [_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8]
    for i, fn in enumerate(screens):
        ox, oy = grid_pos(i, PHONE_COLS, PHONE_W, PHONE_H)
        els += fn(ox, oy)
    els += flow_arrows(len(screens), PHONE_COLS, PHONE_W, PHONE_H)
    return els
