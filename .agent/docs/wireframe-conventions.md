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
| `01-Auth.excalidraw` | Login, Forgot, Users (tenant-bound), multi-role create drawer, Roles, permission matrix |
| `02-Platform-Settings.excalidraw` | Settings hub, Tenants drawer (currency/language/TZ separate; city→address), Branches, Master data, Locale RTL/LTR |
| `03-Inventory.excalidraw` | Hub/valuation, List, Detail, Stock entry (PO+manual), Adjust, Dispose, Transfer, Reserve, Ledger, Reports |
| `04-Sales.excalidraw` | Home, Sale, Rental, Order/Return |
| `05-Procurement.excalidraw` | Home, Suppliers, PO, Receive/Pay |
| `06-Finance.excalidraw` | 5 pillars, cash/expense/AP/AR, P&L |

## UX rules (all modules)

- **Invite feature removed** — users are created directly inside a tenant.
- **Create/edit forms = drawers** — open from **right in LTR**, **left in RTL**.
- **Language** = tenant setting only (English / Dari / Pashto). No per-page language switcher.
- Dari & Pashto → whole UI **RTL**; English → **LTR**.
- Tenant form: **Currency · Language · Timezone** as three fields; **City** then **Address** textarea.

## Agent rule

Do **not** Read full `.excalidraw` into main agent context. Use the excalidraw skill (subagent) or regenerate via `scripts/generate_wireframes.py`.
