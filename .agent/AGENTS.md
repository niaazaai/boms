# BOMS — agent instructions

BOMS is a **specs-only** repository: database, wireframes, flows, features and the
finished visual design. There is no application code yet. Your job is almost always
to change a **generator or a spec**, never a generated artefact.

---

## 1 · One agent folder

`.agent/` is the single home for agent skills, docs, guides and scripts.
`.claude/skills` and `.cursor/skills` are **symlinks** into `.agent/skills` — never
copy skills back out, or the three roots drift apart again.

```
.agent/
  AGENTS.md            this file
  README.md            what is installed and why
  skills-lock.json     source repo + SHA-256 for every installed skill
  skills/
    excalidraw/        create / read / update *.excalidraw
    graphify/          codebase & dependency graphs
    playwright-cli/    browser automation, screenshots
    ui-ux-pro-max/     design-system & UX recommendations
  docs/
    wireframe-conventions.md    how BOMS wireframes are laid out
    design-tokens.md            the AL DUBAI brand palette + type scale
    localisation.md             Dari / Pashto rules, Vazirmatn, RTL mirroring
    skill-usage.md              when to reach for each skill
  guides/
    generate-excalidraw-wireframes.md
    generate-design.md
  scripts/
    wireframes/        Excalidraw generator  (dsl.py · build.py · modules/)
    design/            hi-fi SVG generator   (tokens.py · build.py · screens/)
```

---

## 2 · Hard rules

1. **Never hand-edit `specs/wireframes/*.excalidraw`.** They are 100 % generated.
   Edit `.agent/scripts/wireframes/` and rebuild.
2. **Never hand-edit `specs/design/**/*.svg`.** Edit `.agent/scripts/design/` and rebuild.
3. **Never read a whole `.excalidraw` or a `dd/*.svg` into context** — they are
   megabytes of JSON/paths. Read the Python that produced them.
4. **`specs/database/all` is authoritative.** A change to a per-module schema file
   must be mirrored there in the same commit.
5. Every wireframe screen carries a `note()` naming the tables it reads and writes.
   If the note and the schema disagree, fix one of them — do not leave both.

## 3 · Rebuild commands

```bash
python3 .agent/scripts/wireframes/build.py     # → specs/wireframes/**
python3 .agent/scripts/design/build.py         # → specs/design/**
```

Both are idempotent and overwrite their outputs.

---

## 4 · Product rules the drawings must obey

**Inventory item**

- `barcode` is **derived from the SKU** — never typed. Code128 of the SKU, plus a
  QR code carrying the same SKU, both rendered on the item profile.
- There is **no `purpose` field.** An item is sellable if it has a sale price and
  rentable if it has a rental price. Nothing else decides.
- There is **no fixed rental period.** Rentals are open — the dates come from the
  booking, not from the item record.

**Forms**

- Every create/edit is a **drawer / offcanvas** over its list, with an explicit
  title and subtitle. A list and its form never share a page.
- Drawer opens from the trailing edge of the reading direction.

**Language**

- Language is a **tenant setting** (English · Dari · Pashto). The top bar switcher
  shows only the language name — **never an `LTR` / `RTL` badge**; direction is
  implied, not labelled.
- Dari and Pashto mirror the whole shell. Numbers, SKUs, barcodes, currency
  amounts and dates stay left-to-right inside right-to-left text.
- Dari/Pashto type is **Vazirmatn**. See `docs/localisation.md`.

**Data model** (from `specs/review/02-decisions.md`)

- `owned = on_hand + on_rent`; valuation uses `owned`
- reservations are **not** ledger rows — no `reserve` / `release` types
- weighted average cost per (item, warehouse)
- deposits are a liability, never income
- rental amortisation is its own COGS line
- landed cost is visible on every receipt
- posted documents offer **Void**, never Edit

---

## 5 · Which skill when

| Situation | Skill |
|-----------|-------|
| Touching `*.excalidraw` | `skills/excalidraw` — delegate heavy JSON to a subagent |
| Polished UI, colour, type | `skills/ui-ux-pro-max` + `docs/design-tokens.md` |
| Module / schema dependency maps | `skills/graphify` |
| Verifying a running UI | `skills/playwright-cli` |

## 6 · Spec sources of truth

| Layer | Path |
|-------|------|
| Database | `specs/database/` — `all` is authoritative |
| Features & build order | `specs/features/` |
| Wireframes (structure) | `specs/wireframes/` |
| Visual design (finished) | `specs/design/` |
| Flows | `specs/flows/application-flows.md` |
| Review & decisions | `specs/review/` |
