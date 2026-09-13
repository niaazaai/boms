# Feature Map — Finance-Core (build step 2)

**Build order:** 2 — **before** Inventory, Procurement and Sales
**Depends on:** Platform
**Schema:** `specs/database/finance` (sections `finance_accounts` … `finance_account_transfers`)
**Full spec:** [`06-finance.md`](./06-finance.md) § *Feature map — Finance-Core*
**Decision:** [ADR-007](../review/02-decisions.md) — why the finance module is split in two

---

## Why this exists as its own step

The v1 build order was Platform → Inventory → Sales → Procurement → Finance. That order is **circular**:

```
sales_order_payments.finance_account_id          → FK finance_accounts
procurement_supplier_payments.finance_account_id → FK finance_accounts
```

Sales and Procurement cannot be built before `finance_accounts` exists. So the Finance module is split:

| Phase | Step | Contents |
|-------|------|----------|
| **Finance-Core** | **2** | the money primitives every other module posts into |
| Finance-Reporting | 6 | the pillars, P&L and aging views that read them back |

---

## Scope of this step

| Table | Purpose |
|-------|---------|
| `finance_accounts` | cash drawers, bank accounts, wallets — balance **derived**, cached column reconciled |
| `finance_categories` | income and expense categories, seeded for a bridal shop |
| `finance_transactions` | **the** unified money ledger — exactly one row per movement, `reverses_id` for voids |
| `finance_customer_deposits` | the deposit **liability** — deposits never touch Income (ADR-003) |
| `finance_cogs_entries` | `sale_cogs` and `rental_amortisation` — cost recognition with no cash movement (ADR-002) |
| `finance_account_transfers` | internal moves; posts two transactions with no category |

---

## Deliverables

- [ ] Accounts CRUD + derived balance + "recompute from ledger"
- [ ] Seeded income and expense categories
- [ ] `finance_transactions` write API with `idempotency_key`, `business_date`, `amount_base`
- [ ] Void-by-reversal mechanism (`reverses_id`), reusable by every module
- [ ] Customer deposit take / apply / forfeit / refund operations
- [ ] COGS entry writer for both kinds
- [ ] Account transfer
- [ ] Account statement screen with running balance

---

## Acceptance checks

- [ ] Posting a transaction updates the cached balance inside the same DB transaction.
- [ ] Recomputing an account from the ledger reproduces the cached balance.
- [ ] Voiding a transaction inserts a reversing row and flips the original to `void`; neither is deleted.
- [ ] A deposit movement raises cash and the deposit liability, and leaves Income at zero.
- [ ] A COGS entry carries no cash effect and does not appear on any account statement.
- [ ] Replaying a post with the same `idempotency_key` returns the original row rather than creating a second.

Everything else about Finance — expenses, income, payables, receivables, pillars, P&L — is step 6 in [`06-finance.md`](./06-finance.md).
