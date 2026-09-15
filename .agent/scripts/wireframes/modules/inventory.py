#!/usr/bin/env python3
"""BOMS — Inventory module wireframes (desktop + mobile).

READING ORDER — the board is grouped the way the sidebar is grouped, and every
group starts on a fresh row:

    A. DASHBOARD        A1
    B. ITEMS            B1 list · B2 new drawer · B3 edit drawer ·
                        B4–B9 item profile, one screen per tab
    C. STOCK LEDGER     C1 ledger · C2 stock-in · C3 receive PO · C4 adjust · C5 dispose
    D. RESERVATIONS     D1 list · D2 reserve drawer · D3 availability calendar
    E. TRANSFERS        E1 list · E2 transfer drawer
    F. REPORTS          F1 valuation · F2 movement · F3 rental ROI

Rules this module draws:
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

  • BARCODE is generated from the SKU (Code 128) and never typed. A QR code
    carrying the same SKU is generated beside it and shown on the item profile.
  • There is NO `purpose` field. Sellable = has a sale price.
    Rentable = has a rental price.
  • There is NO fixed rental period. Rentals are open — the dates come from the
    booking, not from the item record.
  • EVERY create / edit is a drawer over its list. A list and a form never
    share a page.
"""

from __future__ import annotations

from dsl import *  # noqa: F401,F403

DESK_COLS = 4
PHONE_COLS = 6

ITEM_TABS = ["Overview", "Stock & movement", "Reservations", "Rentals", "Photos", "Audit"]

SECTION_COLORS = {
    "DASHBOARD": ACCENT,
    "ITEMS": ROSE,
    "STOCK LEDGER": INFO,
    "RESERVATIONS": WARN,
    "TRANSFERS": VIOLET,
    "REPORTS": OK,
}

# ── local compositions (rect/text only) ───────────────────────────


def _sel(x, y, w, label, value="", g=None, required=False, h=36):
    """Select box with chevron — 64px row pitch."""
    g = g or []
    els, ny = field(x, y, w, label, value, g, required, None, h)
    els.append(text(x + w - 22, y + 18 + (h - 16) / 2, ICON["down"], 12, MUTED, g=g))
    return els, ny


def _inp(x, y, w, label, value="", g=None, required=False, h=36):
    return field(x, y, w, label, value, g, required, None, h)


def _ro(x, y, w, label, value, g=None, h=36, hint=None):
    """Read-only / system-generated field — greyed fill, lock glyph, no caret."""
    g = g or []
    els = [text(x, y, label, 12, MUTED, width=w, g=g),
           rect(x, y + 18, w, h, strokeColor=HAIRLINE, backgroundColor=SOFT,
                strokeWidth=1, groupIds=g),
           text(x + 12, y + 18 + (h - 16) / 2, value, 13, INK, width=w - 40, g=g),
           text(x + w - 24, y + 18 + (h - 16) / 2, ICON["lock"], 11, FAINT, g=g)]
    ny = y + 18 + h + 10
    if hint:
        els.append(text(x, ny - 6, hint, 10.5, FAINT, width=w, g=g))
        ny += 14
    return els, ny


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


def _item_head(cx, cy, cw, g, active_tab, actions=None, subtitle=None):
    """Breadcrumb + title + the six-tab strip shared by every item-profile screen."""
    els = [breadcrumb(cx, cy, ["Inventory", "Items", "ADF26-0042"], g)]
    e, y = page_header(cx, cy + 18, cw, "White A-Line Gown",
                       actions=actions or [("Reserve", "secondary"), ("Edit item", "primary")],
                       subtitle=subtitle or "SKU ADF26-0042 · Wedding Dress · A-Line · Size M",
                       g=g)
    els += e
    e, y = tabs(cx, y, cw, ITEM_TABS, ITEM_TABS.index(active_tab), g)
    els += e
    return els, y


def _items_backdrop(cx, cy, cw, g, subtitle="1,284 owned units · 48 SKUs"):
    """The items list, drawn behind a drawer. A list is never a form."""
    els, y = page_header(cx, cy, cw, "Items", actions=[("＋ New item", "primary")],
                         subtitle=subtitle, g=g)
    els += search_bar(cx, y, 460, "Search SKU, name, barcode…", g)
    els += filter_chips(cx, y + 52, ["All 1,284", "Available 954", "On rent 238", "Reserved 92"], 0, g)
    e, _ = table(cx, y + 94, cw,
                 ["SKU", "Name", "Category", "Lifecycle", "On hand", "On rent", "Avail", "Worth"],
                 [["ADF26-0042", "White A-Line Gown", "Wedding Dress", "active", "3", "1", "2", "124,800"],
                  ["ADF26-0043", "Gold Ball Gown", "Engagement", "active", "2", "2", "2", "110,000"],
                  ["ADF26-0051", "Emerald Engagement Set", "Engagement", "active", "1", "0", "0", "44,000"],
                  ["ADF26-0067", "Chantilly Veil", "Accessories", "active", "2", "0", "2", "7,600"]],
                 g, row_h=42, widths=[1.1, 1.9, 1.2, 0.9, 0.75, 0.7, 0.65, 1.0])
    els += e
    return els


def _ledger_backdrop(cx, cy, cw, g, title="Stock ledger"):
    """The stock-ledger list, drawn behind a drawer."""
    els, y = page_header(cx, cy, cw, title,
                         actions=[("＋ New movement", "primary")],
                         subtitle="Append-only. Corrections are reversing rows, never edits.", g=g)
    els += search_bar(cx, y, 340, "Txn # / SKU / reference document", g)
    els += filter_chips(cx + 356, y + 5, ["All types", "Stock in", "Adjust", "Transfer", "Dispose"], 0, g)
    e, _ = table(cx, y + 56, cw,
                 ["Txn #", "Date", "Item", "Type", "Qty", "Unit cost", "Warehouse", "Reference"],
                 [["TRN26-004182", "12 Sep", "White A-Line Gown", "rent_out", "−1", "38,000", "Main Store", "SO26-000019"],
                  ["TRN26-004181", "12 Sep", "Chantilly Veil", "stock_in", "+12", "1,450", "Main Store", "GRN26-0008"],
                  ["TRN26-004179", "11 Sep", "Gold Ball Gown", "rent_return", "+1", "52,000", "Main Store", "SO26-000014"],
                  ["TRN26-004176", "11 Sep", "Pearl Tiara Set", "transfer_out", "−4", "3,200", "Shar-e-Naw", "TRF26-0003"]],
                 g, row_h=40, widths=[1.2, 0.7, 1.7, 1.0, 0.5, 0.8, 1.0, 1.1])
    els += e
    return els


# ══════════════════════════════════════════════════════════════════
#  A.  DASHBOARD
# ══════════════════════════════════════════════════════════════════

def _a1(ox, oy):
    """A1 — Inventory dashboard."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "A1.  Inventory dashboard — stock at a glance",
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

    els += _lab(cx, y, "QUICK ACTIONS — each one opens a drawer", G)
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


# ══════════════════════════════════════════════════════════════════
#  B.  ITEMS
# ══════════════════════════════════════════════════════════════════

def _b1(ox, oy):
    """B1 — Items list."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B1.  Items list — catalogue with the three buckets",
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
                "This page NEVER shows a form. ＋ New item and the row Edit action both open the drawer on B2 / B3 — the list stays on screen behind it.",
                ACCENT, G)
    return els


def _b2(ox, oy):
    """B2 — New item drawer."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B2.  New item — drawer over the items list",
                                     "Inventory", g, sub_active="Items")
    els += _items_backdrop(cx, cy, cw, G)

    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New item",
                            side="right", width=580,
                            subtitle="Catalogue record only · creates NO stock · barcode and QR are generated from the SKU",
                            g=G)
    els += de

    c3 = (fw - 24) / 3
    c4 = (fw - 36) / 4
    fy2 = fy
    e, fy2 = _inp(fx, fy2, fw, "Item name", "White A-Line Gown", G, True)
    els += e

    # ── identity block: SKU is generated, barcode is derived from it
    els += _lab(fx, fy2, "IDENTITY — generated, not typed", G, ROSE)
    fy2 += 22
    e, _ = _ro(fx, fy2, c3 * 1.5 + 6, "SKU", "ADF26-0131", G,
               hint="platform_sequences · ADF{YY}-{0000}")
    els += e
    e, fy2 = _ro(fx + c3 * 1.5 + 22, fy2, c3 * 1.5 + 6, "Barcode", "Code 128 of ADF26-0131", G,
                 hint="derived — regenerates if the SKU ever changes")
    els += e
    els.append(rect(fx, fy2, fw, 104, strokeColor=HAIRLINE, backgroundColor=SOFT2,
                    strokeWidth=1, groupIds=G))
    els.append(text(fx + 14, fy2 + 10, "LIVE PREVIEW — updates as soon as the SKU is issued",
                    10.5, MUTED, width=fw - 28, g=G))
    e, _ = barcode(fx + 14, fy2 + 26, fw - 132, 66, "ADF26-0131", G)
    els += e
    e, _ = qr(fx + fw - 104, fy2 + 24, 64, "ADF26-0131", G)
    els += e
    els.append(text(fx + fw - 104, fy2 + 90, "QR = SKU", 9.5, FAINT, "center", 64, G))
    fy2 += 116

    for i, (lab, val, req) in enumerate([("Main category", "Bridal Dresses", True),
                                         ("Sub-category", "A-Line", True),
                                         ("Item type", "Wedding Dress", False),
                                         ("Model", "Elegance 2026", False)]):
        e, ny = _sel(fx + i * (c4 + 12), fy2, c4, lab, val, G, req)
        els += e
    fy2 = ny
    e, _ = _inp(fx, fy2, c3, "Size", "M", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Colour", "Ivory white", G)
    els += e
    e, fy2 = _sel(fx + 2 * (c3 + 12), fy2, c3, "Lifecycle status", "active", G, True)
    els += e

    els += _lab(fx, fy2, "PRICING — AFN · leave a price empty to switch that channel off", G, ROSE)
    fy2 += 22
    e, _ = _inp(fx, fy2, c3, "Sale price", "48,000", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Rental price", "9,500", G)
    els += e
    e, fy2 = _inp(fx + 2 * (c3 + 12), fy2, c3, "Rental deposit", "5,000", G)
    els += e
    e, _ = _inp(fx, fy2, c3, "Late fee / day", "500", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Cleaning buffer (days)", "2", G)
    els += e
    e, fy2 = _inp(fx + 2 * (c3 + 12), fy2, c3, "Reorder level", "1", G)
    els += e

    els += note(fx, fy2, fw,
                "No Purpose field and no rental period. The prices decide the channel:\n"
                "sale price → sellable · rental price → rentable · both → both. Dates come from the booking.",
                VIOLET, G)
    fy2 += 60

    els.append(rect(fx, fy2, fw, 34, strokeColor=HAIRLINE, backgroundColor=BG,
                    strokeWidth=1, groupIds=G))
    els.append(text(fx + 12, fy2 + 9, "▸  More attributes — fabric, season, quality, components, custom fields",
                    12, MUTED, width=fw - 24, g=G))
    fy2 += 44
    els += _photo(fx, fy2, fw, 52, G, ICON["photo"], "drag photos here · first becomes is_main")

    by = oy + TITLE_H + DESK_H - 68
    els += btn(fx, by, 130, 40, "Cancel", "secondary", G)
    els += btn(fx + fw - 300, by, 140, 40, "Save & new", "secondary", G)
    els += btn(fx + fw - 150, by, 150, 40, "Save item", "primary", G)

    els += note(cx, oy + 792, 560,
                "Writes inventory_items (+ inventory_item_media). SKU comes from\n"
                "platform_sequences. barcode is NOT an input — it is Code 128 over the SKU,\n"
                "stored on inventory_items.barcode so scanners resolve it in one lookup;\n"
                "the QR carries the same SKU and is rendered, never stored.\n"
                "Saving creates NO stock: opening quantities arrive on C2 or C3.",
                ACCENT, G)
    return els


def _b3(ox, oy):
    """B3 — Edit item drawer."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B3.  Edit item — same drawer, identity locked",
                                     "Inventory", g, sub_active="Items")
    els += _items_backdrop(cx, cy, cw, G)

    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Edit item · ADF26-0042",
                            side="right", width=580,
                            subtitle="White A-Line Gown · editing the catalogue record never moves stock",
                            g=G)
    els += de

    c2 = (fw - 16) / 2
    c3 = (fw - 24) / 3
    fy2 = fy
    e, fy2 = _inp(fx, fy2, fw, "Item name", "White A-Line Gown", G, True)
    els += e

    els += _lab(fx, fy2, "IDENTITY — locked after creation", G, ROSE)
    fy2 += 22
    e, _ = _ro(fx, fy2, c2, "SKU", "ADF26-0042", G, hint="immutable — referenced by 41 ledger rows")
    els += e
    e, fy2 = _ro(fx + c2 + 16, fy2, c2, "Barcode", "Code 128 of ADF26-0042", G,
                 hint="derived from the SKU — cannot be edited")
    els += e
    e, fy2 = label_card(fx, fy2, fw, "ADF26-0042", "White A-Line Gown",
                        "scan resolves to inventory_items.id", G, h=168,
                        title="CURRENT LABEL — printed on the garment tag")
    els += e

    e, _ = _sel(fx, fy2, c2, "Main category", "Bridal Dresses", G, True)
    els += e
    e, fy2 = _sel(fx + c2 + 16, fy2, c2, "Sub-category", "A-Line", G, True)
    els += e
    e, _ = _inp(fx, fy2, c3, "Size", "M", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Colour", "Ivory white", G)
    els += e
    e, fy2 = _sel(fx + 2 * (c3 + 12), fy2, c3, "Lifecycle", "active", G, True)
    els += e

    els += _lab(fx, fy2, "PRICING — AFN", G, ROSE)
    fy2 += 22
    e, _ = _inp(fx, fy2, c3, "Sale price", "48,000", G)
    els += e
    e, _ = _inp(fx + c3 + 12, fy2, c3, "Rental price", "9,500", G)
    els += e
    e, fy2 = _inp(fx + 2 * (c3 + 12), fy2, c3, "Rental deposit", "5,000", G)
    els += e

    els += note(fx, fy2, fw,
                "Changing a price affects FUTURE documents only. Posted orders keep the\n"
                "price they were posted at, and posted ledger rows keep their unit cost.",
                WARN, G)
    fy2 += 62
    els += btn(fx, fy2, 130, 40, "Cancel", "secondary", G)
    els += btn(fx + fw - 300, fy2, 140, 40, "Reprint label", "secondary", G)
    els += btn(fx + fw - 150, fy2, 150, 40, "Save changes", "primary", G)

    els += note(cx, oy + 792, 560,
                "Updates inventory_items and writes a platform_audit_logs row per changed\n"
                "field (old → new), surfaced on the item's Audit tab (B9).\n"
                "sku and barcode are read-only: 41 ledger rows, 6 reservations and 3 purchase\n"
                "order lines point at this item, and a printed garment tag is already in the\n"
                "shop. Reprint label re-renders the same Code 128 + QR — it does not reissue.",
                ACCENT, G)
    return els


def _b4(ox, oy):
    """B4 — Item profile · Overview."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B4.  Item profile · Overview — attributes, label, stock",
                                     "Inventory", g, sub_active="Items")
    e, y = _item_head(cx, cy, cw, G, "Overview",
                      actions=[("Stock in", "secondary"), ("Reserve", "secondary"),
                               ("Edit item", "primary")],
                      subtitle="SKU ADF26-0042 · Wedding Dress · A-Line · Size M · Bought 04 Feb 2026")
    els += e

    LW = 340
    els += _photo(cx, y, LW, 196, G, ICON["dress"], "main photo · inventory_item_media")
    for i in range(4):
        els += _photo(cx + i * 88, y + 206, 76, 64, G, ICON["photo"])

    # barcode + QR card — generated from the SKU, always visible on the profile
    e, _ = label_card(cx, y + 282, LW, "ADF26-0042", "White A-Line Gown",
                      "scan → inventory_items.id", G, h=186)
    els += e

    rx = cx + LW + 24
    RW = cw - LW - 24
    cx0 = rx
    for lab, col in [("Available", OK), ("Lifecycle: active", INFO),
                     ("Sale 48,000", ACCENT), ("Rental 9,500", VIOLET),
                     ("Buffer 2 days", WARN), ("Quality: high", ACCENT)]:
        cels, cx0 = chip(cx0, y + 4, lab, col, g=G)
        els += cels

    els += _lab(rx, y + 44, "ATTRIBUTES — inventory_items", G)
    attrs = [("Main category", "Bridal Dresses"), ("Sub-category", "A-Line"),
             ("Item type", "Wedding Dress"), ("Model / designer", "Elegance 2026"),
             ("Size", "M"), ("Colour", "Ivory white"),
             ("Fabric", "Silk mikado + lace"), ("Season", "Spring 2026"),
             ("Quality", "high"), ("Reorder level", "1"),
             ("Cleaning buffer", "2 days"), ("Expected rental uses", "20")]
    colw = (RW - 24) / 3
    for i, (k, v) in enumerate(attrs):
        els += _kv(rx + (i % 3) * (colw + 12), y + 66 + (i // 3) * 38, colw, k, v, G)

    els += _lab(rx, y + 218, "CHANNELS — decided by the prices that are set", G, VIOLET)
    e, _ = table(rx, y + 240, RW,
                 ["Channel", "Enabled by", "Price", "Deposit", "Late fee", "Buffer"],
                 [[("Sale", OK), "sale price is set", "AFN 48,000", "—", "—", "—"],
                  [("Rental", VIOLET), "rental price is set", "AFN 9,500", "AFN 5,000",
                   "AFN 500 / day", "2 days"]],
                 G, row_h=34, widths=[0.8, 1.5, 1.0, 0.9, 1.0, 0.7], zebra=False)
    els += e

    els += _lab(rx, y + 356, "STOCK BY WAREHOUSE — one SKU lives in several warehouses", G, ROSE)
    e, _ = table(rx, y + 378, RW,
                 ["Warehouse", "On hand", "On rent", "Owned", "Rsvd", "Avail", "Avg cost", "Worth"],
                 [["Main Store", "2", "1", "3", "1", ("1", OK), "31,200", "93,600"],
                  ["Shar-e-Naw Branch", "1", "0", "1", "0", ("1", OK), "31,200", "31,200"],
                  ["Repair Room", "0", "0", "0", "0", ("0", MUTED), "—", "—"],
                  [("TOTAL", INK), ("3", INK), ("1", VIOLET), ("4", INK), ("1", WARN),
                   ("2", OK), ("31,200", INK), ("AFN 124,800", ACCENT)]],
                 G, row_h=34, widths=[1.7, 0.8, 0.8, 0.8, 0.7, 0.75, 1.0, 1.15], zebra=False)
    els += e

    els += note(rx, y + 552, RW,
                "Owned 4 = on hand 3 + on rent 1 · Available 2 = on hand 3 − reserved 1 · Valuation 4 × 31,200 = AFN 124,800",
                VIOLET, G)

    els += note(cx, oy + 826, cw,
                "Reads inventory_items + inventory_item_media + inventory_stock_balances (view) grouped by warehouse. An item has NO single warehouse_id —\n"
                "the same SKU holds stock in many warehouses, so the breakdown table is the source of truth. The barcode card is rendered, not fetched:\n"
                "Code 128 over inventory_items.sku and a QR whose payload is that same SKU, so one scan at the till, the rack or the returns desk resolves to one item id.\n"
                "Only lifecycle_status is stored. The green availability chip is DERIVED from on hand, reservations, open rentals and the cleaning buffer.",
                ACCENT, G)
    return els


def _b5(ox, oy):
    """B5 — Item profile · Stock & movement."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B5.  Item profile · Stock & movement (WAC history)",
                                     "Inventory", g, sub_active="Items")
    e, y = _item_head(cx, cy, cw, G, "Stock & movement",
                      actions=[("⬇ Export ledger", "ghost"), ("Stock in", "primary")],
                      subtitle="SKU ADF26-0042 · weighted average cost per (item, warehouse)")
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


def _b6(ox, oy):
    """B6 — Item profile · Reservations tab."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B6.  Item profile · Reservations — who has booked this dress",
                                     "Inventory", g, sub_active="Items")
    e, y = _item_head(cx, cy, cw, G, "Reservations",
                      actions=[("Availability calendar", "secondary"), ("＋ Reserve", "primary")],
                      subtitle="SKU ADF26-0042 · owned 4 · reserved quantity comes from here, never from the ledger")
    els += e

    e, y = stat_row(cx, y, cw, [
        ("Active reservations", "3", WARN, "holding 1 unit each", ICON["reserve"]),
        ("Reserved units", "1", WARN, "of 3 on hand", ICON["inventory"]),
        ("Next booking", "19 Sep", INFO, "Sara Ahmadi · 3 days", ICON["calendar"]),
        ("Blocked until", "23 Sep", VIOLET, "incl. 2-day buffer", ICON["clock"]),
        ("Conflicts", "1", DANGER, "24–26 Sep overlap", ICON["alert"]),
        ("Fulfilled this year", "18", OK, "became rentals", ICON["check"]),
    ], h=88, gap=12, g=G)
    els += e

    els += filter_chips(cx, y, ["Active 3", "Fulfilled 18", "Released 4", "Cancelled 2", "All 27"], 0, G)
    els.append(text(cx + cw - 300, y + 8, "Showing all warehouses  ·  next 90 days ▾", 12, MUTED, "right", 300, G))
    y += 44

    e, y = table(cx, y, cw,
                 ["Reservation", "From", "To", "Buffer", "Blocked until", "Qty",
                  "Warehouse", "Customer", "Order", "Status", ""],
                 [["RSV26-0041", "19 Sep", "21 Sep", "2 d", ("23 Sep", VIOLET), "1", "Main Store",
                   "Sara Ahmadi", "SO26-000019", ("active", OK), "View"],
                  ["RSV26-0311", "24 Sep", "26 Sep", "2 d", ("28 Sep", VIOLET), "1", "Main Store",
                   "Zainab Haidari", "SO26-000470", ("active", OK), "View"],
                  ["RSV26-0314", "24 Sep", "25 Sep", "2 d", ("27 Sep", VIOLET), "1", "Main Store",
                   "Marwa Sadat", "—", ("conflict", DANGER), "Resolve"],
                  ["RSV26-0035", "05 Sep", "07 Sep", "2 d", "09 Sep", "1", "Main Store",
                   "Zainab Karimi", "SO26-000014", ("fulfilled", MUTED), "View"],
                  ["RSV26-0018", "12 Aug", "14 Aug", "2 d", "16 Aug", "1", "Shar-e-Naw",
                   "Nargis Amini", "—", ("released", MUTED), "View"],
                  ["RSV26-0009", "02 Jul", "04 Jul", "2 d", "06 Jul", "1", "Main Store",
                   "Farida Wali", "SO26-000202", ("cancelled", MUTED), "View"]],
                 G, row_h=40,
                 widths=[1.05, 0.62, 0.58, 0.5, 0.95, 0.4, 1.0, 1.15, 1.1, 0.8, 0.55])
    els += e

    els += note(cx, y, cw * 0.56,
                f"{ICON['alert']}  RSV26-0314 overlaps RSV26-0311 on 24–25 Sep. Only 1 unit is\n"
                "free in Main Store for those dates, so the second insert was rejected by the\n"
                "database and parked as a conflict for a human to resolve — move the dates,\n"
                "source from Shar-e-Naw, or offer an alternative gown.",
                DANGER, G)
    els += note(cx + cw * 0.58, y, cw * 0.42,
                "RESERVED IS NOT A MOVEMENT\nreserved_qty = Σ active reservations.\n"
                "Nothing is written to the stock ledger until the\ndress physically leaves the shop as rent_out.",
                VIOLET, G)

    els += note(cx, oy + 826, cw,
                "Reads inventory_reservations WHERE inventory_item_id = :id, with the customer and order joined in. Writes nothing — ＋ Reserve opens the drawer on D2.\n"
                "blocked_until = reserved_to + cleaning buffer days, so the turnaround sits inside the guarded range and the next customer cannot book the gown straight out of a wedding.\n"
                "Double-booking is prevented by the EXCLUDE constraint (ADR-010), not by application code — see the note on D1.",
                ACCENT, G)
    return els


def _b7(ox, oy):
    """B7 — Item profile · Rentals tab."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B7.  Item profile · Rentals — history, earnings, payback",
                                     "Inventory", g, sub_active="Items")
    e, y = _item_head(cx, cy, cw, G, "Rentals",
                      actions=[("⬇ Export", "ghost"), ("Open rental order", "primary")],
                      subtitle="SKU ADF26-0042 · has this dress paid for itself? · AFN")
    els += e

    e, y = stat_row(cx, y, cw, [
        ("Times rented", "24", INK, "since Feb 2026", ICON["rental"]),
        ("Rental revenue", "228,000", OK, "excl. deposits", ICON["cash"]),
        ("Amortised so far", "31,200", VIOLET, "of 31,200 cost", ICON["chart"]),
        ("Payback", "100%", OK, "fully paid back", ICON["check"]),
        ("ROI", "731%", ACCENT, "revenue ÷ cost", ICON["chart"]),
        ("Idle days", "2", OK, "since last return", ICON["clock"]),
    ], h=88, gap=12, g=G)
    els += e

    LW = 660
    els += _lab(cx, y, "COST RECOVERY — acquisition_cost ÷ expected_rental_uses, per use", G, VIOLET)
    e, _ = bar_chart(cx, y + 22, LW, 214, "Rental revenue by month (AFN)",
                     [("Mar", 0.35, "24k"), ("Apr", 0.52, "36k"), ("May", 0.74, "51k"),
                      ("Jun", 0.61, "42k"), ("Jul", 0.88, "61k"), ("Aug", 0.42, "29k"),
                      ("Sep", 0.20, "14k")], G, VIOLET)
    els += e
    e, _ = money_row(cx, y + 254, LW,
                     [("Acquisition cost", "AFN 31,200"),
                      ("Expected rental uses", "20"),
                      ("COGS per use  (31,200 ÷ 20)", "AFN 1,560"),
                      ("Uses booked so far", "24"),
                      ("Amortised to date  (capped)", ("AFN 31,200", VIOLET)),
                      ("Rental revenue to date", ("AFN 228,000", OK))],
                     G, total=("Net contribution", ("AFN 196,800", ACCENT)))
    els += e

    rx = cx + LW + 24
    RW = cw - LW - 24
    els += _lab(rx, y, "RENTAL HISTORY — sales_order_items of type rental", G)
    e, y2 = table(rx, y + 22, RW,
                  ["Order", "Customer", "Out", "Back", "Days", "Charged", "Late fee", "COGS", "State"],
                  [["SO26-0463", "Nasrin Ahmadi", "12 Sep", "15 Sep", "3", "9,500", "—", "1,560", ("on rent", VIOLET)],
                   ["SO26-0417", "Hosna Rahimi", "02 Aug", "09 Aug", "7", "19,000", "500", "1,560", ("returned", OK)],
                   ["SO26-0388", "Latifa Noor", "18 Jul", "20 Jul", "2", "9,500", "—", "1,560", ("returned", OK)],
                   ["SO26-0341", "Malika Sabir", "04 Jul", "07 Jul", "3", "9,500", "—", "1,560", ("returned", OK)],
                   ["SO26-0295", "Shakila Amiri", "21 Jun", "24 Jun", "3", "9,500", "1,000", "1,560", ("returned", OK)],
                   ["SO26-0244", "Palwasha Zia", "06 Jun", "08 Jun", "2", "9,500", "—", "1,560",
                    ("damage claim", DANGER)]],
                  G, row_h=38, widths=[1.0, 1.3, 0.62, 0.62, 0.45, 0.72, 0.65, 0.6, 0.95])
    els += e
    els += note(rx, y2 + 4, RW,
                "OPEN PERIOD — a rental has no fixed length.\nDays are the difference between the dates on\n"
                "the order; the item record carries no period.\nLate fee applies per day past the agreed return.",
                WARN, G)

    els += note(cx, oy + 826, cw,
                "Reads sales_order_items (type=rental) joined to sales_orders and finance_cogs_entries, plus the rent_out / rent_return pairs in inventory_stock_transactions.\n"
                "Rental COGS (ADR-002) is amortisation, not cost of goods: rental_cogs_per_use = acquisition_cost ÷ expected_rental_uses, accumulated into inventory_items.amortised_cost_to_date and CAPPED at acquisition cost.\n"
                "This gown crossed its cap on its 20th rental, so rentals 21–24 carried zero COGS and are pure margin — which is why Payback reads 100% while ROI keeps climbing.",
                ACCENT, G)
    return els


def _b8(ox, oy):
    """B8 — Item profile · Photos tab."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B8.  Item profile · Photos — gallery, main photo, condition shots",
                                     "Inventory", g, sub_active="Items")
    e, y = _item_head(cx, cy, cw, G, "Photos",
                      actions=[("Reorder", "secondary"), ("⬆ Upload photos", "primary")],
                      subtitle="SKU ADF26-0042 · 9 photos · drag to reorder · first photo is the catalogue image")
    els += e

    LW = 760
    els += _lab(cx, y, "CATALOGUE PHOTOS — inventory_item_media, sort_order ascending", G, ROSE)
    yy = y + 24
    els += _photo(cx, yy, 360, 268, G, ICON["dress"], "main photo")
    cels, _ = chip(cx + 12, yy + 12, "is_main", ACCENT, g=G)
    els += cels
    els.append(text(cx, yy + 276, "front-full.jpg · 2.1 MB · 2400×3600", 10.5, MUTED, width=360, g=G))

    tw = (LW - 372 - 12) / 2
    for i, (cap, sub) in enumerate([("back-full.jpg", "2400×3600"), ("detail-lace.jpg", "1800×1800"),
                                    ("train.jpg", "2400×1600"), ("hanger.jpg", "1200×1600")]):
        px = cx + 372 + (i % 2) * (tw + 12)
        py = yy + (i // 2) * 138
        els += _photo(px, py, tw, 122, G, ICON["photo"])
        els.append(text(px, py + 126, cap + " · " + sub, 10, MUTED, width=tw, g=G))

    els.append(rect(cx, yy + 306, LW, 74, strokeColor=LINE, backgroundColor=SOFT2,
                    strokeWidth=1, strokeStyle="dashed", groupIds=G))
    els.append(text(cx, yy + 326, f"{ICON['photo']}   Drop photos here, or click to browse",
                    13, MUTED, "center", LW, G))
    els.append(text(cx, yy + 348, "JPEG / PNG / WebP · max 8 MB each · first upload becomes is_main",
                    10.5, FAINT, "center", LW, G))

    rx = cx + LW + 24
    RW = cw - LW - 24
    els += _lab(rx, y, "CONDITION PHOTOS — on documents, not the catalogue", G, WARN)
    e, y2 = table(rx, y + 24, RW,
                  ["Shot", "Document", "Date", "By"],
                  [[("check-out", VIOLET), "SO26-0463", "12 Sep", "Zahra"],
                   [("check-in", OK), "SO26-0417", "09 Aug", "Zahra"],
                   [("damage", DANGER), "CLM26-0007", "08 Jun", "Ahmad"],
                   [("check-out", VIOLET), "SO26-0244", "06 Jun", "Zahra"]],
                  G, row_h=36, widths=[0.9, 1.15, 0.7, 0.7])
    els += e
    for i in range(3):
        els += _photo(rx + i * ((RW - 24) / 3 + 12), y2 + 8, (RW - 24) / 3, 92, G, ICON["photo"])
    els += note(rx, y2 + 112, RW,
                "Condition shots live in platform_attachments against the\n"
                "rental order or the claim — they prove what the dress\n"
                "looked like when it left and when it came back.\n"
                "They are deliberately NOT in the catalogue gallery.",
                WARN, G)
    els += note(rx, y2 + 214, RW,
                "STORAGE\nfile_path is a key in object storage, not a blob.\n"
                "title · sort_order · is_main are the only metadata.\n"
                "Deleting the is_main photo promotes the next by sort_order.",
                ACCENT, G)

    els += note(cx, oy + 826, cw,
                "Reads and writes inventory_item_media (tenant_id, inventory_item_id, file_path, title, sort_order, is_main). Exactly one row per item may carry is_main = true — the write is a transaction that clears the old one first.\n"
                "Upload is the only place in Inventory that writes binary content. Reordering issues a bulk sort_order update; it does not touch the files themselves.\n"
                "Condition photos are platform_attachments rows keyed to sales_orders / sales_rental_claims and are shown here read-only, so a returns dispute can be settled from the item profile.",
                ACCENT, G)
    return els


def _b9(ox, oy):
    """B9 — Item profile · Audit tab."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "B9.  Item profile · Audit — every change, who and when",
                                     "Inventory", g, sub_active="Items")
    e, y = _item_head(cx, cy, cw, G, "Audit",
                      actions=[("⬇ Export CSV", "ghost"), ("Filter ▾", "secondary")],
                      subtitle="SKU ADF26-0042 · created 04 Feb 2026 by Ahmad Zaki · 37 recorded events")
    els += e

    els += filter_chips(cx, y, ["All 37", "Field changes 14", "Stock postings 18",
                                "Reservations 4", "Photos 1"], 0, G)
    els.append(text(cx + cw - 320, y + 8, "04 Feb 2026 → 12 Sep 2026 ▾", 12, MUTED, "right", 320, G))
    y += 46

    e, y = table(cx, y, cw,
                 ["When", "User", "Action", "Field / document", "Old value", "New value", "Source", ""],
                 [["12 Sep 2026  14:02", "Zahra Nekzad", ("stock posting", VIOLET), "TRN26-004182 · rent_out",
                   "on hand 3", "on hand 2", "SO26-0463", "View"],
                  ["11 Sep 2026  09:40", "Ahmad Zaki", ("field change", INFO), "rental_price",
                   "9,000", "9,500", "Edit drawer", "View"],
                  ["08 Sep 2026  17:12", "Ahmad Zaki", ("field change", INFO), "lifecycle_status",
                   "repairing", "active", "Edit drawer", "View"],
                  ["05 Sep 2026  11:26", "Zahra Nekzad", ("reservation", WARN), "RSV26-0311",
                   "—", "24–26 Sep · 1 unit", "Reserve drawer", "View"],
                  ["27 Jun 2026  10:03", "Rahim Sultani", ("stock posting", VIOLET), "TRN26-002980 · stock_in",
                   "avg cost 30,467", "avg cost 31,200", "GRN26-0024", "View"],
                  ["12 Apr 2026  08:55", "Ahmad Zaki", ("photo", ACCENT), "inventory_item_media",
                   "4 photos", "9 photos", "Photos tab", "View"],
                  ["04 Feb 2026  16:20", "Ahmad Zaki", ("created", OK), "inventory_items",
                   "—", "ADF26-0042", "New item drawer", "View"]],
                 G, row_h=42, widths=[1.35, 1.15, 1.0, 1.75, 1.15, 1.35, 1.1, 0.45])
    els += e
    e, y = pagination(cx, y, cw, "1–7 of 37 events", G)
    els += e

    els += note(cx, y + 6, cw * 0.48,
                "WHAT CANNOT APPEAR HERE\nNo row says “edited TRN26-004182”. Posted documents are\n"
                "immutable — a correction is a reversing document, and the\n"
                "audit trail shows both the original and the reversal.",
                DANGER, G)
    els += note(cx + cw * 0.50, y + 6, cw * 0.50,
                "IMMUTABLE IDENTITY\nsku and barcode have no rows in this table because they\n"
                "cannot change after creation. If a tag is damaged, Reprint\n"
                "label re-renders the same Code 128 and QR — it never reissues.",
                VIOLET, G)

    els += note(cx, oy + 826, cw,
                "Reads platform_audit_logs WHERE entity_type='inventory_items' AND entity_id = :id, unioned with the postings that reference the item "
                "(inventory_stock_transactions, inventory_reservations, inventory_item_media).\n"
                "Field changes store old_value / new_value as jsonb, so the table renders a real before → after rather than a vague “updated”. Every row carries user_id, ip_address and the UI surface that caused it.\n"
                "Nothing on this tab is writable. It is the answer to “who changed the price before that order was posted?” — the single question a bridal shop owner always ends up asking.",
                ACCENT, G)
    return els


# ══════════════════════════════════════════════════════════════════
#  C.  STOCK LEDGER
# ══════════════════════════════════════════════════════════════════

def _c1(ox, oy):
    """C1 — Stock ledger."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C1.  Stock ledger — immutable movement history",
                                     "Inventory", g, sub_active="Stock ledger")
    e, y = page_header(cx, cy, cw, "Stock ledger",
                       actions=[("⬇ Export CSV", "ghost"), ("Rebuild balances", "secondary"),
                                ("＋ New movement", "primary")],
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
                "＋ New movement opens a menu of four drawers — Stock in (C2) · Receive PO (C3) · Adjust (C4) · Dispose (C5) — each over this list, so the ledger never leaves the screen.\n"
                "Types: stock_in · stock_out · adjustment · transfer_in · transfer_out · rent_out · rent_return · dispose.  There is NO reserve / release type — reservations are not stock movements.",
                ACCENT, G)
    return els


def _c2(ox, oy):
    """C2 — Stock in drawer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C2.  Stock in — drawer over the ledger (manual / opening)",
                                     "Inventory", g, sub_active="Stock ledger")
    els += _ledger_backdrop(cx, cy, cw, G)

    DW = 880
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Stock in  ·  MSE26-0022",
                            side="right", width=DW,
                            subtitle="Opening stock or an ad-hoc stock-in with no purchase order · draft", g=G)
    els += de

    q = (fw - 36) / 4
    e, _ = _sel(fx, fy, q, "Entry type", "Manual in", G, True)
    els += e
    e, _ = _sel(fx + q + 12, fy, q, "Warehouse", "Main Store", G, True)
    els += e
    e, _ = _inp(fx + 2 * (q + 12), fy, q, "Entry date", "12 Sep 2026", G, True)
    els += e
    e, fy = _inp(fx + 3 * (q + 12), fy, q, "Reference", "Sept stock take", G)
    els += e

    els += _lab(fx, fy, "LINES", G)
    els.append(text(fx + fw - 120, fy - 2, "＋ Add line", 12, ACCENT, "right", 120, G))
    e, fy2 = table(fx, fy + 22, fw,
                   ["Item", "SKU", "Qty", "Unit cost", "Currency", "Line value", "New avg cost", ""],
                   [["Chantilly Veil", "ADF26-0067", "12", "1,450.00", "AFN", "17,400.00", ("1,462.50", ACCENT), "✕"],
                    ["Pearl Tiara Set", "ADF26-0102", "6", "3,200.00", "AFN", "19,200.00", ("3,200.00", ACCENT), "✕"],
                    ["Bridal Gloves (S)", "ADF26-0121", "10", "480.00", "AFN", "4,800.00", ("492.30", ACCENT), "✕"]],
                   G, row_h=44, widths=[1.8, 1.05, 0.5, 0.85, 0.62, 0.95, 0.95, 0.32])
    els += e

    els.append(rect(fx, fy2 + 8, fw * 0.52, 46, strokeColor=ACCENT, backgroundColor=ACCENT_BG,
                    strokeWidth=1, groupIds=G))
    els.append(text(fx + 14, fy2 + 23, f"{ICON['search']}   Scan a barcode or QR to add a line",
                    13, ACCENT, width=fw * 0.52 - 28, g=G))

    e, _ = money_row(fx + fw - 340, fy2 + 8, 340,
                     [("Lines", "3"), ("Total quantity", "28"), ("Currency", "AFN @ 1.000000")],
                     G, total=("Total entry value", "AFN 41,400.00"))
    els += e

    els += note(fx, fy2 + 156, fw * 0.60,
                "Draft writes inventory_stock_entries + inventory_stock_entry_items only — no stock moves yet.\n"
                "POST writes one inventory_stock_transactions row per line (type=stock_in,\n"
                "reference_type=inventory_stock_entry) and recomputes the weighted average cost:\n"
                "   new_avg = (on_hand × avg + qty_in × unit_cost) / (on_hand + qty_in)\n"
                "The 'New avg cost' column previews that before you commit. Posted = immutable; correct by Void.",
                ACCENT, G)

    by = oy + TITLE_H + DESK_H - 76
    els += btn(fx, by, 120, 42, "Cancel", "secondary", G)
    els += btn(fx + fw - 300, by, 140, 42, "Save draft", "secondary", G)
    els += btn(fx + fw - 150, by, 150, 42, "Post entry", "primary", G)
    return els


def _c3(ox, oy):
    """C3 — Receive against PO (GRN) drawer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C3.  Receive against PO (GRN) — drawer over the ledger",
                                     "Inventory", g, sub_active="Stock ledger")
    els += _ledger_backdrop(cx, cy, cw, G)

    DW = 920
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Receive goods  ·  GRN26-0009",
                            side="right", width=DW,
                            subtitle="PO26-000012 · Istanbul Bridal Co. · ordered 02 Sep 2026 · draft", g=G)
    els += de

    q = (fw - 36) / 4
    e, _ = _sel(fx, fy, q, "Purchase order", "PO26-000012", G, True)
    els += e
    e, _ = _sel(fx + q + 12, fy, q, "Receive into", "Main Store", G, True)
    els += e
    e, _ = _inp(fx + 2 * (q + 12), fy, q, "Received date", "12 Sep 2026", G, True)
    els += e
    e, fy = _inp(fx + 3 * (q + 12), fy, q, "Currency / rate", "USD @ 70.500000", G)
    els += e

    e, fy2 = table(fx, fy, fw,
                   ["Line", "Ordered", "Received", "Receiving now", "Unit cost", "Allocated other", "Landed unit cost", "Line value"],
                   [["White A-Line Gown  ADF26-0042", "4", "0", ("4", ACCENT), "480.00", "162.00", ("520.50", ACCENT), "2,082.00"],
                    ["Chantilly Veil  ADF26-0067", "20", "8", ("12", ACCENT), "18.00", "48.60", ("22.05", ACCENT), "264.60"],
                    [("Blush Tulle Gown  — new item —", VIOLET), "2", "0", ("2", ACCENT), "390.00", "65.80", ("422.90", ACCENT), "845.80"],
                    ["Pearl Tiara Set  ADF26-0102", "10", "10", ("0", MUTED), "42.00", "23.60", ("—", MUTED), "0.00"]],
                   G, row_h=46, widths=[2.3, 0.62, 0.68, 0.85, 0.78, 0.92, 1.0, 0.8])
    els += e

    els += note(fx, fy2 + 6, fw * 0.54,
                "Landed cost (ADR-009): header other_cost USD 300 is allocated PRO-RATA BY LINE VALUE.\n"
                "   allocated_i = 300.00 × (line_value_i / Σ line_value)\n"
                "   landed_unit_cost = unit_cost + (allocated + line_other) / qty_received\n"
                "Only landed_unit_cost reaches inventory — never the raw unit cost.",
                VIOLET, G)
    els += note(fx + fw * 0.56, fy2 + 6, fw * 0.44,
                "Line 3 is free text with no SKU. On POST the system creates the\n"
                "inventory_items row, issues SKU ADF26-0131 from platform_sequences,\n"
                "generates its Code 128 barcode + QR from that SKU, and writes the\n"
                "new id back onto the PO line and this receipt line.",
                WARN, G)

    e, _ = money_row(fx + fw - 360, fy2 + 122, 360,
                     [("Goods value", "USD 3,192.40"), ("Other cost allocated", "USD 300.00"),
                      ("Exchange rate", "70.500000")],
                     G, total=("Total landed (AFN)", "AFN 246,404.20"))
    els += e
    els += note(fx, fy2 + 124, fw * 0.54,
                "POST, in one DB transaction: create items for free-text lines → allocate other cost →\n"
                "insert stock_in at landed_unit_cost → recompute WAC in inventory_stock_balances →\n"
                "open/increase finance_payables → recompute PO quantity_received + status.\n"
                "Over-receipt is blocked unless over_receipt_approved_by is set. Posted = immutable.",
                ACCENT, G)

    by = oy + TITLE_H + DESK_H - 76
    els += btn(fx, by, 120, 42, "Cancel", "secondary", G)
    els += btn(fx + fw - 310, by, 150, 42, "Save draft", "secondary", G)
    els += btn(fx + fw - 150, by, 150, 42, "Post receipt", "primary", G)
    return els


def _c4(ox, oy):
    """C4 — Adjustment drawer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C4.  Stock adjustment — drawer over the ledger",
                                     "Inventory", g, sub_active="Stock ledger")
    els += _ledger_backdrop(cx, cy, cw, G)

    DW = 840
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Stock adjustment  ·  ADJ26-0012",
                            side="right", width=DW,
                            subtitle="Correct on-hand quantity after a physical count. Not the same as Dispose.", g=G)
    els += de

    q = (fw - 36) / 4
    e, _ = _sel(fx, fy, q, "Warehouse", "Main Store", G, True)
    els += e
    e, _ = _sel(fx + q + 12, fy, q, "Reason", "Count mismatch", G, True)
    els += e
    e, _ = _inp(fx + 2 * (q + 12), fy, q, "Date", "12 Sep 2026", G, True)
    els += e
    e, fy = _inp(fx + 3 * (q + 12), fy, q, "Note", "Quarterly count — aisle 3", G)
    els += e

    e, fy2 = table(fx, fy, fw,
                   ["Item", "SKU", "Expected", "Counted", "Difference", "Unit cost", "Value impact", ""],
                   [["Chantilly Veil", "ADF26-0067", "14", "12", ("−2", DANGER), "1,462.50", ("−2,925.00", DANGER), "✕"],
                    ["Bridal Gloves (S)", "ADF26-0121", "10", "13", ("+3", OK), "492.30", ("+1,476.90", OK), "✕"],
                    ["Pearl Tiara Set", "ADF26-0102", "6", "6", ("0", MUTED), "3,200.00", ("0.00", MUTED), "✕"]],
                   G, row_h=44, widths=[1.9, 1.1, 0.75, 0.75, 0.85, 0.9, 1.0, 0.35])
    els += e

    els += _lab(fx, fy2 + 10, "COUNT SHEET PHOTOS", G)
    for i in range(3):
        els += _photo(fx + i * 112, fy2 + 32, 100, 74, G, ICON["photo"], "count sheet" if i == 0 else None)
    els.append(text(fx + 344, fy2 + 62, "＋ Add photo", 12, ACCENT, g=G))
    e, _ = money_row(fx + fw - 340, fy2 + 16, 340,
                     [("Lines", "3"), ("Net quantity change", ("+1", OK))],
                     G, total=("Net value impact", ("AFN −1,448.10", DANGER)))
    els += e

    els += note(fx, fy2 + 126, fw,
                "POST writes one inventory_stock_transactions row per NON-ZERO line (type=adjustment, signed quantity, reference_type=inventory_adjustment)\n"
                "at the current weighted-average cost. Expected quantity is pre-filled from inventory_stock_balances.on_hand_qty when the draft was opened.\n"
                "Adjustment corrects a counting error. Dispose (C5) is a deliberate write-off of goods that still physically existed — the two must never be confused in reports.",
                ACCENT, G)

    by = oy + TITLE_H + DESK_H - 76
    els += btn(fx, by, 120, 42, "Cancel", "secondary", G)
    els += btn(fx + fw - 320, by, 160, 42, "Save draft", "secondary", G)
    els += btn(fx + fw - 150, by, 150, 42, "Post adjustment", "primary", G)
    return els


def _c5(ox, oy):
    """C5 — Dispose drawer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "C5.  Dispose — drawer over the ledger (write-off)",
                                     "Inventory", g, sub_active="Stock ledger")
    els += _ledger_backdrop(cx, cy, cw, G)

    DW = 840
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "Dispose stock  ·  DSP26-0005",
                            side="right", width=DW,
                            subtitle="Remove goods from stock permanently and book the loss", g=G)
    els += de

    q = (fw - 36) / 4
    e, _ = _sel(fx, fy, q, "Warehouse", "Repair Room", G, True)
    els += e
    e, _ = _sel(fx + q + 12, fy, q, "Reason", "Damaged beyond repair", G, True)
    els += e
    e, _ = _inp(fx + 2 * (q + 12), fy, q, "Date", "12 Sep 2026", G, True)
    els += e
    e, fy = _inp(fx + 3 * (q + 12), fy, q, "Note", "Torn bodice — SO26-000009", G)
    els += e

    e, fy2 = table(fx, fy, fw,
                   ["Item", "SKU", "Owned", "Dispose qty", "Avg unit cost", "Write-off value", "Lifecycle after", ""],
                   [["Rose Nikah Abaya", "ADF26-0091", "1", ("1", DANGER), "18,600.00", ("18,600.00", DANGER), ("disposed", DANGER), "✕"],
                    ["Ivory Hair Comb", "ADF26-0128", "5", ("2", DANGER), "640.00", ("1,280.00", DANGER), ("active", MUTED), "✕"]],
                   G, row_h=46, widths=[1.9, 1.1, 0.7, 0.85, 1.0, 1.05, 1.0, 0.35])
    els += e

    e, _ = money_row(fx + fw - 340, fy2 + 14, 340,
                     [("Units disposed", "3"), ("Reason", "Damaged")],
                     G, total=("Total write-off", ("AFN 19,880.00", DANGER)))
    els += e
    els += note(fx, fy2 + 14, fw * 0.60,
                "POST writes inventory_stock_transactions (type=dispose, NEGATIVE quantity) at the\n"
                "weighted-average cost, reference_type=inventory_disposal. For a serialised dress\n"
                "whose owned_qty reaches 0, lifecycle_status becomes 'disposed'.\n"
                "This is NOT a COGS entry — nothing was sold. It reduces stock worth immediately\n"
                "and appears in the Disposal report. A disposal raised from a rental loss is\n"
                "created by sales_rental_claims and links back here.",
                DANGER, G)

    by = oy + TITLE_H + DESK_H - 76
    els += btn(fx, by, 120, 42, "Cancel", "secondary", G)
    els += btn(fx + fw - 320, by, 160, 42, "Save draft", "secondary", G)
    els += btn(fx + fw - 150, by, 150, 42, "Post disposal", "danger", G)
    return els


# ══════════════════════════════════════════════════════════════════
#  D.  RESERVATIONS
# ══════════════════════════════════════════════════════════════════

def _d1(ox, oy):
    """D1 — Reservations list."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D1.  Reservations — every booking in the shop",
                                     "Inventory", g, sub_active="Reservations")
    e, y = page_header(cx, cy, cw, "Reservations",
                       actions=[("⬇ Export", "ghost"), ("Calendar view", "secondary"),
                                ("＋ Reserve", "primary")],
                       subtitle="Reserved quantity comes from here — never from the stock ledger",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("Active", "92", WARN, "units held", ICON["reserve"]),
        ("Starting this week", "14", INFO, "prepare & press", ICON["calendar"]),
        ("Conflicts", "2", DANGER, "need a human", ICON["alert"]),
        ("Fulfilled (30 d)", "118", OK, "became rentals", ICON["check"]),
        ("Released (30 d)", "21", MUTED, "freed the dress", ICON["cross"]),
    ], h=88, gap=14, g=G)
    els += e
    els += search_bar(cx, y, 340, "SKU / customer / order #", G)
    els += filter_chips(cx + 356, y + 5, ["Active", "Conflict", "Fulfilled", "Released", "Cancelled"], 0, G)
    y += 56
    e, y = table(cx, y, cw,
                 ["Reservation", "Item", "Qty", "From", "To", "Buffer", "Blocked until", "Warehouse", "Order", "Customer", "Status", ""],
                 [["RSV26-0041", "White A-Line Gown", "1", "19 Sep", "21 Sep", "2 d", ("23 Sep", VIOLET), "Main Store", "SO26-000019", "Sara Ahmadi", ("active", OK), "View"],
                  ["RSV26-0040", "Gold Ball Gown", "1", "24 Sep", "26 Sep", "2 d", ("28 Sep", VIOLET), "Main Store", "SO26-000021", "Maryam Noori", ("active", OK), "View"],
                  ["RSV26-0314", "White A-Line Gown", "1", "24 Sep", "25 Sep", "2 d", ("27 Sep", VIOLET), "Main Store", "—", "Marwa Sadat", ("conflict", DANGER), "Resolve"],
                  ["RSV26-0038", "Champagne Ball Gown", "1", "01 Oct", "03 Oct", "2 d", ("05 Oct", VIOLET), "Shar-e-Naw", "—", "Fatima Rahimi", ("active", OK), "View"],
                  ["RSV26-0035", "Emerald Engagement Set", "1", "05 Sep", "07 Sep", "2 d", "09 Sep", "Main Store", "SO26-000014", "Zainab Karimi", ("fulfilled", MUTED), "View"],
                  ["RSV26-0031", "Ivory Mermaid Gown", "1", "28 Aug", "30 Aug", "2 d", "01 Sep", "Main Store", "SO26-000009", "Nargis Amini", ("released", MUTED), "View"]],
                 G, row_h=42, widths=[1.0, 1.55, 0.4, 0.58, 0.55, 0.48, 0.85, 1.0, 1.05, 1.05, 0.72, 0.5])
    els += e
    e, y = pagination(cx, y, cw, "1–6 of 92 active reservations", G)
    els += e
    els += note(cx, y + 4, cw,
                "Reservations write ONLY to inventory_reservations — they never touch inventory_stock_transactions. reserved_qty on the balance is the sum of active reservations.\n"
                "Double-booking is prevented BY THE DATABASE (ADR-010), not by application code:  EXCLUDE USING gist (inventory_item_id WITH =, daterange(reserved_from, blocked_until, '[]') WITH &&) WHERE status='active'.\n"
                "blocked_until = reserved_to + buffer_days, so the cleaning turnaround is inside the guarded range. Two staff booking the same gown concurrently — the second insert is rejected by Postgres and lands here as a conflict.",
                ACCENT, G)
    return els


def _d2(ox, oy):
    """D2 — Reserve drawer + conflict guard."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D2.  New reservation — drawer + double-booking guard",
                                     "Inventory", g, sub_active="Reservations")
    e, y = page_header(cx, cy, cw, "Reservations", actions=[("＋ Reserve", "primary")],
                       subtitle="92 active · 2 conflicts", g=G)
    els += e
    e, _ = table(cx, y, cw,
                 ["Reservation", "Item", "From", "To", "Blocked until", "Customer", "Status"],
                 [["RSV26-0041", "White A-Line Gown", "19 Sep", "21 Sep", "23 Sep", "Sara Ahmadi", "active"],
                  ["RSV26-0040", "Gold Ball Gown", "24 Sep", "26 Sep", "28 Sep", "Maryam Noori", "active"],
                  ["RSV26-0038", "Champagne Ball Gown", "01 Oct", "03 Oct", "05 Oct", "Fatima Rahimi", "active"],
                  ["RSV26-0035", "Emerald Engagement Set", "05 Sep", "07 Sep", "09 Sep", "Zainab Karimi", "fulfilled"]],
                 G, row_h=42, widths=[1.1, 1.8, 0.7, 0.7, 0.95, 1.2, 0.8])
    els += e

    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New reservation",
                            side="right", width=560,
                            subtitle="Holds a dress for a customer · writes inventory_reservations only · no stock moves",
                            g=G)
    els += de

    c2 = (fw - 16) / 2
    e, fy = _sel(fx, fy, fw, "Item", "ADF26-0042 — White A-Line Gown", G, True)
    els += e
    els.append(rect(fx, fy, fw, 44, strokeColor=ACCENT, backgroundColor=ACCENT_BG,
                    strokeWidth=1, groupIds=G))
    els.append(text(fx + 14, fy + 14, f"{ICON['search']}   or scan the garment barcode / QR",
                    13, ACCENT, width=fw - 28, g=G))
    fy += 58
    e, _ = _sel(fx, fy, c2, "Warehouse", "Main Store", G, True)
    els += e
    e, fy = _inp(fx + c2 + 16, fy, c2, "Quantity", "1", G, True)
    els += e
    e, _ = _inp(fx, fy, c2, "Reserved from", "24 Sep 2026", G, True)
    els += e
    e, fy = _inp(fx + c2 + 16, fy, c2, "Reserved to", "26 Sep 2026", G, True)
    els += e
    e, _ = _ro(fx, fy, c2, "Cleaning buffer", "2 days", G, hint="from the item record")
    els += e
    e, fy = _ro(fx + c2 + 16, fy, c2, "Blocked until", "28 Sep 2026", G,
                hint="reserved_to + buffer — this is what the guard checks")
    els += e
    e, _ = _sel(fx, fy, c2, "Customer", "Marwa Sadat", G, True)
    els += e
    e, fy = _sel(fx + c2 + 16, fy, c2, "Link to order", "— none yet —", G)
    els += e
    e, fy = textarea(fx, fy, fw, "Note", "Engagement — needs the long veil too", G, rows=2)
    els += e

    els += btn(fx, fy + 6, 130, 40, "Cancel", "secondary", G)
    els += btn(fx + fw - 170, fy + 6, 170, 40, "Reserve dates", "primary", G)

    els += modal(ox, oy + TITLE_H, DESK_W, DESK_H,
                 "⚠  Dress already booked for these dates",
                 "White A-Line Gown (ADF26-0042) is reserved 24–26 Sep for SO26-000470,\n"
                 "and blocked until 28 Sep for the 2-day cleaning buffer.\n"
                 "Only 1 unit is on hand in Main Store, so it cannot be booked again.\n\n"
                 "What you can do:\n"
                 "   • Source the same gown from Shar-e-Naw Branch — 1 available\n"
                 "   • Move the booking to 29 Sep or later\n"
                 "   • Offer Ivory Mermaid Gown  ADF26-0088  size S",
                 w=580, h=310,
                 actions=[("Choose another date", "secondary"), ("Pick alternative", "primary")], g=G)

    els += note(cx, oy + 812, cw,
                "The guard is a Postgres EXCLUDE constraint, so it holds even when two staff press Reserve at the same instant on two tills — the second INSERT raises 23P01 and this dialog is what the user sees.\n"
                "The drawer writes one inventory_reservations row: item, warehouse, qty, reserved_from, reserved_to, blocked_until (= reserved_to + cleaning buffer), customer, optional sales_order_id, status='active'.\n"
                "Nothing reaches the stock ledger. The dress only becomes a rent_out row when it physically leaves the shop, which happens on the sales side.",
                DANGER, G)
    return els


def _d3(ox, oy):
    """D3 — Availability calendar."""
    g = nid()
    G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "D3.  Availability calendar — reserved / on rent / buffer",
                                     "Inventory", g, sub_active="Reservations")
    e, y = page_header(cx, cy, cw, "Availability — White A-Line Gown",
                       actions=[("Month ▾", "secondary"), ("＋ Reserve", "primary")],
                       subtitle="ADF26-0042 · owned 4 · on hand 3 · cleaning buffer 2 days after every return",
                       g=G)
    els += e

    lx = cx
    for lab, col in [("Free", OK), ("Reserved", WARN), ("On rent", ACCENT),
                     ("Cleaning buffer", VIOLET), ("Conflict", DANGER)]:
        cels, lx = chip(lx, y, lab, col, g=G)
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
                "Rentals have no fixed length, so an on-rent band runs from the rent_out date to the agreed return date on the order — the calendar reads it, it does not compute it.",
                ACCENT, G)
    return els


# ══════════════════════════════════════════════════════════════════
#  E.  TRANSFERS
# ══════════════════════════════════════════════════════════════════

def _e1(ox, oy):
    """E1 — Transfers list."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "E1.  Transfers — stock moving between warehouses",
                                     "Inventory", g, sub_active="Transfers")
    e, y = page_header(cx, cy, cw, "Transfers",
                       actions=[("⬇ Export", "ghost"), ("＋ New transfer", "primary")],
                       subtitle="Move stock between warehouses or branches. Cost travels with the goods.",
                       g=G)
    els += e
    e, y = stat_row(cx, y, cw, [
        ("In transit", "3 documents", VIOLET, "18 units", ICON["truck"]),
        ("Value in transit", "AFN 142,900", VIOLET, "still owned", ICON["cash"]),
        ("Awaiting receipt", "2", WARN, "oldest 4 days", ICON["clock"]),
        ("Completed (30 d)", "11", OK, "fully received", ICON["check"]),
    ], h=88, gap=14, g=G)
    els += e
    els += search_bar(cx, y, 340, "Transfer # / item / warehouse", G)
    els += filter_chips(cx + 356, y + 5, ["All", "Draft", "In transit", "Partially received", "Completed"], 0, G)
    y += 56
    e, y = table(cx, y, cw,
                 ["Transfer", "From", "To", "Sent", "Lines", "Units", "Received", "Value", "Status", ""],
                 [["TRF26-0004", "Main Store", "Shar-e-Naw · Floor 2", "12 Sep", "3", "10", ("0 of 10", WARN), "72,112.50", ("in transit", VIOLET), "View"],
                  ["TRF26-0003", "Shar-e-Naw · Floor 2", "Main Store", "11 Sep", "1", "4", ("4 of 4", OK), "12,800.00", ("completed", OK), "View"],
                  ["TRF26-0002", "Main Store", "Repair Room", "09 Sep", "2", "5", ("3 of 5", WARN), "58,900.00", ("partially received", WARN), "View"],
                  ["TRF26-0001", "Main Store", "Shar-e-Naw · Floor 2", "02 Sep", "4", "22", ("22 of 22", OK), "184,300.00", ("completed", OK), "View"],
                  ["TRF26-0005", "Repair Room", "Main Store", "—", "1", "1", ("—", MUTED), "38,900.00", ("draft", MUTED), "Edit"]],
                 G, row_h=42, widths=[1.0, 1.35, 1.5, 0.62, 0.5, 0.5, 0.85, 0.95, 1.1, 0.45])
    els += e
    els += note(cx, y + 4, cw,
                "Reads inventory_transfers + inventory_transfer_items. A transfer is the only document with two postings: Send writes transfer_out at the SOURCE warehouse's weighted-average cost, "
                "Receive writes transfer_in at that SAME unit cost.\nAn internal move therefore never creates or destroys value — total stock worth is identical before and after. "
                "Goods in transit are shown separately from on-hand and are still OWNED for valuation.\n"
                "＋ New transfer and the draft Edit action both open the drawer on E2 — this list never becomes a form.",
                ACCENT, G)
    return els


def _e2(ox, oy):
    """E2 — Transfer drawer."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "E2.  New transfer — drawer over the transfers list",
                                     "Inventory", g, sub_active="Transfers")
    e, y = page_header(cx, cy, cw, "Transfers", actions=[("＋ New transfer", "primary")],
                       subtitle="3 in transit · 18 units · AFN 142,900", g=G)
    els += e
    e, _ = table(cx, y, cw,
                 ["Transfer", "From", "To", "Sent", "Units", "Received", "Value", "Status"],
                 [["TRF26-0004", "Main Store", "Shar-e-Naw · Floor 2", "12 Sep", "10", "0 of 10", "72,112.50", "in transit"],
                  ["TRF26-0003", "Shar-e-Naw · Floor 2", "Main Store", "11 Sep", "4", "4 of 4", "12,800.00", "completed"],
                  ["TRF26-0002", "Main Store", "Repair Room", "09 Sep", "5", "3 of 5", "58,900.00", "partially received"]],
                 G, row_h=42, widths=[1.1, 1.4, 1.6, 0.7, 0.6, 0.9, 1.0, 1.1])
    els += e

    DW = 820
    de, fx, fy, fw = drawer(ox, oy + TITLE_H, DESK_W, DESK_H, "New transfer  ·  TRF26-0006",
                            side="right", width=DW,
                            subtitle="Cost travels with the goods — an internal move never changes stock worth", g=G)
    els += de

    e, fy = timeline(fx, fy, fw * 0.8,
                     [("Draft", "current"), ("In transit", "todo"), ("Received", "todo")], G)
    els += e
    fy += 12

    c3 = (fw - 24) / 3
    e, _ = _sel(fx, fy, c3, "From branch / warehouse", "Main branch · Main Store", G, True)
    els += e
    els.append(text(fx + c3 + 2, fy + 34, "→", 16, MUTED, g=G))
    e, _ = _sel(fx + c3 + 12, fy, c3, "To branch / warehouse", "Shar-e-Naw · Floor 2", G, True)
    els += e
    e, fy = _inp(fx + 2 * (c3 + 12), fy, c3, "Sent date", "12 Sep 2026", G, True)
    els += e
    e, fy = _inp(fx, fy, fw, "Note", "Event weekend stock — return after 20 Sep", G)
    els += e

    els += _lab(fx, fy, "LINES", G)
    els.append(text(fx + fw - 120, fy - 2, "＋ Add line", 12, ACCENT, "right", 120, G))
    e, fy2 = table(fx, fy + 22, fw,
                   ["Item", "SKU", "Available at source", "Send qty", "Unit cost", "Value", ""],
                   [["Pearl Tiara Set", "ADF26-0102", "6", ("4", ACCENT), "3,200.00", "12,800.00", "✕"],
                    ["Chantilly Veil", "ADF26-0067", "12", ("5", ACCENT), "1,462.50", "7,312.50", "✕"],
                    ["Gold Ball Gown", "ADF26-0043", "1", ("1", ACCENT), "52,000.00", "52,000.00", "✕"]],
                   G, row_h=44, widths=[1.9, 1.1, 1.2, 0.8, 0.95, 1.0, 0.35])
    els += e

    e, _ = money_row(fx + fw - 340, fy2 + 8, 340,
                     [("Lines", "3"), ("Units in transit", "10")],
                     G, total=("Value in transit", "AFN 72,112.50"))
    els += e
    els += note(fx, fy2 + 8, fw * 0.58,
                "Send  → inventory_stock_transactions type=transfer_out (negative) at the\n"
                "SOURCE warehouse's weighted-average cost.\n"
                "Receive → type=transfer_in (positive) at that SAME unit cost.\n"
                "Partial receipt is supported via inventory_transfer_items.received_quantity;\n"
                "the receiving branch confirms from its own Transfers list.",
                ACCENT, G)

    by = oy + TITLE_H + DESK_H - 76
    els += btn(fx, by, 120, 42, "Cancel", "secondary", G)
    els += btn(fx + fw - 300, by, 140, 42, "Save draft", "secondary", G)
    els += btn(fx + fw - 150, by, 150, 42, "Send", "primary", G)
    return els


# ══════════════════════════════════════════════════════════════════
#  F.  REPORTS
# ══════════════════════════════════════════════════════════════════

def _f1(ox, oy):
    """F1 — Valuation report."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F1.  Valuation report — what is my stock worth?",
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
                "'As of' a past date replays inventory_stock_transactions WHERE business_date <= :as_of rather than reading today's balances, so a historical valuation reproduces exactly what the dashboard showed that day.",
                ACCENT, G)
    return els


def _f2(ox, oy):
    """F2 — Stock movement / stock-in by source report."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F2.  Stock movement & stock-in by source",
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


def _f3(ox, oy):
    """F3 — Rental utilisation & asset ROI."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = desk_shell(ox, oy, "F3.  Rental utilisation & asset ROI",
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
    """A1 — dashboard."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "A1. Inventory dashboard", g, "Inventory")
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
    """B1 — items list."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B1. Items list", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Items", right=ICON["filter"], g=G)
    els += e
    els += search_bar(cx, y, cw, "Name, SKU or scan barcode", G)
    y += 50
    els += filter_chips(cx, y, ["All", "Available", "On rent"], 0, G)
    y += 44
    rows = [(["White A-Line Gown", "ADF26-0042 · size M", "Sale 48,000 · rent 9,500"], ("on rent", VIOLET)),
            (["Gold Ball Gown", "ADF26-0043 · size L", "Rent 8,000 · avail 0"], ("reserved", WARN)),
            (["Chantilly Veil", "ADF26-0067 · one size", "Sale 2,400 · avail 12"], ("available", OK)),
            (["Ivory Mermaid Gown", "ADF26-0088 · size S", "Rent 7,200 · avail 1"], ("available", OK)),
            (["Rose Nikah Abaya", "ADF26-0091 · size 38", "Repair — torn bodice"], ("repairing", DANGER))]
    for lines, badge in rows:
        e, y = list_card(cx, y, cw, lines, G, h=76, thumb=True, badge=badge)
        els += e
    els += fab(cx + cw, cy + ch - 130, "＋ New item", G)
    return els


def _m3(ox, oy):
    """B2 — new item sheet."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B2. New item (bottom sheet)", g, "Inventory", show_nav=False)
    els.append(rect(ox + 1, oy + TITLE_H + 96, PHONE_W - 2, PHONE_H - 96, strokeColor=LINE,
                    backgroundColor=BG, strokeWidth=2, groupIds=G))
    sy = oy + TITLE_H + 114
    els.append(text(cx, sy, "New item", 19, INK, width=cw - 40, g=G))
    els.append(text(cx, sy + 24, "Catalogue record only — creates no stock", 10.5, MUTED, width=cw - 20, g=G))
    els.append(text(cx + cw - 20, sy + 2, ICON["cross"], 15, MUTED, g=G))
    y = sy + 50
    for lab, val, req in [("Name", "White A-Line Gown", True), ("Category", "Wedding Dress", True),
                          ("Size / colour", "M / Ivory white", False)]:
        e, y = _inp(cx, y, cw, lab, val, G, req, 34)
        els += e
    e, y = _ro(cx, y, cw, "SKU · barcode · QR", "ADF26-0131  — generated", G, 34)
    els += e
    els.append(rect(cx, y, cw, 104, strokeColor=HAIRLINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=G))
    e, _ = barcode(cx + 10, y + 10, cw - 118, 82, "ADF26-0131", G)
    els += e
    e, _ = qr(cx + cw - 100, y + 12, 86, "ADF26-0131", G)
    els += e
    y += 116
    for lab, val in [("Sale price", "AFN 48,000"), ("Rental price", "AFN 9,500")]:
        e, y = _inp(cx, y, cw, lab, val, G, False, 34)
        els += e
    els += btn(cx, y + 2, cw, 44, "Save item", "primary", G)
    return els


def _m4(ox, oy):
    """B4 — item profile · overview."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B4. Item profile · Overview", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "White A-Line", left=ICON["back"], right="⋯", g=G)
    els += e
    els += filter_chips(cx, y, ["Overview", "Stock", "Bookings"], 0, G)
    y += 42
    els += _photo(cx, y, cw, 128, G, ICON["dress"], "1 of 9 photos")
    y += 140
    ch_, xx = chip(cx, y, "on rent", VIOLET, g=G); els += ch_
    ch_, xx = chip(xx, y, "active", OK, g=G); els += ch_
    ch_, _ = chip(xx, y, "sale + rental", ACCENT, g=G); els += ch_
    y += 32
    els.append(rect(cx, y, cw, 84, strokeColor=HAIRLINE, backgroundColor=SOFT2, strokeWidth=1, groupIds=G))
    for i, (lab, val, col) in enumerate([("On hand", "3", INK), ("On rent", "1", VIOLET),
                                         ("Owned", "4", INK), ("Available", "2", OK)]):
        els += _kv(cx + 14 + i * ((cw - 28) / 4), y + 14, (cw - 28) / 4, lab, val, G, col)
    els.append(text(cx + 14, y + 60, "Avg cost 31,200 · worth AFN 124,800", 10.5, MUTED, width=cw - 28, g=G))
    y += 98
    els.append(text(cx, y, "BARCODE & QR — generated from the SKU", 9.5, MUTED, width=cw, g=G))
    y += 16
    els.append(rect(cx, y, cw, 112, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
    e, _ = barcode(cx + 10, y + 10, cw - 116, 88, "ADF26-0042", G)
    els += e
    e, _ = qr(cx + cw - 98, y + 14, 84, "ADF26-0042", G)
    els += e
    y += 124
    els += btn(cx, y, cw / 2 - 4, 42, "Reserve", "primary", G)
    els += btn(cx + cw / 2 + 4, y, cw / 2 - 4, 42, "🖨 Print label", "secondary", G)
    return els


def _m5(ox, oy):
    """B5 — item profile · stock."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B5. Item profile · Stock", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Stock & movement", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y, "ADF26-0042 · White A-Line Gown", 11, MUTED, width=cw, g=G))
    y += 24
    els.append(text(cx, y, "BY WAREHOUSE", 10, MUTED, width=cw, g=G))
    e, y = table(cx, y + 16, cw, ["Warehouse", "Hand", "Rent", "Avail"],
                 [["Main Store", "2", ("1", VIOLET), ("1", OK)],
                  ["Shar-e-Naw", "1", "0", ("1", OK)],
                  ["Repair Room", "0", "0", "0"]], G, row_h=34, widths=[1.6, 0.6, 0.6, 0.6])
    els += e
    els.append(text(cx, y, "MOVEMENTS", 10, MUTED, width=cw, g=G))
    y += 18
    for typ, qty, col, ref in [("rent_out", "−1", VIOLET, "SO26-0463 · 12 Sep"),
                               ("rent_return", "+1", OK, "SO26-0417 · 09 Aug"),
                               ("rent_out", "−1", VIOLET, "SO26-0417 · 02 Aug"),
                               ("stock_in", "+1", OK, "GRN26-0024 · 27 Jun")]:
        els.append(rect(cx, y, cw, 54, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(text(cx + 14, y + 10, typ, 12.5, col, width=cw - 80, g=G))
        els.append(text(cx + 14, y + 30, ref, 10.5, MUTED, width=cw - 80, g=G))
        els.append(text(cx + cw - 62, y + 16, qty, 17, col, "right", 48, G))
        y += 62
    els.append(rect(cx, y, cw, 52, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 14, y + 9, "Owned 4 = on hand 3 + on rent 1", 11, ACCENT, width=cw - 28, g=G))
    els.append(text(cx + 14, y + 28, "Avg cost 31,200 · worth AFN 124,800", 11, ACCENT, width=cw - 28, g=G))
    return els


def _m6(ox, oy):
    """B6 — item profile · reservations."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B6. Item profile · Reservations", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Reservations", left=ICON["back"], right=ICON["add"], g=G)
    els += e
    els.append(text(cx, y, "ADF26-0042 · 3 active · 1 conflict", 11, MUTED, width=cw, g=G))
    y += 24
    els += filter_chips(cx, y, ["Active", "Fulfilled", "All"], 0, G)
    y += 44
    for res, who, dates, blocked, badge in [
            ("RSV26-0041", "Sara Ahmadi", "19 → 21 Sep", "blocked until 23 Sep", ("active", OK)),
            ("RSV26-0311", "Zainab Haidari", "24 → 26 Sep", "blocked until 28 Sep", ("active", OK)),
            ("RSV26-0314", "Marwa Sadat", "24 → 25 Sep", "overlaps RSV26-0311", ("conflict", DANGER)),
            ("RSV26-0035", "Zainab Karimi", "05 → 07 Sep", "became SO26-000014", ("fulfilled", MUTED))]:
        e, y = list_card(cx, y, cw, [who, f"{res} · {dates}", (blocked, VIOLET, 10.5)],
                         G, h=72, badge=badge)
        els += e
    els += note(cx, y, cw,
                "Reserved is not a stock movement.\nThe ledger only sees the dress when it\nphysically leaves as rent_out.", VIOLET, G)
    return els


def _m7(ox, oy):
    """B7 — item profile · rentals."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B7. Item profile · Rentals", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Rentals", left=ICON["back"], g=G)
    els += e
    els.append(rect(cx, y, cw, 84, strokeColor=OK, backgroundColor=OK_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 16, y + 12, "PAID FOR ITSELF", 10, OK, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 30, "24 rentals · AFN 228,000", 20, OK, width=cw - 32, g=G))
    els.append(text(cx + 16, y + 60, "cost 31,200 fully amortised · ROI 731%", 10.5, OK, width=cw - 32, g=G))
    y += 100
    els.append(text(cx, y, "RENTAL HISTORY", 10, MUTED, width=cw, g=G))
    y += 18
    for order, who, out, back, days, amt, badge in [
            ("SO26-0463", "Nasrin Ahmadi", "12 Sep", "15 Sep", "3", "9,500", ("on rent", VIOLET)),
            ("SO26-0417", "Hosna Rahimi", "02 Aug", "09 Aug", "7", "19,500", ("returned", OK)),
            ("SO26-0388", "Latifa Noor", "18 Jul", "20 Jul", "2", "9,500", ("returned", OK)),
            ("SO26-0244", "Palwasha Zia", "06 Jun", "08 Jun", "2", "9,500", ("claim", DANGER))]:
        e, y = list_card(cx, y, cw, [who, f"{order} · {out} → {back} · {days} d",
                                     (f"AFN {amt}", INK, 11)], G, h=70, badge=badge)
        els += e
    els += note(cx, y, cw,
                "Open period — days come from the dates on\nthe order. The item carries no fixed\nrental period.", WARN, G)
    return els


def _m8(ox, oy):
    """B8 — item profile · photos."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B8. Item profile · Photos", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Photos", left=ICON["back"], right=ICON["add"], g=G)
    els += e
    els.append(text(cx, y, "9 photos · long-press to reorder", 11, MUTED, width=cw, g=G))
    y += 24
    els += _photo(cx, y, cw, 150, G, ICON["dress"], "front-full.jpg")
    cels, _ = chip(cx + 10, y + 10, "is_main", ACCENT, g=G)
    els += cels
    y += 162
    tw = (cw - 16) / 3
    for i in range(6):
        px = cx + (i % 3) * (tw + 8)
        py = y + (i // 3) * (tw + 8)
        els += _photo(px, py, tw, tw, G, ICON["photo"])
    y += 2 * (tw + 8) + 6
    els.append(rect(cx, y, cw, 54, strokeColor=LINE, backgroundColor=SOFT2, strokeWidth=1,
                    strokeStyle="dashed", groupIds=G))
    els.append(text(cx, y + 18, f"{ICON['photo']}   Take photo  ·  Choose from gallery",
                    12, MUTED, "center", cw, G))
    return els


def _m9(ox, oy):
    """B9 — item profile · audit."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "B9. Item profile · Audit", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Audit", left=ICON["back"], right=ICON["filter"], g=G)
    els += e
    els.append(text(cx, y, "37 events · created 04 Feb 2026", 11, MUTED, width=cw, g=G))
    y += 24
    for when, who, what, detail, col in [
            ("12 Sep 14:02", "Zahra Nekzad", "stock posting", "rent_out −1 · SO26-0463", VIOLET),
            ("11 Sep 09:40", "Ahmad Zaki", "field change", "rental_price 9,000 → 9,500", INFO),
            ("08 Sep 17:12", "Ahmad Zaki", "field change", "lifecycle repairing → active", INFO),
            ("05 Sep 11:26", "Zahra Nekzad", "reservation", "RSV26-0311 · 24–26 Sep", WARN),
            ("27 Jun 10:03", "Rahim Sultani", "stock posting", "stock_in +1 · GRN26-0024", VIOLET),
            ("04 Feb 16:20", "Ahmad Zaki", "created", "ADF26-0042", OK)]:
        els.append(rect(cx, y, cw, 66, strokeColor=HAIRLINE, backgroundColor=BG, strokeWidth=1, groupIds=G))
        els.append(rect(cx, y, 3, 66, strokeColor=col, backgroundColor=col, strokeWidth=0, groupIds=G))
        els.append(text(cx + 14, y + 9, what, 12, col, width=cw - 28, g=G))
        els.append(text(cx + 14, y + 27, detail, 11, INK, width=cw - 28, g=G))
        els.append(text(cx + 14, y + 45, f"{when} · {who}", 10, MUTED, width=cw - 28, g=G))
        y += 74
    return els


def _m10(ox, oy):
    """C1 — stock ledger."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C1. Stock ledger", g, "Inventory")
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
    els += fab(cx + cw, cy + ch - 130, "＋ New movement", G)
    return els


def _m11(ox, oy):
    """C2 — stock in sheet."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C2. Stock in (bottom sheet)", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Stock in", left=ICON["back"], g=G)
    els += e
    els.append(text(cx, y, "MSE26-0022 · draft", 11, MUTED, width=cw, g=G))
    y += 24
    e, y = _sel(cx, y, cw, "Warehouse", "Main Store", G, True, 34)
    els += e
    e, y = _sel(cx, y, cw, "Entry type", "Manual in", G, True, 34)
    els += e
    els.append(rect(cx, y, cw, 44, strokeColor=ACCENT, backgroundColor=ACCENT_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 14, y + 14, f"{ICON['search']}   Scan barcode to add a line", 12, ACCENT, width=cw - 28, g=G))
    y += 56
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
    els += btn(cx, y + 66, cw, 44, "Post entry", "primary", G)
    return els


def _m12(ox, oy):
    """C3 — receive PO sheet."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C3. Receive PO (GRN)", g, "Inventory")
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


def _m13(ox, oy):
    """C4 / C5 — adjust & dispose sheet."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "C4/C5. Adjust · Dispose", g, "Inventory")
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


def _m14(ox, oy):
    """D1 — reservations list."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "D1. Reservations", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Reservations", right=ICON["filter"], g=G)
    els += e
    els.append(rect(cx, y, cw, 56, strokeColor=DANGER, backgroundColor=DANGER_BG, strokeWidth=1, groupIds=G))
    els.append(text(cx + 14, y + 10, f"{ICON['alert']}  2 booking conflicts", 12, DANGER, width=cw - 28, g=G))
    els.append(text(cx + 14, y + 30, "Tap to resolve — move dates or swap gown", 10.5, DANGER, width=cw - 28, g=G))
    y += 68
    els += filter_chips(cx, y, ["Active 92", "Conflict 2", "All"], 0, G)
    y += 44
    for res, item, who, dates, badge in [
            ("RSV26-0041", "White A-Line Gown", "Sara Ahmadi", "19 → 21 Sep", ("active", OK)),
            ("RSV26-0040", "Gold Ball Gown", "Maryam Noori", "24 → 26 Sep", ("active", OK)),
            ("RSV26-0314", "White A-Line Gown", "Marwa Sadat", "24 → 25 Sep", ("conflict", DANGER)),
            ("RSV26-0038", "Champagne Ball Gown", "Fatima Rahimi", "01 → 03 Oct", ("active", OK))]:
        e, y = list_card(cx, y, cw, [item, f"{who} · {dates}", (res, MUTED, 10.5)],
                         G, h=72, badge=badge)
        els += e
    els += fab(cx + cw, cy + ch - 130, "＋ Reserve", G)
    return els


def _m15(ox, oy):
    """D3 — availability calendar."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "D3. Availability calendar", g, "Inventory")
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


def _m16(ox, oy):
    """E1 — transfers."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "E1. Transfers", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Transfers", right=ICON["filter"], g=G)
    els += e
    els += filter_chips(cx, y, ["All", "In transit", "Draft"], 1, G)
    y += 44
    for trf, route, units, recv, badge in [
            ("TRF26-0004", "Main Store → Shar-e-Naw", "10 units · AFN 72,112", "0 of 10 received", ("in transit", VIOLET)),
            ("TRF26-0002", "Main Store → Repair Room", "5 units · AFN 58,900", "3 of 5 received", ("partial", WARN)),
            ("TRF26-0003", "Shar-e-Naw → Main Store", "4 units · AFN 12,800", "4 of 4 received", ("completed", OK)),
            ("TRF26-0005", "Repair Room → Main Store", "1 unit · AFN 38,900", "not sent yet", ("draft", MUTED))]:
        e, y = list_card(cx, y, cw, [route, units, (recv, MUTED, 10.5)], G, h=72, badge=badge)
        els += e
    els += note(cx, y, cw,
                "Cost travels with the goods: transfer_out and\ntransfer_in post at the SAME unit cost, so an\ninternal move never changes stock worth.", ACCENT, G)
    els += fab(cx + cw, cy + ch - 130, "＋ New transfer", G)
    return els


def _m17(ox, oy):
    """F — reports."""
    g = nid(); G = [g]
    els, cx, cy, cw, ch = phone_shell(ox, oy, "F1–F3. Reports", g, "Inventory")
    e, y = phone_header(cx, cy, cw, "Reports", left=ICON["back"], g=G)
    els += e
    els += filter_chips(cx, y, ["Valuation", "Movement", "ROI"], 2, G)
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

GROUPS = [
    ("DASHBOARD", [_a1]),
    ("ITEMS", [_b1, _b2, _b3, _b4, _b5, _b6, _b7, _b8, _b9]),
    ("STOCK LEDGER", [_c1, _c2, _c3, _c4, _c5]),
    ("RESERVATIONS", [_d1, _d2, _d3]),
    ("TRANSFERS", [_e1, _e2]),
    ("REPORTS", [_f1, _f2, _f3]),
]

MOBILE_SCREENS = [_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8, _m9,
                  _m10, _m11, _m12, _m13, _m14, _m15, _m16, _m17]


def desktop():
    els = board_title(0, -230, "BOMS Desktop — Inventory",
                      "Read top to bottom: A Dashboard · B Items (list → drawers → the six profile tabs) · "
                      "C Stock ledger · D Reservations · E Transfers · F Reports.\n"
                      "Barcode and QR are generated from the SKU · no Purpose field · rentals have no fixed period · "
                      "every create and edit is a drawer over its list.\n"
                      "Owned = on hand + on rent (valuation) · Available = on hand − reserved · "
                      "reservations are not ledger rows · weighted average cost · immutable postings")
    els += grouped_board(GROUPS, DESK_COLS, colors=SECTION_COLORS)
    return els


def mobile():
    els = board_title(0, -150, "BOMS Mobile — Inventory",
                      "Same order as the desktop board: A dashboard · B items and the profile tabs · "
                      "C ledger · D reservations · E transfers · F reports.")
    for i, fn in enumerate(MOBILE_SCREENS):
        ox, oy = grid_pos(i, PHONE_COLS, PHONE_W, PHONE_H)
        els += fn(ox, oy)
    els += flow_arrows(len(MOBILE_SCREENS), PHONE_COLS, PHONE_W, PHONE_H)
    return els
