#!/usr/bin/env python3
"""AL DUBAI design tokens.

Every colour here was read out of `dd/Customer Management - AL DUBAI Admin.svg`
— the existing brand screens — not invented. Only the palette is taken from that
file; layout and structure come from `specs/wireframes/`.

The names are shadcn/ui's, so the CSS variables this file generates can be
pasted straight into a shadcn theme and every component picks the brand up
without being restyled one by one.
"""

from __future__ import annotations

# ── Brand palette, as measured ────────────────────────────────────
# hex                role in the source file
RAW = {
    "#FBF9F6": "page background, and the fill of input controls",
    "#F5F3F0": "the 288px sidebar, and stat tiles on the page",
    "#FFFFFF": "cards and tables",
    "#E8E4DF": "card borders",
    "#EAE8E5": "dividers and icon buttons",
    "#1B1C1A": "headings",
    "#4F4440": "body copy and icons",
    "#6B6B6B": "secondary / helper text",
    "#73594D": "primary button fill (pill), brand marks",
    "#553D32": "primary pressed",
    "#FFDDB7": "active sidebar item",
    "#FED6A8": "warning surface",
    "#2A1800": "text on the peach surfaces",
    "#C9A89A": "tan chip",
    "#4A7C59": "success",
    "#B54A4A": "danger",
    "#C4A035": "gold / caution",
    "#795B36": "bronze",
    "#9CA3AF": "disabled",
}

# ── Semantic tokens ───────────────────────────────────────────────

C = {
    "bg":            "#FBF9F6",
    "sidebar":       "#F5F3F0",
    "surface":       "#FFFFFF",
    "surface_2":     "#F5F3F0",
    "input":         "#FBF9F6",
    "border":        "#E8E4DF",
    "divider":       "#EAE8E5",

    "ink":           "#1B1C1A",
    "body":          "#4F4440",
    "muted":         "#6B6B6B",
    "disabled":      "#9CA3AF",

    "primary":       "#73594D",
    "primary_press": "#553D32",
    "primary_fg":    "#FFFFFF",
    "primary_soft":  "#F0EAE6",

    "accent":        "#FFDDB7",
    "accent_2":      "#FED6A8",
    "accent_ink":    "#2A1800",
    "tan":           "#C9A89A",
    "bronze":        "#795B36",

    "success":       "#4A7C59",
    "success_bg":    "#EDF3EF",
    "danger":        "#B54A4A",
    "danger_bg":     "#F7ECEC",
    "warning":       "#C4A035",
    "warning_bg":    "#FBF4E3",
    "info":          "#73594D",
    "info_bg":       "#F0EAE6",
}

# Status → (text colour, surface colour). One place, so a chip and a table cell
# for the same state can never disagree.
STATUS = {
    "active":        (C["success"], C["success_bg"]),
    "available":     (C["success"], C["success_bg"]),
    "completed":     (C["success"], C["success_bg"]),
    "fulfilled":     (C["muted"],   C["surface_2"]),
    "returned":      (C["success"], C["success_bg"]),
    "on rent":       (C["bronze"],  C["warning_bg"]),
    "reserved":      (C["warning"], C["warning_bg"]),
    "in transit":    (C["bronze"],  C["warning_bg"]),
    "partial":       (C["warning"], C["warning_bg"]),
    "repairing":     (C["warning"], C["warning_bg"]),
    "low stock":     (C["danger"],  C["danger_bg"]),
    "conflict":      (C["danger"],  C["danger_bg"]),
    "disposed":      (C["danger"],  C["danger_bg"]),
    "discontinued":  (C["muted"],   C["surface_2"]),
    "draft":         (C["muted"],   C["surface_2"]),
    "released":      (C["muted"],   C["surface_2"]),
    "cancelled":     (C["muted"],   C["surface_2"]),
}

# ── Type ──────────────────────────────────────────────────────────
# Latin is Inter (shadcn's default, so nothing has to be re-specified).
# Dari and Pashto are Vazirmatn — it has the four-eye heh, the Persian kaf and
# yeh, and Pashto's ښ ځ ټ, which Inter and Noto Naskh handle badly or not at all.

FONT_LATIN = "Inter, -apple-system, 'Segoe UI', Roboto, sans-serif"
FONT_RTL = "Vazirmatn, 'Noto Naskh Arabic', Tahoma, sans-serif"
FONT_MONO = "'JetBrains Mono', 'SF Mono', Menlo, monospace"

TYPE = {
    # name          size  line  weight  tracking
    "display":      (28,  34,   650,    -0.4),
    "h1":           (24,  30,   650,    -0.3),
    "h2":           (20,  26,   620,    -0.2),
    "h3":           (16,  22,   600,    -0.1),
    "body":         (14,  20,   400,     0.0),
    "body_medium":  (14,  20,   540,     0.0),
    "small":        (13,  18,   400,     0.0),
    "caption":      (12,  16,   400,     0.0),
    "label":        (12,  16,   540,     0.0),
    "micro":        (11,  14,   600,     0.6),   # UPPERCASE section labels
    "numeric":      (24,  28,   620,    -0.4),   # KPI values, tabular figures
}

RADIUS = {"card": 16, "control": 12, "tile": 12, "pill": 999, "chip": 999, "sm": 8}

SHADOW = {
    "card": "0 1px 2px rgba(27,28,26,0.04), 0 8px 24px rgba(27,28,26,0.05)",
    "drawer": "-24px 0 48px rgba(27,28,26,0.12)",
    "pop": "0 12px 32px rgba(27,28,26,0.14)",
}

# ── Layout ────────────────────────────────────────────────────────
FRAME_W, FRAME_H = 1440, 1024
SIDEBAR_W = 288
TOPBAR_H = 64
GUTTER = 32
PHONE_W, PHONE_H = 390, 844


def css_variables() -> str:
    """The shadcn theme. Paste into `globals.css` and every component follows."""
    def hsl(hex_):
        h = hex_.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        mx, mn = max(r, g, b), min(r, g, b)
        l = (mx + mn) / 2
        if mx == mn:
            hu = sa = 0.0
        else:
            d = mx - mn
            sa = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
            if mx == r:
                hu = ((g - b) / d + (6 if g < b else 0))
            elif mx == g:
                hu = (b - r) / d + 2
            else:
                hu = (r - g) / d + 4
            hu /= 6
        return f"{hu * 360:.1f} {sa * 100:.1f}% {l * 100:.1f}%"

    m = [
        ("--background", C["bg"]), ("--foreground", C["ink"]),
        ("--card", C["surface"]), ("--card-foreground", C["ink"]),
        ("--popover", C["surface"]), ("--popover-foreground", C["ink"]),
        ("--primary", C["primary"]), ("--primary-foreground", C["primary_fg"]),
        ("--secondary", C["surface_2"]), ("--secondary-foreground", C["body"]),
        ("--muted", C["surface_2"]), ("--muted-foreground", C["muted"]),
        ("--accent", C["accent"]), ("--accent-foreground", C["accent_ink"]),
        ("--destructive", C["danger"]), ("--destructive-foreground", "#FFFFFF"),
        ("--success", C["success"]), ("--warning", C["warning"]),
        ("--border", C["border"]), ("--input", C["border"]), ("--ring", C["primary"]),
        ("--sidebar", C["sidebar"]), ("--sidebar-foreground", C["body"]),
        ("--sidebar-accent", C["accent"]), ("--sidebar-accent-foreground", C["accent_ink"]),
        ("--sidebar-border", C["border"]),
    ]
    lines = [
        "/* AL DUBAI — BOMS theme.",
        "   Generated by .agent/scripts/design/tokens.py — do not hand-edit.",
        "   Colours are measured from dd/Customer Management - AL DUBAI Admin.svg. */",
        "",
        "@layer base {",
        "  :root {",
    ]
    lines += [f"    {k}: {hsl(v)};   /* {v} */" for k, v in m]
    lines += [
        f"    --radius: {RADIUS['control']}px;",
        "",
        f"    --font-sans: {FONT_LATIN};",
        f"    --font-rtl: {FONT_RTL};",
        f"    --font-mono: {FONT_MONO};",
        "  }",
        "",
        "  /* Dari and Pashto. `dir` is set on <html> from the tenant language;",
        "     nothing in the UI ever labels the direction. */",
        '  [dir="rtl"] { font-family: var(--font-rtl); }',
        "",
        "  /* Numbers, SKUs, barcodes, money and dates keep reading left-to-right",
        "     inside right-to-left text. */",
        '  [dir="rtl"] .ltr-island { direction: ltr; unicode-bidi: isolate; }',
        "",
        "  body { background: hsl(var(--background)); color: hsl(var(--foreground)); }",
        "  .tabular { font-variant-numeric: tabular-nums; }",
        "}",
        "",
    ]
    return "\n".join(lines)
