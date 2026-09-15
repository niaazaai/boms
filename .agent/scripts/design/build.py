#!/usr/bin/env python3
"""Build the finished BOMS visual design.

    python3 .agent/scripts/design/build.py

Writes:
    specs/design/inventory/*.svg          screens, English
    specs/design/inventory/*-dari.svg     the same screens in Dari, mirrored
    specs/design/00-design-system.svg     palette, type, components
    specs/design/tokens/colors.json       semantic colour tokens
    specs/design/tokens/typography.json   type scale + font stacks
    specs/design/tokens/theme.css         the shadcn theme, ready to paste
    specs/design/index.html               a contact sheet of everything

SVG because Figma imports it losslessly — rectangles become frames, text stays
editable text. The brand screens in `dd/` are Figma SVG exports, so these
round-trip into the same file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "screens"))

import tokens as TK  # noqa: E402
from screens import inventory as INV  # noqa: E402
from svg import (Canvas, barcode, btn, card, chip, field, icon, icon_btn, line,  # noqa: E402
                 qr, rect, stat, table, txt)
from tokens import C, RADIUS, STATUS, TYPE  # noqa: E402

OUT = HERE.parents[2] / "specs" / "design"

SCREENS = [
    ("inventory/01-dashboard",            INV.a1_dashboard,     "A1 · Inventory dashboard"),
    ("inventory/02-items-list",           INV.b1_items,         "B1 · Items list"),
    ("inventory/03-new-item-drawer",      INV.b2_new_item,      "B2 · New item drawer"),
    ("inventory/04-item-profile",         INV.b4_item_profile,  "B4 · Item profile · Overview"),
    ("inventory/05-item-reservations",    INV.b6_reservations,  "B6 · Item profile · Reservations"),
    ("inventory/06-stock-ledger",         INV.c1_ledger,        "C1 · Stock ledger"),
]

# Which screens also ship a Dari version.
DARI = {"inventory/01-dashboard", "inventory/03-new-item-drawer",
        "inventory/04-item-profile", "inventory/06-stock-ledger"}


# ── design system sheet ───────────────────────────────────────────

def design_system():
    W, H = 1440, 1500
    cv = Canvas(W, H, title="BOMS · AL DUBAI design system")
    txt(cv, 64, 56, "AL DUBAI · BOMS", "display", C["ink"])
    txt(cv, 64, 98, "Design tokens for the Inventory module. Colours measured from "
                    "dd/Customer Management - AL DUBAI Admin.svg.", "body", C["muted"])
    line(cv, 64, 136, W - 128, C["border"])

    # palette
    y = 168
    txt(cv, 64, y, "COLOUR", "micro", C["muted"], upper=True)
    groups = [
        ("Surfaces", [("bg", "Page"), ("sidebar", "Sidebar"), ("surface", "Card"),
                      ("surface_2", "Tile / input"), ("border", "Border"),
                      ("divider", "Divider")]),
        ("Text", [("ink", "Heading"), ("body", "Body"), ("muted", "Secondary"),
                  ("disabled", "Disabled")]),
        ("Brand", [("primary", "Primary"), ("primary_press", "Pressed"),
                   ("accent", "Active nav"), ("accent_2", "Warning surface"),
                   ("tan", "Chip"), ("bronze", "Bronze")]),
        ("Status", [("success", "Success"), ("warning", "Warning"),
                    ("danger", "Danger"), ("info", "Info")]),
    ]
    yy = y + 28
    for name, keys in groups:
        txt(cv, 64, yy + 14, name, "body_medium", C["ink"])
        for i, (k, label) in enumerate(keys):
            sx = 200 + i * 168
            rect(cv, sx, yy, 152, 56, C[k], C["border"] if k in
                 ("bg", "surface", "surface_2", "sidebar") else None, RADIUS["sm"])
            txt(cv, sx, yy + 62, label, "caption", C["body"])
            txt(cv, sx, yy + 78, C[k].upper(), "caption", C["muted"])
        yy += 116

    # type
    ty = yy + 24
    line(cv, 64, ty - 24, W - 128, C["border"])
    txt(cv, 64, ty, "TYPE", "micro", C["muted"], upper=True)
    txt(cv, 64, ty + 24, "Latin — Inter", "body_medium", C["ink"])
    txt(cv, 1240, ty + 24, "Dari & Pashto — Vazirmatn", "body_medium", C["ink"],
        "end", family=TK.FONT_LATIN)
    yy = ty + 60
    for style in ["display", "h1", "h2", "h3", "body", "small", "caption", "micro"]:
        size, lh, weight, track = TYPE[style]
        txt(cv, 64, yy, f"{style}", "caption", C["muted"])
        txt(cv, 200, yy - size / 3, "The gown is still an asset", style, C["ink"])
        # anchored at its right edge — direction="rtl" makes `start` the right side
        txt(cv, 1240, yy - size / 3, "پیراهن هنوز یک دارایی است", style, C["ink"],
            family=TK.FONT_RTL)
        txt(cv, W - 64, yy, f"{size}/{lh} · {weight}", "caption", C["muted"], "end")
        yy += max(34, size + 16)

    # components
    cy = yy + 24
    line(cv, 64, cy - 20, W - 128, C["border"])
    txt(cv, 64, cy, "COMPONENTS", "micro", C["muted"], upper=True)
    by = cy + 28
    btn(cv, 64, by, 140, 44, "Primary", "primary")
    btn(cv, 216, by, 140, 44, "Secondary", "secondary")
    btn(cv, 368, by, 120, 44, "Ghost", "ghost")
    btn(cv, 500, by, 140, 44, "New item", "primary", "plus")
    icon_btn(cv, 656, by + 2, "bell", 40)
    cx = 716
    for state in ["active", "on rent", "reserved", "conflict", "draft"]:
        cx = chip(cv, cx, by + 10, state, state, h=26)

    fy = by + 72
    field(cv, 64, fy, 280, "Sale price", "48,000")
    field(cv, 360, fy, 280, "Warehouse", "Main Store", chevron=True)
    field(cv, 656, fy, 280, "SKU", "ADF26-0042", locked=True,
          hint="generated · read-only")

    # barcode + QR
    ly = fy + 108
    txt(cv, 64, ly, "BARCODE & QR — GENERATED FROM THE SKU", "micro", C["muted"], upper=True)
    rect(cv, 64, ly + 22, 560, 150, C["surface"], C["border"], RADIUS["card"])
    barcode(cv, 88, ly + 46, 380, 96, "ADF26-0042")
    qr(cv, 496, ly + 46, 100, "ADF26-0042")
    txt(cv, 660, ly + 40, "One identity, two symbols.", "h3", C["ink"])
    txt(cv, 660, ly + 70,
        "barcode = code128(sku) — stored, unique per tenant, never typed.", "small", C["body"])
    txt(cv, 660, ly + 92,
        "QR carries the same payload and is rendered, never stored.", "small", C["body"])
    txt(cv, 660, ly + 114,
        "Neither is ever mirrored: a mirrored Code 128 does not scan.", "small", C["danger"])
    return cv


# ── contact sheet ─────────────────────────────────────────────────

def index_html(written):
    rows = "\n".join(
        f'    <figure><a href="{p}" target="_blank"><img src="{p}" alt="{t}"></a>'
        f'<figcaption><b>{t}</b><span>{p}</span></figcaption></figure>'
        for p, t in written)
    return f"""<!doctype html>
<meta charset="utf-8">
<title>BOMS · Inventory design</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ margin:0; padding:48px; background:{C['bg']}; color:{C['ink']};
         font:400 15px/1.55 Inter,-apple-system,'Segoe UI',Roboto,sans-serif; }}
  h1 {{ font-size:30px; margin:0 0 6px; letter-spacing:-.4px; }}
  p.lede {{ color:{C['muted']}; max-width:70ch; margin:0 0 40px; }}
  .grid {{ display:grid; gap:36px; grid-template-columns:repeat(auto-fill,minmax(520px,1fr)); }}
  figure {{ margin:0; }}
  img {{ width:100%; display:block; border:1px solid {C['border']}; border-radius:14px;
         background:#fff; box-shadow:0 8px 24px rgba(27,28,26,.05); }}
  figcaption {{ margin-top:12px; display:flex; flex-direction:column; gap:2px; }}
  figcaption span {{ color:{C['muted']}; font-size:13px; }}
  a {{ color:inherit; text-decoration:none; }}
</style>
<h1>BOMS · Inventory — finished design</h1>
<p class="lede">AL DUBAI palette, shadcn component shapes, Inter for Latin and
Vazirmatn for Dari and Pashto. Every SVG here imports into Figma as editable
frames and text. Structure comes from
<code>specs/wireframes/desktop/02-Inventory.excalidraw</code>; only the finish
differs.</p>
<div class="grid">
{rows}
</div>
"""


# ── main ──────────────────────────────────────────────────────────

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "inventory").mkdir(exist_ok=True)
    (OUT / "tokens").mkdir(exist_ok=True)
    written, log = [], []

    def put(rel, svg, title):
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(svg)
        written.append((rel, title))
        log.append(f"  {rel:46s} {len(svg) // 1024:5d} KB")

    put("00-design-system.svg", design_system().render(), "Design system")
    for rel, fn, title in SCREENS:
        put(f"{rel}.svg", fn("en").render(), title)
        if rel in DARI:
            put(f"{rel}-dari.svg", fn("fa").render(), f"{title} — دری")

    (OUT / "tokens" / "colors.json").write_text(json.dumps(
        {"source": "dd/Customer Management - AL DUBAI Admin.svg",
         "semantic": C, "status": {k: {"fg": v[0], "bg": v[1]} for k, v in STATUS.items()},
         "raw": TK.RAW, "radius": RADIUS, "shadow": TK.SHADOW}, indent=2))
    (OUT / "tokens" / "typography.json").write_text(json.dumps(
        {"fonts": {"latin": TK.FONT_LATIN, "rtl": TK.FONT_RTL, "mono": TK.FONT_MONO},
         "note": "Dari and Pashto are set in Vazirmatn — it carries the four-eye heh, "
                 "the Persian kaf and yeh, and Pashto's ښ ځ ټ. Numbers, SKUs, barcodes, "
                 "money and dates stay left-to-right inside right-to-left text.",
         "scale": {k: {"size": v[0], "line": v[1], "weight": v[2], "tracking": v[3]}
                   for k, v in TYPE.items()}}, indent=2))
    (OUT / "tokens" / "theme.css").write_text(TK.css_variables())
    (OUT / "index.html").write_text(index_html(written))

    print("BOMS design\n")
    print("\n".join(log))
    print(f"  {'tokens/colors.json · typography.json · theme.css':46s}")
    print(f"  {'index.html  (contact sheet)':46s}")
    print(f"\n{len(written)} SVGs → {OUT}")


if __name__ == "__main__":
    main()
