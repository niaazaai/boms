#!/usr/bin/env python3
"""Build every BOMS Excalidraw wireframe.

    python3 .agent/scripts/wireframes/build.py

Writes:
    specs/wireframes/00-All-Modules.excalidraw     every module on one canvas
    specs/wireframes/00-Overview.excalidraw        sidebar / map / sitemap
    specs/wireframes/desktop/*.excalidraw          per module
    specs/wireframes/mobile/*.excalidraw           per module
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dsl import (BG, DESK_H, DESK_W, INK, MUTED, ROSE, board_title,  # noqa: E402
                 doc, rect, section_label, text)
from modules import finance, inventory, overview, platform, procurement, sales  # noqa: E402

ROOT = HERE.parents[2] / "specs" / "wireframes"

MODULES = [
    ("01-Platform", platform, "Platform · Auth · Settings", "#0d9488"),
    ("02-Inventory", inventory, "Inventory", "#2563eb"),
    ("03-Procurement", procurement, "Procurement", "#d97706"),
    ("04-Sales", sales, "Sales", "#059669"),
    ("05-Finance", finance, "Finance", "#7c3aed"),
]


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
    return f"  {rel:52s} {len(elements):6d} el   {int(x1 - x0):6d} × {int(y1 - y0):5d}"


def build_combined():
    """Every module board stacked vertically on one canvas, with banners."""
    els = board_title(0, -420,
                      "BOMS — Complete Wireframes · All Modules",
                      "Bridal Omnichannel Management System.  Overview · Platform · Inventory · "
                      "Procurement · Sales · Finance — desktop and mobile.")
    els.append(text(0, -350,
                    "Reading order: the Overview band defines the navigation shell and the module map. "
                    "Each module band then runs desktop screens left→right, with its mobile screens beneath.\n"
                    "Corrected data model throughout — see specs/review/01-spec-review.md and 02-decisions.md.",
                    14, MUTED, width=3000))

    cursor_y = 0.0
    BAND_GAP = 700.0

    # Overview band
    ov = overview.board()
    _, oy0, _, oy1 = bounds(ov)
    els += translate(ov, 0, cursor_y - oy0)
    cursor_y += (oy1 - oy0) + BAND_GAP

    for name, mod, label, color in MODULES:
        desk = mod.desktop()
        mob = mod.mobile()
        dx0, dy0, dx1, dy1 = bounds(desk)
        mx0, my0, mx1, my1 = bounds(mob)

        # band banner
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
    lines = []
    lines.append(write(ROOT / "00-Overview.excalidraw", overview.board()))
    for name, mod, label, _ in MODULES:
        lines.append(write(ROOT / "desktop" / f"{name}.excalidraw", mod.desktop()))
        lines.append(write(ROOT / "mobile" / f"{name}.excalidraw", mod.mobile()))
    lines.append(write(ROOT / "00-All-Modules.excalidraw", build_combined()))
    print("\n".join(lines))
    print("\nOpen in the Excalidraw VS Code extension, or File → Open at https://excalidraw.com")


if __name__ == "__main__":
    main()
