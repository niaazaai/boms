# Wireframe conventions (BOMS Excalidraw)

Canonical reference: [`specs/wireframes/README.md`](../../specs/wireframes/README.md)

## Generator

```bash
python3 .agent/scripts/wireframes/build.py
```

```
.agent/scripts/wireframes/
  dsl.py        tokens, primitives, components, phone_shell / desk_shell / sidebar
  build.py      writes all boards incl. the combined 00-All-Modules
  modules/      overview · platform · inventory · procurement · sales · finance
```

Each module exposes `desktop()` and `mobile()` returning flat element lists.
Never hand-edit `.excalidraw` JSON — the build overwrites it.

## Layout

- Desktop: 1440×900 frames, 248px icon sidebar, 4 per row
- Mobile: 390×844 frames, bottom tabs, 5–6 per row
- `grid_pos(i, cols)` places frames; `flow_arrows()` links them
- `section_label()` names each grid row

## UX rules

- **Invite feature removed** — users are created directly inside a tenant
- **Create/edit forms are drawers** — right in LTR, **left in RTL**
- **Language is a tenant setting** (English · Dari · Pashto); no per-page switcher
- Dari & Pashto → whole UI RTL; numbers, SKUs, dates stay LTR
- Tenant form: Currency · Language · Timezone as three fields; City then Address
- Posted documents offer **Void**, never Edit
- Every screen carries a `note()` naming the tables it reads and writes

## Data model to draw

Always the corrected model — see `specs/review/02-decisions.md`:

- `owned = on_hand + on_rent`; valuation uses owned
- Reservations are not ledger rows (no reserve/release types)
- Weighted average cost per (item, warehouse)
- Deposits are a liability, never income
- Rental amortisation is its own COGS line
- Landed cost is visible on receipts

## Agent rule

Do **not** read full `.excalidraw` files into context — they are megabytes of JSON.
Read the Python module instead, or regenerate.
