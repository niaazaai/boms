# Generate the visual design

From repo root:

```bash
python3 .agent/scripts/design/build.py
```

Overwrites:

```
specs/design/00-design-system.svg
specs/design/inventory/*.svg          English
specs/design/inventory/*-dari.svg     Dari, mirrored
specs/design/tokens/colors.json  typography.json  theme.css
specs/design/index.html               contact sheet
```

Open `specs/design/index.html` to flip through everything.

## Layout of the generator

```
.agent/scripts/design/
  tokens.py            the measured AL DUBAI palette, type scale, radii
                       → also emits the shadcn theme.css
  svg.py               primitives and components: rect · txt · num · icon ·
                       btn · chip · field · stat · table · barcode · qr ·
                       label_card. Canvas(rtl=True) mirrors x for Dari.
  shell.py             sidebar · topbar · page_header · tabs · drawer
  screens/inventory.py one function per screen, EN + FA string tables
  build.py             SCREENS list, the design-system sheet, index.html
```

## Adding a screen

1. Write `def x9_thing(loc="en")` in `screens/inventory.py`, returning a
   `Canvas`. Copy the shape of an existing one.
2. Put every user-visible string in the `EN` dict and its Dari in `FA`.
3. Append it to `SCREENS` in `build.py`; add its path to `DARI` if it should
   ship a Dari version too.
4. Rebuild.

Name the screen after its wireframe id (`A1`, `B4`, `C1` …) so the wireframe,
the feature map and the design all line up.

## Rules

- **Never hand-edit an SVG in `specs/design/`.** It is regenerated.
- Colour comes from `tokens.py` only. No literal hex in a screen function.
- `Canvas.fx()` does the mirroring — write every component left-to-right and
  let the canvas flip it. The one exception is `barcode` / `qr` / `label_card`,
  which flip the canvas back for their own block because a mirrored Code 128
  does not scan.
- Numbers go through `num()` (tabular figures, pinned left-to-right), never
  `txt()`.
- Never apply tracking to Perso-Arabic — `txt()` already zeroes it; do not
  work around that.

## Checking the result

macOS renders SVG through Quick Look:

```bash
qlmanage -t -s 1440 -o /tmp specs/design/inventory/01-dashboard.svg
```

It fits the image into a square, so pad the viewBox to a square first if the
right-hand side looks cut off. Install **Inter** and **Vazirmatn** or the
preview will substitute fonts.
