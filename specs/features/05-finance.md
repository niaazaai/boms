# Feature Spec — Finance Module

**Status:** ready after Sales + Procurement postings exist  
**Depends on:** Platform + Sales payments + Procurement payments/expenses  
**Schema:** `specs/database/finance`  
**Wireframes:** `specs/wireframes/06-finance.md`  
**Flows:** `specs/flows/application-flows.md` § end-of-day profit

---

## Goal

Give the shop owner a clear daily answer: **Am I making or losing money?** via five simple pillars — not a full accounting suite.

---

## Five pillars

| # | Pillar | Meaning | Primary tables |
|---|--------|---------|----------------|
| 1 | Cash & Banks | Money available now | `finance_accounts`, movements |
| 2 | Income | Money earned (sales, rentals, other) | sales payments + `finance_other_income` |
| 3 | Expenses | Money spent to run shop | `finance_expenses` |
| 4 | Accounts Payable | What we owe suppliers | `finance_payables` |
| 5 | Accounts Receivable | What customers owe us | `finance_receivables` |

**Net profit (daily/period):**  
`Income − Expenses − COGS`  
COGS from sold item `unit_cost_snapshot` (and optional rental cost policy later).

---

## Personas

| Role | Needs |
|------|--------|
| Owner | Dashboard, P&L, record expense, see who owes whom |
| Manager | Record expenses, collect A/R, pay A/P |
| Cashier | Usually no finance access (or expenses only if permitted) |

---

## Features

### F1 — Finance accounts (Cash & Banks)
- [ ] CRUD accounts: cash, bank, wallet
- [ ] Opening balance + live current balance
- [ ] Default account per branch optional
- [ ] Transfer between accounts (not income/expense)

### F2 — Categories
- [ ] Income categories & expense categories
- [ ] Seed defaults for bridal shop (rent, salary, repair, marketing, utilities, transport…)

### F3 — Expenses
- [ ] Add expense in < 30 seconds (category, amount, pay-from, note, photo)
- [ ] Post → `finance_transactions` direction out + reduce account balance

### F4 — Other income
- [ ] Manual income not from sales (rare)
- [ ] Post → transaction in

### F5 — Payables & Receivables
- [ ] Auto-create/update from Procurement & Sales
- [ ] Lists with Pay / Collect actions
- [ ] Status open / partial / paid

### F6 — Ledger
- [ ] Unified `finance_transactions` list with filters (date, account, direction, reference)
- [ ] Void with reversing logic (no silent delete)

### F7 — Dashboard & P&L
- [ ] 5 pillar cards on Finance home + mirrored on app Home
- [ ] Period filters: today, week, month, custom
- [ ] Branch filter
- [ ] P&L report screen + share/export later
- [ ] Optional `finance_daily_summaries` snapshot job

---

## Screens (implementation order)

1. Finance dashboard (5 pillars)  
2. Add expense (highest manual frequency)  
3. Cash & banks + transfer  
4. Income / expense lists  
5. A/P list + pay  
6. A/R list + collect  
7. P&L report  

---

## Business rules

- Posted sales/procurement payments must create finance transactions (single source of truth).
- Dashboard uses **posted** rows only.
- Multi-currency: store original + `amount_base` in tenant default currency.
- Voiding a transaction reverses account balance and linked payable/receivable effects.
- COGS counted when sale completes (not when draft).

---

## Integrations (inbound)

| Source | Finance effect |
|--------|----------------|
| Sales payment | IN + reduce AR |
| Sales refund | OUT |
| Supplier payment | OUT + reduce AP |
| PO receive | open AP |
| Sale with balance | open AR |
| Manual expense/income | OUT / IN |

---

## Out of scope

- Full double-entry general ledger / chart of accounts hierarchy  
- Bank statement import / auto-reconcile (v2)  
- Shareholder splits, cost centers, tax engine  
- Payroll module  

---

## Acceptance checks

- After a sale and an expense, Today Net Profit matches manual calc.
- A/R pillar equals sum of open order balances.
- A/P pillar equals unpaid PO balances.
- Owner understands dashboard without training beyond one walkthrough.
