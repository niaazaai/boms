# Features index — build order

Implement **one module at a time**, in this order. The order is FK-safe: nothing
references a table that does not exist yet.

| Order | File | Module | Depends on |
|------:|------|--------|------------|
| 1 | [01-platform.md](./01-platform.md) | Platform · auth · RBAC · master data · infrastructure | — |
| 2 | [02-finance-core.md](./02-finance-core.md) | Finance-Core · accounts, ledger, deposits, COGS | Platform |
| 3 | [03-inventory.md](./03-inventory.md) | Inventory · catalogue, ledger, WAC, reservations | Platform, Finance-Core |
| 4 | [04-procurement.md](./04-procurement.md) | Procurement · suppliers, PO, GRN, payments → A/P | Inventory |
| 5 | [05-sales.md](./05-sales.md) | Sales · customers, orders, rentals, returns → A/R | Inventory, Procurement |
| 6 | [06-finance.md](./06-finance.md) | Finance-Reporting · 5 pillars, P&L, aging | Sales, Procurement |

> **Why Finance is split.** `sales_order_payments.finance_account_id` and
> `procurement_supplier_payments.finance_account_id` are FKs into `finance_accounts`,
> so the v1 order (Finance last) was circular. See [ADR-007](../review/02-decisions.md).

---

## Read these first

| Document | What it is |
|----------|------------|
| [`../review/01-spec-review.md`](../review/01-spec-review.md) | 43 defects found in the v1 spec, 12 of them blocking |
| [`../review/02-decisions.md`](../review/02-decisions.md) | 12 ADRs resolving them — including the ones marked 🔶 for you to confirm |
| [`../database/all`](../database/all) | The corrected schema, with every fix annotated |
| [`../flows/application-flows.md`](../flows/application-flows.md) | Corrected end-to-end flows |
| [`../wireframes/`](../wireframes/) | Excalidraw screens for every module |

---

## Product summary

**BOMS** — Bridal Omnichannel Management System for shops that **rent** and **sell**
bridal clothing.

- Mobile-first, owner-friendly
- Tenant-bound users, multi-role RBAC, no invite flow
- UI locale from tenant settings: English (LTR) · Dari (RTL) · Pashto (RTL)
- Create/edit forms in drawers that follow the text direction
- Auditable stock ledger with weighted average cost and DB-enforced booking guards
- Sale, rental and **mixed** orders
- Lightweight procurement with correct landed cost
- Five finance pillars → a daily profit answer the owner can trust

---

## The four ideas the whole system rests on

1. **Owned = on hand + on rent.** A gown at a wedding is still an asset, and stock
   worth must say so.
2. **Deposits are a liability.** Cash includes money that is not the shop's, so the
   dashboard shows "your cash" separately.
3. **A rented dress still costs something.** Its purchase price is amortised per use,
   so rental margin is real rather than imaginary.
4. **Nothing posted is ever edited.** Correction is a reversing document, always.

---

## Stack

**Deferred** — deliberately. The specs are implementation-agnostic; the only hard
requirements are a relational database with:

- range types and `EXCLUDE` constraints (double-booking guard, ADR-010)
- transactional atomicity across ledger + balance writes
- `jsonb` or equivalent for `custom_fields` / audit snapshots

PostgreSQL satisfies all three.
