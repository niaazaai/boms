# Wireframes

Excalidraw is the **only** wireframe source of truth — there are no markdown screen specs.

## Files

| File | Contents |
|------|----------|
| [`00-Overview.excalidraw`](./00-Overview.excalidraw) | **Open this first.** Sidebar design system, icon set, module map, sitemap, v1→v2 corrections |
| [`00-All-Modules.excalidraw`](./00-All-Modules.excalidraw) | Everything on one canvas — overview + all five modules, desktop and mobile (~14k elements, large file) |
| [`desktop/`](./desktop/) | Per-module desktop boards, 1440×900 frames |
| [`mobile/`](./mobile/) | Per-module mobile boards, 390×844 frames |

| Module | Desktop | Mobile |
|--------|--------:|-------:|
| `01-Platform` — auth, users, roles, tenant, settings, RTL | 14 | 9 |
| `02-Inventory` — items, ledger, movements, reservations, reports | 16 | 10 |
| `03-Procurement` — suppliers, PO, GRN, payments, reports | 14 | 8 |
| `04-Sales` — orders, rentals, returns, customers, reports | 16 | 10 |
| `05-Finance` — 5 pillars, ledger, A/P, A/R, P&L, deposits | 12 | 8 |
| | **72** | **45** |

## Regenerate

```bash
python3 .agent/scripts/wireframes/build.py
```

Everything is generated from Python — never hand-edit the `.excalidraw` JSON, it is
overwritten on every build.

```
.agent/scripts/wireframes/
  dsl.py              design tokens, primitives, components, app shells
  build.py            writes every file, including the combined board
  modules/
    overview.py       sidebar system · module map · sitemap · corrections
    platform.py  inventory.py  procurement.py  sales.py  finance.py
```

Each module exposes `desktop()` and `mobile()`, returning flat lists of Excalidraw
elements. To add a screen, write a `_dN(ox, oy)` function and append it to the
`screens` list in that module's `desktop()`.

## Opening

- VS Code / Cursor: the Excalidraw extension opens `.excalidraw` directly
- Web: <https://excalidraw.com> → File → Open

`00-All-Modules.excalidraw` is ~11 MB; the per-module boards open faster if the
combined canvas is sluggish.

## Conventions

### Layout
- Desktop frames: 1440×900 with a 248px icon sidebar, laid out 4 per row
- Mobile frames: 390×844 with bottom tabs, laid out 5–6 per row
- Screens flow left → right in implementation order, with arrows between them
- Each grid row carries a `section_label` naming that phase of the module

### Annotation
Every screen carries a **note box** stating exactly what it reads and writes, using
real table names. These notes are the contract between the wireframe and
[`specs/database/`](../database/) — if a screen and the schema disagree, the note is
where the disagreement shows up.

### UX rules
- **No invite feature** — users are created directly inside a tenant
- **Create/edit forms are drawers** — right in LTR, **left in RTL**
- **Language is a tenant setting only** (English · Dari · Pashto); no per-page switcher
- Dari and Pashto → the whole UI mirrors; numbers, SKUs and dates stay LTR
- Tenant form: Currency · Language · Timezone as three fields; City, then Address
- Posted documents show **Void**, never Edit

### Data model shown
The wireframes draw the **corrected** model from
[`specs/review/02-decisions.md`](../review/02-decisions.md):

- Owned = on hand + on rent — valuation uses owned
- Reservations are not ledger rows
- Weighted average cost
- Deposits are a liability, shown separately from income
- Rental amortisation as its own COGS line
- Landed cost visible on every receipt
