# Features index — agent build order

Implement **one feature file at a time** in this order:

| Order | File | Module | Depends on |
|------:|------|--------|------------|
| 1 | [01-platform.md](./01-platform.md) | Platform / Auth / Settings | — |
| 2 | [02-inventory.md](./02-inventory.md) | Inventory | Platform |
| 3 | [03-sales.md](./03-sales.md) | Sales + Rental + Return | Platform, Inventory |
| 4 | [04-procurement.md](./04-procurement.md) | Simple purchasing | Platform, Inventory |
| 5 | [05-finance.md](./05-finance.md) | 5 pillars + P&L | Platform, Sales, Procurement |

## Related specs

- Database: `specs/database/` (`platform`, `inventory`, `sales`, `procurement`, `finance`, `all`)
- Wireframes: `specs/wireframes/`
- Flows: `specs/flows/application-flows.md`

## Product summary

**BOMS** — Bridal Omnichannel Management System for shops that **rent** and **sell** bridal clothing.

- Mobile-first, owner-friendly
- Simple inventory with auditable stock ledger
- Easy sale + rental + return
- Lightweight procurement for correct stock cost & A/P
- Finance with 5 pillars so owner sees profit/loss daily

Stack / infrastructure: **decide later** (explicitly deferred).
