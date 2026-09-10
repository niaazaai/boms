# BOMS Agent Kit (`.agent`)

Project-local agent skills and docs for BOMS wireframes, UX, graphs, and browser checks.

## Skills installed

| Skill | Source | Use for |
|-------|--------|---------|
| `skills/excalidraw` | softaworks/agent-toolkit | Create/read/update `*.excalidraw` via subagents (never load raw JSON in main chat) |
| `skills/graphify` | graphify-labs/graphify | Codebase / dependency graphs |
| `skills/playwright-cli` | microsoft/playwright-cli | Browser automation & UI verification |
| `skills/ui-ux-pro-max` | nextlevelbuilder/ui-ux-pro-max-skill | Design system / UX recommendations |

Cursor also mirrors these under:

- `.agents/skills/` (skills CLI install root)
- `.cursor/skills/` (Cursor discovery)

## Docs

- [`docs/wireframe-conventions.md`](./docs/wireframe-conventions.md) — how BOMS Excalidraw wireframes are laid out
- [`docs/skill-usage.md`](./docs/skill-usage.md) — when to invoke each skill
- [`guides/generate-excalidraw-wireframes.md`](./guides/generate-excalidraw-wireframes.md) — regenerate wireframes

## Scripts

- [`scripts/generate_wireframes.py`](./scripts/generate_wireframes.py) — builds clean mobile-first Excalidraw wireframes into `specs/wireframes/`

```bash
python3 .agent/scripts/generate_wireframes.py
```

## Spec sources of truth

1. Database → `specs/database/`
2. Features → `specs/features/`
3. Wireframes (Excalidraw) → `specs/wireframes/mobile/` + `specs/wireframes/desktop/`
4. Flows → `specs/flows/`
5. Features → `specs/features/`
