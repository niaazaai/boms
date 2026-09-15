#!/usr/bin/env python3
"""Build every BOMS Excalidraw wireframe.

    python3 .agent/scripts/wireframes/build.py

Writes:
    specs/wireframes/00-All-Modules.excalidraw     every module on one canvas
    specs/wireframes/00-Overview.excalidraw        sidebar / map / sitemap
    specs/wireframes/desktop/*.excalidraw          per module
    specs/wireframes/mobile/*.excalidraw           per module
    specs/wireframes/desktop/*-Dari.excalidraw     mirrored, Dari   (fa)
    specs/wireframes/desktop/*-Pashto.excalidraw   mirrored, Pashto (ps)
    …and the mobile equivalents

A localised board is not drawn by hand. It is the English board reflected by
`dsl.mirror()` and run through `i18n.localise()`, so a layout change can never
leave the three language versions disagreeing with each other.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import i18n  # noqa: E402
from dsl import (BG, DESK_H, DESK_W, INK, MUTED, ROSE, board_title,  # noqa: E402
                 doc, mirror, rect, section_label, text)
from modules import finance, inventory, overview, platform, procurement, sales  # noqa: E402

ROOT = HERE.parents[2] / "specs" / "wireframes"

MODULES = [
    ("01-Platform", platform, "Platform · Auth · Settings", "#0d9488"),
    ("02-Inventory", inventory, "Inventory", "#2563eb"),
    ("03-Procurement", procurement, "Procurement", "#d97706"),
    ("04-Sales", sales, "Sales", "#059669"),
    ("05-Finance", finance, "Finance", "#7c3aed"),
]

# Modules that also ship a Dari and a Pashto board. Add a name here once its
# strings are covered by i18n.TABLES — `--coverage` reports what is missing.
LOCALISED = ["02-Inventory"]

LOCALE_FILE_SUFFIX = {"fa": "Dari", "ps": "Pashto"}

BANNER = {
    "fa": ("نسخهٔ دری — راست‌چین",
           "همان تختهٔ انگلیسی است که آینه شده و ترجمه گردیده: یک تغییر در طرح، هر سه نسخه را تازه می‌کند.\n"
           "قلم تولیدی Vazirmatn است. اکسلیدرا فونت سفارشی را جاسازی کرده نمی‌تواند، بنابراین اینجا قلم سیستم به کار رفته —\n"
           "قلم دقیق در specs/design/tokens/typography.json ثبت است.\n"
           "اعداد، مبالغ، SKU، بارکد و شماره اسناد چپ‌چین می‌مانند. کادرهای یادداشت عمداً انگلیسی‌اند: آن‌ها نام جدول‌ها و SQL را\n"
           "برای تیم انکشاف می‌نویسند، نه متن رابط کاربر."),
    "ps": ("پښتو نسخه — ښي‌لوري",
           "همدا انګلیسي تخته ده چې هېنداره او ژباړل شوې: په ډیزاین کې یو بدلون درې واړه نسخې تازه کوي.\n"
           "تولیدي فونټ Vazirmatn دی. Excalidraw ځانګړی فونټ نه شي ځای‌پرځای کولی، نو دلته د سیسټم فونټ کارول شوی —\n"
           "دقیق فونټ په specs/design/tokens/typography.json کې ثبت دی.\n"
           "شمېرې، مبالغ، SKU، بارکوډ او د سند شمېرې کيڼ‌لوري پاتې کېږي. د یادښت بکسونه په قصد انګلیسي دي: هغه د پراختیا ټیم لپاره\n"
           "د جدولونو نومونه او SQL لیکي، نه د کاروونکي متن."),
}


def translate(elements, dx, dy):
    """Deep-copy elements shifted by (dx, dy)."""
    out = []
    for el in elements:
        e = copy.deepcopy(el)
        e["x"] = e.get("x", 0) + dx
        e["y"] = e.get("y", 0) + dy
        out.append(e)
    return out


def bounds(elements):
    xs0 = [e["x"] for e in elements if "x" in e]
    ys0 = [e["y"] for e in elements if "y" in e]
    xs1 = [e["x"] + e.get("width", 0) for e in elements if "x" in e]
    ys1 = [e["y"] + e.get("height", 0) for e in elements if "y" in e]
    if not xs0:
        return 0, 0, 0, 0
    return min(xs0), min(ys0), max(xs1), max(ys1)


def write(path: Path, elements):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc(elements), indent=1))
    x0, y0, x1, y1 = bounds(elements)
    rel = str(path.relative_to(ROOT.parents[1]))
    return f"  {rel:56s} {len(elements):6d} el   {int(x1 - x0):6d} × {int(y1 - y0):5d}"


def localise_board(elements, locale):
    """Mirror the whole board, then swap the strings. Returns (elements, misses).

    Mirroring the board rather than each frame means the screens themselves also
    re-order right-to-left, which is how the board should be read in Dari.
    """
    els = copy.deepcopy(elements)
    x0, _, x1, _ = bounds(els)
    els = mirror(els, x0, x1 - x0)
    _, misses = i18n.localise(els, locale)

    title, body = BANNER[locale]
    bx0, by0, bx1, _ = bounds(els)
    banner = [
        rect(bx0, by0 - 250, bx1 - bx0, 150, strokeColor=ROSE, backgroundColor="#fff1f2",
             strokeWidth=2),
        text(bx1 - 40 - 900, by0 - 232, title, 26, ROSE, "right", 900),
        text(bx0 + 40, by0 - 192, body, 13, MUTED, "right", (bx1 - bx0) - 80),
    ]
    return banner + els, misses


def build_combined():
    """Every module board stacked vertically on one canvas, with banners."""
    els = board_title(0, -420,
                      "BOMS — Complete Wireframes · All Modules",
                      "Bridal Omnichannel Management System.  Overview · Platform · Inventory · "
                      "Procurement · Sales · Finance — desktop and mobile.")
    els.append(text(0, -350,
                    "Reading order: the Overview band defines the navigation shell and the module map. "
                    "Each module band then runs desktop screens left→right, with its mobile screens beneath.\n"
                    "Corrected data model throughout — see specs/review/01-spec-review.md and 02-decisions.md.\n"
                    "Dari and Pashto boards are separate files — see desktop/02-Inventory-Dari.excalidraw.",
                    14, MUTED, width=3000))

    cursor_y = 0.0
    BAND_GAP = 700.0

    ov = overview.board()
    _, oy0, _, oy1 = bounds(ov)
    els += translate(ov, 0, cursor_y - oy0)
    cursor_y += (oy1 - oy0) + BAND_GAP

    for name, mod, label, color in MODULES:
        desk = mod.desktop()
        mob = mod.mobile()
        dx0, dy0, dx1, dy1 = bounds(desk)
        mx0, my0, mx1, my1 = bounds(mob)

        els.append(rect(0, cursor_y - 120, 2400, 76, strokeColor=color,
                        backgroundColor=BG, strokeWidth=3))
        els.append(rect(0, cursor_y - 120, 14, 76, strokeColor=color,
                        backgroundColor=color, strokeWidth=1))
        els.append(text(40, cursor_y - 100, label.upper(), 30, color, width=1400))
        els.append(text(40, cursor_y - 62,
                        f"desktop {len(desk)} elements  ·  mobile {len(mob)} elements", 13, MUTED,
                        width=1400))

        els += translate(desk, -dx0, cursor_y - dy0)
        cursor_y += (dy1 - dy0) + 260

        els.append(text(0, cursor_y - 180, f"{label} — mobile", 22, color, width=1200))
        els += translate(mob, -mx0, cursor_y - my0)
        cursor_y += (my1 - my0) + BAND_GAP

    return els


def main():
    print("BOMS wireframes\n")
    lines, report = [], []
    lines.append(write(ROOT / "00-Overview.excalidraw", overview.board()))
    for name, mod, label, _ in MODULES:
        desk, mob = mod.desktop(), mod.mobile()
        lines.append(write(ROOT / "desktop" / f"{name}.excalidraw", desk))
        lines.append(write(ROOT / "mobile" / f"{name}.excalidraw", mob))
        if name in LOCALISED:
            for loc, suffix in LOCALE_FILE_SUFFIX.items():
                d, dm = localise_board(desk, loc)
                m, mm = localise_board(mob, loc)
                lines.append(write(ROOT / "desktop" / f"{name}-{suffix}.excalidraw", d))
                lines.append(write(ROOT / "mobile" / f"{name}-{suffix}.excalidraw", m))
                report.append(f"  {name} {suffix:7s} untranslated strings: "
                              f"desktop {dm}  mobile {mm}")
    lines.append(write(ROOT / "00-All-Modules.excalidraw", build_combined()))
    print("\n".join(lines))
    if report:
        print("\nlocalisation")
        print("\n".join(report))
    print("\nOpen in the Excalidraw VS Code extension, or File → Open at https://excalidraw.com")


def coverage():
    """Print every string a locale still leaves in English."""
    for name, mod, _, _ in MODULES:
        if name not in LOCALISED:
            continue
        for loc in LOCALE_FILE_SUFFIX:
            els = copy.deepcopy(mod.desktop() + mod.mobile())
            i18n.localise(els, loc)
            missing = i18n.coverage(els, loc)
            print(f"\n=== {name} · {loc} — {len(missing)} untranslated ===")
            for s in missing:
                print("   ", s.replace("\n", " ⏎ ")[:150])


if __name__ == "__main__":
    if "--coverage" in sys.argv:
        coverage()
    else:
        main()
