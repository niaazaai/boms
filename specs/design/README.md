# Design — Inventory

The finished visual layer. Structure comes from
[`specs/wireframes/`](../wireframes/); this folder decides only how it looks.

> **Generated.** Never hand-edit an SVG here.
> `python3 .agent/scripts/design/build.py`

Open [`index.html`](./index.html) for a contact sheet of everything below.

## Files

| File | What it is |
|------|-----------|
| [`00-design-system.svg`](./00-design-system.svg) | Palette, type scale, components, the barcode/QR rule |
| [`inventory/01-dashboard.svg`](./inventory/01-dashboard.svg) | A1 · Inventory dashboard |
| [`inventory/02-items-list.svg`](./inventory/02-items-list.svg) | B1 · Items list |
| [`inventory/03-new-item-drawer.svg`](./inventory/03-new-item-drawer.svg) | B2 · New item drawer, with the live barcode + QR preview |
| [`inventory/04-item-profile.svg`](./inventory/04-item-profile.svg) | B4 · Item profile · Overview |
| [`inventory/05-item-reservations.svg`](./inventory/05-item-reservations.svg) | B6 · Item profile · Reservations |
| [`inventory/06-stock-ledger.svg`](./inventory/06-stock-ledger.svg) | C1 · Stock ledger |
| `inventory/*-dari.svg` | The same screens in Dari, mirrored |
| [`tokens/theme.css`](./tokens/theme.css) | **The shadcn theme.** Paste into `globals.css` |
| [`tokens/colors.json`](./tokens/colors.json) | Semantic colours, status pairs, radii, shadows |
| [`tokens/typography.json`](./tokens/typography.json) | Type scale and font stacks |

Screen ids match the wireframe ids, so the two can be read side by side.

## Into Figma

Figma imports SVG losslessly: rectangles become frames, text stays editable
text, and the icons arrive as vector paths. The brand screens in `dd/` are Figma
SVG exports, so these land in the same file alongside them.

```
Figma → File → Import…  →  select every .svg in this folder
```

Install **Inter** and **Vazirmatn** first, or Figma substitutes them.

## Into shadcn/ui

The token names are shadcn's, so the theme applies to every component without
restyling them one at a time:

```bash
cp specs/design/tokens/theme.css app/globals.css   # or paste the @layer base block
```

| This design | shadcn component |
|-------------|------------------|
| Sidebar, active nav pill | `sidebar` (`SidebarMenuButton isActive`) |
| Top bar search | `command` in a `dialog` (⌘K) |
| KPI tile | `card` with `CardHeader` / `CardContent` |
| Data table | `table` + TanStack Table |
| Status chip | `badge`, one variant per status in `tokens/colors.json` |
| Drawer / offcanvas | `sheet` with `side="right"` — `side="left"` when `dir="rtl"` |
| Field | `label` + `input` / `select` |
| Pill button | `button` with `rounded-full` |
| Toolbar filter pills | `toggle-group` |

Icons are **lucide-react** — the exact shapes drawn here.

## Rules this design encodes

**Colour comes from the brand, not from a template.** Every hex is measured out
of `dd/Customer Management - AL DUBAI Admin.svg`: the warm off-white page
`#FBF9F6`, the `#F5F3F0` sidebar, the `#73594D` primary pill, the `#FFDDB7`
active nav. `tokens/colors.json` records which role each measured colour plays.

**Barcode and QR are generated from the SKU.** Both carry the same payload.
Neither is ever mirrored — a mirrored Code 128 does not scan — so on the Dari
screens the label card flips position but its contents stay left-to-right.

**No Purpose field, no rental period.** The item profile has a *Channels* table
instead: sale is enabled by a sale price, rental by a rental price. Rental dates
come from the booking.

**Every create and edit is a drawer.** `03-new-item-drawer.svg` shows the
pattern: the list stays on screen behind a dimmed scrim, the drawer has its own
title, subtitle and pinned footer.

**The language switcher names a language.** `English`, `دری`, `پښتو` — never a
direction badge. Direction follows from the language and is set once on `<html>`.

**Numbers stay left-to-right.** Money, quantities, SKUs, barcodes, transaction
numbers and dates use `.ltr-island` (in `theme.css`) and tabular figures, so a
column of afghanis lines up in both directions.

## Still to draw

The Inventory module is complete for the screens listed above. Not yet started:
the remaining Inventory tabs (Stock & movement, Rentals, Photos, Audit), and the
Platform, Procurement, Sales and Finance modules. Their wireframes exist —
adding a screen means adding one function in
`.agent/scripts/design/screens/` and one line in `build.py`.
