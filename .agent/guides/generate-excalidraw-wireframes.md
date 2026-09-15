# Generate Excalidraw wireframes

From repo root:

```bash
python3 .agent/scripts/wireframes/build.py
python3 .agent/scripts/wireframes/build.py --coverage   # untranslated strings
```

Outputs overwrite:

```
specs/wireframes/00-Overview.excalidraw
specs/wireframes/00-All-Modules.excalidraw
specs/wireframes/desktop/*.excalidraw
specs/wireframes/mobile/*.excalidraw
specs/wireframes/desktop|mobile/02-Inventory-Dari.excalidraw
specs/wireframes/desktop|mobile/02-Inventory-Pashto.excalidraw
```

Open any file in the Excalidraw VS Code/Cursor extension, or at
<https://excalidraw.com> (File → Open).

**Excalidraw is the only wireframe source of truth** — there are no markdown
screen specs, and the JSON is never hand-edited.

## Adding a screen

1. Write `def _x9(ox, oy)` in `.agent/scripts/wireframes/modules/<module>.py`.
2. Add it to the right group in that module's `GROUPS` list.
3. Rebuild, then check the screen fits its frame: its bounding box must stay
   inside `(0, 0, DESK_W, TITLE_H + DESK_H)`.

## Adding a localised board

Add the module name to `LOCALISED` in `build.py`, run `--coverage`, and fill the
gaps in `i18n.py`. See [`../docs/localisation.md`](../docs/localisation.md).
