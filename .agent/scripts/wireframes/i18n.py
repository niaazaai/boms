#!/usr/bin/env python3
"""BOMS wireframe localisation — Dari (fa) and Pashto (ps).

The localised boards are the SAME drawing as the English one, mirrored by
`dsl.mirror()` and then run through `localise()`. Building them by reflection
and substitution rather than by hand means one layout change updates all three
boards, and the Dari board can never quietly drift from the English one.

What is translated
    Everything a shop assistant reads: navigation, page titles, buttons, tabs,
    field labels, table headers, status chips, KPI captions, sample data.

What is NOT translated
    1. The green/violet `note()` boxes. They are developer annotations naming
       real tables, columns and SQL — `inventory_stock_transactions` is not a
       word anyone should translate. `dsl.note()` tags them `spec`.
    2. Numbers, money amounts, SKUs, barcodes, transaction numbers and times.
       These keep reading left-to-right inside right-to-left text, which is the
       correct typographic behaviour and the rule in `specs/wireframes/README`.

Type
    Dari and Pashto UI is set in **Vazirmatn**. Excalidraw cannot embed a custom
    font — its `fontFamily` is a small enum — so the boards use the sans-serif
    face (2) and the shipped UI plus the hi-fi design in `specs/design/` use
    Vazirmatn proper. `specs/design/tokens/` carries the exact stack.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsl import _measure  # noqa: E402

# ── shared across both Perso-Arabic locales ───────────────────────
# People, places, product names and Gregorian months are written the same way
# in Dari and Pashto, so they live here once.

SHARED = {
    # people
    "Ahmad Zaki": "احمد ذکی", "Ahmad": "احمد", "Zahra Nekzad": "زهرا نیک‌زاد",
    "Zahra": "زهرا", "Rahim Sultani": "رحیم سلطانی", "Sara Ahmadi": "سارا احمدی",
    "Maryam Noori": "مریم نوری", "Marwa Sadat": "مروه سادات",
    "Fatima Rahimi": "فاطمه رحیمی", "Zainab Karimi": "زینب کریمی",
    "Zainab Haidari": "زینب حیدری", "Nargis Amini": "نرگس امینی",
    "Farida Wali": "فریده ولی", "Nasrin Ahmadi": "نسرین احمدی",
    "Hosna Rahimi": "حسنا رحیمی", "Latifa Noor": "لطیفه نور",
    "Malika Sabir": "ملکه صابر", "Shakila Amiri": "شکیلا امیری",
    "Palwasha Zia": "پلوشه ضیا",
    # brand & places
    "BOMS": "BOMS", "Al Dubai Bridal": "الدوبی برایدل",
    "Main Store": "فروشگاه مرکزی", "Shar-e-Naw": "شهر نو",
    "Shar-e-Naw Branch": "شعبه شهر نو", "Shar-e-Naw · Floor 2": "شهر نو · منزل ۲",
    "Repair Room": "اتاق ترمیم", "Istanbul Bridal Co.": "شرکت عروسی استانبول",
    # product names
    "White A-Line Gown": "پیراهن سفید ای‌لاین", "White A-Line": "پیراهن سفید",
    "Gold Ball Gown": "پیراهن مجلسی طلایی",
    "Emerald Engagement Set": "ست نامزدی زمردی", "Emerald Set": "ست زمردی",
    "Chantilly Veil": "تور شانتیلی", "Ivory Mermaid Gown": "پیراهن ماهی‌دم عاجی",
    "Rose Nikah Abaya": "عبای نکاح گلابی", "Pearl Tiara Set": "ست تاج مرواریدی",
    "Champagne Ball Gown": "پیراهن مجلسی شامپاینی", "Champagne Gown": "پیراهن شامپاینی",
    "Bridal Gloves (S)": "دستکش عروس (S)", "Ivory Hair Comb": "شانه موی عاجی",
    "Blush Tulle Gown": "پیراهن تور گلابی", "Sapphire Gown": "پیراهن یاقوتی",
    "Elegance 2026": "الگانس ۲۰۲۶", "Silk mikado + lace": "ابریشم میکادو + دانتیل",
    "Silk mikado": "ابریشم میکادو", "Ivory white": "سفید عاجی", "A-Line": "ای‌لاین",
    "One size": "یک سایز", "One size ": "یک سایز",
    # months (Gregorian, as used in Afghanistan)
    "Jan": "جنوری", "Feb": "فبروری", "Mar": "مارچ", "Apr": "اپریل", "May": "می",
    "Jun": "جون", "Jul": "جولای", "Aug": "اگست", "Sep": "سپتمبر", "Oct": "اکتوبر",
    "Nov": "نومبر", "Dec": "دسمبر",
    "Spring 2026": "بهار ۲۰۲۶",
    # currency / units that stay as codes
    "AFN": "AFN", "USD": "USD", "SKU": "SKU", "QR = SKU": "QR = SKU",
    "Code 128": "Code 128",
}

# ── Dari (fa) ─────────────────────────────────────────────────────

FA = {
    # ledger type names — these are chips a shop assistant reads, so they are
    # translated here even though the spec notes keep the enum spelling
    "stock_in": "ورود موجودی", "stock_out": "خروج موجودی",
    "transfer_in": "انتقال ورودی", "transfer_out": "انتقال خروجی",
    "rent_out": "خروج کرایه", "rent_return": "بازگشت کرایه", "dispose": "ضایعات",
    "rent_out ledger →": "→ دفتر خروج کرایه",
    # composed strings the fragment pass cannot get word order right for
    "1–8 of 48 SKUs · 1,284 owned units · AFN 4.82M worth":
        "۱–۸ از ۴۸ SKU · ۱٬۲۸۴ واحد در تملک · ارزش AFN 4.82M",
    "1–9 of 4,182 transactions": "۱–۹ از ۴٬۱۸۲ سند",
    "1–6 of 92 active reservations": "۱–۶ از ۹۲ رزرو فعال",
    "1–7 of 37 events": "۱–۷ از ۳۷ رویداد",
    "37 events · created 04 Feb 2026": "۳۷ رویداد · ایجاد ۰۴ فبروری ۲۰۲۶",
    "31,200 (held)": "۳۱٬۲۰۰ (نگه‌داشته)",
    "ADF26-0131  — generated": "ADF26-0131  — تولیدشده",
    "GRN26-0009 · PO26-000012\nIstanbul Bridal Co. · USD @ 70.50":
        "GRN26-0009 · PO26-000012\nشرکت عروسی استانبول · USD @ 70.50",
    "Inventory  /  Items  /  ADF26-0042": "موجودی  /  اقلام  /  ADF26-0042",
    "M / Ivory white": "M / سفید عاجی", "MSE26-0022 · draft": "MSE26-0022 · مسوده",
    "Value in": "ارزش ورودی", "Value in transit": "ارزش در راه",
    "0 of 10 received": "۰ از ۱۰ رسید شده", "3 of 5 received": "۳ از ۵ رسید شده",
    "4 of 4 received": "۴ از ۴ رسید شده", "22 of 22": "۲۲ از ۲۲",
    "94 of 148": "۹۴ از ۱۴۸",
    # shell & navigation
    "Home": "خانه", "Inventory": "موجودی", "Sales": "فروش",
    "Procurement": "تدارکات", "Finance": "مالی", "Reports": "گزارش‌ها",
    "Settings": "تنظیمات", "More": "بیشتر", "Owner": "مالک",
    "MAIN": "اصلی", "OPERATIONS": "عملیات", "MONEY": "پول",
    "INSIGHT": "تحلیل", "SYSTEM": "سیستم",
    "🏬  Main branch  ▾": "شعبه مرکزی  ▾  🏬",
    "🌐 English ▾    🔔 3    👤 Ahmad ▾": "دری  🌐    ۳  🔔    احمد  👤",
    "🔒 boms.app/inventory": "🔒 boms.app/inventory",
    "Main branch · Main Store": "شعبه مرکزی · فروشگاه مرکزی",

    # sub-nav
    "Items": "اقلام", "  Items": "  اقلام", "• Items": "• اقلام",
    "Stock ledger": "دفتر موجودی", "  Stock ledger": "  دفتر موجودی",
    "• Stock ledger": "• دفتر موجودی",
    "Reservations": "رزروها", "  Reservations": "  رزروها",
    "• Reservations": "• رزروها",
    "Transfers": "انتقالات", "  Transfers": "  انتقالات", "• Transfers": "• انتقالات",
    "  Reports": "  گزارش‌ها", "• Reports": "• گزارش‌ها",

    # section headings on the board
    "A.  DASHBOARD": "الف.  داشبورد",
    "B.  ITEMS": "ب.  اقلام",
    "C.  STOCK LEDGER": "ج.  دفتر موجودی",
    "D.  RESERVATIONS": "د.  رزروها",
    "E.  TRANSFERS": "هـ.  انتقالات",
    "F.  REPORTS": "و.  گزارش‌ها",

    # board & screen titles
    "BOMS Desktop — Inventory": "BOMS دسکتاپ — موجودی (دری)",
    "BOMS Mobile — Inventory": "BOMS موبایل — موجودی (دری)",
    "A1.  Inventory dashboard — stock at a glance": "الف۱.  داشبورد موجودی — یک نگاه به موجودی",
    "A1. Inventory dashboard": "الف۱. داشبورد موجودی",
    "B1.  Items list — catalogue with the three buckets": "ب۱.  فهرست اقلام — کتلاگ با سه شمارنده",
    "B1. Items list": "ب۱. فهرست اقلام",
    "B2.  New item — drawer over the items list": "ب۲.  قلم جدید — کشو روی فهرست اقلام",
    "B2. New item (bottom sheet)": "ب۲. قلم جدید (ورقهٔ پایینی)",
    "B3.  Edit item — same drawer, identity locked": "ب۳.  ویرایش قلم — همان کشو، شناسه قفل",
    "B4.  Item profile · Overview — attributes, label, stock":
        "ب۴.  پروفایل قلم · نمای کلی — مشخصات، لیبل، موجودی",
    "B4. Item profile · Overview": "ب۴. پروفایل قلم · نمای کلی",
    "B5.  Item profile · Stock & movement (WAC history)":
        "ب۵.  پروفایل قلم · موجودی و حرکات (تاریخچه قیمت اوسط)",
    "B5. Item profile · Stock": "ب۵. پروفایل قلم · موجودی",
    "B6.  Item profile · Reservations — who has booked this dress":
        "ب۶.  پروفایل قلم · رزروها — چه کسی این پیراهن را رزرو کرده",
    "B6. Item profile · Reservations": "ب۶. پروفایل قلم · رزروها",
    "B7.  Item profile · Rentals — history, earnings, payback":
        "ب۷.  پروفایل قلم · کرایه‌ها — تاریخچه، عاید، بازگشت سرمایه",
    "B7. Item profile · Rentals": "ب۷. پروفایل قلم · کرایه‌ها",
    "B8.  Item profile · Photos — gallery, main photo, condition shots":
        "ب۸.  پروفایل قلم · عکس‌ها — گالری، عکس اصلی، عکس‌های وضعیت",
    "B8. Item profile · Photos": "ب۸. پروفایل قلم · عکس‌ها",
    "B9.  Item profile · Audit — every change, who and when":
        "ب۹.  پروفایل قلم · سابقه تغییرات — هر تغییر، توسط کی و چه وقت",
    "B9. Item profile · Audit": "ب۹. پروفایل قلم · سابقه تغییرات",
    "C1.  Stock ledger — immutable movement history": "ج۱.  دفتر موجودی — تاریخچهٔ غیرقابل تغییر حرکات",
    "C1. Stock ledger": "ج۱. دفتر موجودی",
    "C2.  Stock in — drawer over the ledger (manual / opening)":
        "ج۲.  ورود موجودی — کشو روی دفتر (دستی / افتتاحیه)",
    "C2. Stock in (bottom sheet)": "ج۲. ورود موجودی (ورقهٔ پایینی)",
    "C3.  Receive against PO (GRN) — drawer over the ledger":
        "ج۳.  رسید در برابر فرمایش خرید — کشو روی دفتر",
    "C3. Receive PO (GRN)": "ج۳. رسید فرمایش خرید",
    "C4.  Stock adjustment — drawer over the ledger": "ج۴.  تعدیل موجودی — کشو روی دفتر",
    "C4/C5. Adjust · Dispose": "ج۴/ج۵. تعدیل · ضایعات",
    "C5.  Dispose — drawer over the ledger (write-off)": "ج۵.  ضایعات — کشو روی دفتر (حذف از موجودی)",
    "D1.  Reservations — every booking in the shop": "د۱.  رزروها — تمام رزروهای فروشگاه",
    "D1. Reservations": "د۱. رزروها",
    "D2.  New reservation — drawer + double-booking guard":
        "د۲.  رزرو جدید — کشو + محافظ رزرو دوگانه",
    "D3.  Availability calendar — reserved / on rent / buffer":
        "د۳.  تقویم دسترسی — رزرو شده / در کرایه / مهلت پاک‌کاری",
    "D3. Availability calendar": "د۳. تقویم دسترسی",
    "E1.  Transfers — stock moving between warehouses": "هـ۱.  انتقالات — حرکت موجودی میان انبارها",
    "E1. Transfers": "هـ۱. انتقالات",
    "E2.  New transfer — drawer over the transfers list": "هـ۲.  انتقال جدید — کشو روی فهرست انتقالات",
    "F1.  Valuation report — what is my stock worth?": "و۱.  گزارش ارزیابی — ارزش موجودی من چند است؟",
    "F1–F3. Reports": "و۱–و۳. گزارش‌ها",
    "F2.  Stock movement & stock-in by source": "و۲.  حرکت موجودی و ورود بر اساس منبع",
    "F3.  Rental utilisation & asset ROI": "و۳.  بهره‌برداری کرایه و بازگشت سرمایه",

    # board subtitles
    "Read top to bottom: A Dashboard · B Items (list → drawers → the six profile tabs) · C Stock ledger · D Reservations · E Transfers · F Reports.\n"
    "Barcode and QR are generated from the SKU · no Purpose field · rentals have no fixed period · every create and edit is a drawer over its list.\n"
    "Owned = on hand + on rent (valuation) · Available = on hand − reserved · reservations are not ledger rows · weighted average cost · immutable postings":
        "از بالا به پایین بخوانید: الف داشبورد · ب اقلام (فهرست ← کشوها ← شش زبانهٔ پروفایل) · ج دفتر موجودی · د رزروها · هـ انتقالات · و گزارش‌ها.\n"
        "بارکد و QR از روی SKU ساخته می‌شوند · فیلد «هدف» وجود ندارد · کرایه مدت ثابت ندارد · هر ایجاد و ویرایش در کشو روی فهرست خودش باز می‌شود.\n"
        "در تملک = در انبار + در کرایه (مبنای ارزیابی) · قابل دسترس = در انبار − رزرو شده · رزروها سطر دفتر نیستند · قیمت اوسط وزنی · اسناد ثبت‌شده تغییرناپذیر",
    "Same order as the desktop board: A dashboard · B items and the profile tabs · C ledger · D reservations · E transfers · F reports.":
        "به همان ترتیب تختهٔ دسکتاپ: الف داشبورد · ب اقلام و زبانه‌های پروفایل · ج دفتر · د رزروها · هـ انتقالات · و گزارش‌ها.",

    # page headers & subtitles
    "Al Dubai Bridal · Main branch · all warehouses · as of 12 Sep 2026":
        "الدوبی برایدل · شعبه مرکزی · تمام انبارها · تا ۱۲ سپتمبر ۲۰۲۶",
    "1,284 owned units · 48 SKUs · Main branch": "۱٬۲۸۴ واحد در تملک · ۴۸ SKU · شعبه مرکزی",
    "1,284 owned units · 48 SKUs": "۱٬۲۸۴ واحد در تملک · ۴۸ SKU",
    "Inventory valuation": "ارزیابی موجودی",
    "Availability — White A-Line Gown": "دسترسی — پیراهن سفید ای‌لاین",
    "Stock movement": "حرکت موجودی",
    "Rental utilisation & asset ROI": "بهره‌برداری کرایه و بازگشت سرمایه",
    "Adjust stock": "تعدیل موجودی",
    "Availability": "دسترسی",
    "Audit": "سابقه تغییرات",
    "Photos": "عکس‌ها",
    "Rentals": "کرایه‌ها",
    "Stock & movement": "موجودی و حرکات",
    "Overview": "نمای کلی",
    "Receive": "رسید",
    "Stock in": "ورود موجودی",
    "Every quantity change in the system. Append-only — corrections are reversing rows.":
        "هر تغییر مقدار در سیستم. فقط افزودنی — اصلاح با سند معکوس انجام می‌شود.",
    "Append-only. Corrections are reversing rows, never edits.":
        "فقط افزودنی. اصلاح با سند معکوس، هرگز با ویرایش.",
    "Reserved quantity comes from here — never from the stock ledger":
        "مقدار رزرو شده از اینجا می‌آید — هرگز از دفتر موجودی",
    "Move stock between warehouses or branches. Cost travels with the goods.":
        "انتقال موجودی میان انبارها یا شعبه‌ها. قیمت همراه مال حرکت می‌کند.",
    "Correct on-hand quantity after a physical count. Not the same as Dispose.":
        "اصلاح مقدار موجود پس از شمارش فزیکی. با ضایعات فرق دارد.",
    "Remove goods from stock permanently and book the loss":
        "حذف دایمی مال از موجودی و ثبت ضرر",
    "Owned quantity × weighted average cost, in AFN":
        "مقدار در تملک × قیمت اوسط وزنی، به افغانی",
    "Has each dress paid for itself? · since acquisition · AFN":
        "آیا هر پیراهن قیمت خود را برگردانده؟ · از زمان خرید · افغانی",
    "01 Sep – 12 Sep 2026 · all warehouses": "۰۱ سپتمبر – ۱۲ سپتمبر ۲۰۲۶ · تمام انبارها",
    "92 active · 2 conflicts": "۹۲ فعال · ۲ تداخل",
    "3 in transit · 18 units · AFN 142,900": "۳ در راه · ۱۸ واحد · AFN 142,900",
    "SKU ADF26-0042 · Wedding Dress · A-Line · Size M · Bought 04 Feb 2026":
        "SKU ADF26-0042 · لباس عروسی · ای‌لاین · سایز M · خریداری ۰۴ فبروری ۲۰۲۶",
    "SKU ADF26-0042 · weighted average cost per (item, warehouse)":
        "SKU ADF26-0042 · قیمت اوسط وزنی به تفکیک (قلم، انبار)",
    "SKU ADF26-0042 · owned 4 · reserved quantity comes from here, never from the ledger":
        "SKU ADF26-0042 · ۴ در تملک · مقدار رزرو از اینجا می‌آید، نه از دفتر",
    "SKU ADF26-0042 · has this dress paid for itself? · AFN":
        "SKU ADF26-0042 · آیا این پیراهن قیمت خود را برگردانده؟ · افغانی",
    "SKU ADF26-0042 · 9 photos · drag to reorder · first photo is the catalogue image":
        "SKU ADF26-0042 · ۹ عکس · برای ترتیب بکشید · عکس اول تصویر کتلاگ است",
    "SKU ADF26-0042 · created 04 Feb 2026 by Ahmad Zaki · 37 recorded events":
        "SKU ADF26-0042 · ایجاد ۰۴ فبروری ۲۰۲۶ توسط احمد ذکی · ۳۷ رویداد ثبت‌شده",
    "ADF26-0042 · owned 4 · on hand 3 · cleaning buffer 2 days after every return":
        "ADF26-0042 · ۴ در تملک · ۳ در انبار · ۲ روز مهلت پاک‌کاری پس از هر بازگشت",
    "White A-Line Gown · ADF26-0042 · 1 owned": "پیراهن سفید ای‌لاین · ADF26-0042 · ۱ در تملک",
    "ADF26-0042 · White A-Line Gown": "ADF26-0042 · پیراهن سفید ای‌لاین",
    "ADF26-0042 · 3 active · 1 conflict": "ADF26-0042 · ۳ فعال · ۱ تداخل",
    "White A-Line Gown · editing the catalogue record never moves stock":
        "پیراهن سفید ای‌لاین · ویرایش رکورد کتلاگ هرگز موجودی را حرکت نمی‌دهد",
    "Catalogue record only · creates NO stock · barcode and QR are generated from the SKU":
        "فقط رکورد کتلاگ · هیچ موجودی ایجاد نمی‌کند · بارکد و QR از روی SKU ساخته می‌شوند",
    "Catalogue record only — creates no stock": "فقط رکورد کتلاگ — موجودی ایجاد نمی‌کند",
    "Opening stock or an ad-hoc stock-in with no purchase order · draft":
        "موجودی افتتاحیه یا ورود موردی بدون فرمایش خرید · مسوده",
    "PO26-000012 · Istanbul Bridal Co. · ordered 02 Sep 2026 · draft":
        "PO26-000012 · شرکت عروسی استانبول · فرمایش ۰۲ سپتمبر ۲۰۲۶ · مسوده",
    "Holds a dress for a customer · writes inventory_reservations only · no stock moves":
        "یک پیراهن را برای مشتری نگه می‌دارد · فقط در inventory_reservations می‌نویسد · موجودی حرکت نمی‌کند",
    "Cost travels with the goods — an internal move never changes stock worth":
        "قیمت همراه مال حرکت می‌کند — انتقال داخلی ارزش موجودی را تغییر نمی‌دهد",
    "Torn bodice — SO26-000009": "بالاتنه پاره — SO26-000009",
    "Quarterly count — aisle 3": "شمارش ربعوار — راهرو ۳",
    "Sept stock take": "شمارش موجودی سپتمبر",
    "Event weekend stock — return after 20 Sep": "موجودی آخر هفتهٔ مراسم — بازگشت پس از ۲۰ سپتمبر",
    "Engagement — needs the long veil too": "نامزدی — تور دراز هم لازم است",
    "Repair — torn bodice": "ترمیم — بالاتنه پاره",

    # buttons & actions
    "Cancel": "لغو", "Save item": "ذخیره قلم", "Save changes": "ذخیره تغییرات",
    "Save & new": "ذخیره و جدید", "Save draft": "ذخیره مسوده",
    "Post entry": "ثبت سند", "Post receipt": "ثبت رسید",
    "Post adjustment": "ثبت تعدیل", "Post disposal": "ثبت ضایعات",
    "Reserve dates": "رزرو تاریخ‌ها", "Send": "ارسال", "Run": "اجرا",
    "Back": "بازگشت", "Edit": "ویرایش", "View": "مشاهده", "Resolve": "حل تداخل",
    "Reorder": "ترتیب مجدد", "Reprint label": "چاپ مجدد لیبل",
    "Edit item": "ویرایش قلم", "Edit item · ADF26-0042": "ویرایش قلم · ADF26-0042",
    "New item": "قلم جدید", "New reservation": "رزرو جدید",
    "New transfer  ·  TRF26-0006": "انتقال جدید  ·  TRF26-0006",
    "Stock in  ·  MSE26-0022": "ورود موجودی  ·  MSE26-0022",
    "Receive goods  ·  GRN26-0009": "رسید اجناس  ·  GRN26-0009",
    "Stock adjustment  ·  ADJ26-0012": "تعدیل موجودی  ·  ADJ26-0012",
    "Dispose stock  ·  DSP26-0005": "ضایعات موجودی  ·  DSP26-0005",
    "Import CSV": "درون‌ریزی CSV", "Rebuild balances": "بازسازی بیلانس‌ها",
    "Calendar view": "نمای تقویم", "Availability calendar": "تقویم دسترسی",
    "Open rental order": "باز کردن فرمایش کرایه",
    "Choose another date": "انتخاب تاریخ دیگر", "Pick alternative": "انتخاب جایگزین",
    "Columns ▾": "ستون‌ها ▾", "Month ▾": "ماه ▾", "Filter ▾": "فیلتر ▾",
    "Warehouse: All ▾": "انبار: همه ▾",
    "‹ Prev": "قبلی ›", "Next ›": "‹ بعدی",
    "☰  Filters": "فیلترها  ☰", "☰": "☰",
    "⬇ Export": "خروجی ⬇", "⬇ Export CSV": "خروجی CSV ⬇",
    "⬇ Export ledger": "خروجی دفتر ⬇", "⬇ Download": "دانلود ⬇",
    "⬆ Upload photos": "بارگذاری عکس ⬆",
    "🖨 Print": "چاپ 🖨", "🖨 Print label": "چاپ لیبل 🖨",
    "＋ New item": "قلم جدید ＋", "＋ New movement": "حرکت جدید ＋",
    "＋ New transfer": "انتقال جدید ＋", "＋ Reserve": "رزرو ＋",
    "＋ Reserve these dates": "این تاریخ‌ها را رزرو کن ＋",
    "＋ Add line": "افزودن سطر ＋", "＋ Add photo": "افزودن عکس ＋", "＋ Add": "افزودن ＋",
    "View ledger →": "→ مشاهده دفتر",
    "Reserve": "رزرو", "Receive PO": "رسید فرمایش", "Adjust": "تعدیل",
    "Dispose": "ضایعات", "Transfer": "انتقال",

    # search placeholders
    "🔍  Search SKU, name, barcode, model…": "جستجوی SKU، نام، بارکد، مودل…  🔍",
    "🔍  Search SKU, name, barcode…": "جستجوی SKU، نام، بارکد…  🔍",
    "🔍  Txn # / SKU / reference document": "شماره سند / SKU / سند مرجع  🔍",
    "🔍  SKU / customer / order #": "SKU / مشتری / شماره فرمایش  🔍",
    "🔍  Transfer # / item / warehouse": "شماره انتقال / قلم / انبار  🔍",
    "🔍  Name, SKU or scan barcode": "نام، SKU یا سکن بارکد  🔍",
    "🔍   Scan a barcode or QR to add a line": "برای افزودن سطر بارکد یا QR را سکن کنید   🔍",
    "🔍   Scan barcode to add a line": "برای افزودن سطر بارکد را سکن کنید   🔍",
    "🔍   or scan the garment barcode / QR": "یا بارکد / QR لباس را سکن کنید   🔍",

    # KPI labels
    "Stock worth": "ارزش موجودی", "Total stock worth": "مجموع ارزش موجودی",
    "TOTAL STOCK WORTH": "مجموع ارزش موجودی",
    "Owned units": "واحدهای در تملک", "On hand": "در انبار", "On rent": "در کرایه",
    "Reserved": "رزرو شده", "Available": "قابل دسترس", "Low stock": "کمبود موجودی",
    "Owned": "در تملک", "Avail": "قابل دسترس", "Rsvd": "رزرو",
    "Avg cost": "قیمت اوسط", "Avg cost (WAC)": "قیمت اوسط وزنی",
    "Avg unit cost": "قیمت اوسط واحد", "Worth": "ارزش",
    "Active reservations": "رزروهای فعال", "Reserved units": "واحدهای رزرو شده",
    "Next booking": "رزرو بعدی", "Blocked until": "مسدود تا",
    "Conflicts": "تداخل‌ها", "Fulfilled this year": "تکمیل‌شده امسال",
    "Times rented": "دفعات کرایه", "Rental revenue": "عاید کرایه",
    "Amortised so far": "مستهلک‌شده تا اکنون", "Payback": "بازگشت سرمایه",
    "ROI": "بازگشت سرمایه", "ROI %": "٪ بازگشت سرمایه", "Idle days": "روزهای بیکار",
    "In transit": "در راه", "Value in transit": "ارزش در راه",
    "Awaiting receipt": "منتظر رسید", "Completed (30 d)": "تکمیل‌شده (۳۰ روز)",
    "Active": "فعال", "Starting this week": "شروع این هفته",
    "Fulfilled (30 d)": "تکمیل‌شده (۳۰ روز)", "Released (30 d)": "آزاد شده (۳۰ روز)",
    "Stock in": "ورود موجودی", "Stock out": "خروج موجودی",
    "Net change": "تغییر خالص", "Closing owned": "مانده در تملک",
    "On-hand value": "ارزش در انبار", "On-rent value": "ارزش در کرایه",
    "Rental fleet": "ناوگان کرایه", "Revenue to date": "عاید تا امروز",
    "Fleet ROI": "بازگشت سرمایه ناوگان", "FLEET ROI": "بازگشت سرمایه ناوگان",
    "Paid back": "بازپرداخت‌شده", "Idle 90+ days": "بیکار ۹۰+ روز",
    "PAID FOR ITSELF": "قیمت خود را برگردانده",

    # KPI captions
    "owned × avg cost": "در تملک × قیمت اوسط", "on hand + on rent": "در انبار + در کرایه",
    "in the warehouse": "در انبار", "out with customers": "نزد مشتریان",
    "from reservations": "از رزروها", "on hand − reserved": "در انبار − رزرو شده",
    "below reorder level": "زیر حد سفارش مجدد", "valuation basis": "مبنای ارزیابی",
    "holding 1 unit each": "هر کدام ۱ واحد", "of 3 on hand": "از ۳ در انبار",
    "incl. 2-day buffer": "شامل ۲ روز مهلت", "became rentals": "به کرایه تبدیل شد",
    "excl. deposits": "بدون تضمین", "of 31,200 cost": "از قیمت ۳۱٬۲۰۰",
    "fully paid back": "کاملاً بازپرداخت‌شده", "revenue ÷ cost": "عاید ÷ قیمت",
    "revenue ÷ acquisition": "عاید ÷ قیمت خرید", "since last return": "از آخرین بازگشت",
    "units held": "واحد نگه‌داشته‌شده", "prepare & press": "آماده‌سازی و اتو",
    "need a human": "نیاز به بررسی انسانی", "freed the dress": "پیراهن آزاد شد",
    "still owned": "هنوز در تملک", "oldest 4 days": "قدیمی‌ترین ۴ روز",
    "fully received": "کاملاً رسید شده", "since Feb 2026": "از فبروری ۲۰۲۶",
    "due back 15 Sep": "بازگشت ۱۵ سپتمبر", "Main 2 · Shar-e-Naw 1": "مرکزی ۲ · شهر نو ۱",
    "24–26 Sep booking": "رزرو ۲۴–۲۶ سپتمبر", "24–26 Sep overlap": "تداخل ۲۴–۲۶ سپتمبر",
    "AFN · Main Store": "AFN · فروشگاه مرکزی",
    "238 units — still an asset": "۲۳۸ واحد — هنوز دارایی است",
    "AFN 3.94M acquired": "AFN 3.94M خریداری‌شده",
    "AFN 486,000 tied up": "AFN 486,000 قفل‌شده",
    "63% of fleet": "۶۳٪ ناوگان",

    # form labels
    "Item name *": "نام قلم *", "Name": "نام", "Name *": "نام *",
    "Barcode": "بارکد", "Main category": "کتگوری اصلی", "Main category *": "کتگوری اصلی *",
    "Sub-category": "زیرکتگوری", "Sub-category *": "زیرکتگوری *",
    "Item type": "نوع قلم", "Model": "مودل", "Model / designer": "مودل / دیزاینر",
    "Size": "سایز", "Colour": "رنگ", "Fabric": "تکه", "Season": "فصل",
    "Quality": "کیفیت", "Lifecycle": "وضعیت قلم", "Lifecycle *": "وضعیت قلم *",
    "Lifecycle status *": "وضعیت قلم *", "Lifecycle after": "وضعیت پس از ثبت",
    "Sale price": "قیمت فروش", "Rental price": "قیمت کرایه",
    "Rental deposit": "تضمین کرایه", "Late fee / day": "جریمه تأخیر / روز",
    "Late fee": "جریمه تأخیر",
    "Cleaning buffer (days)": "مهلت پاک‌کاری (روز)", "Cleaning buffer": "مهلت پاک‌کاری",
    "Reorder level": "حد سفارش مجدد", "Reorder": "سفارش مجدد",
    "Category": "کتگوری", "Category *": "کتگوری *", "Size / colour": "سایز / رنگ",
    "SKU · barcode · QR": "SKU · بارکد · QR",
    "Warehouse": "انبار", "Warehouse *": "انبار *", "Entry type *": "نوع سند *",
    "Entry date *": "تاریخ سند *", "Reference": "مرجع", "Note": "یادداشت",
    "Date": "تاریخ", "Date *": "تاریخ *", "Reason": "دلیل", "Reason *": "دلیل *",
    "Purchase order *": "فرمایش خرید *", "Receive into *": "رسید به انبار *",
    "Received date *": "تاریخ رسید *", "Currency / rate": "اسعار / نرخ",
    "Currency": "اسعار", "Quantity *": "مقدار *", "Item *": "قلم *",
    "Reserved from *": "رزرو از *", "Reserved to *": "رزرو تا *",
    "Customer *": "مشتری *", "Customer": "مشتری", "Link to order": "اتصال به فرمایش",
    "From branch / warehouse *": "از شعبه / انبار *",
    "To branch / warehouse *": "به شعبه / انبار *", "Sent date *": "تاریخ ارسال *",
    "As of date": "تا تاریخ", "Branch": "شعبه", "Group by": "گروه‌بندی بر اساس",
    "Sort by": "ترتیب بر اساس", "Acquired": "خریداری‌شده",
    "All branches": "تمام شعبه‌ها", "All warehouses": "تمام انبارها",
    "All categories": "تمام کتگوری‌ها", "All time": "تمام مدت",
    "ROI % (high → low)": "٪ بازگشت سرمایه (زیاد ← کم)",

    # generated-identity block
    "IDENTITY — generated, not typed": "شناسه — تولیدشده، نه تایپ‌شده",
    "IDENTITY — locked after creation": "شناسه — پس از ایجاد قفل می‌شود",
    "LIVE PREVIEW — updates as soon as the SKU is issued":
        "پیش‌نمای زنده — به مجرد صدور SKU تازه می‌شود",
    "BARCODE & QR — generated from the SKU": "بارکد و QR — تولیدشده از روی SKU",
    "CURRENT LABEL — printed on the garment tag": "لیبل فعلی — چاپ‌شده روی تگ لباس",
    "platform_sequences · ADF{YY}-{0000}": "platform_sequences · ADF{YY}-{0000}",
    "derived — regenerates if the SKU ever changes":
        "مشتق — اگر SKU تغییر کند دوباره ساخته می‌شود",
    "derived from the SKU — cannot be edited": "مشتق از SKU — قابل ویرایش نیست",
    "immutable — referenced by 41 ledger rows": "تغییرناپذیر — ۴۱ سطر دفتر به آن ارجاع دارد",
    "Code 128 of ADF26-0131": "Code 128 از ADF26-0131",
    "Code 128 of ADF26-0042": "Code 128 از ADF26-0042",
    "Code 128  ·  scan → inventory_items.id": "Code 128  ·  سکن ← inventory_items.id",
    "Code 128  ·  scan resolves to inventory_items.id":
        "Code 128  ·  سکن به inventory_items.id می‌رسد",
    "▸  More attributes — fabric, season, quality, components, custom fields":
        "▸  مشخصات بیشتر — تکه، فصل، کیفیت، اجزا، فیلدهای سفارشی",
    "drag photos here · first becomes is_main": "عکس‌ها را اینجا بکشید · اولی is_main می‌شود",

    # section labels
    "QUICK ACTIONS": "اقدامات سریع",
    "QUICK ACTIONS — each one opens a drawer": "اقدامات سریع — هر کدام یک کشو باز می‌کند",
    "RECENT MOVEMENTS": "حرکات اخیر",
    "LOW STOCK — BELOW REORDER LEVEL": "کمبود موجودی — زیر حد سفارش مجدد",
    "BOOKING CONFLICTS — NEXT 30 DAYS": "تداخل رزرو — ۳۰ روز آینده",
    "ATTRIBUTES — inventory_items": "مشخصات — inventory_items",
    "CHANNELS — decided by the prices that are set": "کانال‌ها — بر اساس قیمت‌های تعیین‌شده",
    "STOCK BY WAREHOUSE — one SKU lives in several warehouses":
        "موجودی به تفکیک انبار — یک SKU در چند انبار موجود است",
    "BY WAREHOUSE": "به تفکیک انبار", "MOVEMENTS": "حرکات",
    "WEIGHTED AVERAGE COST HISTORY — recomputed on every stock-in":
        "تاریخچه قیمت اوسط وزنی — با هر ورود موجودی دوباره محاسبه می‌شود",
    "STOCK LEDGER — inventory_stock_transactions for this SKU":
        "دفتر موجودی — inventory_stock_transactions برای این SKU",
    "COST RECOVERY — acquisition_cost ÷ expected_rental_uses, per use":
        "بازیافت قیمت — قیمت خرید ÷ دفعات متوقعه کرایه، به ازای هر بار",
    "RENTAL HISTORY — sales_order_items of type rental":
        "تاریخچه کرایه — sales_order_items از نوع کرایه",
    "RENTAL HISTORY": "تاریخچه کرایه",
    "CATALOGUE PHOTOS — inventory_item_media, sort_order ascending":
        "عکس‌های کتلاگ — inventory_item_media، به ترتیب sort_order",
    "CONDITION PHOTOS — on documents, not the catalogue":
        "عکس‌های وضعیت — روی اسناد، نه در کتلاگ",
    "COUNT SHEET PHOTOS": "عکس‌های ورقهٔ شمارش", "LINES": "سطرها",
    "PRICING — AFN": "قیمت‌گذاری — افغانی",
    "PRICING — AFN · leave a price empty to switch that channel off":
        "قیمت‌گذاری — افغانی · قیمت را خالی بگذارید تا آن کانال غیرفعال شود",
    "TOTAL": "مجموع", "TOTALS — 284 items": "مجموع — ۲۸۴ قلم",
    "TOTAL STOCK IN": "مجموع ورود موجودی",

    # table headers
    "Txn #": "شماره سند", "Item": "قلم", "Type": "نوع", "Qty": "مقدار",
    "Qty ±": "مقدار ±", "Qty in": "مقدار ورودی", "Unit cost": "قیمت واحد",
    "Unit cost (AFN)": "قیمت واحد (AFN)", "Value": "ارزش", "Reference": "مرجع",
    "Status": "حالت", "State": "حالت", "Source": "منبع", "Order": "فرمایش",
    "From": "از", "To": "به", "Buffer": "مهلت", "Balance": "بیلانس",
    "Doc": "سند", "Event": "رویداد", "Landed": "قیمت نهایی",
    "Landed unit cost": "قیمت نهایی واحد", "Owned after": "در تملک پس از",
    "New avg cost": "قیمت اوسط جدید", "Line": "سطر", "Line value": "ارزش سطر",
    "Lines": "سطرها", "Ordered": "فرمایش‌شده", "Received": "رسید شده",
    "Receiving now": "رسید فعلی", "Allocated other": "مصارف تخصیص‌یافته",
    "Expected": "متوقعه", "Counted": "شمارش‌شده", "Difference": "تفاوت",
    "Value impact": "اثر ارزشی", "Dispose qty": "مقدار ضایعات",
    "Write-off value": "ارزش حذف‌شده", "Available at source": "قابل دسترس در مبدا",
    "Send qty": "مقدار ارسال", "Reservation": "رزرو", "Res / Doc": "رزرو / سند",
    "Channel": "کانال", "Enabled by": "فعال‌شده توسط", "Price": "قیمت",
    "Deposit": "تضمین", "Days": "روز", "Charged": "دریافت‌شده", "COGS": "قیمت تمام‌شد",
    "Out": "خروج", "Dress": "پیراهن", "Cost": "قیمت", "Revenue": "عاید",
    "Amortised": "مستهلک", "Shot": "عکس", "Document": "سند", "Documents": "اسناد",
    "By": "توسط", "When": "چه وقت", "User": "کاربر", "Action": "عمل",
    "Field / document": "فیلد / سند", "Old value": "مقدار قبلی",
    "New value": "مقدار جدید", "Units": "واحدها", "Units in": "واحد ورودی",
    "Units in transit": "واحد در راه", "Units disposed": "واحد ضایع‌شده",
    "Share": "سهم", "Sent": "ارسال‌شده", "Hand": "انبار", "Rent": "کرایه",
    "Total quantity": "مجموع مقدار", "Total entry value": "مجموع ارزش سند",
    "Total landed": "مجموع قیمت نهایی", "Total landed (AFN)": "مجموع قیمت نهایی (AFN)",
    "Total write-off": "مجموع حذف‌شده", "Net quantity change": "تغییر خالص مقدار",
    "Net value impact": "اثر خالص ارزشی", "Net contribution": "سهم خالص",
    "Goods value": "ارزش اجناس", "Other cost allocated": "مصارف دیگر تخصیص‌یافته",
    "Exchange rate": "نرخ تبادله", "Acquisition cost": "قیمت خرید",
    "Expected rental uses": "دفعات متوقعه کرایه",
    "COGS per use  (31,200 ÷ 20)": "قیمت تمام‌شد هر بار  (۳۱٬۲۰۰ ÷ ۲۰)",
    "Uses booked so far": "دفعات ثبت‌شده تا اکنون",
    "Amortised to date  (capped)": "مستهلک تا امروز  (سقف‌دار)",
    "Rental revenue to date": "عاید کرایه تا امروز",

    # chips, statuses, values
    "All": "همه", "All types": "تمام انواع", "In": "ورود",
    "All 1,284": "همه ۱٬۲۸۴", "Available 954": "قابل دسترس ۹۵۴",
    "Reserved 92": "رزرو شده ۹۲", "On rent 238": "در کرایه ۲۳۸",
    "Repairing 14": "در ترمیم ۱۴", "Low stock 11": "کمبود موجودی ۱۱",
    "Disposed 8": "ضایع‌شده ۸", "Active 3": "فعال ۳", "Active 92": "فعال ۹۲",
    "Fulfilled 18": "تکمیل‌شده ۱۸", "Released 4": "آزاد شده ۴",
    "Cancelled 2": "لغوشده ۲", "All 27": "همه ۲۷", "All 37": "همه ۳۷",
    "Conflict 2": "تداخل ۲", "Field changes 14": "تغییر فیلد ۱۴",
    "Stock postings 18": "ثبت موجودی ۱۸", "Reservations 4": "رزرو ۴",
    "Photos 1": "عکس ۱",
    "active": "فعال", "repairing": "در ترمیم", "discontinued": "متوقف‌شده",
    "disposed": "ضایع‌شده", "available": "قابل دسترس", "on rent": "در کرایه",
    "reserved": "رزرو شده", "conflict": "تداخل", "fulfilled": "تکمیل‌شده",
    "released": "آزاد شده", "cancelled": "لغوشده", "draft": "مسوده",
    "in transit": "در راه", "completed": "تکمیل‌شده", "partial": "قسمی",
    "partially received": "قسماً رسید شده", "Partially received": "قسماً رسید شده",
    "Completed": "تکمیل‌شده", "Draft": "مسوده", "Conflict": "تداخل",
    "Fulfilled": "تکمیل‌شده", "Released": "آزاد شده", "Cancelled": "لغوشده",
    "returned": "برگشت‌داده‌شده", "claim": "ادعا", "damage claim": "ادعای خسارت",
    "damage": "خسارت", "check-out": "تحویل‌دهی", "check-in": "تحویل‌گیری",
    "created": "ایجاد شد", "field change": "تغییر فیلد", "stock posting": "ثبت موجودی",
    "reservation": "رزرو", "photo": "عکس", "count sheet": "ورقهٔ شمارش",
    "is_main": "is_main", "main photo": "عکس اصلی",
    "main photo · inventory_item_media": "عکس اصلی · inventory_item_media",
    "Lifecycle: active": "وضعیت: فعال", "Quality: high": "کیفیت: عالی",
    "Buffer 2 days": "مهلت ۲ روز", "Sale 48,000": "فروش ۴۸٬۰۰۰",
    "Rental 9,500": "کرایه ۹٬۵۰۰", "sale + rental": "فروش + کرایه",
    "high": "عالی", "Sale": "فروش", "Rental": "کرایه",
    "sale price is set": "قیمت فروش تعیین شده", "rental price is set": "قیمت کرایه تعیین شده",
    "Free": "آزاد", "Free — bookable": "آزاد — قابل رزرو",
    "Reserved — booked for a customer": "رزرو شده — برای یک مشتری",
    "On rent — with the customer now": "در کرایه — فعلاً نزد مشتری",
    "Cleaning buffer — 2 days after return": "مهلت پاک‌کاری — ۲ روز پس از بازگشت",
    "Manual in": "ورود دستی", "Manual": "دستی", "Manual entry": "سند دستی",
    "Count mismatch": "عدم تطابق شمارش", "Damaged beyond repair": "خسارت غیرقابل ترمیم",
    "Damaged": "خسارت‌دیده", "Opening stock": "موجودی افتتاحیه",
    "Receipt": "رسید", "Receipt vs PO": "رسید در برابر فرمایش",
    "Purchase receipt (GRN)": "رسید خرید (GRN)", "Sale return": "برگشت فروش",
    "Sale return restock": "بازگرداندن برگشت فروش", "Transfer in": "ورود انتقالی",
    "Movement summary": "خلاصه حرکات", "Stock-in by source": "ورود بر اساس منبع",
    "Stock-out by reason": "خروج بر اساس دلیل", "Valuation": "ارزیابی",
    "Movement": "حرکت", "Stock": "موجودی", "Bookings": "رزروها",
    "Adjustment": "تعدیل", "adjustment": "تعدیل",
    "In progress": "در جریان", "Idle": "بیکار", "✓ paid back": "✓ بازپرداخت‌شده",
    "never rented": "هرگز کرایه نشده", "not sent yet": "هنوز ارسال نشده",
    "Wedding Dress": "لباس عروسی", "Engagement": "نامزدی",
    "Accessories": "لوازم جانبی", "Jewellery": "زیورات", "Nikah Wear": "لباس نکاح",
    "Bridal Dresses": "لباس‌های عروسی",
    "— none yet —": "— هنوز هیچ —",
    "Unit 1 of 3 on hand  ·  switch unit ▾": "واحد ۱ از ۳ در انبار  ·  تعویض واحد ▾",
    "Showing all warehouses  ·  next 90 days ▾": "تمام انبارها  ·  ۹۰ روز آینده ▾",
    "Rental revenue by month (AFN)": "عاید کرایه به تفکیک ماه (AFN)",
    "Stock-in value by source (AFN)": "ارزش ورود بر اساس منبع (AFN)",
    "September 2026": "سپتمبر ۲۰۲۶", "October 2026": "اکتوبر ۲۰۲۶",
    "Blush Tulle Gown  — new item —": "پیراهن تور گلابی  — قلم جدید —",
    "Blush Tulle Gown (new)": "پیراهن تور گلابی (جدید)",
    "Chantilly Veil  ADF26-0067": "تور شانتیلی  ADF26-0067",
    "Pearl Tiara Set  ADF26-0102": "ست تاج مرواریدی  ADF26-0102",
    "White A-Line Gown  ADF26-0042": "پیراهن سفید ای‌لاین  ADF26-0042",
    "Main Store → Shar-e-Naw": "فروشگاه مرکزی ← شهر نو",
    "Main Store → Repair Room": "فروشگاه مرکزی ← اتاق ترمیم",
    "Shar-e-Naw → Main Store": "شهر نو ← فروشگاه مرکزی",
    "Repair Room → Main Store": "اتاق ترمیم ← فروشگاه مرکزی",
    "from the item record": "از رکورد قلم",
    "reserved_to + buffer — this is what the guard checks":
        "رزرو تا + مهلت — محافظ همین را بررسی می‌کند",
    "rental_price 9,000 → 9,500": "rental_price ۹٬۰۰۰ ← ۹٬۵۰۰",
    "lifecycle repairing → active": "وضعیت در ترمیم ← فعال",
    "avg cost 30,467": "قیمت اوسط ۳۰٬۴۶۷", "avg cost 31,200": "قیمت اوسط ۳۱٬۲۰۰",
    "on hand 2": "در انبار ۲", "on hand 3": "در انبار ۳",
    "Edit drawer": "کشوی ویرایش", "New item drawer": "کشوی قلم جدید",
    "Reserve drawer": "کشوی رزرو", "Photos tab": "زبانه عکس‌ها",
    "Rent out (snapshot)": "خروج کرایه (عکس لحظه‌ای)",

    # longer in-UI copy
    "⚠️  11 items below reorder level": "۱۱ قلم زیر حد سفارش مجدد  ⚠️",
    "⚠️  2 booking conflicts": "۲ تداخل رزرو  ⚠️",
    "⚠  Dress already booked for these dates": "⚠  پیراهن برای این تاریخ‌ها قبلاً رزرو شده",
    "Tap to resolve — move dates or swap gown":
        "برای حل ضربه بزنید — تاریخ را تغییر دهید یا پیراهن را عوض کنید",
    "Chantilly Veil · 2 left (reorder 10)\nPearl Tiara Set · 1 left (reorder 6)":
        "تور شانتیلی · ۲ باقی (سفارش ۱۰)\nست تاج مرواریدی · ۱ باقی (سفارش ۶)",
    "White A-Line Gown (ADF26-0042) is reserved 24–26 Sep for SO26-000470,\n"
    "and blocked until 28 Sep for the 2-day cleaning buffer.\n"
    "Only 1 unit is on hand in Main Store, so it cannot be booked again.\n\n"
    "What you can do:\n"
    "   • Source the same gown from Shar-e-Naw Branch — 1 available\n"
    "   • Move the booking to 29 Sep or later\n"
    "   • Offer Ivory Mermaid Gown  ADF26-0088  size S":
        "پیراهن سفید ای‌لاین (ADF26-0042) از ۲۴ تا ۲۶ سپتمبر برای SO26-000470 رزرو است\n"
        "و به دلیل ۲ روز مهلت پاک‌کاری تا ۲۸ سپتمبر مسدود می‌باشد.\n"
        "تنها ۱ واحد در فروشگاه مرکزی موجود است، پس دوباره رزرو شده نمی‌تواند.\n\n"
        "گزینه‌های شما:\n"
        "   • همین پیراهن را از شعبه شهر نو بگیرید — ۱ قابل دسترس\n"
        "   • رزرو را به ۲۹ سپتمبر یا بعد از آن انتقال دهید\n"
        "   • پیراهن ماهی‌دم عاجی  ADF26-0088  سایز S را پیشنهاد کنید",
    "🖼   Drop photos here, or click to browse": "عکس‌ها را اینجا رها کنید، یا برای انتخاب کلیک کنید   🖼",
    "JPEG / PNG / WebP · max 8 MB each · first upload becomes is_main":
        "JPEG / PNG / WebP · حداکثر ۸ MB هر کدام · اولین بارگذاری is_main می‌شود",
    "🖼   Take photo  ·  Choose from gallery": "عکس بگیرید  ·  از گالری انتخاب کنید   🖼",
    "🖼  ＋ Attach count sheet photo": "＋ پیوست عکس ورقهٔ شمارش  🖼",
    "9 photos · long-press to reorder": "۹ عکس · برای ترتیب فشار طولانی بدهید",
    "1 of 9 photos": "۱ از ۹ عکس",
    "cost 31,200 fully amortised · ROI 731%": "قیمت ۳۱٬۲۰۰ کاملاً مستهلک · بازگشت ۷۳۱٪",
    "94 of 148 dresses have paid for themselves": "۹۴ از ۱۴۸ پیراهن قیمت خود را برگردانده‌اند",
    "1,284 owned = 1,046 on hand + 238 on rent":
        "۱٬۲۸۴ در تملک = ۱٬۰۴۶ در انبار + ۲۳۸ در کرایه",
    "Owned 4 = on hand 3 + on rent 1": "۴ در تملک = ۳ در انبار + ۱ در کرایه",
    "Avg cost 31,200 · worth AFN 124,800": "قیمت اوسط ۳۱٬۲۰۰ · ارزش AFN 124,800",
    "Sale 48,000 · rent 9,500": "فروش ۴۸٬۰۰۰ · کرایه ۹٬۵۰۰",
    "Sale 2,400 · avail 12": "فروش ۲٬۴۰۰ · قابل دسترس ۱۲",
    "Rent 8,000 · avail 0": "کرایه ۸٬۰۰۰ · قابل دسترس ۰",
    "Rent 7,200 · avail 1": "کرایه ۷٬۲۰۰ · قابل دسترس ۱",
    "front-full.jpg": "front-full.jpg",
    "Sara Ahmadi · 3 days": "سارا احمدی · ۳ روز",
}

# ── Pashto (ps) ───────────────────────────────────────────────────
# Same layout, same data, Pashto wording. Where Pashto administrative usage has
# settled on the Dari/Arabic term (رزرو، بارکد، مسوده) it is kept — that is what
# Afghan software and Afghan shopkeepers actually use.

PS = {
    "stock_in": "زېرمې ته ننوتل", "stock_out": "له زېرمې وتل",
    "transfer_in": "لېږد ننوتل", "transfer_out": "لېږد وتل",
    "rent_out": "کرایې ته وتل", "rent_return": "له کرایې راتګ", "dispose": "له منځه وړل",
    "rent_out ledger →": "→ د کرایې وتلو دفتر",
    "1–8 of 48 SKUs · 1,284 owned units · AFN 4.82M worth":
        "۱–۸ له ۴۸ SKU · ۱٬۲۸۴ واحده ملکیت · ارزښت AFN 4.82M",
    "1–9 of 4,182 transactions": "۱–۹ له ۴٬۱۸۲ سندونو",
    "1–6 of 92 active reservations": "۱–۶ له ۹۲ فعالو ریزرونو",
    "1–7 of 37 events": "۱–۷ له ۳۷ پېښو",
    "37 events · created 04 Feb 2026": "۳۷ پېښې · جوړ شوی ۰۴ فبروري ۲۰۲۶",
    "31,200 (held)": "۳۱٬۲۰۰ (ساتل شوی)",
    "ADF26-0131  — generated": "ADF26-0131  — جوړ شوی",
    "GRN26-0009 · PO26-000012\nIstanbul Bridal Co. · USD @ 70.50":
        "GRN26-0009 · PO26-000012\nد استانبول د واده شرکت · USD @ 70.50",
    "Inventory  /  Items  /  ADF26-0042": "زېرمه  /  توکي  /  ADF26-0042",
    "M / Ivory white": "M / عاجي سپین", "MSE26-0022 · draft": "MSE26-0022 · مسوده",
    "Value in": "ننوتی ارزښت", "Value in transit": "په لار کې ارزښت",
    "0 of 10 received": "۰ له ۱۰ رسید شوي", "3 of 5 received": "۳ له ۵ رسید شوي",
    "4 of 4 received": "۴ له ۴ رسید شوي", "22 of 22": "۲۲ له ۲۲",
    "94 of 148": "۹۴ له ۱۴۸",
    "Home": "کور", "Inventory": "زېرمه", "Sales": "پلور",
    "Procurement": "تدارکات", "Finance": "مالي", "Reports": "راپورونه",
    "Settings": "تنظیمات", "More": "نور", "Owner": "مالک",
    "MAIN": "اصلي", "OPERATIONS": "عملیات", "MONEY": "پیسې",
    "INSIGHT": "شننه", "SYSTEM": "سیستم",
    "🏬  Main branch  ▾": "مرکزي څانګه  ▾  🏬",
    "🌐 English ▾    🔔 3    👤 Ahmad ▾": "پښتو  🌐    ۳  🔔    احمد  👤",
    "🔒 boms.app/inventory": "🔒 boms.app/inventory",
    "Main branch · Main Store": "مرکزي څانګه · مرکزي پلورنځی",

    "Items": "توکي", "  Items": "  توکي", "• Items": "• توکي",
    "Stock ledger": "د زېرمې دفتر", "  Stock ledger": "  د زېرمې دفتر",
    "• Stock ledger": "• د زېرمې دفتر",
    "Reservations": "ریزرونه", "  Reservations": "  ریزرونه",
    "• Reservations": "• ریزرونه",
    "Transfers": "لېږدونه", "  Transfers": "  لېږدونه", "• Transfers": "• لېږدونه",
    "  Reports": "  راپورونه", "• Reports": "• راپورونه",

    "A.  DASHBOARD": "الف.  ډشبورډ",
    "B.  ITEMS": "ب.  توکي",
    "C.  STOCK LEDGER": "ج.  د زېرمې دفتر",
    "D.  RESERVATIONS": "د.  ریزرونه",
    "E.  TRANSFERS": "هـ.  لېږدونه",
    "F.  REPORTS": "و.  راپورونه",

    "BOMS Desktop — Inventory": "BOMS ډیسکټاپ — زېرمه (پښتو)",
    "BOMS Mobile — Inventory": "BOMS موبایل — زېرمه (پښتو)",
    "A1.  Inventory dashboard — stock at a glance": "الف۱.  د زېرمې ډشبورډ — یوه کتنه",
    "A1. Inventory dashboard": "الف۱. د زېرمې ډشبورډ",
    "B1.  Items list — catalogue with the three buckets": "ب۱.  د توکو لړلیک — کتلاګ له درېو شمېرونو سره",
    "B1. Items list": "ب۱. د توکو لړلیک",
    "B2.  New item — drawer over the items list": "ب۲.  نوی توکی — د لړلیک پر سر کشویي",
    "B2. New item (bottom sheet)": "ب۲. نوی توکی (لاندینۍ پاڼه)",
    "B3.  Edit item — same drawer, identity locked": "ب۳.  د توکي سمون — هماغه کشویي، پېژندنه ځنځیر",
    "B4.  Item profile · Overview — attributes, label, stock":
        "ب۴.  د توکي پروفایل · لنډه کتنه — ځانګړنې، لیبل، زېرمه",
    "B4. Item profile · Overview": "ب۴. د توکي پروفایل · لنډه کتنه",
    "B5.  Item profile · Stock & movement (WAC history)":
        "ب۵.  د توکي پروفایل · زېرمه او خوځښت (د اوسط بیې تاریخچه)",
    "B5. Item profile · Stock": "ب۵. د توکي پروفایل · زېرمه",
    "B6.  Item profile · Reservations — who has booked this dress":
        "ب۶.  د توکي پروفایل · ریزرونه — چا دا کالي ریزرو کړي",
    "B6. Item profile · Reservations": "ب۶. د توکي پروفایل · ریزرونه",
    "B7.  Item profile · Rentals — history, earnings, payback":
        "ب۷.  د توکي پروفایل · کرایې — تاریخچه، عاید، بیرته راګرځېدنه",
    "B7. Item profile · Rentals": "ب۷. د توکي پروفایل · کرایې",
    "B8.  Item profile · Photos — gallery, main photo, condition shots":
        "ب۸.  د توکي پروفایل · عکسونه — ګالري، اصلي عکس، د حالت عکسونه",
    "B8. Item profile · Photos": "ب۸. د توکي پروفایل · عکسونه",
    "B9.  Item profile · Audit — every change, who and when":
        "ب۹.  د توکي پروفایل · د بدلونونو ثبت — هر بدلون، چا او کله",
    "B9. Item profile · Audit": "ب۹. د توکي پروفایل · د بدلونونو ثبت",
    "C1.  Stock ledger — immutable movement history": "ج۱.  د زېرمې دفتر — د خوځښتونو نه بدلېدونکې تاریخچه",
    "C1. Stock ledger": "ج۱. د زېرمې دفتر",
    "C2.  Stock in — drawer over the ledger (manual / opening)":
        "ج۲.  زېرمې ته ننوتل — د دفتر پر سر کشویي (لاسي / پرانیستې)",
    "C2. Stock in (bottom sheet)": "ج۲. زېرمې ته ننوتل (لاندینۍ پاڼه)",
    "C3.  Receive against PO (GRN) — drawer over the ledger":
        "ج۳.  د پیرود فرمایش په وړاندې رسید — د دفتر پر سر کشویي",
    "C3. Receive PO (GRN)": "ج۳. د پیرود رسید",
    "C4.  Stock adjustment — drawer over the ledger": "ج۴.  د زېرمې سمون — د دفتر پر سر کشویي",
    "C4/C5. Adjust · Dispose": "ج۴/ج۵. سمون · له منځه وړل",
    "C5.  Dispose — drawer over the ledger (write-off)": "ج۵.  له منځه وړل — د دفتر پر سر کشویي",
    "D1.  Reservations — every booking in the shop": "د۱.  ریزرونه — د پلورنځي ټول ریزرونه",
    "D1. Reservations": "د۱. ریزرونه",
    "D2.  New reservation — drawer + double-booking guard":
        "د۲.  نوی ریزرو — کشویي + د دوه‌ځلي ریزرو ساتونکی",
    "D3.  Availability calendar — reserved / on rent / buffer":
        "د۳.  د شتون جنتري — ریزرو شوی / په کرایه / د پاکولو موده",
    "D3. Availability calendar": "د۳. د شتون جنتري",
    "E1.  Transfers — stock moving between warehouses": "هـ۱.  لېږدونه — د ګودامونو ترمنځ د زېرمې خوځښت",
    "E1. Transfers": "هـ۱. لېږدونه",
    "E2.  New transfer — drawer over the transfers list": "هـ۲.  نوی لېږد — د لړلیک پر سر کشویي",
    "F1.  Valuation report — what is my stock worth?": "و۱.  د ارزښت راپور — زما د زېرمې ارزښت څومره دی؟",
    "F1–F3. Reports": "و۱–و۳. راپورونه",
    "F2.  Stock movement & stock-in by source": "و۲.  د زېرمې خوځښت او د سرچینې له مخې ننوتل",
    "F3.  Rental utilisation & asset ROI": "و۳.  د کرایې ګټه اخیستنه او د پانګې بیرته راګرځېدنه",

    "Read top to bottom: A Dashboard · B Items (list → drawers → the six profile tabs) · C Stock ledger · D Reservations · E Transfers · F Reports.\n"
    "Barcode and QR are generated from the SKU · no Purpose field · rentals have no fixed period · every create and edit is a drawer over its list.\n"
    "Owned = on hand + on rent (valuation) · Available = on hand − reserved · reservations are not ledger rows · weighted average cost · immutable postings":
        "له پورته څخه ښکته ولولئ: الف ډشبورډ · ب توکي (لړلیک ← کشویۍ ← د پروفایل شپږ ټبونه) · ج د زېرمې دفتر · د ریزرونه · هـ لېږدونه · و راپورونه.\n"
        "بارکوډ او QR له SKU څخه جوړېږي · د «موخې» ډګر نشته · کرایه ټاکلې موده نه لري · هر جوړول او سمون د خپل لړلیک پر سر په کشویي کې پرانیستل کېږي.\n"
        "ملکیت = په ګودام کې + په کرایه (د ارزښت بنسټ) · شته = په ګودام کې − ریزرو شوي · ریزرونه د دفتر کرښې نه دي · اوسط وزني بیه · ثبت شوي اسناد نه بدلېږي",
    "Same order as the desktop board: A dashboard · B items and the profile tabs · C ledger · D reservations · E transfers · F reports.":
        "د ډیسکټاپ تختې په څېر ترتیب: الف ډشبورډ · ب توکي او د پروفایل ټبونه · ج دفتر · د ریزرونه · هـ لېږدونه · و راپورونه.",

    "Al Dubai Bridal · Main branch · all warehouses · as of 12 Sep 2026":
        "الدوبی برایدل · مرکزي څانګه · ټول ګودامونه · تر ۱۲ سپتمبر ۲۰۲۶",
    "1,284 owned units · 48 SKUs · Main branch": "۱٬۲۸۴ واحده ملکیت · ۴۸ SKU · مرکزي څانګه",
    "1,284 owned units · 48 SKUs": "۱٬۲۸۴ واحده ملکیت · ۴۸ SKU",
    "Inventory valuation": "د زېرمې ارزونه",
    "Availability — White A-Line Gown": "شتون — سپین ای‌لاین کالي",
    "Stock movement": "د زېرمې خوځښت",
    "Rental utilisation & asset ROI": "د کرایې ګټه اخیستنه او د پانګې بیرته راګرځېدنه",
    "Adjust stock": "د زېرمې سمون", "Availability": "شتون",
    "Audit": "د بدلونونو ثبت", "Photos": "عکسونه", "Rentals": "کرایې",
    "Stock & movement": "زېرمه او خوځښت", "Overview": "لنډه کتنه",
    "Receive": "رسید", "Stock in": "زېرمې ته ننوتل",
    "Every quantity change in the system. Append-only — corrections are reversing rows.":
        "په سیسټم کې د مقدار هر بدلون. یوازې زیاتونکی — سمون د معکوس سند له لارې.",
    "Append-only. Corrections are reversing rows, never edits.":
        "یوازې زیاتونکی. سمون د معکوس سند له لارې، هیڅکله د سمولو له لارې نه.",
    "Reserved quantity comes from here — never from the stock ledger":
        "ریزرو شوی مقدار له دې ځایه راځي — هیڅکله د زېرمې له دفتره نه",
    "Move stock between warehouses or branches. Cost travels with the goods.":
        "د ګودامونو یا څانګو ترمنځ د زېرمې لېږد. بیه له مالونو سره ځي.",
    "Correct on-hand quantity after a physical count. Not the same as Dispose.":
        "تر فزیکي شمېرنې وروسته د شته مقدار سمون. له منځه وړلو سره توپیر لري.",
    "Remove goods from stock permanently and book the loss":
        "مالونه له زېرمې څخه د تل لپاره لرې کړئ او زیان ثبت کړئ",
    "Owned quantity × weighted average cost, in AFN":
        "د ملکیت مقدار × اوسط وزني بیه، په افغانیو",
    "Has each dress paid for itself? · since acquisition · AFN":
        "ایا هر کالي خپله بیه بیرته راګرځولې؟ · د پیرود راهیسې · افغانۍ",
    "01 Sep – 12 Sep 2026 · all warehouses": "۰۱ سپتمبر – ۱۲ سپتمبر ۲۰۲۶ · ټول ګودامونه",
    "92 active · 2 conflicts": "۹۲ فعال · ۲ ټکر",
    "3 in transit · 18 units · AFN 142,900": "۳ په لار کې · ۱۸ واحده · AFN 142,900",
    "SKU ADF26-0042 · Wedding Dress · A-Line · Size M · Bought 04 Feb 2026":
        "SKU ADF26-0042 · د واده کالي · ای‌لاین · سایز M · پیرود ۰۴ فبروري ۲۰۲۶",
    "SKU ADF26-0042 · weighted average cost per (item, warehouse)":
        "SKU ADF26-0042 · اوسط وزني بیه د (توکي، ګودام) له مخې",
    "SKU ADF26-0042 · owned 4 · reserved quantity comes from here, never from the ledger":
        "SKU ADF26-0042 · ۴ ملکیت · ریزرو شوی مقدار له دې ځایه راځي، نه له دفتره",
    "SKU ADF26-0042 · has this dress paid for itself? · AFN":
        "SKU ADF26-0042 · ایا دې کالي خپله بیه بیرته راګرځولې؟ · افغانۍ",
    "SKU ADF26-0042 · 9 photos · drag to reorder · first photo is the catalogue image":
        "SKU ADF26-0042 · ۹ عکسونه · د ترتیب لپاره یې ورسره کش کړئ · لومړی عکس د کتلاګ انځور دی",
    "SKU ADF26-0042 · created 04 Feb 2026 by Ahmad Zaki · 37 recorded events":
        "SKU ADF26-0042 · جوړ شوی ۰۴ فبروري ۲۰۲۶ د احمد ذکي لخوا · ۳۷ ثبت شوي پېښې",
    "ADF26-0042 · owned 4 · on hand 3 · cleaning buffer 2 days after every return":
        "ADF26-0042 · ۴ ملکیت · ۳ په ګودام کې · د هر بیرته راتګ وروسته ۲ ورځې د پاکولو موده",
    "White A-Line Gown · ADF26-0042 · 1 owned": "سپین ای‌لاین کالي · ADF26-0042 · ۱ ملکیت",
    "ADF26-0042 · White A-Line Gown": "ADF26-0042 · سپین ای‌لاین کالي",
    "ADF26-0042 · 3 active · 1 conflict": "ADF26-0042 · ۳ فعال · ۱ ټکر",
    "White A-Line Gown · editing the catalogue record never moves stock":
        "سپین ای‌لاین کالي · د کتلاګ ریکارډ سمول هیڅکله زېرمه نه خوځوي",
    "Catalogue record only · creates NO stock · barcode and QR are generated from the SKU":
        "یوازې د کتلاګ ریکارډ · هیڅ زېرمه نه جوړوي · بارکوډ او QR له SKU څخه جوړېږي",
    "Catalogue record only — creates no stock": "یوازې د کتلاګ ریکارډ — زېرمه نه جوړوي",
    "Opening stock or an ad-hoc stock-in with no purchase order · draft":
        "پرانیستې زېرمه یا د پیرود فرمایش پرته ننوتل · مسوده",
    "PO26-000012 · Istanbul Bridal Co. · ordered 02 Sep 2026 · draft":
        "PO26-000012 · د استانبول د واده شرکت · فرمایش ۰۲ سپتمبر ۲۰۲۶ · مسوده",
    "Holds a dress for a customer · writes inventory_reservations only · no stock moves":
        "د پیرودونکي لپاره کالي ساتي · یوازې inventory_reservations لیکي · زېرمه نه خوځي",
    "Cost travels with the goods — an internal move never changes stock worth":
        "بیه له مالونو سره ځي — کورنی لېږد د زېرمې ارزښت نه بدلوي",
    "Torn bodice — SO26-000009": "څیرې شوې تنه — SO26-000009",
    "Quarterly count — aisle 3": "ربعواره شمېرنه — دهلیز ۳",
    "Sept stock take": "د سپتمبر د زېرمې شمېرنه",
    "Event weekend stock — return after 20 Sep": "د مراسمو د اونۍ پای زېرمه — تر ۲۰ سپتمبر وروسته بیرته",
    "Engagement — needs the long veil too": "کوژده — اوږد تور هم پکار دی",
    "Repair — torn bodice": "ترمیم — څیرې شوې تنه",

    "Cancel": "لغوه", "Save item": "توکی خوندي کړئ", "Save changes": "بدلونونه خوندي کړئ",
    "Save & new": "خوندي او نوی", "Save draft": "مسوده خوندي کړئ",
    "Post entry": "سند ثبت کړئ", "Post receipt": "رسید ثبت کړئ",
    "Post adjustment": "سمون ثبت کړئ", "Post disposal": "له منځه وړل ثبت کړئ",
    "Reserve dates": "نېټې ریزرو کړئ", "Send": "ولېږئ", "Run": "چل کړئ",
    "Back": "بیرته", "Edit": "سمون", "View": "کتل", "Resolve": "ټکر حل کړئ",
    "Reorder": "بیا ترتیب", "Reprint label": "لیبل بیا چاپ کړئ",
    "Edit item": "د توکي سمون", "Edit item · ADF26-0042": "د توکي سمون · ADF26-0042",
    "New item": "نوی توکی", "New reservation": "نوی ریزرو",
    "New transfer  ·  TRF26-0006": "نوی لېږد  ·  TRF26-0006",
    "Stock in  ·  MSE26-0022": "زېرمې ته ننوتل  ·  MSE26-0022",
    "Receive goods  ·  GRN26-0009": "د مالونو رسید  ·  GRN26-0009",
    "Stock adjustment  ·  ADJ26-0012": "د زېرمې سمون  ·  ADJ26-0012",
    "Dispose stock  ·  DSP26-0005": "زېرمه له منځه وړل  ·  DSP26-0005",
    "Import CSV": "CSV واردول", "Rebuild balances": "بیلانسونه بیا جوړ کړئ",
    "Calendar view": "د جنتري کتنه", "Availability calendar": "د شتون جنتري",
    "Open rental order": "د کرایې فرمایش پرانیځئ",
    "Choose another date": "بله نېټه وټاکئ", "Pick alternative": "بدیل وټاکئ",
    "Columns ▾": "کالمونه ▾", "Month ▾": "میاشت ▾", "Filter ▾": "فلټر ▾",
    "Warehouse: All ▾": "ګودام: ټول ▾",
    "‹ Prev": "پخوانی ›", "Next ›": "‹ راتلونکی",
    "☰  Filters": "فلټرونه  ☰", "☰": "☰",
    "⬇ Export": "وتنه ⬇", "⬇ Export CSV": "CSV وتنه ⬇",
    "⬇ Export ledger": "د دفتر وتنه ⬇", "⬇ Download": "ښکته کول ⬇",
    "⬆ Upload photos": "عکسونه پورته کړئ ⬆",
    "🖨 Print": "چاپ 🖨", "🖨 Print label": "لیبل چاپ کړئ 🖨",
    "＋ New item": "نوی توکی ＋", "＋ New movement": "نوی خوځښت ＋",
    "＋ New transfer": "نوی لېږد ＋", "＋ Reserve": "ریزرو ＋",
    "＋ Reserve these dates": "دا نېټې ریزرو کړئ ＋",
    "＋ Add line": "کرښه زیاته کړئ ＋", "＋ Add photo": "عکس زیات کړئ ＋",
    "＋ Add": "زیاتول ＋", "View ledger →": "→ دفتر وګورئ",
    "Reserve": "ریزرو", "Receive PO": "د فرمایش رسید", "Adjust": "سمون",
    "Dispose": "له منځه وړل", "Transfer": "لېږد",

    "🔍  Search SKU, name, barcode, model…": "د SKU، نوم، بارکوډ، موډل لټون…  🔍",
    "🔍  Search SKU, name, barcode…": "د SKU، نوم، بارکوډ لټون…  🔍",
    "🔍  Txn # / SKU / reference document": "د سند شمېره / SKU / مرجع سند  🔍",
    "🔍  SKU / customer / order #": "SKU / پیرودونکی / د فرمایش شمېره  🔍",
    "🔍  Transfer # / item / warehouse": "د لېږد شمېره / توکی / ګودام  🔍",
    "🔍  Name, SKU or scan barcode": "نوم، SKU یا بارکوډ سکن کړئ  🔍",
    "🔍   Scan a barcode or QR to add a line": "د کرښې زیاتولو لپاره بارکوډ یا QR سکن کړئ   🔍",
    "🔍   Scan barcode to add a line": "د کرښې زیاتولو لپاره بارکوډ سکن کړئ   🔍",
    "🔍   or scan the garment barcode / QR": "یا د کالي بارکوډ / QR سکن کړئ   🔍",

    "Stock worth": "د زېرمې ارزښت", "Total stock worth": "د زېرمې ټول ارزښت",
    "TOTAL STOCK WORTH": "د زېرمې ټول ارزښت",
    "Owned units": "د ملکیت واحدونه", "On hand": "په ګودام کې", "On rent": "په کرایه",
    "Reserved": "ریزرو شوي", "Available": "شته", "Low stock": "د زېرمې کمښت",
    "Owned": "ملکیت", "Avail": "شته", "Rsvd": "ریزرو",
    "Avg cost": "اوسط بیه", "Avg cost (WAC)": "اوسط وزني بیه",
    "Avg unit cost": "د واحد اوسط بیه", "Worth": "ارزښت",
    "Active reservations": "فعال ریزرونه", "Reserved units": "ریزرو شوي واحدونه",
    "Next booking": "راتلونکی ریزرو", "Blocked until": "بند تر",
    "Conflicts": "ټکرونه", "Fulfilled this year": "سږکال بشپړ شوي",
    "Times rented": "د کرایې شمېر", "Rental revenue": "د کرایې عاید",
    "Amortised so far": "تر اوسه استهلاک شوی", "Payback": "بیرته راګرځېدنه",
    "ROI": "د پانګې بیرته راګرځېدنه", "ROI %": "٪ بیرته راګرځېدنه",
    "Idle days": "بېکارې ورځې", "In transit": "په لار کې",
    "Value in transit": "په لار کې ارزښت", "Awaiting receipt": "د رسید په تمه",
    "Completed (30 d)": "بشپړ شوي (۳۰ ورځې)", "Active": "فعال",
    "Starting this week": "دا اونۍ پیلېږي",
    "Fulfilled (30 d)": "بشپړ شوي (۳۰ ورځې)", "Released (30 d)": "خوشې شوي (۳۰ ورځې)",
    "Stock out": "له زېرمې وتل", "Net change": "خالص بدلون",
    "Closing owned": "د پای ملکیت", "On-hand value": "په ګودام کې ارزښت",
    "On-rent value": "په کرایه ارزښت", "Rental fleet": "د کرایې ټولګه",
    "Revenue to date": "تر نن پورې عاید", "Fleet ROI": "د ټولګې بیرته راګرځېدنه",
    "FLEET ROI": "د ټولګې بیرته راګرځېدنه", "Paid back": "بیرته ورکړل شوی",
    "Idle 90+ days": "بېکار ۹۰+ ورځې", "PAID FOR ITSELF": "خپله بیه یې راګرځولې",

    "owned × avg cost": "ملکیت × اوسط بیه", "on hand + on rent": "په ګودام کې + په کرایه",
    "in the warehouse": "په ګودام کې", "out with customers": "د پیرودونکو سره",
    "from reservations": "له ریزرونو", "on hand − reserved": "په ګودام کې − ریزرو شوي",
    "below reorder level": "د بیا فرمایش تر کچې ښکته", "valuation basis": "د ارزونې بنسټ",
    "holding 1 unit each": "هر یو ۱ واحد", "of 3 on hand": "له ۳ څخه په ګودام کې",
    "incl. 2-day buffer": "له ۲ ورځې مودې سره", "became rentals": "کرایې ته واوښتل",
    "excl. deposits": "پرته له تضمین", "of 31,200 cost": "له ۳۱٬۲۰۰ بیې څخه",
    "fully paid back": "بشپړ بیرته ورکړل شوی", "revenue ÷ cost": "عاید ÷ بیه",
    "revenue ÷ acquisition": "عاید ÷ د پیرود بیه", "since last return": "له وروستي راتګ راهیسې",
    "units held": "ساتل شوي واحدونه", "prepare & press": "چمتو کول او استري",
    "need a human": "انساني کتنې ته اړتیا", "freed the dress": "کالي یې خوشې کړل",
    "still owned": "لا هم ملکیت", "oldest 4 days": "تر ټولو زوړ ۴ ورځې",
    "fully received": "بشپړ رسید شوی", "since Feb 2026": "د فبروري ۲۰۲۶ راهیسې",
    "due back 15 Sep": "بیرته راتګ ۱۵ سپتمبر", "Main 2 · Shar-e-Naw 1": "مرکزي ۲ · شهر نو ۱",
    "24–26 Sep booking": "د ۲۴–۲۶ سپتمبر ریزرو", "24–26 Sep overlap": "د ۲۴–۲۶ سپتمبر ټکر",
    "AFN · Main Store": "AFN · مرکزي پلورنځی",
    "238 units — still an asset": "۲۳۸ واحده — لا هم شتمني ده",
    "AFN 3.94M acquired": "AFN 3.94M پیرل شوي",
    "AFN 486,000 tied up": "AFN 486,000 بند پاتې",
    "63% of fleet": "۶۳٪ ټولګه",

    "Item name *": "د توکي نوم *", "Name": "نوم", "Name *": "نوم *",
    "Barcode": "بارکوډ", "Main category": "اصلي کټګورۍ", "Main category *": "اصلي کټګورۍ *",
    "Sub-category": "فرعي کټګورۍ", "Sub-category *": "فرعي کټګورۍ *",
    "Item type": "د توکي ډول", "Model": "موډل", "Model / designer": "موډل / ډیزاینر",
    "Size": "سایز", "Colour": "رنګ", "Fabric": "ټوکر", "Season": "فصل",
    "Quality": "کیفیت", "Lifecycle": "د توکي حالت", "Lifecycle *": "د توکي حالت *",
    "Lifecycle status *": "د توکي حالت *", "Lifecycle after": "وروسته حالت",
    "Sale price": "د پلور بیه", "Rental price": "د کرایې بیه",
    "Rental deposit": "د کرایې تضمین", "Late fee / day": "د ځنډ جریمه / ورځ",
    "Late fee": "د ځنډ جریمه",
    "Cleaning buffer (days)": "د پاکولو موده (ورځې)", "Cleaning buffer": "د پاکولو موده",
    "Reorder level": "د بیا فرمایش کچه", "Reorder": "بیا فرمایش",
    "Category": "کټګورۍ", "Category *": "کټګورۍ *", "Size / colour": "سایز / رنګ",
    "SKU · barcode · QR": "SKU · بارکوډ · QR",
    "Warehouse": "ګودام", "Warehouse *": "ګودام *", "Entry type *": "د سند ډول *",
    "Entry date *": "د سند نېټه *", "Reference": "مرجع", "Note": "یادښت",
    "Date": "نېټه", "Date *": "نېټه *", "Reason": "دلیل", "Reason *": "دلیل *",
    "Purchase order *": "د پیرود فرمایش *", "Receive into *": "ګودام ته رسید *",
    "Received date *": "د رسید نېټه *", "Currency / rate": "اسعار / نرخ",
    "Currency": "اسعار", "Quantity *": "مقدار *", "Item *": "توکی *",
    "Reserved from *": "ریزرو له *", "Reserved to *": "ریزرو تر *",
    "Customer *": "پیرودونکی *", "Customer": "پیرودونکی", "Link to order": "له فرمایش سره تړل",
    "From branch / warehouse *": "له څانګې / ګودام *",
    "To branch / warehouse *": "څانګې / ګودام ته *", "Sent date *": "د لېږد نېټه *",
    "As of date": "تر نېټې", "Branch": "څانګه", "Group by": "ګروپ بندي",
    "Sort by": "ترتیب", "Acquired": "پیرل شوی",
    "All branches": "ټولې څانګې", "All warehouses": "ټول ګودامونه",
    "All categories": "ټولې کټګورۍ", "All time": "ټوله موده",
    "ROI % (high → low)": "٪ بیرته راګرځېدنه (لوړ ← ټیټ)",

    "IDENTITY — generated, not typed": "پېژندنه — جوړه شوې، ټایپ شوې نه",
    "IDENTITY — locked after creation": "پېژندنه — تر جوړېدو وروسته بنده",
    "LIVE PREVIEW — updates as soon as the SKU is issued":
        "ژوندۍ کتنه — همدا چې SKU صادر شي تازه کېږي",
    "BARCODE & QR — generated from the SKU": "بارکوډ او QR — له SKU څخه جوړ شوي",
    "CURRENT LABEL — printed on the garment tag": "اوسنی لیبل — د کالي پر ټګ چاپ شوی",
    "platform_sequences · ADF{YY}-{0000}": "platform_sequences · ADF{YY}-{0000}",
    "derived — regenerates if the SKU ever changes":
        "اخیستل شوی — که SKU بدل شي بیا جوړېږي",
    "derived from the SKU — cannot be edited": "له SKU څخه اخیستل شوی — نه سمېږي",
    "immutable — referenced by 41 ledger rows": "نه بدلېږي — ۴۱ د دفتر کرښې ورته اشاره کوي",
    "Code 128 of ADF26-0131": "د ADF26-0131 Code 128",
    "Code 128 of ADF26-0042": "د ADF26-0042 Code 128",
    "Code 128  ·  scan → inventory_items.id": "Code 128  ·  سکن ← inventory_items.id",
    "Code 128  ·  scan resolves to inventory_items.id":
        "Code 128  ·  سکن inventory_items.id ته رسېږي",
    "▸  More attributes — fabric, season, quality, components, custom fields":
        "▸  نورې ځانګړنې — ټوکر، فصل، کیفیت، برخې، ځانګړي ډګرونه",
    "drag photos here · first becomes is_main": "عکسونه دلته راکش کړئ · لومړی is_main کېږي",

    "QUICK ACTIONS": "چټک اقدامات",
    "QUICK ACTIONS — each one opens a drawer": "چټک اقدامات — هر یو کشویي پرانیزي",
    "RECENT MOVEMENTS": "وروستي خوځښتونه",
    "LOW STOCK — BELOW REORDER LEVEL": "د زېرمې کمښت — د بیا فرمایش تر کچې ښکته",
    "BOOKING CONFLICTS — NEXT 30 DAYS": "د ریزرو ټکرونه — راتلونکې ۳۰ ورځې",
    "ATTRIBUTES — inventory_items": "ځانګړنې — inventory_items",
    "CHANNELS — decided by the prices that are set": "کانالونه — د ټاکل شویو بیو له مخې",
    "STOCK BY WAREHOUSE — one SKU lives in several warehouses":
        "زېرمه د ګودام له مخې — یو SKU په څو ګودامونو کې وي",
    "BY WAREHOUSE": "د ګودام له مخې", "MOVEMENTS": "خوځښتونه",
    "WEIGHTED AVERAGE COST HISTORY — recomputed on every stock-in":
        "د اوسط وزني بیې تاریخچه — د هر ننوتلو سره بیا محاسبه کېږي",
    "STOCK LEDGER — inventory_stock_transactions for this SKU":
        "د زېرمې دفتر — د دې SKU لپاره inventory_stock_transactions",
    "COST RECOVERY — acquisition_cost ÷ expected_rental_uses, per use":
        "د بیې بیرته ترلاسه کول — د پیرود بیه ÷ د کرایې تمه شوی شمېر، هر ځل",
    "RENTAL HISTORY — sales_order_items of type rental":
        "د کرایې تاریخچه — د کرایې ډول sales_order_items",
    "RENTAL HISTORY": "د کرایې تاریخچه",
    "CATALOGUE PHOTOS — inventory_item_media, sort_order ascending":
        "د کتلاګ عکسونه — inventory_item_media، د sort_order له مخې",
    "CONDITION PHOTOS — on documents, not the catalogue":
        "د حالت عکسونه — پر اسنادو، نه په کتلاګ کې",
    "COUNT SHEET PHOTOS": "د شمېرنې پاڼې عکسونه", "LINES": "کرښې",
    "PRICING — AFN": "بیه ټاکنه — افغانۍ",
    "PRICING — AFN · leave a price empty to switch that channel off":
        "بیه ټاکنه — افغانۍ · بیه خالي پرېږدئ چې هغه کانال بند شي",
    "TOTAL": "ټول", "TOTALS — 284 items": "ټولټال — ۲۸۴ توکي",
    "TOTAL STOCK IN": "ټول ننوتل",

    "Txn #": "د سند شمېره", "Item": "توکی", "Type": "ډول", "Qty": "مقدار",
    "Qty ±": "مقدار ±", "Qty in": "ننوتی مقدار", "Unit cost": "د واحد بیه",
    "Unit cost (AFN)": "د واحد بیه (AFN)", "Value": "ارزښت",
    "Status": "حالت", "State": "حالت", "Source": "سرچینه", "Order": "فرمایش",
    "From": "له", "To": "تر", "Buffer": "موده", "Balance": "بیلانس",
    "Doc": "سند", "Event": "پېښه", "Landed": "وروستۍ بیه",
    "Landed unit cost": "د واحد وروستۍ بیه", "Owned after": "وروسته ملکیت",
    "New avg cost": "نوې اوسط بیه", "Line": "کرښه", "Line value": "د کرښې ارزښت",
    "Lines": "کرښې", "Ordered": "فرمایش شوی", "Received": "رسید شوی",
    "Receiving now": "اوس رسید", "Allocated other": "ځانګړي شوي نور لګښتونه",
    "Expected": "تمه شوی", "Counted": "شمېرل شوی", "Difference": "توپیر",
    "Value impact": "د ارزښت اغېز", "Dispose qty": "د لرې کولو مقدار",
    "Write-off value": "لرې شوی ارزښت", "Available at source": "په سرچینه کې شته",
    "Send qty": "د لېږد مقدار", "Reservation": "ریزرو", "Res / Doc": "ریزرو / سند",
    "Channel": "کانال", "Enabled by": "فعال شوی د", "Price": "بیه",
    "Deposit": "تضمین", "Days": "ورځې", "Charged": "اخیستل شوی", "COGS": "تمام شوې بیه",
    "Out": "وتل", "Dress": "کالي", "Cost": "بیه", "Revenue": "عاید",
    "Amortised": "استهلاک", "Shot": "عکس", "Document": "سند", "Documents": "اسناد",
    "By": "لخوا", "When": "کله", "User": "کاروونکی", "Action": "کړنه",
    "Field / document": "ډګر / سند", "Old value": "پخوانی ارزښت",
    "New value": "نوی ارزښت", "Units": "واحدونه", "Units in": "ننوتي واحدونه",
    "Units in transit": "په لار کې واحدونه", "Units disposed": "لرې شوي واحدونه",
    "Share": "برخه", "Sent": "لېږل شوی", "Hand": "ګودام", "Rent": "کرایه",
    "Total quantity": "ټول مقدار", "Total entry value": "د سند ټول ارزښت",
    "Total landed": "ټوله وروستۍ بیه", "Total landed (AFN)": "ټوله وروستۍ بیه (AFN)",
    "Total write-off": "ټول لرې شوي", "Net quantity change": "د مقدار خالص بدلون",
    "Net value impact": "د ارزښت خالص اغېز", "Net contribution": "خالصه ونډه",
    "Goods value": "د مالونو ارزښت", "Other cost allocated": "ځانګړي شوي نور لګښتونه",
    "Exchange rate": "د تبادلې نرخ", "Acquisition cost": "د پیرود بیه",
    "Expected rental uses": "د کرایې تمه شوی شمېر",
    "COGS per use  (31,200 ÷ 20)": "هر ځل تمام شوې بیه  (۳۱٬۲۰۰ ÷ ۲۰)",
    "Uses booked so far": "تر اوسه ثبت شوي ځلې",
    "Amortised to date  (capped)": "تر نن استهلاک شوی  (تر سقف)",
    "Rental revenue to date": "تر نن د کرایې عاید",

    "All": "ټول", "All types": "ټول ډولونه", "In": "ننوتل",
    "All 1,284": "ټول ۱٬۲۸۴", "Available 954": "شته ۹۵۴",
    "Reserved 92": "ریزرو شوي ۹۲", "On rent 238": "په کرایه ۲۳۸",
    "Repairing 14": "په ترمیم کې ۱۴", "Low stock 11": "کمښت ۱۱",
    "Disposed 8": "لرې شوي ۸", "Active 3": "فعال ۳", "Active 92": "فعال ۹۲",
    "Fulfilled 18": "بشپړ شوي ۱۸", "Released 4": "خوشې شوي ۴",
    "Cancelled 2": "لغوه شوي ۲", "All 27": "ټول ۲۷", "All 37": "ټول ۳۷",
    "Conflict 2": "ټکر ۲", "Field changes 14": "د ډګر بدلون ۱۴",
    "Stock postings 18": "د زېرمې ثبت ۱۸", "Reservations 4": "ریزرو ۴",
    "Photos 1": "عکس ۱",
    "active": "فعال", "repairing": "په ترمیم کې", "discontinued": "درول شوی",
    "disposed": "لرې شوی", "available": "شته", "on rent": "په کرایه",
    "reserved": "ریزرو شوی", "conflict": "ټکر", "fulfilled": "بشپړ شوی",
    "released": "خوشې شوی", "cancelled": "لغوه شوی", "draft": "مسوده",
    "in transit": "په لار کې", "completed": "بشپړ شوی", "partial": "جزوي",
    "partially received": "جزوي رسید شوی", "Partially received": "جزوي رسید شوی",
    "Completed": "بشپړ شوی", "Draft": "مسوده", "Conflict": "ټکر",
    "Fulfilled": "بشپړ شوی", "Released": "خوشې شوی", "Cancelled": "لغوه شوی",
    "returned": "بیرته راغلی", "claim": "ادعا", "damage claim": "د زیان ادعا",
    "damage": "زیان", "check-out": "سپارل", "check-in": "بیرته اخیستل",
    "created": "جوړ شو", "field change": "د ډګر بدلون", "stock posting": "د زېرمې ثبت",
    "reservation": "ریزرو", "photo": "عکس", "count sheet": "د شمېرنې پاڼه",
    "is_main": "is_main", "main photo": "اصلي عکس",
    "main photo · inventory_item_media": "اصلي عکس · inventory_item_media",
    "Lifecycle: active": "حالت: فعال", "Quality: high": "کیفیت: لوړ",
    "Buffer 2 days": "موده ۲ ورځې", "Sale 48,000": "پلور ۴۸٬۰۰۰",
    "Rental 9,500": "کرایه ۹٬۵۰۰", "sale + rental": "پلور + کرایه",
    "high": "لوړ", "Sale": "پلور", "Rental": "کرایه",
    "sale price is set": "د پلور بیه ټاکل شوې", "rental price is set": "د کرایې بیه ټاکل شوې",
    "Free": "خالي", "Free — bookable": "خالي — د ریزرو وړ",
    "Reserved — booked for a customer": "ریزرو شوی — د یوه پیرودونکي لپاره",
    "On rent — with the customer now": "په کرایه — اوس د پیرودونکي سره",
    "Cleaning buffer — 2 days after return": "د پاکولو موده — تر بیرته راتګ وروسته ۲ ورځې",
    "Manual in": "لاسي ننوتل", "Manual": "لاسي", "Manual entry": "لاسي سند",
    "Count mismatch": "د شمېرنې نا اړخوالی", "Damaged beyond repair": "د ترمیم نه وړ زیان",
    "Damaged": "زیانمن", "Opening stock": "پرانیستې زېرمه",
    "Receipt": "رسید", "Receipt vs PO": "رسید په وړاندې فرمایش",
    "Purchase receipt (GRN)": "د پیرود رسید (GRN)", "Sale return": "د پلور بیرته راتګ",
    "Sale return restock": "د بیرته راغلي پلور زېرمه", "Transfer in": "لېږد ننوتل",
    "Movement summary": "د خوځښتونو لنډیز", "Stock-in by source": "د سرچینې له مخې ننوتل",
    "Stock-out by reason": "د دلیل له مخې وتل", "Valuation": "ارزونه",
    "Movement": "خوځښت", "Stock": "زېرمه", "Bookings": "ریزرونه",
    "Adjustment": "سمون", "adjustment": "سمون",
    "In progress": "روان", "Idle": "بېکار", "✓ paid back": "✓ بیرته ورکړل شوی",
    "never rented": "هیڅکله کرایه شوی نه", "not sent yet": "لا نه دی لېږل شوی",
    "Wedding Dress": "د واده کالي", "Engagement": "کوژده",
    "Accessories": "لوازم", "Jewellery": "ګاڼې", "Nikah Wear": "د نکاح کالي",
    "Bridal Dresses": "د واده کالي",
    "— none yet —": "— لا هیڅ نشته —",
    "Unit 1 of 3 on hand  ·  switch unit ▾": "واحد ۱ له ۳ څخه په ګودام کې  ·  واحد بدل کړئ ▾",
    "Showing all warehouses  ·  next 90 days ▾": "ټول ګودامونه  ·  راتلونکې ۹۰ ورځې ▾",
    "Rental revenue by month (AFN)": "د میاشتې له مخې د کرایې عاید (AFN)",
    "Stock-in value by source (AFN)": "د سرچینې له مخې د ننوتلو ارزښت (AFN)",
    "September 2026": "سپتمبر ۲۰۲۶", "October 2026": "اکتوبر ۲۰۲۶",
    "Blush Tulle Gown  — new item —": "ګلابي تور کالي  — نوی توکی —",
    "Blush Tulle Gown (new)": "ګلابي تور کالي (نوی)",
    "Chantilly Veil  ADF26-0067": "شانتیلي تور  ADF26-0067",
    "Pearl Tiara Set  ADF26-0102": "د ملغلرو تاج سیټ  ADF26-0102",
    "White A-Line Gown  ADF26-0042": "سپین ای‌لاین کالي  ADF26-0042",
    "Main Store → Shar-e-Naw": "مرکزي پلورنځی ← شهر نو",
    "Main Store → Repair Room": "مرکزي پلورنځی ← د ترمیم خونه",
    "Shar-e-Naw → Main Store": "شهر نو ← مرکزي پلورنځی",
    "Repair Room → Main Store": "د ترمیم خونه ← مرکزي پلورنځی",
    "from the item record": "د توکي له ریکارډه",
    "reserved_to + buffer — this is what the guard checks":
        "ریزرو تر + موده — ساتونکی همدا ګوري",
    "rental_price 9,000 → 9,500": "rental_price ۹٬۰۰۰ ← ۹٬۵۰۰",
    "lifecycle repairing → active": "حالت په ترمیم کې ← فعال",
    "avg cost 30,467": "اوسط بیه ۳۰٬۴۶۷", "avg cost 31,200": "اوسط بیه ۳۱٬۲۰۰",
    "on hand 2": "په ګودام کې ۲", "on hand 3": "په ګودام کې ۳",
    "Edit drawer": "د سمون کشویي", "New item drawer": "د نوي توکي کشویي",
    "Reserve drawer": "د ریزرو کشویي", "Photos tab": "د عکسونو ټب",
    "Rent out (snapshot)": "کرایې ته وتل (شېبه‌یي انځور)",

    "⚠️  11 items below reorder level": "۱۱ توکي د بیا فرمایش تر کچې ښکته  ⚠️",
    "⚠️  2 booking conflicts": "۲ د ریزرو ټکرونه  ⚠️",
    "⚠  Dress already booked for these dates": "⚠  کالي د دې نېټو لپاره مخکې ریزرو شوي",
    "Tap to resolve — move dates or swap gown":
        "د حل لپاره ټک وکړئ — نېټې بدلې کړئ یا کالي بدل کړئ",
    "Chantilly Veil · 2 left (reorder 10)\nPearl Tiara Set · 1 left (reorder 6)":
        "شانتیلي تور · ۲ پاتې (فرمایش ۱۰)\nد ملغلرو تاج سیټ · ۱ پاتې (فرمایش ۶)",
    "White A-Line Gown (ADF26-0042) is reserved 24–26 Sep for SO26-000470,\n"
    "and blocked until 28 Sep for the 2-day cleaning buffer.\n"
    "Only 1 unit is on hand in Main Store, so it cannot be booked again.\n\n"
    "What you can do:\n"
    "   • Source the same gown from Shar-e-Naw Branch — 1 available\n"
    "   • Move the booking to 29 Sep or later\n"
    "   • Offer Ivory Mermaid Gown  ADF26-0088  size S":
        "سپین ای‌لاین کالي (ADF26-0042) د ۲۴ تر ۲۶ سپتمبر پورې د SO26-000470 لپاره ریزرو دي\n"
        "او د ۲ ورځو د پاکولو مودې له امله تر ۲۸ سپتمبر پورې بند دي.\n"
        "یوازې ۱ واحد په مرکزي پلورنځي کې شته، نو بیا ریزرو کېدای نشي.\n\n"
        "څه کولی شئ:\n"
        "   • همدا کالي د شهر نو له څانګې واخلئ — ۱ شته\n"
        "   • ریزرو ۲۹ سپتمبر یا وروسته ته ولېږدوئ\n"
        "   • د عاجي ماهي‌لکۍ کالي  ADF26-0088  سایز S وړاندیز کړئ",
    "🖼   Drop photos here, or click to browse": "عکسونه دلته پرېږدئ، یا د ټاکلو لپاره کلیک وکړئ   🖼",
    "JPEG / PNG / WebP · max 8 MB each · first upload becomes is_main":
        "JPEG / PNG / WebP · هر یو تر ۸ MB · لومړی پورته شوی is_main کېږي",
    "🖼   Take photo  ·  Choose from gallery": "عکس واخلئ  ·  له ګالرۍ وټاکئ   🖼",
    "🖼  ＋ Attach count sheet photo": "＋ د شمېرنې پاڼې عکس ونښلوئ  🖼",
    "9 photos · long-press to reorder": "۹ عکسونه · د ترتیب لپاره اوږد ټک وکړئ",
    "1 of 9 photos": "۱ له ۹ عکسونو",
    "cost 31,200 fully amortised · ROI 731%": "بیه ۳۱٬۲۰۰ بشپړ استهلاک شوې · بیرته ۷۳۱٪",
    "94 of 148 dresses have paid for themselves": "۹۴ له ۱۴۸ کالیو خپله بیه راګرځولې",
    "1,284 owned = 1,046 on hand + 238 on rent":
        "۱٬۲۸۴ ملکیت = ۱٬۰۴۶ په ګودام کې + ۲۳۸ په کرایه",
    "Owned 4 = on hand 3 + on rent 1": "۴ ملکیت = ۳ په ګودام کې + ۱ په کرایه",
    "Avg cost 31,200 · worth AFN 124,800": "اوسط بیه ۳۱٬۲۰۰ · ارزښت AFN 124,800",
    "Sale 48,000 · rent 9,500": "پلور ۴۸٬۰۰۰ · کرایه ۹٬۵۰۰",
    "Sale 2,400 · avail 12": "پلور ۲٬۴۰۰ · شته ۱۲",
    "Rent 8,000 · avail 0": "کرایه ۸٬۰۰۰ · شته ۰",
    "Rent 7,200 · avail 1": "کرایه ۷٬۲۰۰ · شته ۱",
    "front-full.jpg": "front-full.jpg",
    "Sara Ahmadi · 3 days": "سارا احمدی · ۳ ورځې",
    # Pashto product-name overrides where the Pashto word differs
    "White A-Line Gown": "سپین ای‌لاین کالي", "White A-Line": "سپین کالي",
    "Gold Ball Gown": "طلایي مجلسي کالي",
    "Ivory Mermaid Gown": "عاجي ماهي‌لکۍ کالي",
    "Chantilly Veil": "شانتیلي تور",
    "Pearl Tiara Set": "د ملغلرو تاج سیټ",
    "Emerald Engagement Set": "زمردي کوژدې سیټ", "Emerald Set": "زمردي سیټ",
    "Champagne Ball Gown": "شامپاین مجلسي کالي", "Champagne Gown": "شامپاین کالي",
    "Rose Nikah Abaya": "ګلابي نکاح عبا",
    "Bridal Gloves (S)": "د ناوې دستکشې (S)", "Ivory Hair Comb": "عاجي ږمنځ",
    "Blush Tulle Gown": "ګلابي تور کالي", "Sapphire Gown": "یاقوتي کالي",
    "Main Store": "مرکزي پلورنځی", "Shar-e-Naw Branch": "د شهر نو څانګه",
    "Shar-e-Naw · Floor 2": "شهر نو · دویم پوړ", "Repair Room": "د ترمیم خونه",
    "Istanbul Bridal Co.": "د استانبول د واده شرکت",
    "Silk mikado + lace": "د وریښمو میکاډو + دانتیل", "Silk mikado": "د وریښمو میکاډو",
    "Ivory white": "عاجي سپین", "One size": "یو سایز",
}

LOCALES = {
    "fa": {"name": "دری", "english": "Dari", "dir": "rtl", **{}},
    "ps": {"name": "پښتو", "english": "Pashto", "dir": "rtl"},
}

TABLES = {"fa": {**SHARED, **FA}, "ps": {**SHARED, **PS}}

# ── fragment pass ─────────────────────────────────────────────────
# Composed strings — "12 Sep", "4 of 4 received", "qty 12 × AFN 1,450" — are far
# too numerous to list one by one. After an exact-match miss, these word-level
# rules run instead, so the numbers survive untouched and only the words change.

def _fragments(t):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    frags = [(rf"\b{m}\b", SHARED[m]) for m in months]
    frags += [(re.escape(k), v) for k, v in sorted(
        ((k, t[k]) for k in (
            "White A-Line Gown", "Gold Ball Gown", "Emerald Engagement Set",
            "Chantilly Veil", "Ivory Mermaid Gown", "Rose Nikah Abaya",
            "Pearl Tiara Set", "Champagne Ball Gown", "Bridal Gloves (S)",
            "Ivory Hair Comb", "Sapphire Gown", "Main Store", "Shar-e-Naw",
            "Repair Room", "Ahmad Zaki", "Zahra Nekzad", "Rahim Sultani",
            "Sara Ahmadi", "Maryam Noori", "Marwa Sadat", "Fatima Rahimi",
            "Zainab Karimi", "Zainab Haidari", "Nargis Amini", "Farida Wali",
            "Nasrin Ahmadi", "Hosna Rahimi", "Latifa Noor", "Malika Sabir",
            "Shakila Amiri", "Palwasha Zia") if k in t),
        key=lambda kv: -len(kv[0]))]
    types = ("rent_return", "rent_out", "stock_in", "stock_out",
             "transfer_in", "transfer_out", "dispose")
    frags += [(rf"\b{ty}\b", t[ty]) for ty in types if ty in t]
    # generic words, longest first so "on hand" beats "hand"
    words = {
        "fa": {"received": "رسید شده", "reorder": "سفارش مجدد", "receiving": "رسید",
               "ordered": "فرمایش", "rentals": "کرایه", "photos": "عکس",
               "units": "واحد", "unit": "واحد", "owned": "در تملک",
               "on hand": "در انبار", "on rent": "در کرایه", "avail": "قابل دسترس",
               "expected": "متوقعه", "counted": "شمارش", "blocked until": "مسدود تا",
               "became": "تبدیل شد به", "overlaps": "تداخل با",
               "landed unit cost": "قیمت نهایی واحد", "qty": "مقدار",
               "left": "باقی", "events": "رویداد", "created": "ایجاد",
               "dresses": "پیراهن", "documents": "سند", "in transit": "در راه",
               "of": "از", "days": "روز", "day": "روز", "and": "و",
               "worth": "ارزش", "size": "سایز", "Size": "سایز", "cost": "قیمت",
               "active reservations": "رزرو فعال", "in progress": "در جریان",
               "slow": "کند", "paid back": "بازپرداخت‌شده", "fleet": "ناوگان",
               "all warehouses": "تمام انبارها"},
        "ps": {"received": "رسید شوی", "reorder": "بیا فرمایش", "receiving": "رسید",
               "ordered": "فرمایش", "rentals": "کرایې", "photos": "عکسونه",
               "units": "واحده", "unit": "واحد", "owned": "ملکیت",
               "on hand": "په ګودام کې", "on rent": "په کرایه", "avail": "شته",
               "expected": "تمه شوی", "counted": "شمېرل شوی", "blocked until": "بند تر",
               "became": "واوښت", "overlaps": "ټکر له",
               "landed unit cost": "د واحد وروستۍ بیه", "qty": "مقدار",
               "left": "پاتې", "events": "پېښې", "created": "جوړ شو",
               "dresses": "کالي", "documents": "اسناد", "in transit": "په لار کې",
               "of": "له", "days": "ورځې", "day": "ورځ", "and": "او",
               "worth": "ارزښت", "size": "سایز", "Size": "سایز", "cost": "بیه",
               "active reservations": "فعال ریزرونه", "in progress": "روان",
               "slow": "ورو", "paid back": "بیرته ورکړل شوی", "fleet": "ټولګه",
               "all warehouses": "ټول ګودامونه"},
    }
    return frags, words


def localise(elements, locale):
    """Swap English text for `locale`, leaving spec notes and numbers alone."""
    table = TABLES[locale]
    frags, words = _fragments(table)
    wordmap = sorted(words[locale].items(), key=lambda kv: -len(kv[0]))
    hits = misses = 0
    for el in elements:
        if el.get("type") != "text":
            continue
        if (el.get("customData") or {}).get("spec"):
            continue
        src = el["text"]
        if src in table:
            out = table[src]
            hits += 1
        else:
            out = src
            for pat, rep in frags:
                out = re.sub(pat, rep, out)
            for w, rep in wordmap:
                out = re.sub(rf"(?<![\w؀-ۿ]){re.escape(w)}(?![\w؀-ۿ])",
                             rep, out)
            if out == src and re.search(r"[A-Za-z]{3}", src):
                misses += 1
        if out != src and (el.get("customData") or {}).get("auto"):
            # The box was auto-measured from the English string; re-measure it so
            # a longer Dari phrase keeps its anchored edge instead of colliding.
            nw = max(8.0, max(_measure(L, el["fontSize"]) for L in out.split("\n")))
            align = el.get("textAlign", "left")
            if align == "right":
                el["x"] += el["width"] - nw
            elif align == "center":
                el["x"] += (el["width"] - nw) / 2
            el["width"] = nw
        el["text"] = out
        el["originalText"] = out
        # sans-serif renders Perso-Arabic; production type is Vazirmatn
        el["fontFamily"] = 2
    return hits, misses


def coverage(elements, locale):
    """Strings that still read as English after localise() — a build-time check."""
    out = []
    for el in elements:
        if el.get("type") != "text" or (el.get("customData") or {}).get("spec"):
            continue
        if re.search(r"[A-Za-z]{4}", el["text"]) and not re.match(
                r"^[\sA-Z0-9·\-−+/.,()%×÷:→←▾]*$", el["text"]):
            out.append(el["text"])
    return sorted(set(out))
