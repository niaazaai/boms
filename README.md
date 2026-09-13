# BOMS

**Bridal Omnichannel Management System**

Mobile-first system for bridal shops that **rent** and **sell** bridal clothing —
auditable inventory, easy sales and rentals, lightweight procurement, and a daily
profit answer the owner can trust.

```
procurement  →  inventory  →  sales  →  finance
```

---

## Start here

| Document | What it is |
|----------|------------|
| [`specs/review/01-spec-review.md`](./specs/review/01-spec-review.md) | **43 defects** found in the v1 spec — 12 blocking |
| [`specs/review/02-decisions.md`](./specs/review/02-decisions.md) | **12 ADRs** resolving them · 6 open questions marked 🔶 for you |
| [`specs/wireframes/00-Overview.excalidraw`](./specs/wireframes/00-Overview.excalidraw) | Navigation shell, module map, sitemap, corrections board |
| [`specs/features/README.md`](./specs/features/README.md) | Build order and module specs |

---

## Specs

| Area | Path |
|------|------|
| Database schema (v2, corrected) | [`specs/database/`](./specs/database/) — `all` is authoritative |
| Feature maps (build order) | [`specs/features/`](./specs/features/) |
| Wireframes (Excalidraw) | [`specs/wireframes/`](./specs/wireframes/) |
| Application flows | [`specs/flows/application-flows.md`](./specs/flows/application-flows.md) |
| Spec review & decisions | [`specs/review/`](./specs/review/) |
| Agent skills & docs | [`.agent/`](./.agent/) |

Regenerate wireframes:

```bash
python3 .agent/scripts/wireframes/build.py
```

---

## Build order

FK-safe. Finance-Core sits at step 2 because sales and procurement payments hold
foreign keys into `finance_accounts`.

| # | Module | Contents |
|---|--------|----------|
| 1 | **Platform** | tenants, auth, RBAC, branches, warehouses, master data, sequences, audit |
| 2 | **Finance-Core** | accounts, categories, unified transaction ledger, deposits, COGS |
| 3 | **Inventory** | catalogue, stock ledger, balances (WAC), reservations, movements |
| 4 | **Procurement** | suppliers, purchase orders, GRN with landed cost, payments → A/P |
| 5 | **Sales** | customers, sale + rental + mixed orders, returns, claims → A/R |
| 6 | **Finance-Reporting** | five pillars, P&L, A/P & A/R aging, deposits register |

---

## Finance pillars

1. Cash & banks
2. Income
3. Expenses
4. Accounts payable — what we owe
5. Accounts receivable — what customers owe us

Plus a sixth tile: **customer deposits held** — a liability sitting inside cash.

```
Cash & banks              412,000 AFN
  of which deposits held   68,000 AFN   ← not yours
  your cash               344,000 AFN
```

---

## The four ideas the system rests on

**1 · Owned = on hand + on rent.**
A gown at a wedding is still an asset. Valuation uses `owned`, not what is physically
on the rack — otherwise total stock worth collapses every busy weekend.

**2 · Deposits are a liability, not income.**
A refundable deposit is the customer's money. Booking it as revenue overstates the
one number the owner trusts most.

**3 · A rented dress still costs something.**
Its purchase price is amortised per use — `acquisition_cost ÷ expected_rental_uses` —
until the dress has paid for itself. Without this, rental margin looks like 100%
forever.

**4 · Nothing posted is ever edited.**
Correction is a reversing document, in every module. The original stays visible.

---

## Status

Specs are **ready for development**. Six business decisions are flagged 🔶 in
[`specs/review/02-decisions.md`](./specs/review/02-decisions.md) — they are implemented
with sensible defaults and can be changed on request.

Stack and infrastructure: **deferred**. The only hard requirement is a relational
database with range types and `EXCLUDE` constraints (for the double-booking guard),
transactional atomicity, and `jsonb`. PostgreSQL satisfies all three.
