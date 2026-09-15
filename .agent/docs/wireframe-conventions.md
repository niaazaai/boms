# Wireframe conventions (BOMS Excalidraw)

Canonical reference: [`specs/wireframes/README.md`](../../specs/wireframes/README.md)

## Generator

```bash
python3 .agent/scripts/wireframes/build.py
python3 .agent/scripts/wireframes/build.py --coverage   # untranslated strings
```

```
.agent/scripts/wireframes/
  dsl.py        tokens, primitives, components, shells, barcode/QR, mirror()
  i18n.py       Dari and Pashto string tables + localise()
  build.py      writes every board, including the localised ones
  modules/      overview · platform · inventory · procurement · sales · finance
```

Each module exposes `desktop()` and `mobile()` returning flat element lists.
**Never hand-edit `.excalidraw` JSON** — the build overwrites it.

## Layout

- Desktop: 1440×900 frames, 248 px sidebar, 4 per row
- Mobile: 390×844 frames, bottom tabs, 5–6 per row
- `grouped_board(groups, cols)` lays a board out **section by section**, each
  section starting on a fresh row. Use it instead of `grid_pos` for any module
  with more than one group of screens — it is what makes a board readable
  top to bottom.
- Screen ids carry their group: `A1`, `B1…B9`, `C1…C5`, `D1…D3`, `E1`, `E2`,
  `F1…F3`. The same ids appear in `specs/features/` and `specs/design/`.
- `section_label()` names each group; `flow_arrows()` links frames in a row

## UX rules the drawings must obey

- **Every create and edit is a drawer / offcanvas over its list**, with an
  explicit title and subtitle. A list and its form never share a page. Document
  builders with line tables use a wide drawer (760–920 px), not a full page.
- **Invite feature removed** — users are created directly inside a tenant
- **Language is a tenant setting** (English · Dari · Pashto). The switcher shows
  the language name and **never a direction badge** — no `EN (LTR)`, no `RTL`.
- Dari and Pashto mirror the whole shell; numbers, SKUs, barcodes and dates stay
  left to right. See [`localisation.md`](./localisation.md).
- Posted documents offer **Void**, never Edit
- Every screen carries a `note()` naming the tables it reads and writes

## Inventory item rules

- **Barcode is generated from the SKU** (Code 128) and never typed. A QR with
  the same payload sits beside it. `dsl.barcode()`, `dsl.qr()`,
  `dsl.label_card()`.
- **No `purpose` field.** Sellable = has a sale price; rentable = has a rental
  price (ADR-013).
- **No fixed rental period.** Dates come from the booking (ADR-013).

## Data model to draw

Always the corrected model — see `specs/review/02-decisions.md`:

- `owned = on_hand + on_rent`; valuation uses owned
- reservations are not ledger rows (no reserve / release types)
- weighted average cost per (item, warehouse)
- deposits are a liability, never income
- rental amortisation is its own COGS line
- landed cost is visible on receipts

## Checking a board before committing

There is no linter, but two checks catch nearly everything:

1. **Overflow.** Call each `_xN(0, 0)` and compare its bounding box with
   `(0, 0, DESK_W, TITLE_H + DESK_H)`. Anything past the frame edge is a bug.
2. **Coverage.** `build.py --coverage` lists every string a locale still leaves
   in English. Identifiers and file names are expected there; UI copy is not.

## Agent rule

Do **not** read full `.excalidraw` files into context — they are megabytes of
JSON. Read the Python module instead, or regenerate.
