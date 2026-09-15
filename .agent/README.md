# BOMS Agent Kit (`.agent`)

One folder. One copy of every skill. Everything an assistant needs to work on the
BOMS specs.

> Start at [`AGENTS.md`](./AGENTS.md).

## Layout

```
.agent/
  AGENTS.md            rules every agent must follow
  README.md            this file
  skills-lock.json     source repo + SHA-256 for every installed skill
  skills/              the four skills — single canonical copy
  docs/                conventions and reference
  guides/              runbooks
  scripts/             generators (wireframes · design)
```

## Skills

| Skill | Source | Use for |
|-------|--------|---------|
| [`skills/excalidraw`](./skills/excalidraw) | softaworks/agent-toolkit | Create/read/update `*.excalidraw` via subagents — never load raw JSON in the main chat |
| [`skills/graphify`](./skills/graphify) | graphify-labs/graphify | Codebase / dependency / schema graphs |
| [`skills/playwright-cli`](./skills/playwright-cli) | microsoft/playwright-cli | Browser automation & UI verification |
| [`skills/ui-ux-pro-max`](./skills/ui-ux-pro-max) | nextlevelbuilder/ui-ux-pro-max-skill | Design-system & UX recommendations |

Provenance and hashes: [`skills-lock.json`](./skills-lock.json).

### One copy, three roots

There used to be three full copies of `skills/` — `.agent/`, `.agents/` and
`.cursor/` — ~25 MB that silently drifted. Now there is one:

| Tool | Path | Kind |
|------|------|------|
| Any agent | `.agent/skills` | **real directory** |
| Claude Code | `.claude/skills` | symlink → `../.agent/skills` |
| Cursor | `.cursor/skills` | symlink → `../.agent/skills` |
| Repo root | `CLAUDE.md` | symlink → `.agent/AGENTS.md` |
| Repo root | `AGENTS.md` | pointer file |

To add a skill, install it into `.agent/skills/` and record it in
`skills-lock.json`. Never copy it into `.claude/` or `.cursor/`.

## Docs

| File | Contents |
|------|----------|
| [`docs/wireframe-conventions.md`](./docs/wireframe-conventions.md) | How BOMS Excalidraw wireframes are laid out and what the notes mean |
| [`docs/design-tokens.md`](./docs/design-tokens.md) | AL DUBAI brand palette, type scale, radii, shadows — the shadcn theme |
| [`docs/localisation.md`](./docs/localisation.md) | Dari / Pashto terminology, Vazirmatn, RTL mirroring rules |
| [`docs/skill-usage.md`](./docs/skill-usage.md) | When to invoke each skill |
| [`docs/excalidraw-skill-readme.md`](./docs/excalidraw-skill-readme.md) | Upstream Excalidraw skill notes |

## Guides

- [`guides/generate-excalidraw-wireframes.md`](./guides/generate-excalidraw-wireframes.md)
- [`guides/generate-design.md`](./guides/generate-design.md)

## Scripts

```bash
python3 .agent/scripts/wireframes/build.py     # → specs/wireframes/**
python3 .agent/scripts/design/build.py         # → specs/design/**
```

```
scripts/
  wireframes/
    dsl.py            tokens, primitives, components, shells (LTR + RTL)
    i18n.py           EN · Dari · Pashto string tables
    build.py          writes every board, per module and combined
    modules/          overview · platform · inventory · procurement · sales · finance
  design/
    tokens.py         the AL DUBAI palette as design tokens
    svg.py            hi-fi SVG primitive layer
    build.py          writes the finished Inventory screens
    screens/          one module per screen group
```

## Spec sources of truth

1. Database → `specs/database/` (`all` is authoritative)
2. Features → `specs/features/`
3. Wireframes → `specs/wireframes/desktop|mobile/`
4. Visual design → `specs/design/`
5. Flows → `specs/flows/`
6. Review & decisions → `specs/review/`
