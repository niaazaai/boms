#!/usr/bin/env python3
"""Finished Inventory screens — AL DUBAI brand, shadcn-shaped.

Every screen is the same structure as its wireframe in
`specs/wireframes/desktop/02-Inventory.excalidraw`; only the finish differs.
Screen ids match the wireframe ids (A1, B1, B2, B4, B6, C1) so the two can be
read side by side.

`STR` holds every user-visible string once, in English and Dari, so the RTL
screens are the same code with a different table and `Canvas(rtl=True)`.
"""

from __future__ import annotations

from shell import (content_box, drawer, drawer_footer, page_header, sidebar,
                   tabs, topbar)
from svg import (Canvas, barcode, btn, card, chip, field, icon, icon_btn,
                 label_card, line, mono, num, paragraph, qr, rect, stat, table,
                 txt, wrap)
from tokens import C, FRAME_H, FRAME_W, GUTTER, RADIUS, SIDEBAR_W, TYPE

# ── strings ───────────────────────────────────────────────────────

EN = {
    "brand": "AL DUBAI", "brand_sub": "Bridal · BOMS",
    "branch": "Main branch", "user": "Ahmad Zaki", "user_short": "Ahmad",
    "user_initial": "A", "role": "Owner", "language": "English",
    "search_global": "Search items, orders, customers…",
    "MAIN": "MAIN", "OPERATIONS": "OPERATIONS", "MONEY": "MONEY",
    "INSIGHT": "INSIGHT", "SYSTEM": "SYSTEM",

    "inventory": "Inventory", "items": "Items", "stock_ledger": "Stock ledger",
    "reservations": "Reservations", "transfers": "Transfers", "reports": "Reports",

    "dash_sub": "Main branch · all warehouses · as of 12 Sep 2026",
    "export": "Export", "stock_in": "Stock in", "new_item": "New item",
    "stock_worth": "Stock worth", "owned_units": "Owned units",
    "on_hand": "On hand", "on_rent": "On rent", "reserved": "Reserved",
    "available": "Available", "low_stock": "Low stock",
    "c_owned": "owned × avg cost", "c_onhand_onrent": "on hand + on rent",
    "c_warehouse": "in the warehouse", "c_customers": "out with customers",
    "c_reservations": "from reservations", "c_minus": "on hand − reserved",
    "c_reorder": "below reorder level",
    "quick_actions": "QUICK ACTIONS", "recent": "RECENT MOVEMENTS",
    "view_ledger": "View ledger", "low_stock_t": "LOW STOCK",
    "conflicts_t": "BOOKING CONFLICTS · NEXT 30 DAYS",
    "receive_po": "Receive PO", "adjust": "Adjust", "dispose": "Dispose",
    "transfer": "Transfer", "reserve": "Reserve",

    "items_sub": "1,284 owned units · 48 SKUs · Main branch",
    "search_items": "Search SKU, name or scan a barcode",
    "filters": "Filters", "columns": "Columns", "import": "Import CSV",

    "new_item_sub": "Catalogue record only · creates no stock",
    "identity": "IDENTITY — GENERATED, NOT TYPED",
    "sku": "SKU", "barcode": "Barcode", "live_preview": "LIVE PREVIEW",
    "hint_sku": "platform_sequences · ADF{YY}-{0000}",
    "hint_barcode": "Code 128 of the SKU · read-only",
    "item_name": "Item name", "main_cat": "Main category", "sub_cat": "Sub-category",
    "size": "Size", "colour": "Colour", "lifecycle": "Lifecycle status",
    "pricing": "PRICING — AFN",
    "pricing_hint": "Leave a price empty to switch that channel off",
    "sale_price": "Sale price", "rental_price": "Rental price",
    "deposit": "Rental deposit", "late_fee": "Late fee / day",
    "buffer": "Cleaning buffer (days)", "reorder_level": "Reorder level",
    "no_purpose": "No Purpose field and no rental period. The prices decide the "
                  "channel; the booking decides the dates.",
    "more_attrs": "More attributes — fabric, season, quality, components",
    "photos_drop": "Drag photos here · the first becomes the catalogue image",
    "cancel": "Cancel", "save_new": "Save & new", "save_item": "Save item",

    "overview": "Overview", "stock_movement": "Stock & movement",
    "rentals": "Rentals", "photos": "Photos", "audit": "Audit",
    "edit_item": "Edit item",
    "item_title": "White A-Line Gown",
    "item_sub": "SKU ADF26-0042 · Wedding Dress · A-Line · Size M · Bought 04 Feb 2026",
    "attributes": "ATTRIBUTES", "channels": "CHANNELS",
    "stock_by_wh": "STOCK BY WAREHOUSE",
    "label_title": "BARCODE & QR — GENERATED FROM THE SKU",
    "label_sub": "Code 128 · one scan resolves to one item",
    "print_label": "Print label", "download": "Download",
    "owned_eq": "Owned 4 = on hand 3 + on rent 1   ·   Available 2 = on hand 3 − reserved 1",

    "res_sub": "SKU ADF26-0042 · reserved quantity comes from here, never from the ledger",
    "availability": "Availability calendar",
    "active_res": "Active reservations", "reserved_units": "Reserved units",
    "next_booking": "Next booking", "blocked_until": "Blocked until",
    "conflicts": "Conflicts", "fulfilled_year": "Fulfilled this year",
    "conflict_title": "RSV26-0314 overlaps RSV26-0311 on 24–25 Sep",
    "conflict_body": "Only 1 unit is free in Main Store for those dates, so the second "
                     "insert was rejected by the database and parked for a human to resolve.",
    "resolve": "Resolve conflict", "alternatives": "See alternatives",

    "ledger_sub": "Every quantity change. Append-only — corrections are reversing rows.",
    "new_movement": "New movement", "rebuild": "Rebuild balances",
}

FA = {
    "brand": "الدوبی", "brand_sub": "برایدل · BOMS",
    "branch": "شعبه مرکزی", "user": "احمد ذکی", "user_short": "احمد",
    "user_initial": "ا", "role": "مالک", "language": "دری",
    "search_global": "جستجوی اقلام، فرمایش‌ها، مشتریان…",
    "MAIN": "اصلی", "OPERATIONS": "عملیات", "MONEY": "پول",
    "INSIGHT": "تحلیل", "SYSTEM": "سیستم",

    "Home": "خانه", "Inventory": "موجودی", "Sales": "فروش",
    "Procurement": "تدارکات", "Finance": "مالی", "Reports": "گزارش‌ها",
    "Settings": "تنظیمات",
    "Items": "اقلام", "Stock ledger": "دفتر موجودی", "Reservations": "رزروها",
    "Transfers": "انتقالات",

    "inventory": "موجودی", "items": "اقلام", "stock_ledger": "دفتر موجودی",
    "reservations": "رزروها", "transfers": "انتقالات", "reports": "گزارش‌ها",

    "dash_sub": "شعبه مرکزی · تمام انبارها · تا ۱۲ سپتمبر ۲۰۲۶",
    "export": "خروجی", "stock_in": "ورود موجودی", "new_item": "قلم جدید",
    "stock_worth": "ارزش موجودی", "owned_units": "واحدهای در تملک",
    "on_hand": "در انبار", "on_rent": "در کرایه", "reserved": "رزرو شده",
    "available": "قابل دسترس", "low_stock": "کمبود موجودی",
    "c_owned": "در تملک × قیمت اوسط", "c_onhand_onrent": "در انبار + در کرایه",
    "c_warehouse": "در انبار موجود", "c_customers": "نزد مشتریان",
    "c_reservations": "از رزروها", "c_minus": "در انبار − رزرو شده",
    "c_reorder": "زیر حد سفارش مجدد",
    "quick_actions": "اقدامات سریع", "recent": "حرکات اخیر",
    "view_ledger": "مشاهده دفتر", "low_stock_t": "کمبود موجودی",
    "conflicts_t": "تداخل رزرو · ۳۰ روز آینده",
    "receive_po": "رسید فرمایش", "adjust": "تعدیل", "dispose": "ضایعات",
    "transfer": "انتقال", "reserve": "رزرو",

    "items_sub": "۱٬۲۸۴ واحد در تملک · ۴۸ SKU · شعبه مرکزی",
    "search_items": "جستجوی SKU، نام یا سکن بارکد",
    "filters": "فیلترها", "columns": "ستون‌ها", "import": "درون‌ریزی CSV",

    "new_item_sub": "فقط رکورد کتلاگ · موجودی ایجاد نمی‌کند",
    "identity": "شناسه — تولیدشده، نه تایپ‌شده",
    "sku": "SKU", "barcode": "بارکد", "live_preview": "پیش‌نمای زنده",
    "hint_sku": "platform_sequences · ADF{YY}-{0000}",
    "hint_barcode": "Code 128 از روی SKU · فقط خواندنی",
    "item_name": "نام قلم", "main_cat": "کتگوری اصلی", "sub_cat": "زیرکتگوری",
    "size": "سایز", "colour": "رنگ", "lifecycle": "وضعیت قلم",
    "pricing": "قیمت‌گذاری — افغانی",
    "pricing_hint": "قیمت را خالی بگذارید تا آن کانال غیرفعال شود",
    "sale_price": "قیمت فروش", "rental_price": "قیمت کرایه",
    "deposit": "تضمین کرایه", "late_fee": "جریمه تأخیر / روز",
    "buffer": "مهلت پاک‌کاری (روز)", "reorder_level": "حد سفارش مجدد",
    "no_purpose": "فیلد «هدف» و مدت کرایه وجود ندارد. قیمت‌ها کانال را تعیین می‌کنند و "
                  "تاریخ‌ها از رزرو می‌آیند.",
    "more_attrs": "مشخصات بیشتر — تکه، فصل، کیفیت، اجزا",
    "photos_drop": "عکس‌ها را اینجا بکشید · اولی تصویر کتلاگ می‌شود",
    "cancel": "لغو", "save_new": "ذخیره و جدید", "save_item": "ذخیره قلم",

    "overview": "نمای کلی", "stock_movement": "موجودی و حرکات",
    "rentals": "کرایه‌ها", "photos": "عکس‌ها", "audit": "سابقه تغییرات",
    "edit_item": "ویرایش قلم",
    "item_title": "پیراهن سفید ای‌لاین",
    "item_sub": "SKU ADF26-0042 · لباس عروسی · ای‌لاین · سایز M · خریداری ۰۴ فبروری ۲۰۲۶",
    "attributes": "مشخصات", "channels": "کانال‌ها",
    "stock_by_wh": "موجودی به تفکیک انبار",
    "label_title": "بارکد و QR — تولیدشده از روی SKU",
    "label_sub": "Code 128 · یک سکن، یک قلم",
    "print_label": "چاپ لیبل", "download": "دانلود",
    "owned_eq": "۴ در تملک = ۳ در انبار + ۱ در کرایه   ·   ۲ قابل دسترس = ۳ در انبار − ۱ رزرو",

    "res_sub": "SKU ADF26-0042 · مقدار رزرو از اینجا می‌آید، هرگز از دفتر موجودی",
    "availability": "تقویم دسترسی",
    "active_res": "رزروهای فعال", "reserved_units": "واحدهای رزرو شده",
    "next_booking": "رزرو بعدی", "blocked_until": "مسدود تا",
    "conflicts": "تداخل‌ها", "fulfilled_year": "تکمیل‌شده امسال",
    "conflict_title": "RSV26-0314 با RSV26-0311 در ۲۴–۲۵ سپتمبر تداخل دارد",
    "conflict_body": "تنها ۱ واحد در فروشگاه مرکزی برای آن تاریخ‌ها آزاد است، بنابراین درج دوم "
                     "توسط دیتابیس رد شد و برای بررسی انسانی نگه داشته شد.",
    "resolve": "حل تداخل", "alternatives": "دیدن جایگزین‌ها",

    "ledger_sub": "هر تغییر مقدار. فقط افزودنی — اصلاح با سند معکوس.",
    "new_movement": "حرکت جدید", "rebuild": "بازسازی بیلانس‌ها",
}


def T(loc):
    return EN if loc == "en" else {**EN, **FA}


# ── data (identical in both locales; only the words change) ───────

def _items(t, loc):
    en = loc == "en"
    return [
        ["ADF26-0042", "White A-Line Gown" if en else "پیراهن سفید ای‌لاین",
         "Wedding Dress" if en else "لباس عروسی", "M",
         ("active" if en else "فعال", None, "active"),
         ("3", None, None, 1), ("1", None, None, 1), ("2", C["success"], None, 1),
         ("124,800", None, None, 1)],
        ["ADF26-0043", "Gold Ball Gown" if en else "پیراهن مجلسی طلایی",
         "Engagement" if en else "نامزدی", "L",
         ("active" if en else "فعال", None, "active"),
         ("2", None, None, 1), ("2", None, None, 1), ("2", C["success"], None, 1),
         ("110,000", None, None, 1)],
        ["ADF26-0051", "Emerald Engagement Set" if en else "ست نامزدی زمردی",
         "Engagement" if en else "نامزدی", "40",
         ("active" if en else "فعال", None, "active"),
         ("1", None, None, 1), ("0", None, None, 1), ("0", C["danger"], None, 1),
         ("44,000", None, None, 1)],
        ["ADF26-0067", "Chantilly Veil" if en else "تور شانتیلی",
         "Accessories" if en else "لوازم جانبی", "—",
         ("low stock" if en else "کمبود", None, "low stock"),
         ("2", None, None, 1), ("0", None, None, 1), ("2", C["warning"], None, 1),
         ("7,600", None, None, 1)],
        ["ADF26-0088", "Ivory Mermaid Gown" if en else "پیراهن ماهی‌دم عاجی",
         "Wedding Dress" if en else "لباس عروسی", "S",
         ("repairing" if en else "در ترمیم", None, "repairing"),
         ("1", None, None, 1), ("0", None, None, 1), ("0", C["danger"], None, 1),
         ("38,900", None, None, 1)],
        ["ADF26-0091", "Rose Nikah Abaya" if en else "عبای نکاح گلابی",
         "Nikah Wear" if en else "لباس نکاح", "38",
         ("active" if en else "فعال", None, "active"),
         ("4", None, None, 1), ("1", None, None, 1), ("2", C["success"], None, 1),
         ("62,000", None, None, 1)],
        ["ADF26-0102", "Pearl Tiara Set" if en else "ست تاج مرواریدی",
         "Jewellery" if en else "زیورات", "—",
         ("active" if en else "فعال", None, "active"),
         ("1", None, None, 1), ("0", None, None, 1), ("1", C["warning"], None, 1),
         ("6,900", None, None, 1)],
    ]


# ══════════════════════════════════════════════════════════════════
#  A1 · Dashboard
# ══════════════════════════════════════════════════════════════════

def a1_dashboard(loc="en"):
    t = T(loc)
    rtl = loc != "en"
    cv = Canvas(FRAME_W, FRAME_H, rtl=rtl, title=f"BOMS · Inventory dashboard ({loc})")
    sidebar(cv, t, "Inventory", "Items")
    topbar(cv, t)
    x, w = content_box()
    y = page_header(cv, 104, t["inventory"], t["dash_sub"],
                    [(t["export"], "ghost", "download"),
                     (t["stock_in"], "secondary", None),
                     (t["new_item"], "primary", "plus")])

    # KPI row — four tiles, the four numbers the owner actually asks for
    cells = [(t["stock_worth"], "AFN 4.82M", t["c_owned"], "wallet", C["primary"]),
             (t["owned_units"], "1,284", t["c_onhand_onrent"], "package", None),
             (t["on_rent"], "238", t["c_customers"], "clock", C["bronze"]),
             (t["available"], "954", t["c_minus"], "check", C["success"])]
    cw = (w - 3 * 16) / 4
    for i, (lab, val, cap, ic, tone) in enumerate(cells):
        stat(cv, x + i * (cw + 16), y, cw, 116, lab, val, cap, ic, tone)
    y += 140

    LW = w * 0.615
    RW = w - LW - 24
    rx = x + LW + 24

    # quick actions
    txt(cv, x, y, t["quick_actions"], "micro", C["muted"], upper=True)
    tiles = [("package", t["stock_in"]), ("truck", t["receive_po"]),
             ("scale", t["adjust"]), ("trash", t["dispose"]),
             ("transfer", t["transfer"]), ("bookmark", t["reserve"])]
    tw = (LW - 5 * 12) / 6
    for i, (ic, lab) in enumerate(tiles):
        bx = x + i * (tw + 12)
        rect(cv, bx, y + 24, tw, 84, C["surface"], C["border"], RADIUS["tile"])
        icon(cv, bx + (tw - 20) / 2, y + 42, ic, 20, C["primary"], 1.7)
        txt(cv, bx + tw / 2, y + 76, lab, "caption", C["body"], "middle")

    # recent movements
    my = y + 132
    txt(cv, x, my, t["recent"], "micro", C["muted"], upper=True)
    txt(cv, x + LW, my, t["view_ledger"], "caption", C["primary"], "end")
    f = card(cv, x, my + 24, LW, 306)
    en = loc == "en"
    rows = [
        ["12 Sep" if en else "۱۲ سپتمبر", "TRN26-004182",
         "White A-Line Gown" if en else "پیراهن سفید ای‌لاین",
         ("rent out" if en else "خروج کرایه", None, "on rent"),
         ("−1", C["danger"], None, 1)],
        ["12 Sep" if en else "۱۲ سپتمبر", "TRN26-004181",
         "Chantilly Veil" if en else "تور شانتیلی",
         ("stock in" if en else "ورود", None, "available"),
         ("+12", C["success"], None, 1)],
        ["11 Sep" if en else "۱۱ سپتمبر", "TRN26-004179",
         "Gold Ball Gown" if en else "پیراهن مجلسی طلایی",
         ("rent return" if en else "بازگشت کرایه", None, "returned"),
         ("+1", C["success"], None, 1)],
        ["11 Sep" if en else "۱۱ سپتمبر", "TRN26-004176",
         "Pearl Tiara Set" if en else "ست تاج مرواریدی",
         ("transfer" if en else "انتقال", None, "in transit"),
         ("−4", C["danger"], None, 1)],
        ["10 Sep" if en else "۱۰ سپتمبر", "TRN26-004170",
         "Rose Nikah Abaya" if en else "عبای نکاح گلابی",
         ("dispose" if en else "ضایعات", None, "disposed"),
         ("−1", C["danger"], None, 1)],
    ]
    table(cv, x + 1, my + 25, LW - 2,
          [t["stock_worth"][:0] + ("Date" if en else "تاریخ"), "Txn #" if en else "شماره سند",
           "Item" if en else "قلم", "Type" if en else "نوع", "Qty" if en else "مقدار"],
          rows, [0.85, 1.2, 1.9, 1.1, 0.6], row_h=50,
          align=["start", "start", "start", "start", "end"])

    # low stock
    txt(cv, rx, y, t["low_stock_t"], "micro", C["danger"], upper=True)
    card(cv, rx, y + 24, RW, 216)
    table(cv, rx + 1, y + 25, RW - 2,
          ["Item" if en else "قلم", "Avail" if en else "موجود",
           "Reorder" if en else "سفارش"],
          [["Chantilly Veil" if en else "تور شانتیلی", ("2", C["danger"], None, 1), ("10", None, None, 1)],
           ["Pearl Tiara Set" if en else "ست تاج مرواریدی", ("1", C["danger"], None, 1), ("6", None, None, 1)],
           ["Ivory Hair Comb" if en else "شانه موی عاجی", ("0", C["danger"], None, 1), ("8", None, None, 1)]],
          [2.0, 0.8, 0.9], row_h=44, align=["start", "end", "end"])

    # conflicts
    cy = y + 264
    txt(cv, rx, cy, t["conflicts_t"], "micro", C["warning"], upper=True)
    rect(cv, rx, cy + 24, RW, 174, C["warning_bg"], None, RADIUS["card"])
    icon(cv, rx + 24, cy + 46, "alert", 20, C["warning"], 1.8)
    txt(cv, rx + 56, cy + 48, "2 conflicts detected" if en else "۲ تداخل شناسایی شد",
        "body_medium", C["accent_ink"])
    txt(cv, rx + 24, cy + 84,
        "ADF26-0042 · 24–26 Sep" if en else "ADF26-0042 · ۲۴–۲۶ سپتمبر",
        "small", C["body"])
    txt(cv, rx + 24, cy + 106,
        "2 reservations, 1 unit available" if en else "۲ رزرو، ۱ واحد قابل دسترس",
        "caption", C["muted"])
    line(cv, rx + 24, cy + 132, RW - 48, C["accent_2"])
    txt(cv, rx + 24, cy + 144,
        "ADF26-0115 · returns 04 Oct after buffer" if en
        else "ADF26-0115 · بازگشت ۰۴ اکتوبر پس از مهلت", "caption", C["muted"])
    return cv


# ══════════════════════════════════════════════════════════════════
#  B1 · Items list
# ══════════════════════════════════════════════════════════════════

def b1_items(loc="en"):
    t = T(loc)
    en = loc == "en"
    cv = Canvas(FRAME_W, FRAME_H, rtl=not en, title=f"BOMS · Items ({loc})")
    sidebar(cv, t, "Inventory", "Items")
    topbar(cv, t)
    x, w = content_box()
    y = page_header(cv, 104, t["items"], t["items_sub"],
                    [(t["export"], "ghost", "download"),
                     (t["import"], "secondary", None),
                     (t["new_item"], "primary", "plus")])

    # toolbar
    rect(cv, x, y, 460, 44, C["surface"], C["border"], RADIUS["pill"])
    icon(cv, x + 16, y + 13, "search", 18, C["muted"], 1.7)
    txt(cv, x + 46, y + 14, t["search_items"], "body", C["disabled"])
    icon(cv, x + 460 - 40, y + 13, "scan", 18, C["primary"], 1.7)
    btn(cv, x + 476, y, 124, 44, t["filters"], "secondary", "filter")
    btn(cv, x + w - 130, y, 130, 44, t["columns"], "secondary", None)
    y += 60

    # filter chips
    cx = x
    for lab, on in [("All 1,284" if en else "همه ۱٬۲۸۴", True),
                    ("Available 954" if en else "قابل دسترس ۹۵۴", False),
                    ("Reserved 92" if en else "رزرو شده ۹۲", False),
                    ("On rent 238" if en else "در کرایه ۲۳۸", False),
                    ("Repairing 14" if en else "در ترمیم ۱۴", False),
                    ("Low stock 11" if en else "کمبود ۱۱", False)]:
        cx = chip(cv, cx, y, lab,
                  fg=C["primary_fg"] if on else C["body"],
                  bg=C["primary"] if on else C["surface"], h=32)
    y += 52

    card(cv, x, y, w, 500)
    table(cv, x + 1, y + 1, w - 2,
          ["SKU", "Item" if en else "قلم", "Category" if en else "کتگوری",
           "Size" if en else "سایز", "Status" if en else "حالت",
           "On hand" if en else "در انبار", "On rent" if en else "در کرایه",
           "Avail" if en else "آزاد", "Worth (AFN)" if en else "ارزش (AFN)"],
          _items(t, loc), [1.15, 2.1, 1.25, 0.6, 1.0, 0.85, 0.85, 0.85, 1.15],
          row_h=56, align=["start"] * 5 + ["end"] * 4)

    fy = y + 500 - 52
    txt(cv, x + 24, fy + 18,
        "1–7 of 48 SKUs" if en else "۱–۷ از ۴۸ SKU", "caption", C["muted"])
    bx = x + w - 24
    for lab in reversed(["1", "2", "3"]):
        bx -= 36
        rect(cv, bx, fy + 8, 32, 32, C["primary"] if lab == "1" else C["surface"],
             None if lab == "1" else C["border"], RADIUS["sm"])
        txt(cv, bx + 16, fy + 17, lab, "caption",
            C["primary_fg"] if lab == "1" else C["body"], "middle")
    return cv


# ══════════════════════════════════════════════════════════════════
#  B2 · New item drawer
# ══════════════════════════════════════════════════════════════════

def b2_new_item(loc="en"):
    t = T(loc)
    en = loc == "en"
    cv = Canvas(FRAME_W, FRAME_H, rtl=not en, title=f"BOMS · New item drawer ({loc})")
    sidebar(cv, t, "Inventory", "Items")
    topbar(cv, t)
    x, w = content_box()
    page_header(cv, 104, t["items"], t["items_sub"], [(t["new_item"], "primary", "plus")])
    card(cv, x, 240, w, 460)
    table(cv, x + 1, 241, w - 2,
          ["SKU", "Item" if en else "قلم", "Category" if en else "کتگوری",
           "Size" if en else "سایز", "Status" if en else "حالت",
           "On hand" if en else "در انبار", "On rent" if en else "در کرایه",
           "Avail" if en else "آزاد", "Worth (AFN)" if en else "ارزش (AFN)"],
          _items(t, loc)[:6], [1.15, 2.1, 1.25, 0.6, 1.0, 0.85, 0.85, 0.85, 1.15],
          row_h=56, align=["start"] * 5 + ["end"] * 4)

    DW = 560
    fx, fy, fw = drawer(cv, t, t["new_item"], t["new_item_sub"], DW)
    half = (fw - 16) / 2

    fy = field(cv, fx, fy, fw, t["item_name"] + " *", "White A-Line Gown" if en
               else "پیراهن سفید ای‌لاین")

    txt(cv, fx, fy, t["identity"], "micro", C["primary"], upper=True)
    fy += 24
    field(cv, fx, fy, half, t["sku"], "ADF26-0131", locked=True, hint=t["hint_sku"])
    fy = field(cv, fx + half + 16, fy, half, t["barcode"], "Code 128", locked=True,
               hint=t["hint_barcode"])

    # live preview — the two symbols the tag will carry
    rect(cv, fx, fy, fw, 156, C["surface_2"], None, RADIUS["card"])
    txt(cv, fx + 20, fy + 16, t["live_preview"], "micro", C["muted"], upper=True)
    saved, cv.rtl = cv.rtl, False
    bx = (cv.w - fx - fw) + 20 if saved else fx + 20
    barcode(cv, bx, fy + 44, fw - 160, 84, "ADF26-0131")
    qr(cv, bx + fw - 132, fy + 44, 92, "ADF26-0131")
    cv.rtl = saved
    fy += 176

    field(cv, fx, fy, half, t["main_cat"] + " *", "Bridal Dresses" if en
          else "لباس‌های عروسی", chevron=True)
    fy = field(cv, fx + half + 16, fy, half, t["sub_cat"] + " *",
               "A-Line" if en else "ای‌لاین", chevron=True)
    third = (fw - 24) / 3
    field(cv, fx, fy, third, t["size"], "M")
    field(cv, fx + third + 12, fy, third, t["colour"], "Ivory white" if en else "سفید عاجی")
    fy = field(cv, fx + 2 * (third + 12), fy, third, t["lifecycle"],
               "active" if en else "فعال", chevron=True)

    txt(cv, fx, fy, t["pricing"], "micro", C["primary"], upper=True)
    txt(cv, fx + fw, fy, t["pricing_hint"], "caption", C["muted"], "end")
    fy += 24
    field(cv, fx, fy, third, t["sale_price"], "48,000")
    field(cv, fx + third + 12, fy, third, t["rental_price"], "9,500")
    fy = field(cv, fx + 2 * (third + 12), fy, third, t["deposit"], "5,000")

    rect(cv, fx, fy, fw, 64, C["info_bg"], None, RADIUS["control"])
    icon(cv, fx + 18, fy + 21, "alert", 18, C["primary"], 1.7)
    paragraph(cv, fx + 48, fy + 14, t["no_purpose"], 62, "caption", C["body"], 18)
    fy += 80

    rect(cv, fx, fy, fw, 44, C["surface"], C["border"], RADIUS["control"])
    icon(cv, fx + 16, fy + 13, "chevron_right", 18, C["muted"], 1.7)
    txt(cv, fx + 44, fy + 14, t["more_attrs"], "body", C["muted"])

    drawer_footer(cv, t, DW, [(t["cancel"], "secondary"),
                              (t["save_new"], "secondary"),
                              (t["save_item"], "primary")])
    return cv


# ══════════════════════════════════════════════════════════════════
#  B4 · Item profile · Overview
# ══════════════════════════════════════════════════════════════════

def b4_item_profile(loc="en"):
    t = T(loc)
    en = loc == "en"
    cv = Canvas(FRAME_W, FRAME_H, rtl=not en, title=f"BOMS · Item profile ({loc})")
    sidebar(cv, t, "Inventory", "Items")
    topbar(cv, t)
    x, w = content_box()

    txt(cv, x, 96, ("Inventory  /  Items  /  ADF26-0042" if en
                    else "موجودی  /  اقلام  /  ADF26-0042"), "caption", C["muted"])
    y = page_header(cv, 120, t["item_title"], t["item_sub"],
                    [(t["stock_in"], "secondary", None),
                     (t["reserve"], "secondary", "bookmark"),
                     (t["edit_item"], "primary", None)])
    y = tabs(cv, x, y, w, [t["overview"], t["stock_movement"], t["reservations"],
                           t["rentals"], t["photos"], t["audit"]], 0)

    LW = 360
    rx = x + LW + 24
    RW = w - LW - 24

    # gallery
    f = card(cv, x, y, LW, 280)
    rect(cv, x + 16, y + 16, LW - 32, 200, C["surface_2"], None, RADIUS["tile"])
    icon(cv, x + LW / 2 - 16, y + 100, "image", 32, C["disabled"], 1.4)
    for i in range(4):
        tw = (LW - 32 - 3 * 8) / 4
        rect(cv, x + 16 + i * (tw + 8), y + 228, tw, 40, C["surface_2"], None, RADIUS["sm"])
    # barcode + QR card
    label_card(cv, x, y + 300, LW, "ADF26-0042", t["label_sub"], t["label_title"],
               t["print_label"], t["download"])

    # status chips
    cx = rx
    for lab, st in [(t["available"], "available"),
                    ("Lifecycle: active" if en else "وضعیت: فعال", "active"),
                    ("Sale 48,000" if en else "فروش ۴۸٬۰۰۰", None),
                    ("Rental 9,500" if en else "کرایه ۹٬۵۰۰", "on rent"),
                    ("Buffer 2 days" if en else "مهلت ۲ روز", "reserved")]:
        cx = chip(cv, cx, y + 4, lab, st, h=28)

    # attributes
    ay = y + 48
    txt(cv, rx, ay, t["attributes"], "micro", C["muted"], upper=True)
    attrs = [("Main category", "Bridal Dresses"), ("Sub-category", "A-Line"),
             ("Item type", "Wedding Dress"), ("Model", "Elegance 2026"),
             ("Size", "M"), ("Colour", "Ivory white"),
             ("Fabric", "Silk mikado + lace"), ("Season", "Spring 2026"),
             ("Cleaning buffer", "2 days"), ("Expected rental uses", "20"),
             ("Reorder level", "1"), ("Quality", "high")]
    attrs_fa = [("کتگوری اصلی", "لباس‌های عروسی"), ("زیرکتگوری", "ای‌لاین"),
                ("نوع قلم", "لباس عروسی"), ("مودل", "الگانس ۲۰۲۶"),
                ("سایز", "M"), ("رنگ", "سفید عاجی"),
                ("تکه", "ابریشم میکادو + دانتیل"), ("فصل", "بهار ۲۰۲۶"),
                ("مهلت پاک‌کاری", "۲ روز"), ("دفعات متوقعه کرایه", "۲۰"),
                ("حد سفارش مجدد", "۱"), ("کیفیت", "عالی")]
    colw = (RW - 32) / 4
    for i, (k, v) in enumerate(attrs if en else attrs_fa):
        ax = rx + (i % 4) * (colw + 10)
        ay2 = ay + 26 + (i // 4) * 54
        txt(cv, ax, ay2, k, "caption", C["muted"])
        txt(cv, ax, ay2 + 18, v, "body_medium", C["ink"])

    # channels
    chy = ay + 196
    txt(cv, rx, chy, t["channels"], "micro", C["muted"], upper=True)
    card(cv, rx, chy + 22, RW, 152)
    table(cv, rx + 1, chy + 23, RW - 2,
          ["Channel" if en else "کانال", "Enabled by" if en else "فعال‌شده توسط",
           "Price" if en else "قیمت", "Deposit" if en else "تضمین",
           "Late fee" if en else "جریمه تأخیر"],
          [[("Sale" if en else "فروش", C["success"]),
            "sale price is set" if en else "قیمت فروش تعیین شده",
            ("AFN 48,000", None, None, 1), ("—", C["muted"], None, 1), ("—", C["muted"], None, 1)],
           [("Rental" if en else "کرایه", C["bronze"]),
            "rental price is set" if en else "قیمت کرایه تعیین شده",
            ("AFN 9,500", None, None, 1), ("AFN 5,000", None, None, 1),
            ("AFN 500 / day" if en else "AFN 500 / روز", None, None, 1)]],
          [0.9, 1.9, 1.1, 1.0, 1.2], row_h=52,
          align=["start", "start", "end", "end", "end"])

    # stock by warehouse
    sy = chy + 198
    txt(cv, rx, sy, t["stock_by_wh"], "micro", C["muted"], upper=True)
    card(cv, rx, sy + 22, RW, 208)
    table(cv, rx + 1, sy + 23, RW - 2,
          ["Warehouse" if en else "انبار", "On hand" if en else "در انبار",
           "On rent" if en else "در کرایه", "Owned" if en else "در تملک",
           "Rsvd" if en else "رزرو", "Avail" if en else "آزاد",
           "Avg cost" if en else "قیمت اوسط", "Worth" if en else "ارزش"],
          [["Main Store" if en else "فروشگاه مرکزی", ("2", None, None, 1), ("1", None, None, 1),
            ("3", None, None, 1), ("1", None, None, 1), ("1", C["success"], None, 1),
            ("31,200", None, None, 1), ("93,600", None, None, 1)],
           ["Shar-e-Naw" if en else "شهر نو", ("1", None, None, 1), ("0", None, None, 1),
            ("1", None, None, 1), ("0", None, None, 1), ("1", C["success"], None, 1),
            ("31,200", None, None, 1), ("31,200", None, None, 1)],
           [("TOTAL" if en else "مجموع", C["ink"]), ("3", C["ink"], None, 1),
            ("1", C["bronze"], None, 1), ("4", C["ink"], None, 1),
            ("1", C["warning"], None, 1), ("2", C["success"], None, 1),
            ("31,200", C["ink"], None, 1), ("AFN 124,800", C["primary"], None, 1)]],
          [1.6, 0.85, 0.85, 0.85, 0.7, 0.75, 1.05, 1.25], row_h=52,
          align=["start"] + ["end"] * 7)

    ey = sy + 246
    rect(cv, rx, ey, RW, 48, C["info_bg"], None, RADIUS["control"])
    txt(cv, rx + 20, ey + 15, t["owned_eq"], "small", C["primary"])
    return cv


# ══════════════════════════════════════════════════════════════════
#  B6 · Item profile · Reservations
# ══════════════════════════════════════════════════════════════════

def b6_reservations(loc="en"):
    t = T(loc)
    en = loc == "en"
    cv = Canvas(FRAME_W, FRAME_H, rtl=not en, title=f"BOMS · Item reservations ({loc})")
    sidebar(cv, t, "Inventory", "Items")
    topbar(cv, t)
    x, w = content_box()
    txt(cv, x, 96, ("Inventory  /  Items  /  ADF26-0042" if en
                    else "موجودی  /  اقلام  /  ADF26-0042"), "caption", C["muted"])
    y = page_header(cv, 120, t["item_title"], t["res_sub"],
                    [(t["availability"], "secondary", "calendar"),
                     (t["reserve"], "primary", "plus")])
    y = tabs(cv, x, y, w, [t["overview"], t["stock_movement"], t["reservations"],
                           t["rentals"], t["photos"], t["audit"]], 2)

    cells = [(t["active_res"], "3", None, "bookmark", C["warning"]),
             (t["reserved_units"], "1", "of 3 on hand" if en else "از ۳ در انبار",
              "package", None),
             (t["next_booking"], "19 Sep" if en else "۱۹ سپتمبر",
              "Sara Ahmadi" if en else "سارا احمدی", "calendar", C["primary"]),
             (t["blocked_until"], "23 Sep" if en else "۲۳ سپتمبر",
              "incl. 2-day buffer" if en else "شامل ۲ روز مهلت", "clock", C["bronze"]),
             (t["conflicts"], "1", "24–26 Sep" if en else "۲۴–۲۶ سپتمبر",
              "alert", C["danger"])]
    cw = (w - 4 * 16) / 5
    for i, (lab, val, cap, ic, tone) in enumerate(cells):
        stat(cv, x + i * (cw + 16), y, cw, 116, lab, val, cap, ic, tone)
    y += 140

    # conflict banner
    rect(cv, x, y, w, 96, C["danger_bg"], None, RADIUS["card"])
    icon(cv, x + 24, y + 22, "alert", 22, C["danger"], 1.8)
    txt(cv, x + 60, y + 22, t["conflict_title"], "body_medium", C["danger"])
    txt(cv, x + 60, y + 46, t["conflict_body"], "small", C["body"])
    btn(cv, x + w - 320, y + 28, 150, 40, t["alternatives"], "secondary", None)
    btn(cv, x + w - 160, y + 28, 136, 40, t["resolve"], "danger", None)
    y += 120

    card(cv, x, y, w, 400)
    rows = [
        ["RSV26-0041", "19 Sep" if en else "۱۹ سپتمبر", "21 Sep" if en else "۲۱ سپتمبر",
         ("23 Sep" if en else "۲۳ سپتمبر", C["bronze"]),
         "Sara Ahmadi" if en else "سارا احمدی", "SO26-000019",
         ("active" if en else "فعال", None, "active")],
        ["RSV26-0311", "24 Sep" if en else "۲۴ سپتمبر", "26 Sep" if en else "۲۶ سپتمبر",
         ("28 Sep" if en else "۲۸ سپتمبر", C["bronze"]),
         "Zainab Haidari" if en else "زینب حیدری", "SO26-000470",
         ("active" if en else "فعال", None, "active")],
        ["RSV26-0314", "24 Sep" if en else "۲۴ سپتمبر", "25 Sep" if en else "۲۵ سپتمبر",
         ("27 Sep" if en else "۲۷ سپتمبر", C["bronze"]),
         "Marwa Sadat" if en else "مروه سادات", "—",
         ("conflict" if en else "تداخل", None, "conflict")],
        ["RSV26-0035", "05 Sep" if en else "۰۵ سپتمبر", "07 Sep" if en else "۰۷ سپتمبر",
         ("09 Sep" if en else "۰۹ سپتمبر", C["muted"]),
         "Zainab Karimi" if en else "زینب کریمی", "SO26-000014",
         ("fulfilled" if en else "تکمیل‌شده", None, "fulfilled")],
        ["RSV26-0018", "12 Aug" if en else "۱۲ اگست", "14 Aug" if en else "۱۴ اگست",
         ("16 Aug" if en else "۱۶ اگست", C["muted"]),
         "Nargis Amini" if en else "نرگس امینی", "—",
         ("released" if en else "آزاد شده", None, "released")],
    ]
    table(cv, x + 1, y + 1, w - 2,
          ["Reservation" if en else "رزرو", "From" if en else "از", "To" if en else "به",
           "Blocked until" if en else "مسدود تا", "Customer" if en else "مشتری",
           "Order" if en else "فرمایش", "Status" if en else "حالت"],
          rows, [1.15, 0.85, 0.85, 1.1, 1.5, 1.2, 1.0], row_h=58)
    return cv


# ══════════════════════════════════════════════════════════════════
#  C1 · Stock ledger
# ══════════════════════════════════════════════════════════════════

def c1_ledger(loc="en"):
    t = T(loc)
    en = loc == "en"
    cv = Canvas(FRAME_W, FRAME_H, rtl=not en, title=f"BOMS · Stock ledger ({loc})")
    sidebar(cv, t, "Inventory", "Stock ledger")
    topbar(cv, t)
    x, w = content_box()
    y = page_header(cv, 104, t["stock_ledger"], t["ledger_sub"],
                    [(t["export"], "ghost", "download"),
                     (t["rebuild"], "secondary", None),
                     (t["new_movement"], "primary", "plus")])

    rect(cv, x, y, 380, 44, C["surface"], C["border"], RADIUS["pill"])
    icon(cv, x + 16, y + 13, "search", 18, C["muted"], 1.7)
    txt(cv, x + 46, y + 14,
        "Txn # / SKU / reference" if en else "شماره سند / SKU / مرجع", "body", C["disabled"])
    cx = x + 396
    for lab, on in [("All types" if en else "تمام انواع", True),
                    ("Stock in" if en else "ورود", False),
                    ("Stock out" if en else "خروج", False),
                    ("Adjust" if en else "تعدیل", False),
                    ("Transfer" if en else "انتقال", False),
                    ("Rent" if en else "کرایه", False),
                    ("Dispose" if en else "ضایعات", False)]:
        cx = chip(cv, cx, y + 6, lab,
                  fg=C["primary_fg"] if on else C["body"],
                  bg=C["primary"] if on else C["surface"], h=32)
    y += 60

    card(cv, x, y, w, 560)
    rows = []
    src = [("TRN26-004182", "12 Sep", "White A-Line Gown", "rent out", "on rent", "−1", "38,000", "SO26-000019"),
           ("TRN26-004181", "12 Sep", "Chantilly Veil", "stock in", "available", "+12", "1,450", "GRN26-0008"),
           ("TRN26-004179", "11 Sep", "Gold Ball Gown", "rent return", "returned", "+1", "52,000", "SO26-000014"),
           ("TRN26-004178", "11 Sep", "Ivory Mermaid Gown", "stock out", "disposed", "−1", "44,500", "SO26-000017"),
           ("TRN26-004176", "11 Sep", "Pearl Tiara Set", "transfer", "in transit", "−4", "3,200", "TRF26-0003"),
           ("TRN26-004175", "11 Sep", "Pearl Tiara Set", "transfer", "in transit", "+4", "3,200", "TRF26-0003"),
           ("TRN26-004172", "10 Sep", "Champagne Ball Gown", "adjustment", "reserved", "−1", "41,000", "ADJ26-0011"),
           ("TRN26-004170", "10 Sep", "Rose Nikah Abaya", "dispose", "disposed", "−1", "18,600", "DSP26-0004")]
    names_fa = {"White A-Line Gown": "پیراهن سفید ای‌لاین", "Chantilly Veil": "تور شانتیلی",
                "Gold Ball Gown": "پیراهن مجلسی طلایی", "Ivory Mermaid Gown": "پیراهن ماهی‌دم عاجی",
                "Pearl Tiara Set": "ست تاج مرواریدی", "Champagne Ball Gown": "پیراهن مجلسی شامپاینی",
                "Rose Nikah Abaya": "عبای نکاح گلابی"}
    types_fa = {"rent out": "خروج کرایه", "stock in": "ورود موجودی", "rent return": "بازگشت کرایه",
                "stock out": "خروج موجودی", "transfer": "انتقال", "adjustment": "تعدیل",
                "dispose": "ضایعات"}
    months_fa = {"12 Sep": "۱۲ سپتمبر", "11 Sep": "۱۱ سپتمبر", "10 Sep": "۱۰ سپتمبر"}
    for txn, date, item, ty, st, qty, cost, ref in src:
        rows.append([txn, date if en else months_fa[date],
                     item if en else names_fa[item],
                     (ty if en else types_fa[ty], None, st),
                     (qty, C["danger"] if qty.startswith("−") else C["success"], None, 1),
                     (cost, None, None, 1), ref])
    table(cv, x + 1, y + 1, w - 2,
          ["Txn #" if en else "شماره سند", "Date" if en else "تاریخ",
           "Item" if en else "قلم", "Type" if en else "نوع", "Qty" if en else "مقدار",
           "Unit cost" if en else "قیمت واحد", "Reference" if en else "مرجع"],
          rows, [1.3, 0.9, 2.0, 1.2, 0.7, 1.0, 1.3], row_h=58,
          align=["start", "start", "start", "start", "end", "end", "start"])
    return cv
