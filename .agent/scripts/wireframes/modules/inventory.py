#!/usr/bin/env python3
"""BOMS — Inventory module wireframes (desktop + mobile).

Draws the CORRECTED stock model:
  • Owned    = on hand + on rent   (valuation basis)
  • Available = on hand − reserved
  • Reserved comes from inventory_reservations, never from the ledger
  • Ledger types: stock_in, stock_out, adjustment, transfer_in, transfer_out,
                  rent_out, rent_return, dispose      (no reserve / release)
  • Costing    = weighted average cost (WAC) per (item, warehouse)
  • lifecycle_status is stored; availability is derived
  • an item has stock in MANY warehouses
  • rental_buffer_days blocks a dress after rent_return (cleaning)
  • posted documents are immutable — correct by Void (reversing document)
"""

from __future__ import annotations

from dsl import *  # noqa: F401,F403

DESK_COLS = 4
PHONE_COLS = 6

# ── local compositions (rect/text only) ───────────────────────────


def _sel(x, y, w, label, value="", g=None, required=False, h=36):
    """Select box with chevron — 64px row pitch."""
    g = g or []
    els, ny = field(x, y, w, label, value, g, required, None, h)
    els.append(text(x + w - 22, y + 18 + (h - 16) / 2, ICON["down"], 12, MUTED, g=g))
    return els, ny


def _inp(x, y, w, label, value="", g=None, required=False, h=36):
    return field(x, y, w, label, value, g, required, None, h)


def _photo(x, y, w, h, g, glyph=None, caption=None):
    glyph = glyph or ICON["dress"]
    els = [rect(x, y, w, h, strokeColor=LINE, backgroundColor=SOFT, strokeWidth=1,
                strokeStyle="dashed", groupIds=g)]
    els.append(text(x, y + h / 2 - 20, glyph, 24, FAINT, "center", w, g))
    if caption:
        els.append(text(x, y + h / 2 + 12, caption, 10.5, FAINT, "center", w, g))
    return els


def _tile(x, y, w, h, icon, label, g, color=INK):
    return [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=g),
            text(x, y + 12, icon, 17, color, "center", w, g),
            text(x, y + h - 22, label, 11, color, "center", w, g)]


def _kv(x, y, w, label, value, g, color=INK, size=13):
    return [text(x, y, label, 10.5, MUTED, width=w, g=g),
            text(x, y + 15, value, size, color, width=w, g=g)]


def _lab(x, y, s, g, color=MUTED, size=11.5):
    return [text(x, y, s, size, color, g=g)]


def _panel(x, y, w, h, title, g, bg=BG, color=MUTED):
    els = [rect(x, y, w, h, strokeColor=HAIRLINE, backgroundColor=bg, strokeWidth=1, groupIds=g)]
    if title:
        els.append(text(x + 16, y + 13, title, 12, color, width=w - 32, g=g))
    return els


# ── shared sample data ────────────────────────────────────────────

ITEMS = [
    ("ADF26-0042", "White A-Line Gown", "Wedding Dress", "M"),
    ("ADF26-0043", "Gold Ball Gown", "Engagement Dress", "L"),
    ("ADF26-0051", "Emerald Engagement Set", "Engagement Set", "40"),
    ("ADF26-0067", "Chantilly Veil", "Veil", "One size"),
    ("ADF26-0088", "Ivory Mermaid Gown", "Wedding Dress", "S"),
    ("ADF26-0091", "Rose Nikah Abaya", "Nikah Wear", "38"),
    ("ADF26-0102", "Pearl Tiara Set", "Jewellery", "One size"),
    ("ADF26-0115", "Champagne Ball Gown", "Engagement Dress", "40"),
]


# ══════════════════════════════════════════════════════════════════
#  DESKTOP
# ══════════════════════════════════════════════════════════════════

def _d1(ox, oy):
    """Inventory hub."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "1. Inventory hub — stock at a glance",
                                     "Inventory", g)
    e, y = page_header(cx, cy, cw, "Inventory",
                       actions=[("⬇ Export", "ghost"), ("Stock in", "secondary"),
                                ("＋ New item", "primary")],
                       subtitle="Al Dubai Bridal · Main branch · all warehouses · as of 12 Sep 2026",
                       g=G)
    els += e

    e, y = stat_row(cx, y, cw, [
        ("Stock worth", "AFN 4.82M", ACCENT, "owned × avg cost", ICON["cash"]),
        ("Owned units", "1,284", INK, "on hand + on rent", ICON["inventory"]),
        ("On hand", "1,046", INK, "in the warehouse", ICON["warehouse"]),
        ("On rent", "238", VIOLET, "out with customers", ICON["rental"]),
        ("Reserved", "92", WARN, "from reservations", ICON["reserve"]),
        ("Available", "954", OK, "on hand − reserved", ICON["check"]),
        ("Low stock", "11", DANGER, "below reorder level", ICON["alert"]),
    ], h=92, gap=12, g=G)
    els += e

    LW, RW = 716, 404
    rx = cx + LW + 16

    # ── left: quick actions + recent movements
    els += _lab(cx, y, "QUICK ACTIONS", G)
    tw = (LW - 5 * 12) / 6
    for i, (ic, lb) in enumerate([(ICON["inventory"], "Stock in"), (ICON["truck"], "Receive PO"),
                                  (ICON["adjust"], "Adjust"), (ICON["dispose"], "Dispose"),
                                  (ICON["transfer"], "Transfer"), (ICON["reserve"], "Reserve")]):
        els += _tile(cx + i * (tw + 12), y + 22, tw, 72, ic, lb, G)

    els += _lab(cx, y + 112, "RECENT MOVEMENTS", G)
    els.append(text(cx + LW - 90, y + 112, "View ledger →", 11.5, ACCENT, "right", 90, G))
    e, _ = table(cx, y + 134, LW,
                 ["Date", "Txn #", "Item", "Type", "Qty", "Warehouse"],
                 [["12 Sep", "TRN26-004182", "White A-Line Gown", ("rent_out", VIOLET), ("−1", DANGER), "Main Store"],
                  ["12 Sep", "TRN26-004181", "Chantilly Veil", ("stock_in", OK), ("+12", OK), "Main Store"],
                  ["11 Sep", "TRN26-004179", "Gold Ball Gown", ("rent_return", OK), ("+1", OK), "Main Store"],
                  ["11 Sep", "TRN26-004176", "Pearl Tiara Set", ("transfer_out", INFO), ("−4", DANGER), "Shar-e-Naw"],
                  ["10 Sep", "TRN26-004170", "Rose Nikah Abaya", ("dispose", DANGER), ("−1", DANGER), "Repair Room"]],
                 G, row_h=40, widths=[0.8, 1.25, 1.9, 1.05, 0.55, 1.0])
    els += e

    # ── right: low stock + conflicts
    els += _lab(rx, y, "LOW STOCK — BELOW REORDER LEVEL", G, DANGER)
    e, _ = table(rx, y + 22, RW, ["Item", "Avail", "Reorder"],
                 [["Chantilly Veil", ("2", DANGER), "10"],
                  ["Pearl Tiara Set", ("1", DANGER), "6"],
                  ["Ivory Hair Comb", ("0", DANGER), "8"],
                  ["Bridal Gloves (S)", ("3", WARN), "6"]],
                 G, row_h=40, widths=[2.0, 0.8, 0.9])
    els += e

    els += _lab(rx, y + 244, "BOOKING CONFLICTS — NEXT 30 DAYS", G, WARN)
    els += note(rx, y + 266, RW,
                "2 conflicts detected\nADF26-0042 · 24–26 Sep — 2 reservations,\n1 unit available\nADF26-0115 · 03 Oct — returns 04 Oct after\n2-day cleaning buffer",
                WARN, G)

    els += note(cx, oy + 740, cw,
                "Read-only dashboard — writes nothing. Reads inventory_stock_balances (view) for on-hand / on-rent / reserved / available / avg cost, "
                "inventory_stock_transactions for recent movements,\nand inventory_reservations for upcoming bookings and conflicts. "
                "Stock worth = Σ(owned_qty × avg_unit_cost) where owned = on hand + on rent — a gown out on rent is still an asset and must be valued.\n"
                "Available = on hand − reserved. Reserved is read from inventory_reservations (status=active) — it is NOT a stock movement and never appears in the ledger.",
                ACCENT, G)
    return els


def _d2(ox, oy):
    """Items list."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "2. Items list — catalogue with the three buckets",
                                     "Inventory", g, sub_active="Items")
    e, y = page_header(cx, cy, cw, "Items",
                       actions=[("⬇ Export", "ghost"), ("Import CSV", "secondary"),
                                ("＋ New item", "primary")],
                       subtitle="1,284 owned units · 48 SKUs · Main branch", g=G)
    els += e

    els += search_bar(cx, y, 460, "Search SKU, name, barcode, model…", G)
    els += btn(cx + 476, y, 130, 40, f"{ICON['filter']}  Filters", "secondary", G)
    els += btn(cx + 616, y, 150, 40, "Warehouse: All ▾", "secondary", G)
    els += btn(cx + cw - 150, y, 150, 40, "Columns ▾", "secondary", G)
    y += 52

    els += filter_chips(cx, y, ["All 1,284", "Available 954", "Reserved 92", "On rent 238",
                                "Repairing 14", "Low stock 11", "Disposed 8"], 0, G)
    y += 42

    cols = ["SKU", "", "Name", "Category", "Size", "Lifecycle",
            "On hand", "On rent", "Rsvd", "Avail", "Avg cost", "Worth"]
    wts = [1.15, 0.4, 1.9, 1.15, 0.55, 0.95, 0.72, 0.68, 0.55, 0.62, 0.95, 1.0]
    rows = [
        ["ADF26-0042", ICON["photo"], "White A-Line Gown", "Wedding Dress", "M",
         ("active", OK), "3", "1", "1", ("2", OK), "31,200", "124,800"],
        ["ADF26-0043", ICON["photo"], "Gold Ball Gown", "Engagement", "L",
         ("active", OK), "2", "2", "0", ("2", OK), "27,500", "110,000"],
        ["ADF26-0051", ICON["photo"], "Emerald Engagement Set", "Engagement", "40",
         ("active", OK), "1", "0", "1", ("0", DANGER), "44,000", "44,000"],
        ["ADF26-0067", ICON["photo"], "Chantilly Veil", "Accessories", "One size",
         ("active", OK), "2", "0", "0", ("2", WARN), "3,800", "7,600"],
        ["ADF26-0088", ICON["photo"], "Ivory Mermaid Gown", "Wedding Dress", "S",
         ("repairing", WARN), "1", "0", "0", ("0", DANGER), "38,900", "38,900"],
        ["ADF26-0091", ICON["photo"], "Rose Nikah Abaya", "Nikah Wear", "38",
         ("active", OK), "4", "1", "2", ("2", OK), "12,400", "62,000"],
        ["ADF26-0102", ICON["photo"], "Pearl Tiara Set", "Jewellery", "One size",
         ("active", OK), "1", "0", "0", ("1", WARN), "6,900", "6,900"],
        ["ADF26-0115", ICON["photo"], "Champagne Ball Gown", "Engagement", "40",
         ("discontinued", MUTED), "0", "1", "0", ("0", MUTED), "29,700", "29,700"],
    ]
    e, y = table(cx, y, cw, cols, rows, G, row_h=42, widths=wts)
    els += e
    e, y = pagination(cx, y, cw, "1–8 of 48 SKUs · 1,284 owned units · AFN 4.82M worth", G)
    els += e

    els += note(cx, y + 10, cw,
                "Reads inventory_items joined to inventory_stock_balances (view). Lifecycle column = inventory_items.lifecycle_status "
                "(active / repairing / discontinued / disposed) — a STORED value.\nOn hand, On rent and Avg cost come from the ledger roll-up; "
                "Rsvd comes from inventory_reservations (status=active). Avail = on hand − reserved, Worth = (on hand + on rent) × avg cost (WAC).\n"
                "Availability (available / reserved / rented / out of stock) is never stored — it is derived per row at read time.",
                ACCENT, G)
    return els


def _d3(ox, oy):
    """Item detail — overview."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "3. Item detail — overview & per-warehouse stock",
                                     "Inventory", g, sub_active="Items")
    els.append(breadcrumb(cx, cy, ["Inventory", "Items", "ADF26-0042"], G))
    e, y = page_header(cx, cy + 18, cw, "White A-Line Gown",
                       actions=[("Stock in", "secondary"), ("Reserve", "secondary"),
                                ("Edit item", "primary")],
                       subtitle="SKU ADF26-0042 · Wedding Dress · A-Line · Size M · Bought 04 Feb 2026",
                       g=G)
    els += e
    e, y = tabs(cx, y, cw, ["Overview", "Stock & movement", "Reservations",
                            "Rentals", "Photos", "Audit"], 0, G)
    els += e

    # left column — photos + pricing
    LW = 340
    els += _photo(cx, y, LW, 220, G, ICON["dress"], "main photo · inventory_item_media")
    for i in range(4):
        els += _photo(cx + i * 88, y + 230, 76, 72, G, ICON["photo"])
    els += _lab(cx, y + 318, "PRICING", G)
    e, _ = money_row(cx, y + 340, LW,
                     [("Sale price", "AFN 48,000"),
                      ("Rental price / 3 days", "AFN 9,500"),
                      ("Rental deposit", "AFN 5,000"),
                      ("Late fee / day", "AFN 500"),
                      ("Turnaround buffer", "2 days")],
                     G, total=("Avg cost (WAC)", "AFN 31,200"))
    els += e

    # right column
    rx = cx + LW + 24
    RW = cw - LW - 24
    cx0 = rx
    cels, cx0 = chip(cx0, y + 4, "Available", OK, g=G)
    els += cels
    cels, cx0 = chip(cx0, y + 4, "Lifecycle: active", INFO, g=G)
    els += cels
    cels, cx0 = chip(cx0, y + 4, "Purpose: rental + sale", VIOLET, g=G)
    els += cels
    cels, cx0 = chip(cx0, y + 4, "Buffer 2 days", WARN, g=G)
    els += cels
    cels, cx0 = chip(cx0, y + 4, "Quality: high", ACCENT, g=G)
    els += cels

    els += _lab(rx, y + 44, "ATTRIBUTES — inventory_items", G)
    attrs = [("Main category", "Bridal Dresses"), ("Sub-category", "A-Line"),
             ("Item type", "Wedding Dress"), ("Model / designer", "Elegance 2026"),
             ("Size", "M"), ("Colour", "Ivory white"),
             ("Fabric", "Silk mikado + lace"), ("Season", "Spring 2026"),
             ("Purpose", "both (sale + rental)"), ("Quality", "high"),
             ("Reorder level", "1"), ("Barcode", "8901234500421")]
    colw = (RW - 24) / 3
    for i, (k, v) in enumerate(attrs):
        els += _kv(rx + (i % 3) * (colw + 12), y + 66 + (i // 3) * 38, colw, k, v, G)

    els += _lab(rx, y + 230, "STOCK BY WAREHOUSE — one SKU lives in several warehouses", G, ROSE)
    e, _ = table(rx, y + 252, RW,
                 ["Warehouse", "On hand", "On rent", "Owned", "Rsvd", "Avail", "Avg cost", "Worth"],
                 [["Main Store", "2", "1", "3", "1", ("1", OK), "31,200", "93,600"],
                  ["Shar-e-Naw Branch", "1", "0", "1", "0", ("1", OK), "31,200", "31,200"],
                  ["Repair Room", "0", "0", "0", "0", ("0", MUTED), "—", "—"],
                  [("TOTAL", INK), ("3", INK), ("1", VIOLET), ("4", INK), ("1", WARN),
                   ("2", OK), ("31,200", INK), ("AFN 124,800", ACCENT)]],
                 G, row_h=36, widths=[1.7, 0.8, 0.8, 0.8, 0.7, 0.75, 1.0, 1.15], zebra=False)
    els += e

    els += note(rx, y + 452, RW,
                "Owned 4 = on hand 3 + on rent 1 · Available 2 = on hand 3 − reserved 1 · Valuation 4 × 31,200 = AFN 124,800",
                VIOLET, G)

    els += note(cx, oy + 826, cw,
                "Reads inventory_items + inventory_item_media + inventory_stock_balances (view) grouped by warehouse. "
                "An item has NO single warehouse_id — the same SKU holds stock in many warehouses, so the breakdown table is the source of truth.\n"
                "Only lifecycle_status (active / repairing / discontinued / disposed) is stored on inventory_items. "
                "The green availability chip is DERIVED at read time from on hand, reservations, open rentals and the cleaning buffer.\n"
                "Edit item opens the drawer (screen 5) and never changes stock — quantities move only through posted documents.",
                ACCENT, G)
    return els


def _d4(ox, oy):
    """Item detail — stock & movement tab."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "4. Item detail — Stock & movement (WAC history)",
                                     "Inventory", g, sub_active="Items")
    els.append(breadcrumb(cx, cy, ["Inventory", "Items", "ADF26-0042"], G))
    e, y = page_header(cx, cy + 18, cw, "White A-Line Gown",
                       actions=[("⬇ Export ledger", "ghost"), ("Stock in", "primary")],
                       subtitle="SKU ADF26-0042 · weighted average cost per (item, warehouse)", g=G)
    els += e
    e, y = tabs(cx, y, cw, ["Overview", "Stock & movement", "Reservations",
                            "Rentals", "Photos", "Audit"], 1, G)
    els += e

    e, y = stat_row(cx, y, cw, [
        ("On hand", "3", INK, "Main 2 · Shar-e-Naw 1", ICON["warehouse"]),
        ("On rent", "1", VIOLET, "due back 15 Sep", ICON["rental"]),
        ("Owned", "4", INK, "valuation basis", ICON["inventory"]),
        ("Reserved", "1", WARN, "24–26 Sep booking", ICON["reserve"]),
        ("Available", "2", OK, "on hand − reserved", ICON["check"]),
        ("Avg cost (WAC)", "31,200", ACCENT, "AFN · Main Store", ICON["cash"]),
    ], h=88, gap=12, g=G)
    els += e

    els += _lab(cx, y, "WEIGHTED AVERAGE COST HISTORY — recomputed on every stock-in", G, ACCENT)
    e, y = table(cx, y + 22, cw,
                 ["Date", "Event", "Doc", "Qty in", "Unit cost (AFN)", "Landed", "Owned after", "New avg cost"],
                 [["04 Feb 2026", ("Opening stock", OK), "MSE26-0001", "+2", "29,000", "29,000", "2", "29,000"],
                  ["18 Apr 2026", ("Receipt vs PO", OK), "GRN26-0011", "+1", "32,000", "33,400", "3", "30,467"],
                  ["27 Jun 2026", ("Receipt vs PO", OK), "GRN26-0024", "+1", "33,100", "33,400", "4", "31,200"],
                  ["02 Aug 2026", ("Rent out (snapshot)", VIOLET), "SO26-0417", "—", "—", "—", "4", "31,200 (held)"]],
                 G, row_h=36, widths=[1.05, 1.3, 1.05, 0.7, 1.2, 0.85, 0.95, 1.2], zebra=True)
    els += e

    els += _lab(cx, y, "STOCK LEDGER — inventory_stock_transactions for this SKU", G)
    e, y = table(cx, y + 22, cw,
                 ["Date", "Txn #", "Type", "Warehouse", "Qty ±", "Unit cost", "Balance", "Reference"],
                 [["27 Jun", "TRN26-002980", ("stock_in", OK), "Main Store", ("+1", OK), "33,400", "4", "GRN26-0024 →"],
                  ["02 Aug", "TRN26-003641", ("rent_out", VIOLET), "Main Store", ("−1", DANGER), "31,200", "3", "SO26-0417 →"],
                  ["09 Aug", "TRN26-003702", ("rent_return", OK), "Main Store", ("+1", OK), "31,200", "4", "SO26-0417 →"],
                  ["12 Sep", "TRN26-004182", ("rent_out", VIOLET), "Main Store", ("−1", DANGER), "31,200", "3", "SO26-0463 →"]],
                 G, row_h=36, widths=[0.75, 1.3, 1.05, 1.2, 0.7, 0.95, 0.75, 1.3], zebra=True)
    els += e

    els += note(cx, y, cw,
                "Reads inventory_stock_transactions for this item. Types are exactly stock_in, stock_out, adjustment, transfer_in, transfer_out, rent_out, rent_return, dispose.\n"
                "Avg cost is a weighted average per (item, warehouse): recomputed on every stock-in ((old_qty×old_avg + in_qty×landed) ÷ new_qty) and SNAPSHOTTED onto every stock-out row.\n"
                "Note the rent_out / rent_return pair: on hand falls to 3 but owned stays 4, so valuation is unchanged. The 24–26 Sep reservation writes no ledger row at all.",
                ACCENT, G)
    return els


def _d5(ox, oy):
    """Add / edit item drawer."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "5. New / edit item — drawer over the items list",
                                     "Inventory", g, sub_active="Items")
    e, y = page_header(cx, cy, cw, "Items", actions=[("＋ New item", "primary")],
                       subtitle="1,284 owned units · 48 SKUs", g=G)
    els += e
    els += search_bar(cx, y, 460, "Search SKU, name, barcode…", G)
    els += filter_chips(cx, y + 52, ["All 1,284", "Available 954", "On rent 238", "Reserved 92"], 0, G)
    e, _ = table(cx, y + 94, cw, ["SKU", "Name", "Category", "Lifecycle", "On hand", "On rent", "Avail", "Worth"],
                 [["ADF26-0042", "White A-Line Gown", "Wedding Dress", "active", "3", "1", "2", "124,800"],
                  ["ADF26-0043", "Gold Ball Gown", "Engagement", "active", "2", "2", "2", "110,000"],
                  ["ADF26-0051", "Emerald Engagement Set", "Engagement", "active", "1", "0", "0", "44,000"],
                  ["ADF26-0067", "Chantilly Veil", "Accessories", "active", "2", "0", "2", "7,600"]],
                 G, row_h=42, widths=[1.1, 1.9, 1.2, 0.9, 0.75, 0.7, 0.65, 1.0])
    els += e

    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New item",
                            side="right", width=560,
                            subtitle="Creates inventory_items (+ inventory_item_media) — does NOT create stock",
                            g=G)
    els += de

    c2 = (fw - 16) / 2
    c3 = (fw - 24) / 3
    fy2 = fy
    e, fy2 = _inp(fx, fy2, fw, "Item name", "White A-Line Gown", G, True)
    els += e
    e, _ = _inp(fx, fy2, c2, "SKU (auto)", "ADF26-0042", G)
    els += e
    e, fy2 = _inp(fx + c2 + 16, fy2, c2, "Barcode", "e.g. 8901234500421", G)
    els += e
    e, _ = _sel(fx, fy2, c2, "Main category", "Bridal Dresses", G, True)
    els += e
    e, fy2 = _sel(fx + c2 + 16, fy2, c2, "Sub-category", "A-Line", G, True)
    els += e
    e, _ = _sel(fx, fy2, c2, "Item type", "Wedding Dress", G)
    els += e
    e, fy2 = _sel(fx + c2 + 16, fy2, c2, "Model / designer", "Elegance 2026", G)
    els += e
    e, _ = _inp(fx, fy2, c3, "Size", "M", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Colour", "Ivory white", G)
    els += e
    e, fy2 = _inp(fx + 2 * (c3 + 12), fy2, c3, "Fabric", "Silk mikado", G)
    els += e
    e, _ = _inp(fx, fy2, c3, "Season", "Spring 2026", G)
    els += e
    e, _ = _sel(fx + c3 + 12, fy2, c3, "Purpose", "both", G)
    els += e
    e, fy2 = _sel(fx + 2 * (c3 + 12), fy2, c3, "Quality", "high", G)
    els += e
    e, _ = _sel(fx, fy2, c3, "Lifecycle status", "active", G, True)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Reorder level", "1", G)
    els += e
    e, fy2 = _inp(fx + 2 * (c3 + 12), fy2, c3, "Buffer days", "2", G)
    els += e

    els += _lab(fx, fy2, "SALE & RENTAL PRICING — AFN", G, ROSE)
    fy2 += 22
    e, _ = _inp(fx, fy2, c3, "Sale price", "48,000", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Rental price", "9,500", G)
    els += e
    e, fy2 = _inp(fx + 2 * (c3 + 12), fy2, c3, "Rental period (days)", "3", G)
    els += e
    e, _ = _inp(fx, fy2, c3, "Deposit", "5,000", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Late fee / day", "500", G)
    els += e
    e, fy2 = _sel(fx + 2 * (c3 + 12), fy2, c3, "Currency", "AFN", G)
    els += e

    els += _lab(fx, fy2, "PHOTOS — inventory_item_media", G, ROSE)
    els += _photo(fx, fy2 + 22, fw, 68, G, ICON["photo"], "drag photos here · first photo becomes is_main")
    fy2 += 104
    els += btn(fx, fy2, 130, 40, "Cancel", "secondary", G)
    els += btn(fx + fw - 300, fy2, 140, 40, "Save & new", "secondary", G)
    els += btn(fx + fw - 150, fy2, 150, 40, "Save item", "primary", G)

    els += note(cx, oy + 800, 540,
                "Writes inventory_items (+ inventory_item_media).\nSKU auto-generated as ADF{YY}-{0000}. Stores lifecycle_status only —\n"
                "availability stays derived. Saving creates NO stock and NO\ninventory_stock_transactions row: opening quantities arrive via\n"
                "Manual stock entry (screen 8) or Receive PO (screen 9).",
                ACCENT, G)
    return els


def _d6(ox, oy):
    """Availability calendar."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "6. Availability calendar — reserved / on rent / buffer",
                                     "Inventory", g, sub_active="Reservations")
    e, y = page_header(cx, cy, cw, "Availability — White A-Line Gown",
                       actions=[("Month ▾", "secondary"), ("＋ Reserve", "primary")],
                       subtitle="ADF26-0042 · owned 4 · on hand 3 · rental buffer 2 days after every return",
                       g=G)
    els += e

    lx = cx
    cels, lx = chip(lx, y, "Free", OK, g=G)
    els += cels
    cels, lx = chip(lx, y, "Reserved", WARN, g=G)
    els += cels
    cels, lx = chip(lx, y, "On rent", ACCENT, g=G)
    els += cels
    cels, lx = chip(lx, y, "Cleaning buffer", VIOLET, g=G)
    els += cels
    cels, lx = chip(lx, y, "Conflict", DANGER, g=G)
    els += cels
    els.append(text(cx + cw - 320, y + 3, "Unit 1 of 3 on hand  ·  switch unit ▾", 12, MUTED, "right", 320, G))
    y += 34

    calw = (cw - 24) / 2
    sept = {2: ACCENT, 3: ACCENT, 4: ACCENT, 5: VIOLET, 6: VIOLET,
            12: ACCENT, 13: ACCENT, 14: ACCENT, 15: VIOLET, 16: VIOLET,
            24: DANGER, 25: DANGER, 26: DANGER, 27: VIOLET, 28: VIOLET}
    octo = {3: WARN, 4: WARN, 5: VIOLET, 6: VIOLET, 17: WARN, 18: WARN, 19: VIOLET, 20: VIOLET}
    e, _ = calendar_grid(cx, y, calw, 360, "September 2026", sept, G)
    els += e
    e, _ = calendar_grid(cx + calw + 24, y, calw, 360, "October 2026", octo, G)
    els += e
    y += 376

    els += note(cx, y, cw,
                f"{ICON['alert']}  Booking conflict 24–26 Sep — 2 active reservations against 1 available unit. Reserving again is blocked until a unit is freed or another warehouse is picked.",
                DANGER, G)
    y += 62

    e, y = table(cx, y, cw,
                 ["Res / Doc", "Customer", "From", "To", "Qty", "State", "Warehouse", "Source"],
                 [["RSV26-0311", "Zainab Haidari", "24 Sep", "26 Sep", "1", ("reserved", WARN), "Main Store", "SO26-0470 →"],
                  ["RSV26-0314", "Marwa Sadat", "24 Sep", "25 Sep", "1", ("conflict", DANGER), "Main Store", "SO26-0472 →"],
                  ["SO26-0463", "Nasrin Ahmadi", "12 Sep", "15 Sep", "1", ("on rent", ACCENT), "Main Store", "rent_out ledger →"]],
                 G, row_h=34, widths=[1.1, 1.4, 0.8, 0.8, 0.55, 1.0, 1.15, 1.4])
    els += e

    els += note(cx, y, cw,
                "Read-only view. Reads inventory_reservations (reserved bands) and inventory_stock_transactions rent_out / rent_return (on-rent bands) per unit.\n"
                "After every rent_return the unit is blocked for inventory_items.rental_buffer_days for cleaning and pressing — a DERIVED band, no row is written for it.\n"
                "A conflict is an overlap of reserved + on-rent + buffer days beyond the available qty for that warehouse. ＋ Reserve writes inventory_reservations only.",
                ACCENT, G)
    return els


def _d7(ox, oy):
    """Stock ledger."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "7. Stock ledger — immutable movement history",
                                     "Inventory", g, sub_active="Stock ledger")
    e, y = page_header(cx, cy, cw, "Stock ledger",
                       actions=[("⬇ Export CSV", "ghost"), ("Rebuild balances", "secondary")],
                       subtitle="Every quantity change in the system. Append-only — corrections are reversing rows.",
                       g=G)
    els += e
    els += search_bar(cx, y, 340, "Txn # / SKU / reference document", G)
    els += filter_chips(cx + 356, y + 5, ["All types", "Stock in", "Stock out", "Adjust",
                                          "Transfer", "Rent", "Dispose"], 0, G)
    y += 56
    e, y = table(cx, y, cw,
                 ["Txn #", "Date", "Item", "Type", "Qty", "Unit cost", "Value", "Warehouse", "Reference", ""],
                 [["TRN26-004182", "12 Sep", "White A-Line Gown", ("rent_out", VIOLET), ("−1", DANGER), "38,000", ("−38,000", DANGER), "Main Store", "SO26-000019", "View"],
                  ["TRN26-004181", "12 Sep", "Chantilly Veil", ("stock_in", OK), ("+12", OK), "1,450", ("+17,400", OK), "Main Store", "GRN26-0008", "View"],
                  ["TRN26-004179", "11 Sep", "Gold Ball Gown", ("rent_return", OK), ("+1", OK), "52,000", ("+52,000", OK), "Main Store", "SO26-000014", "View"],
                  ["TRN26-004178", "11 Sep", "Ivory Mermaid Gown", ("stock_out", DANGER), ("−1", DANGER), "44,500", ("−44,500", DANGER), "Main Store", "SO26-000017", "View"],
                  ["TRN26-004176", "11 Sep", "Pearl Tiara Set", ("transfer_out", INFO), ("−4", DANGER), "3,200", ("−12,800", DANGER), "Shar-e-Naw", "TRF26-0003", "View"],
                  ["TRN26-004175", "11 Sep", "Pearl Tiara Set", ("transfer_in", INFO), ("+4", OK), "3,200", ("+12,800", OK), "Main Store", "TRF26-0003", "View"],
                  ["TRN26-004172", "10 Sep", "Champagne Ball Gown", ("adjustment", WARN), ("−1", DANGER), "41,000", ("−41,000", DANGER), "Main Store", "ADJ26-0011", "View"],
                  ["TRN26-004170", "10 Sep", "Rose Nikah Abaya", ("dispose", DANGER), ("−1", DANGER), "18,600", ("−18,600", DANGER), "Repair Room", "DSP26-0004", "View"],
                  ["TRN26-004168", "09 Sep", "Emerald Engagement Set", ("stock_in", OK), ("+1", OK), "27,000", ("+27,000", OK), "Main Store", "MSE26-0021", "View"]],
                 G, row_h=40, widths=[1.15, 0.62, 1.6, 0.95, 0.48, 0.7, 0.78, 0.92, 1.0, 0.45])
    els += e
    e, y = pagination(cx, y, cw, "1–9 of 4,182 transactions", G)
    els += e
    els += note(cx, y + 4, cw,
                "Read-only. inventory_stock_transactions is append-only and immutable — no row is ever edited or deleted.\n"
                "Types: stock_in · stock_out · adjustment · transfer_in · transfer_out · rent_out · rent_return · dispose.  There is NO reserve / release type — reservations are not stock movements.\n"
                "unit_cost on a stock_in is the landed cost from the source document; on a stock_out it is the weighted-average cost snapshotted at posting time.",
                ACCENT, G)
    return els


def _d8(ox, oy):
    """Manual stock entry."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "8. Stock in — manual / opening entry",
                                     "Inventory", g, sub_active="Items")
    e, y = page_header(cx, cy, cw, "Manual stock entry  MSE26-0022",
                       actions=[("Cancel", "ghost"), ("Save draft", "secondary"), ("Post entry", "primary")],
                       subtitle="Opening stock or an ad-hoc stock-in with no purchase order",
                       g=G)
    els += e
    e, _ = _sel(cx, y, 260, "Entry type", "Manual in", G, True)
    els += e
    e, _ = _sel(cx + 276, y, 260, "Warehouse", "Main Store", G, True)
    els += e
    e, _ = _inp(cx + 552, y, 200, "Entry date", "12 Sep 2026", G, True)
    els += e
    e, _ = _inp(cx + 768, y, cw - 768, "Note", "Opening count — Sept stock take", G)
    els += e
    y += 92
    els += _lab(cx, y, "LINES", G)
    els.append(text(cx + cw - 120, y - 2, "＋ Add line", 12, ACCENT, "right", 120, G))
    e, y2 = table(cx, y + 22, cw,
                  ["Item", "SKU", "Qty", "Unit cost", "Currency", "Line value", "New avg cost", ""],
                  [["Chantilly Veil", "ADF26-0067", "12", "1,450.00", "AFN", "17,400.00", ("1,462.50", ACCENT), "✕"],
                   ["Pearl Tiara Set", "ADF26-0102", "6", "3,200.00", "AFN", "19,200.00", ("3,200.00", ACCENT), "✕"],
                   ["Bridal Gloves (S)", "ADF26-0121", "10", "480.00", "AFN", "4,800.00", ("492.30", ACCENT), "✕"]],
                  G, row_h=44, widths=[1.8, 1.05, 0.5, 0.85, 0.62, 0.95, 0.95, 0.32])
    els += e
    e, _ = money_row(cx + cw - 360, y2 + 8, 360,
                     [("Lines", "3"), ("Total quantity", "28"), ("Currency", "AFN @ 1.000000")],
                     G, total=("Total entry value", "AFN 41,400.00"))
    els += e
    els += note(cx, y2 + 150, cw - 380,
                "Draft writes inventory_stock_entries + inventory_stock_entry_items only — no stock moves yet.\n"
                "POST writes one inventory_stock_transactions row per line (type=stock_in, reference_type=inventory_stock_entry)\n"
                "and recomputes the weighted average cost in inventory_stock_balances:\n"
                "   new_avg = (on_hand × avg + qty_in × unit_cost) / (on_hand + qty_in)\n"
                "The 'New avg cost' column previews that result before you commit. After posting the entry is immutable — correct it by Void.",
                ACCENT, G)
    return els


def _d9(ox, oy):
    """Receive against PO (GRN)."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "9. Stock in — receive against PO (GRN)",
                                     "Inventory", g, sub_active="Items")
    e, y = page_header(cx, cy, cw, "Receive goods  GRN26-0009",
                       actions=[("Cancel", "ghost"), ("Save draft", "secondary"), ("Post receipt", "primary")],
                       subtitle="PO26-000012 · Istanbul Bridal Co. · ordered 02 Sep 2026",
                       g=G)
    els += e
    e, _ = _sel(cx, y, 300, "Purchase order", "PO26-000012 — Istanbul Bridal Co.", G, True)
    els += e
    e, _ = _sel(cx + 316, y, 260, "Receive into warehouse", "Main Store", G, True)
    els += e
    e, _ = _inp(cx + 592, y, 200, "Received date", "12 Sep 2026", G, True)
    els += e
    e, _ = _inp(cx + 808, y, 240, "Currency / rate", "USD @ 70.500000", G)
    els += e
    e, _ = _inp(cx + 1064, y, cw - 1064, "Header other cost", "USD 300.00", G)
    els += e
    y += 92
    e, y2 = table(cx, y, cw,
                  ["Line", "Ordered", "Received", "Receiving now", "Unit cost", "Allocated other", "Landed unit cost", "Line value"],
                  [["White A-Line Gown  ADF26-0042", "4", "0", ("4", ACCENT), "480.00", "162.00", ("520.50", ACCENT), "2,082.00"],
                   ["Chantilly Veil  ADF26-0067", "20", "8", ("12", ACCENT), "18.00", "48.60", ("22.05", ACCENT), "264.60"],
                   [("Blush Tulle Gown  — new item —", VIOLET), "2", "0", ("2", ACCENT), "390.00", "65.80", ("422.90", ACCENT), "845.80"],
                   ["Pearl Tiara Set  ADF26-0102", "10", "10", ("0", MUTED), "42.00", "23.60", ("—", MUTED), "0.00"]],
                  G, row_h=46, widths=[2.3, 0.62, 0.68, 0.85, 0.78, 0.92, 1.0, 0.8])
    els += e
    els += note(cx, y2 + 6, cw * 0.58,
                "Landed cost (ADR-009): header other_cost is allocated to lines PRO-RATA BY LINE VALUE.\n"
                "   allocated_i = 300.00 × (line_value_i / Σ line_value)\n"
                "   landed_unit_cost = unit_cost + (allocated + line_other) / qty_received\n"
                "Only landed_unit_cost reaches inventory — never the raw unit cost.",
                VIOLET, G)
    els += note(cx + cw * 0.60, y2 + 6, cw * 0.40,
                "Line 3 is free text with no SKU. On POST the system creates the\n"
                "inventory_items row, generates SKU ADF26-0131 from platform_sequences,\n"
                "and writes the new id back onto the PO line and this receipt line.",
                WARN, G)
    e, _ = money_row(cx + cw - 380, y2 + 150, 380,
                     [("Goods value", "USD 3,192.40"), ("Other cost allocated", "USD 300.00"),
                      ("Exchange rate", "70.500000")],
                     G, total=("Total landed (AFN)", "AFN 246,404.20"))
    els += e
    els += note(cx, y2 + 152, cw * 0.58,
                "POST, in one DB transaction: create items for free-text lines → allocate other cost → insert stock_in at landed_unit_cost →\n"
                "recompute WAC in inventory_stock_balances → open/increase finance_payables → recompute PO quantity_received + status.\n"
                "Over-receipt is blocked unless over_receipt_approved_by is set. Posted receipts are immutable — correct by Void.",
                ACCENT, G)
    return els


def _d10(ox, oy):
    """Adjustment."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "10. Stock adjustment — count correction",
                                     "Inventory", g, sub_active="Items")
    e, y = page_header(cx, cy, cw, "Stock adjustment  ADJ26-0012",
                       actions=[("Cancel", "ghost"), ("Save draft", "secondary"), ("Post adjustment", "primary")],
                       subtitle="Correct on-hand quantity after a physical count. Not the same as Dispose.",
                       g=G)
    els += e
    e, _ = _sel(cx, y, 260, "Warehouse", "Main Store", G, True)
    els += e
    e, _ = _sel(cx + 276, y, 260, "Reason", "Count mismatch", G, True)
    els += e
    e, _ = _inp(cx + 552, y, 200, "Date", "12 Sep 2026", G, True)
    els += e
    e, _ = _inp(cx + 768, y, cw - 768, "Note", "Quarterly count — aisle 3", G)
    els += e
    y += 92
    e, y2 = table(cx, y, cw,
                  ["Item", "SKU", "Expected", "Counted", "Difference", "Unit cost", "Value impact", ""],
                  [["Chantilly Veil", "ADF26-0067", "14", "12", ("−2", DANGER), "1,462.50", ("−2,925.00", DANGER), "✕"],
                   ["Bridal Gloves (S)", "ADF26-0121", "10", "13", ("+3", OK), "492.30", ("+1,476.90", OK), "✕"],
                   ["Pearl Tiara Set", "ADF26-0102", "6", "6", ("0", MUTED), "3,200.00", ("0.00", MUTED), "✕"]],
                  G, row_h=44, widths=[1.9, 1.1, 0.75, 0.75, 0.85, 0.9, 1.0, 0.35])
    els += e
    els += _lab(cx, y2 + 12, "ATTACHMENTS", G)
    for i in range(3):
        els += _photo(cx + i * 116, y2 + 34, 104, 78, G, ICON["photo"], "count sheet" if i == 0 else None)
    els.append(text(cx + 356, y2 + 66, "＋ Add photo", 12, ACCENT, g=G))
    e, _ = money_row(cx + cw - 360, y2 + 20, 360,
                     [("Lines", "3"), ("Net quantity change", ("+1", OK))],
                     G, total=("Net value impact", ("AFN −1,448.10", DANGER)))
    els += e
    els += note(cx, y2 + 134, cw,
                "POST writes one inventory_stock_transactions row per NON-ZERO line (type=adjustment, signed quantity, reference_type=inventory_adjustment) at the current weighted-average cost.\n"
                "Expected quantity is pre-filled from inventory_stock_balances.on_hand_qty at the moment the draft was opened. Photos go to platform_attachments (many per document).\n"
                "Adjustment corrects a counting error. Dispose (next screen) is a deliberate write-off of goods that still physically existed — the two must not be confused in reports.",
                ACCENT, G)
    return els


def _d11(ox, oy):
    """Dispose."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "11. Dispose — permanent write-off",
                                     "Inventory", g, sub_active="Items")
    e, y = page_header(cx, cy, cw, "Dispose stock  DSP26-0005",
                       actions=[("Cancel", "ghost"), ("Save draft", "secondary"), ("Post disposal", "danger")],
                       subtitle="Remove goods from stock permanently and book the loss",
                       g=G)
    els += e
    e, _ = _sel(cx, y, 260, "Warehouse", "Repair Room", G, True)
    els += e
    e, _ = _sel(cx + 276, y, 260, "Reason", "Damaged beyond repair", G, True)
    els += e
    e, _ = _inp(cx + 552, y, 200, "Date", "12 Sep 2026", G, True)
    els += e
    e, _ = _inp(cx + 768, y, cw - 768, "Note", "Torn bodice after rental SO26-000009 — not repairable", G)
    els += e
    y += 92
    e, y2 = table(cx, y, cw,
                  ["Item", "SKU", "Owned", "Dispose qty", "Avg unit cost", "Write-off value", "Lifecycle after", ""],
                  [["Rose Nikah Abaya", "ADF26-0091", "1", ("1", DANGER), "18,600.00", ("18,600.00", DANGER), ("disposed", DANGER), "✕"],
                   ["Ivory Hair Comb", "ADF26-0128", "5", ("2", DANGER), "640.00", ("1,280.00", DANGER), ("active", MUTED), "✕"]],
                  G, row_h=46, widths=[1.9, 1.1, 0.7, 0.85, 1.0, 1.05, 1.0, 0.35])
    els += e
    e, _ = money_row(cx + cw - 360, y2 + 16, 360,
                     [("Units disposed", "3"), ("Reason", "Damaged")],
                     G, total=("Total write-off", ("AFN 19,880.00", DANGER)))
    els += e
    els += note(cx, y2 + 16, cw * 0.62,
                "POST writes inventory_stock_transactions (type=dispose, NEGATIVE quantity) at the weighted-average cost, reference_type=inventory_disposal.\n"
                "For a serialised dress whose owned_qty reaches 0, inventory_items.lifecycle_status becomes 'disposed'.\n"
                "The write-off reduces stock worth immediately. It is NOT a COGS entry — nothing was sold — it appears in the Disposal report and reduces inventory value.\n"
                "A disposal raised from a rental loss is created by sales_rental_claims and links back here.",
                DANGER, G)
    return els


def _d12(ox, oy):
    """Transfer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "12. Transfer between warehouses",
                                     "Inventory", g, sub_active="Transfers")
    e, y = page_header(cx, cy, cw, "Transfer  TRF26-0004",
                       actions=[("Cancel", "ghost"), ("Save draft", "secondary"), ("Send", "primary")],
                       subtitle="Move stock between warehouses or branches. Cost travels with the goods.",
                       g=G)
    els += e
    e, y2 = timeline(cx, y, cw * 0.72,
                     [("Draft", "done"), ("In transit", "current"), ("Received", "todo")], G)
    els += e
    e, _ = _sel(cx, y2 + 10, 300, "From branch / warehouse", "Main branch · Main Store", G, True)
    els += e
    els.append(text(cx + 314, y2 + 44, "→", 18, MUTED, g=G))
    e, _ = _sel(cx + 340, y2 + 10, 300, "To branch / warehouse", "Shar-e-Naw · Floor 2", G, True)
    els += e
    e, _ = _inp(cx + 656, y2 + 10, 200, "Sent date", "12 Sep 2026", G)
    els += e
    e, _ = _inp(cx + 872, y2 + 10, cw - 872, "Note", "Event weekend stock", G)
    els += e
    y3 = y2 + 88
    e, y4 = table(cx, y3, cw,
                  ["Item", "SKU", "Available at source", "Send qty", "Unit cost", "Value", "Received", ""],
                  [["Pearl Tiara Set", "ADF26-0102", "6", ("4", ACCENT), "3,200.00", "12,800.00", ("—", MUTED), "✕"],
                   ["Chantilly Veil", "ADF26-0067", "12", ("5", ACCENT), "1,462.50", "7,312.50", ("—", MUTED), "✕"],
                   ["Gold Ball Gown", "ADF26-0043", "1", ("1", ACCENT), "52,000.00", "52,000.00", ("—", MUTED), "✕"]],
                  G, row_h=44, widths=[1.8, 1.05, 1.15, 0.75, 0.9, 0.95, 0.8, 0.32])
    els += e
    e, _ = money_row(cx + cw - 360, y4 + 8, 360,
                     [("Lines", "3"), ("Units in transit", "10")],
                     G, total=("Value in transit", "AFN 72,112.50"))
    els += e
    els += note(cx, y4 + 8, cw * 0.62,
                "Send  → inventory_stock_transactions type=transfer_out (negative) at the SOURCE warehouse's weighted-average cost.\n"
                "Receive → type=transfer_in (positive) at that SAME unit cost, so an internal move never creates or destroys value.\n"
                "Partial receive is supported via inventory_transfer_items.received_quantity. Goods in transit are shown separately from on-hand and are still Owned for valuation.",
                ACCENT, G)
    return els


def _d13(ox, oy):
    """Reservations + conflict."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "13. Reservations — bookings & conflict guard",
                                     "Inventory", g, sub_active="Reservations")
    e, y = page_header(cx, cy, cw, "Reservations",
                       actions=[("Calendar view", "secondary"), ("＋ Reserve", "primary")],
                       subtitle="Reserved quantity comes from here — never from the stock ledger",
                       g=G)
    els += e
    els += search_bar(cx, y, 340, "SKU / customer / order #", G)
    els += filter_chips(cx + 356, y + 5, ["Active", "Fulfilled", "Released", "Cancelled"], 0, G)
    y += 56
    e, y2 = table(cx, y, cw,
                  ["Reservation", "Item", "Qty", "From", "To", "Buffer", "Blocked until", "Order", "Customer", "Status"],
                  [["RSV26-0041", "White A-Line Gown", "1", "19 Sep", "21 Sep", "2 d", ("23 Sep", VIOLET), "SO26-000019", "Sara Ahmadi", ("active", OK)],
                   ["RSV26-0040", "Gold Ball Gown", "1", "24 Sep", "26 Sep", "2 d", ("28 Sep", VIOLET), "SO26-000021", "Maryam Noori", ("active", OK)],
                   ["RSV26-0038", "Champagne Ball Gown", "1", "01 Oct", "03 Oct", "2 d", ("05 Oct", VIOLET), "—", "Fatima Rahimi", ("active", OK)],
                   ["RSV26-0035", "Emerald Engagement Set", "1", "05 Sep", "07 Sep", "2 d", "09 Sep", "SO26-000014", "Zainab Karimi", ("fulfilled", MUTED)],
                   ["RSV26-0031", "Ivory Mermaid Gown", "1", "28 Aug", "30 Aug", "2 d", "01 Sep", "SO26-000009", "Nargis Amini", ("released", MUTED)]],
                  G, row_h=42, widths=[1.05, 1.65, 0.42, 0.6, 0.6, 0.5, 0.85, 1.05, 1.0, 0.72])
    els += e
    els += modal(cx, cy - 20, cw, ch,
                 "⚠  Dress already booked for these dates",
                 "White A-Line Gown (ADF26-0042) is reserved 19–21 Sep for SO26-000019,\n"
                 "and blocked until 23 Sep for the 2-day cleaning buffer.\n"
                 "Only 1 unit is owned, so it cannot be booked again for 22 Sep.\n\n"
                 "Available alternatives for 22 Sep:\n"
                 "   • Ivory Mermaid Gown  ADF26-0088  size S\n"
                 "   • Champagne Ball Gown  ADF26-0115  size 40",
                 w=560, h=300,
                 actions=[("Choose another date", "secondary"), ("Pick alternative", "primary")], g=G)
    els += note(cx, oy + 812, cw,
                "Reservations write ONLY to inventory_reservations — they never touch inventory_stock_transactions. reserved_qty on the balance is the sum of active reservations.\n"
                "Double-booking is prevented BY THE DATABASE (ADR-010), not by application code:  EXCLUDE USING gist (inventory_item_id WITH =, daterange(reserved_from, blocked_until, '[]') WITH &&) WHERE status='active'.\n"
                "blocked_until = reserved_to + buffer_days, so the cleaning turnaround is inside the guarded range. Two staff booking the same gown concurrently — the second insert is rejected by Postgres.",
                DANGER, G)
    return els


def _d14(ox, oy):
    """Valuation report."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "14. Valuation report — what is my stock worth?",
                                     "Inventory", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Inventory valuation",
                       actions=[("🖨 Print", "ghost"), ("⬇ Export CSV", "secondary")],
                       subtitle="Owned quantity × weighted average cost, in AFN",
                       g=G)
    els += e
    e, _ = _inp(cx, y, 190, "As of date", "12 Sep 2026", G)
    els += e
    e, _ = _sel(cx + 206, y, 190, "Branch", "All branches", G)
    els += e
    e, _ = _sel(cx + 412, y, 190, "Warehouse", "All warehouses", G)
    els += e
    e, _ = _sel(cx + 618, y, 190, "Category", "All categories", G)
    els += e
    e, _ = _sel(cx + 824, y, 190, "Group by", "Category", G)
    els += e
    els += btn(cx + 1030, y + 18, 110, 38, "Run", "primary", G)
    y += 92
    e, y = stat_row(cx, y, cw, [
        ("Total stock worth", "AFN 4,821,340", ACCENT, "owned × avg cost", ICON["cash"]),
        ("Owned units", "1,284", INK, "on hand + on rent", ICON["inventory"]),
        ("On-hand value", "AFN 3,918,220", INK, "1,046 units", ICON["warehouse"]),
        ("On-rent value", "AFN 903,120", VIOLET, "238 units — still an asset", ICON["rental"]),
    ], h=88, gap=14, g=G)
    els += e
    e, y2 = table(cx, y, cw,
                  ["SKU", "Item", "Category", "On hand", "On rent", "Owned", "Rsvd", "Avail", "Avg cost", "Stock worth"],
                  [["ADF26-0042", "White A-Line Gown", "Wedding Dress", "0", ("1", VIOLET), "1", "1", ("0", DANGER), "38,000.00", "38,000.00"],
                   ["ADF26-0043", "Gold Ball Gown", "Engagement", "1", "0", "1", "1", ("0", DANGER), "52,000.00", "52,000.00"],
                   ["ADF26-0067", "Chantilly Veil", "Accessories", "12", "0", "12", "0", ("12", OK), "1,462.50", "17,550.00"],
                   ["ADF26-0088", "Ivory Mermaid Gown", "Wedding Dress", "1", "0", "1", "0", ("1", OK), "44,500.00", "44,500.00"],
                   ["ADF26-0102", "Pearl Tiara Set", "Jewellery", "6", "0", "6", "0", ("6", OK), "3,200.00", "19,200.00"],
                   ["ADF26-0115", "Champagne Ball Gown", "Engagement", "0", ("1", VIOLET), "1", "1", ("0", DANGER), "41,000.00", "41,000.00"],
                   [("TOTALS — 284 items", INK), "", "", ("1,046", INK), ("238", VIOLET), ("1,284", INK), ("92", WARN), ("954", OK), "", ("AFN 4,821,340", ACCENT)]],
                  G, row_h=40, widths=[1.0, 1.75, 1.05, 0.62, 0.62, 0.6, 0.5, 0.55, 0.85, 1.05])
    els += e
    els += note(cx, y2 + 6, cw,
                "Stock worth = Σ(owned_qty × avg_cost) where owned = on_hand + on_rent. The four gowns currently at weddings are still owned and still valued — this is the v1 bug that made\n"
                "total worth collapse every busy weekend. Available (on_hand − reserved) is what can be sold or booked today and is deliberately a different number.\n"
                "'As of' a past date replays inventory_stock_transactions WHERE business_date <= :as_of rather than reading today's balances, so a historical valuation reproduces exactly what the hub showed that day.",
                ACCENT, G)
    return els


def _d15(ox, oy):
    """Stock movement / stock-in by source report."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "15. Stock movement & stock-in by source",
                                     "Inventory", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Stock movement",
                       actions=[("🖨 Print", "ghost"), ("⬇ Export CSV", "secondary")],
                       subtitle="01 Sep – 12 Sep 2026 · all warehouses",
                       g=G)
    els += e
    els += filter_chips(cx, y, ["Movement summary", "Stock-in by source", "Stock-out by reason"], 1, G)
    y += 50
    e, y = stat_row(cx, y, cw, [
        ("Stock in", "+312 units", OK, "AFN 684,200", ICON["money_in"]),
        ("Stock out", "−188 units", DANGER, "AFN 402,850", ICON["money_out"]),
        ("Net change", "+124 units", ACCENT, "AFN +281,350", ICON["chart"]),
        ("Closing owned", "1,284 units", INK, "AFN 4,821,340", ICON["inventory"]),
    ], h=88, gap=14, g=G)
    els += e
    LW = 560
    e, _ = bar_chart(cx, y, LW, 250, "Stock-in value by source (AFN)",
                     [("Receipt", 0.92, "512k"), ("Manual", 0.28, "98k"),
                      ("Sale return", 0.09, "31k"), ("Transfer in", 0.12, "43k")], G, OK)
    els += e
    e, y2 = table(cx + LW + 24, y, cw - LW - 24,
                  ["Source", "Documents", "Units in", "Value in", "Share"],
                  [[("Purchase receipt (GRN)", OK), "9", "241", "AFN 512,400", "74.9%"],
                   [("Manual entry", OK), "4", "42", "AFN 98,300", "14.4%"],
                   [("Transfer in", INFO), "3", "19", "AFN 42,900", "6.3%"],
                   [("Sale return restock", OK), "2", "10", "AFN 30,600", "4.5%"],
                   [("TOTAL STOCK IN", INK), "18", ("312", OK), ("AFN 684,200", OK), "100%"]],
                  G, row_h=44, widths=[1.6, 0.8, 0.7, 1.0, 0.6])
    els += e
    els += note(cx + LW + 24, y2 + 6, cw - LW - 24,
                "RECONCILIATION\nΣ stock-in  AFN 684,200\n−  Σ stock-out  AFN 402,850\n=  net change  AFN 281,350  ✓ matches the\n   inventory balance movement for the period.",
                ACCENT, G)
    els += note(cx, y + 268, LW,
                "This is the report that ties procurement to inventory: every unit that entered the building,\n"
                "grouped by the document that brought it in, with a deep link to that document.\n"
                "Reads inventory_stock_transactions grouped by reference_type for the period.",
                ACCENT, G)
    return els


def _d16(ox, oy):
    """Rental utilisation & asset ROI."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "16. Rental utilisation & asset ROI",
                                     "Inventory", g, sub_active="Reports")
    e, y = page_header(cx, cy, cw, "Rental utilisation & asset ROI",
                       actions=[("🖨 Print", "ghost"), ("⬇ Export CSV", "secondary")],
                       subtitle="Has each dress paid for itself? · since acquisition · AFN",
                       g=G)
    els += e
    e, _ = _sel(cx, y, 210, "Category", "All categories", G)
    els += e
    e, _ = _sel(cx + 226, y, 210, "Acquired", "All time", G)
    els += e
    e, _ = _sel(cx + 452, y, 210, "Sort by", "ROI % (high → low)", G)
    els += e
    els += filter_chips(cx + 678, y + 18, ["All", "Paid back", "In progress", "Idle"], 0, G)
    y += 92
    e, y = stat_row(cx, y, cw, [
        ("Rental fleet", "148 dresses", INK, "AFN 3.94M acquired", ICON["dress"]),
        ("Revenue to date", "AFN 5,212,000", OK, "1,884 rentals", ICON["cash"]),
        ("Fleet ROI", "132%", ACCENT, "revenue ÷ acquisition", ICON["chart"]),
        ("Paid back", "94 of 148", OK, "63% of fleet", ICON["check"]),
        ("Idle 90+ days", "17 dresses", DANGER, "AFN 486,000 tied up", ICON["alert"]),
    ], h=88, gap=14, g=G)
    els += e
    e, y2 = table(cx, y, cw,
                  ["SKU", "Dress", "Acquired", "Cost", "Times rented", "Revenue", "Amortised", "ROI %", "Idle days", "Payback"],
                  [["ADF26-0043", "Gold Ball Gown", "Jan 26", "52,000", "31", "108,500", "52,000", ("209%", OK), "4", ("✓ paid back", OK)],
                   ["ADF26-0042", "White A-Line Gown", "Feb 26", "38,000", "24", "72,000", "38,000", ("189%", OK), "2", ("✓ paid back", OK)],
                   ["ADF26-0115", "Champagne Ball Gown", "Mar 26", "41,000", "12", "30,000", "24,600", ("73%", WARN), "11", ("60% — in progress", WARN)],
                   ["ADF26-0088", "Ivory Mermaid Gown", "Jun 26", "44,500", "6", "15,000", "13,350", ("34%", WARN), "23", ("30% — in progress", WARN)],
                   ["ADF26-0051", "Emerald Engagement Set", "Jul 26", "27,000", "2", "4,800", "2,700", ("18%", DANGER), "61", ("10% — slow", DANGER)],
                   ["ADF26-0126", "Sapphire Gown", "Aug 26", "39,000", "0", "0", "0", ("0%", DANGER), ("112", DANGER), ("never rented", DANGER)]],
                  G, row_h=42, widths=[0.95, 1.7, 0.7, 0.72, 0.85, 0.85, 0.85, 0.6, 0.65, 1.15])
    els += e
    els += note(cx, y2 + 6, cw,
                "The key inventory decision for a rental business: which dresses earn their purchase price back, and how fast.\n"
                "ROI % = rental_revenue_to_date ÷ acquisition_cost.   Payback % = amortised_cost_to_date ÷ acquisition_cost — driven by the per-use amortisation in ADR-002:\n"
                "   rental_cogs_per_use = acquisition_cost ÷ expected_rental_uses   (default 20, overridable per item), accumulated until it reaches acquisition_cost.\n"
                "Once a dress is fully amortised it has paid for itself and further rentals carry ZERO COGS — which is correct, and is why 'paid back' rows show pure margin from then on.\n"
                "Idle rows are capital doing nothing: 17 dresses worth AFN 486,000 have not left the rack in 90 days. Reads inventory_items + sales_order_items + finance_cogs_entries.",
                ACCENT, G)
    return els


# ══════════════════════════════════════════════════════════════════
#  MOBILE
# ══════════════════════════════════════════════════════════════════

def _m1(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "1. Inventory hub", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Inventory", right=ICON["search"], g=G)
    els += e
    els.append(rect(cx, y, cw, 96, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 16, y + 14, "TOTAL STOCK WORTH", 10, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 34, "AFN 4.82M", 28, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 70, "1,284 owned = 1,046 on hand + 238 on rent", 10.5, ACCENT, width=cw - 32, g=G))
    y += 112
    cells = [("On hand", "1,046", INK), ("On rent", "238", VIOLET),
             ("Reserved", "92", WARN), ("Available", "954", OK)]
    for i, (lab, val, col) in enumerate(cells):
        bx = cx + (i % 2) * (cw / 2 + 4)
        by = y + (i // 2) * 70
        els += kpi_card(bx, by, cw / 2 - 4, 62, lab, val, col, g=G)
    y += 152
    els.append(text(cx, y, "QUICK ACTIONS", 10, MUTED, width=cw, g=G))
    y += 18
    for i, (ic, lb) in enumerate([(ICON["inventory"], "Stock in"), (ICON["truck"], "Receive"),
                                  (ICON["adjust"], "Adjust"), (ICON["dispose"], "Dispose"),
                                  (ICON["transfer"], "Transfer"), (ICON["reserve"], "Reserve")]):
        bx = cx + (i % 3) * (cw / 3 + 2)
        by = y + (i // 3) * 74
        els += _tile(bx, by, cw / 3 - 4, 66, ic, lb, G)
    y += 162
    els.append(rect(cx, y, cw, 76, strokeColor=DANGER, backgroundColor=DANGER_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 14, y + 12, f"{ICON['alert']}  11 items below reorder level", 12, DANGER, width=cw - 28, g=G))
    els.append(text(cx + 14, y + 34, "Chantilly Veil · 2 left (reorder 10)\nPearl Tiara Set · 1 left (reorder 6)", 10.5, DANGER, width=cw - 28, g=G))
    return els


def _m2(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "2. Items list", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Items", right=ICON["filter"], g=G)
    els += e
    els += search_bar(cx, y, cw, "Name, SKU or barcode", G)
    y += 50
    els += filter_chips(cx, y, ["All", "Available", "On rent"], 0, G)
    y += 44
    rows = [(["White A-Line Gown", "ADF26-0042 · size M", "Rent 6,500 / 3d · avail 0"], ("on rent", VIOLET)),
            (["Gold Ball Gown", "ADF26-0043 · size L", "Rent 8,000 / 3d · avail 0"], ("reserved", WARN)),
            (["Chantilly Veil", "ADF26-0067 · one size", "Sale 2,400 · avail 12"], ("available", OK)),
            (["Ivory Mermaid Gown", "ADF26-0088 · size S", "Rent 7,200 / 3d · avail 1"], ("available", OK)),
            (["Rose Nikah Abaya", "ADF26-0091 · size 38", "Repair — torn bodice"], ("repairing", DANGER))]
    for lines, badge in rows:
        e, y = list_card(cx, y, cw, lines, G, h=76, thumb=True, badge=badge)
        els += e
    els += fab(cx + cw, cy + ch - 130, "＋ New item", G)
    return els


def _m3(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "3. Item detail", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "White A-Line", left=ICON["back"], right="⋯", g=G)
    els += e
    els += _photo(cx, y, cw, 150, G, ICON["dress"], "1 of 4 photos")
    y += 162
    ch_, xx = chip(cx, y, "on rent", VIOLET, g=G); els += ch_
    ch_, xx = chip(xx, y, "active", OK, g=G); els += ch_
    ch_, _ = chip(xx, y, "rental", ACCENT, g=G); els += ch_
    y += 32
    els.append(text(cx, y, "ADF26-0042 · size M · white · lace", 11.5, MUTED, width=cw, g=G))
    y += 26
    els.append(rect(cx, y, cw, 84, strokeColor=HAIRLINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=G))
    for i, (lab, val, col) in enumerate([("On hand", "0", INK), ("On rent", "1", VIOLET),
                                         ("Owned", "1", INK), ("Available", "0", DANGER)]):
        els += _kv(cx + 14 + i * ((cw - 28) / 4), y + 14, (cw - 28) / 4, lab, val, G, col)
    els.append(text(cx + 14, y + 60, "Avg cost 38,000 · worth AFN 38,000", 10.5, MUTED, width=cw - 28, g=G))
    y += 98
    els.append(text(cx, y, "STOCK BY WAREHOUSE", 10, MUTED, width=cw, g=G))
    e, y = table(cx, y + 16, cw, ["Warehouse", "Hand", "Rent", "Avail"],
                 [["Main Store", "0", ("1", VIOLET), ("0", DANGER)],
                  ["Shar-e-Naw", "0", "0", "0"]], G, row_h=34, widths=[1.6, 0.6, 0.6, 0.6])
    els += e
    els += btn(cx, y, cw / 2 - 4, 42, "Reserve", "primary", G)
    els += btn(cx + cw / 2 + 4, y, cw / 2 - 4, 42, "Calendar", "secondary", G)
    return els


def _m4(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "4. Add item (sheet)", g, "Inventory", show_nav=False)
    els.append(rect(ox + 1, oy + TITLE_H + 150, PHONE_W - 2, PHONE_H - 150, strokeColor=LINE,
                    backgroundColor=BG, strokeWidth=2, groupIds=G))
    sy = oy + TITLE_H + 168
    els.append(text(cx, sy, "New item", 19, INK, width=cw - 40, g=G))
    els.append(text(cx + cw - 20, sy + 2, ICON["cross"], 15, MUTED, g=G))
    y = sy + 36
    for lab, val, req in [("Name", "White A-Line Gown", True), ("SKU (auto)", "ADF26-0131", False),
                          ("Category", "Wedding Dress", True), ("Size / colour", "M / White", False),
                          ("Purpose", "Both — sale & rental", True), ("Sale price", "AFN 96,000", False),
                          ("Rental price / days", "AFN 6,500 / 3", False)]:
        e, y = _inp(cx, y, cw, lab, val, G, req, 34)
        els += e
    els += btn(cx, y + 4, cw, 44, "Save item", "primary", G)
    return els


def _m5(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "5. Availability calendar", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Availability", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y, "White A-Line Gown · ADF26-0042 · 1 owned", 11, MUTED, width=cw, g=G))
    y += 24
    e, y = calendar_grid(cx, y, cw, 240, "September 2026",
                         {19: WARN, 20: WARN, 21: WARN, 22: VIOLET, 23: VIOLET,
                          24: DANGER, 25: DANGER, 26: DANGER}, G)
    els += e
    for lab, col, txt in [("Reserved", WARN, "booked for a customer"),
                          ("Cleaning buffer", VIOLET, "2 days after return"),
                          ("On rent", DANGER, "with the customer now"),
                          ("Free", MUTED, "bookable")]:
        els.append(rect(cx, y, 14, 14, strokeColor=col, backgroundColor=
                        {WARN: WARN_BG, VIOLET: VIOLET_BG, DANGER: DANGER_BG}.get(col, BG),
                        strokeWidth=1, groupIds=G))
        els.append(text(cx + 22, y, f"{lab} — {txt}", 11, MUTED, width=cw - 30, g=G))
        y += 22
    els += btn(cx, y + 8, cw, 44, "＋ Reserve these dates", "primary", G)
    return els


def _m6(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "6. Manual stock entry", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Stock entry", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y, "MSE26-0022 · draft", 11, MUTED, width=cw, g=G))
    y += 24
    e, y = _sel(cx, y, cw, "Warehouse", "Main Store", G, True, 34)
    els += e
    e, y = _sel(cx, y, cw, "Entry type", "Manual in", G, True, 34)
    els += e
    els.append(text(cx, y, "LINES", 10, MUTED, width=cw, g=G))
    els.append(text(cx + cw - 70, y, "＋ Add", 11, ACCENT, "right", 70, G))
    y += 18
    for nm, q, c in [("Chantilly Veil", "12", "1,450"), ("Pearl Tiara Set", "6", "3,200"),
                     ("Bridal Gloves (S)", "10", "480")]:
        e, y = list_card(cx, y, cw, [nm, f"qty {q} × AFN {c}"], G, h=54)
        els += e
    els.append(rect(cx, y, cw, 56, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=G))
    els.append(text(cx + 14, y + 10, "Total entry value", 11, MUTED, width=cw - 28, g=G))
    els.append(text(cx + 14, y + 28, "AFN 41,400.00", 18, ACCENT, width=cw - 28, g=G))
    els += btn(cx, y + 68, cw, 44, "Post entry", "primary", G)
    return els


def _m7(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "7. Receive PO (GRN)", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Receive", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y, "GRN26-0009 · PO26-000012\nIstanbul Bridal Co. · USD @ 70.50", 11, MUTED, width=cw, g=G))
    y += 40
    for nm, ordd, now, landed in [("White A-Line Gown", "4", "4", "520.50"),
                                  ("Chantilly Veil", "20", "12", "22.05"),
                                  ("Blush Tulle Gown (new)", "2", "2", "422.90")]:
        e, y = list_card(cx, y, cw, [nm, f"ordered {ordd} · receiving {now}",
                                     (f"landed unit cost USD {landed}", ACCENT, 11)], G, h=70)
        els += e
    els += note(cx, y, cw, "Header other cost USD 300\nallocated pro-rata by line value.\nOnly landed cost reaches inventory.", VIOLET, G)
    y += 80
    els.append(rect(cx, y, cw, 56, strokeColor=HAIRLINE, backgroundColor=SOFT, strokeWidth=1, groupIds=G))
    els.append(text(cx + 14, y + 10, "Total landed", 11, MUTED, width=cw - 28, g=G))
    els.append(text(cx + 14, y + 28, "AFN 246,404.20", 17, ACCENT, width=cw - 28, g=G))
    els += btn(cx, y + 66, cw, 44, "Post receipt", "primary", G)
    return els


def _m8(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "8. Adjust / Dispose", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Adjust stock", left=ICON["back"], g=G)
    els += e
    els += filter_chips(cx, y, ["Adjustment", "Dispose"], 0, G)
    y += 44
    e, y = _sel(cx, y, cw, "Warehouse", "Main Store", G, True, 34)
    els += e
    e, y = _sel(cx, y, cw, "Reason", "Count mismatch", G, True, 34)
    els += e
    els.append(text(cx, y, "LINES", 10, MUTED, width=cw, g=G))
    y += 18
    for nm, exp, cnt, diff, col in [("Chantilly Veil", "14", "12", "−2", DANGER),
                                    ("Bridal Gloves (S)", "10", "13", "+3", OK)]:
        els.append(rect(cx, y, cw, 62, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, nm, 13, INK, width=cw - 28, g=G))
        els.append(text(cx + 14, y + 32, f"expected {exp} · counted {cnt}", 11, MUTED, width=cw - 100, g=G))
        els.append(text(cx + cw - 60, y + 26, diff, 17, col, "right", 48, G))
        y += 72
    els.append(text(cx, y, f"{ICON['photo']}  ＋ Attach count sheet photo", 12, ACCENT, width=cw, g=G))
    els += btn(cx, y + 28, cw, 44, "Post adjustment", "primary", G)
    return els


def _m9(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "9. Stock ledger", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Stock ledger", right=ICON["filter"], g=G)
    els += e
    els += filter_chips(cx, y, ["All", "In", "Out", "Rent"], 0, G)
    y += 44
    rows = [("TRN26-004182", "White A-Line Gown", "rent_out", "−1", VIOLET, "SO26-000019 · 12 Sep"),
            ("TRN26-004181", "Chantilly Veil", "stock_in", "+12", OK, "GRN26-0008 · 12 Sep"),
            ("TRN26-004179", "Gold Ball Gown", "rent_return", "+1", OK, "SO26-000014 · 11 Sep"),
            ("TRN26-004178", "Ivory Mermaid Gown", "stock_out", "−1", DANGER, "SO26-000017 · 11 Sep"),
            ("TRN26-004176", "Pearl Tiara Set", "transfer_out", "−4", INFO, "TRF26-0003 · 11 Sep"),
            ("TRN26-004170", "Rose Nikah Abaya", "dispose", "−1", DANGER, "DSP26-0004 · 10 Sep")]
    for txn, item, typ, qty, col, ref in rows:
        els.append(rect(cx, y, cw, 66, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, item, 12.5, INK, width=cw - 80, g=G))
        els.append(text(cx + 14, y + 29, typ, 11, col, width=cw - 80, g=G))
        els.append(text(cx + 14, y + 46, ref, 10, MUTED, width=cw - 80, g=G))
        els.append(text(cx + cw - 62, y + 22, qty, 17, col, "right", 48, G))
        y += 74
    return els


def _m10(ox, oy):
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "10. Reports", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Reports", left=ICON["back"], g=G)
    els += e
    els += filter_chips(cx, y, ["Valuation", "ROI"], 1, G)
    y += 46
    els.append(rect(cx, y, cw, 78, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 16, y + 12, "FLEET ROI", 10, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 30, "132%", 26, ACCENT, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 58, "94 of 148 dresses have paid for themselves", 10, ACCENT, width=cw - 32, g=G))
    y += 94
    for sku, nm, times, rev, roi, col in [("ADF26-0043", "Gold Ball Gown", "31", "108,500", "209%", OK),
                                          ("ADF26-0042", "White A-Line Gown", "24", "72,000", "189%", OK),
                                          ("ADF26-0115", "Champagne Gown", "12", "30,000", "73%", WARN),
                                          ("ADF26-0051", "Emerald Set", "2", "4,800", "18%", DANGER),
                                          ("ADF26-0126", "Sapphire Gown", "0", "0", "0%", DANGER)]:
        els.append(rect(cx, y, cw, 62, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, nm, 12.5, INK, width=cw - 80, g=G))
        els.append(text(cx + 14, y + 30, f"{times} rentals · AFN {rev}", 11, MUTED, width=cw - 80, g=G))
        els.append(text(cx + cw - 76, y + 20, roi, 16, col, "right", 62, G))
        y += 70
    return els


# ══════════════════════════════════════════════════════════════════

def desktop():
    els = board_title(0, -170, "BOMS Desktop — Inventory",
                      "Corrected stock model · Owned = on hand + on rent (valuation) · Available = on hand − reserved · "
                      "reservations are not ledger rows · weighted average cost · immutable postings")
    screens = [_d1, _d2, _d3, _d4, _d5, _d6, _d7, _d8, _d9, _d10, _d11, _d12, _d13, _d14, _d15, _d16]
    labels = {0: "CATALOGUE & ITEMS", 4: "STOCK IN", 8: "MOVEMENTS & CORRECTIONS", 12: "BOOKINGS & REPORTS"}
    for i, fn in enumerate(screens):
        ox, oy = grid_pos(i, DESK_COLS)
        if i in labels:
            els += section_label(ox, oy - 74, labels[i])
        els += fn(ox, oy)
    els += flow_arrows(len(screens), DESK_COLS)
    return els


def mobile():
    els = board_title(0, -150, "BOMS Mobile — Inventory",
                      "Mobile-first stock control · bottom tabs · same corrected quantity model as desktop")
    screens = [_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8, _m9, _m10]
    for i, fn in enumerate(screens):
        ox, oy = grid_pos(i, PHONE_COLS, PHONE_W, PHONE_H)
        els += fn(ox, oy)
    els += flow_arrows(len(screens), PHONE_COLS, PHONE_W, PHONE_H)
    return els
