# Skill usage (BOMS)

## excalidraw

Trigger when creating/editing `*.excalidraw` or discussing wireframe diagrams.

- Prefer regenerate via `.agent/scripts/generate_wireframes.py` for full module redraws.
- For small edits, delegate a **subagent** (excalidraw skill) — never load raw JSON in main chat.

## ui-ux-pro-max

Trigger before polished UI implementation (not required for low-fi wireframes).

- Search styles / colors / typography for bridal retail, mobile-first POS.
- Avoid generic purple gradients / Inter-only stacks when building real UI later.

## graphify

Trigger when mapping module dependencies, schema relationships, or codebase structure after code exists.

## playwright-cli

Trigger when verifying running UI (screenshots, flows) after implementation — not needed for wireframe generation.
