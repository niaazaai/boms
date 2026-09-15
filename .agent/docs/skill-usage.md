# Skill usage (BOMS)

## excalidraw

Trigger when creating/editing `*.excalidraw` or discussing wireframe diagrams.

- Prefer regenerating: `python3 .agent/scripts/wireframes/build.py`.
- For small edits, delegate to a **subagent** — never load raw `.excalidraw`
  JSON into the main chat; the Inventory board alone is ~5,000 elements.
- Conventions: [`wireframe-conventions.md`](./wireframe-conventions.md).

## ui-ux-pro-max

Trigger before polished UI work (not needed for low-fidelity wireframes).

- The palette is already decided and measured —
  [`design-tokens.md`](./design-tokens.md). Use the skill for interaction and
  layout judgement, not to pick colours.
- Never introduce a blue or violet: the finished design is a warm neutral
  palette taken from the client's own brand screens.

## graphify

Trigger when mapping module dependencies, schema relationships, or codebase
structure once code exists.

## playwright-cli

Trigger when verifying a running UI (screenshots, flows) after implementation.
Not needed for wireframe or design generation — those render with
`qlmanage -t` on macOS.
