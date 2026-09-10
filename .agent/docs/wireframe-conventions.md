# Wireframe conventions (BOMS Excalidraw)

## Layout

### Mobile (`specs/wireframes/mobile/`)
- Screens flow **left → right** in page order.
- Each screen is a **phone frame** ~375×812.
- Bottom tab nav: Home · Inventory · Sales · More.

### Desktop (`specs/wireframes/desktop/`)
- Screens flow **left → right** in page order.
- Each screen is a **browser window** ~1280×800.
- Left sidebar nav (except Auth): Home · Inventory · Sales · Procurement · Finance · Settings.
- Content uses tables, KPI cards, and split panels (cashier-friendly).

## Modules → files (both folders)

| File | Screens |
|------|---------|
| `01-Auth.excalidraw` | Welcome, Login, Register, Invite |
| `02-Platform-Settings.excalidraw` | Home, Settings, Shop, Branches/Users |
| `03-Inventory.excalidraw` | List, Detail, Add, Adjust/Transfer |
| `04-Sales.excalidraw` | Home, Sale, Rental, Order/Return |
| `05-Procurement.excalidraw` | Home, Suppliers, PO, Receive/Pay |
| `06-Finance.excalidraw` | 5 pillars, cash/expense/AP/AR, P&L |

## Agent rule

Do **not** Read full `.excalidraw` into main agent context. Use the excalidraw skill (subagent) or regenerate via `scripts/generate_wireframes.py`.
