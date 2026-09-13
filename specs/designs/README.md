# Designs

Visual UI designs will live here. **Nothing here yet.**

## Current source of truth

| Layer | Where | Owns |
|-------|-------|------|
| Structure & behaviour | [`specs/wireframes/`](../wireframes/) (Excalidraw) | Screen layout, fields, states, what each screen reads and writes |
| Data | [`specs/database/`](../database/) | Tables, constraints, posting effects |
| Flows | [`specs/flows/`](../flows/) | End-to-end sequences |
| Visual polish | *this folder* — not started | Type scale, colour, spacing, motion, components |

Wireframes are deliberately low-fidelity: greys, one teal accent, one rose accent.
They define **what is on the screen and what it does**, not how it should look.

## Next step

Build a component library from the wireframe DSL primitives
(`.agent/scripts/wireframes/dsl.py`), which already encodes the intended structure:

| Wireframe primitive | Design system component |
|---------------------|-------------------------|
| `sidebar` | App navigation shell, expanded + 72px rail + RTL mirror |
| `page_header` | Page title, subtitle, action cluster |
| `stat_row` / `kpi_card` | KPI tiles with delta and icon |
| `table` | Data table: header, zebra, cell colour states, pagination |
| `drawer` | Side sheet — right in LTR, left in RTL |
| `field` / `select` / `textarea` | Form controls with label, required marker, hint |
| `chip` / `filter_chips` | Status chips and filter pills |
| `timeline` | Document status stepper |
| `note` | Spec annotation — **wireframe only**, not shipped |
| `empty_state` / `modal` | Empty and confirm states |

## Design constraints already fixed by the specs

- **RTL is not optional.** Dari and Pashto are primary locales; every component
  needs a mirrored form. Numbers, SKUs, currency and dates stay LTR inside RTL text.
- **Mobile-first.** The owner's daily loop happens on a phone: Home · Inventory ·
  Sales · Finance · More.
- **Money needs three weights** — a value, its currency, and whether it is *yours*
  (the deposits-held distinction runs through the whole finance UI).
- **Posted documents show Void, never Edit.** The visual language must make an
  immutable document feel different from a draft.
