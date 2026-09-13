# Feature Map — Finance Module

**Build order:** Finance-**Core** at step 2 · Finance-**Reporting** at step 6
**Depends on:** Platform (core) · Sales + Procurement postings (reporting)
**Schema:** `specs/database/finance`
**Wireframes:** `specs/wireframes/{desktop,mobile}/05-Finance.excalidraw`
**Decisions:** ADR-003 (deposits) · ADR-002 (rental cost) · ADR-005 (void) · ADR-007 (split build)

---

## Goal

Answer one question, correctly, every evening: **am I making money or losing money?**

Not a general ledger. Five pillars an owner can read without an accountant — plus the one liability that makes the cash number honest.

---

## Why this module is split

`sales_order_payments.finance_account_id` and `procurement_supplier_payments.finance_account_id` are foreign keys into `finance_accounts`. Sales cannot be built before Finance exists, so:

| Phase | Step | Contents |
|-------|------|----------|
| **Finance-Core** | 2 | accounts, categories, `finance_transactions`, customer deposits, COGS ledger, account transfers |
| **Finance-Reporting** | 6 | expenses, other income, payables, receivables, daily summaries, pillars, P&L |

---

## The five pillars (+ the liability)

| # | Pillar | Meaning | Source |
|---|--------|---------|--------|
| 1 | **Cash & banks** | Money available now | `finance_accounts` + posted `finance_transactions` |
| 2 | **Income** | Money earned | `finance_transactions` where category kind = income |
| 3 | **Expenses** | Money spent running the shop | `finance_transactions` where category kind = expense |
| 4 | **Accounts payable** | What we owe suppliers | `finance_payables` |
| 5 | **Accounts receivable** | What customers owe us | `finance_receivables` |
| — | **Deposits held** | Customer security money — *not yours* | `finance_customer_deposits` |

**Cash is presented in three parts, always:**

```
Cash & banks              412,000 AFN
  of which deposits held   68,000 AFN   ← a liability
  your cash               344,000 AFN
```

---

## Profit & loss

```
  Revenue              sale revenue + rental revenue + late fees
                       + forfeited deposits + other income
− COGS                 sale COGS (WAC of dresses sold)
                     + rental amortisation (acquisition ÷ expected uses)
= Gross profit
− Operating expenses   rent, salaries, utilities, cleaning, marketing, transport
= Net profit
```

**Rental amortisation is the line the v1 spec had no home for.** A rented dress is not consumed, so charging its full cost on first rental is wrong — and charging nothing makes rental margin look like 100% forever. See ADR-002.

---

## Personas

| Role | Needs |
|------|-------|
| Owner | Dashboard, P&L, who owes whom, is the cash real |
| Manager | Record expenses, collect A/R, pay A/P |
| Cashier | Usually no finance access; expenses only if granted |

---

## Feature map — Finance-Core (step 2)

### F1 · Accounts (Pillar 1)
| | Feature | Notes |
|---|---|---|
| F1.1 | CRUD cash / bank / wallet accounts | |
| F1.2 | Opening balance | |
| F1.3 | **Balance is derived** | `opening + Σ posted transactions` |
| F1.4 | `cached_balance` refreshed inside the posting transaction | a cache, never the truth |
| F1.5 | Nightly reconciliation job | mismatch → `platform_notifications` |
| F1.6 | "Recompute from ledger" action | |
| F1.7 | Default account per branch | |
| F1.8 | Account statement with running balance | |

### F2 · Categories
| | Feature |
|---|---|
| F2.1 | Income and expense categories, two-level |
| F2.2 | Seeded for bridal: rent, salaries, utilities, dry cleaning, repair, marketing, transport, bank fees |
| F2.3 | Seeded income: dress sale, rental fee, late fee, forfeited deposit, other |

### F3 · Unified transaction ledger
| | Feature | Notes |
|---|---|---|
| F3.1 | **Every money movement has exactly one row** | including sales and supplier payments |
| F3.2 | `finance_transaction_id` links back from every source document | corrected flaw E2 |
| F3.3 | Original amount + exchange rate + `amount_base` | multi-currency safe |
| F3.4 | `business_date` on every row | ADR-011 |
| F3.5 | Filters: date, account, direction, category, reference type | |
| F3.6 | **Void = a reversing row** | `reverses_id`; nothing edited, nothing deleted |
| F3.7 | Source-document deep link on every row | |

### F4 · Customer deposits (the liability)
| | Feature | Notes |
|---|---|---|
| F4.1 | Taken / applied / forfeited / refunded / still held | |
| F4.2 | Never enters Income | `is_deposit_movement = true` |
| F4.3 | Forfeited portion becomes Income at settlement | |
| F4.4 | Deposit register reconciles to the dashboard tile | |
| F4.5 | Alert on deposits unsettled beyond N days | |

### F5 · COGS ledger
| | Feature | Notes |
|---|---|---|
| F5.1 | `sale_cogs` — WAC of a dress sold | written at sale completion |
| F5.2 | `rental_amortisation` — cost per use | written at rental completion |
| F5.3 | Accumulates in `inventory_items.amortised_cost_to_date`, capped at acquisition cost | |
| F5.4 | Reversed when a sale or rental is voided | |
| F5.5 | Queryable as a period total alongside income and expenses | corrected flaw E6 |

### F6 · Account transfers
| | Feature |
|---|---|
| F6.1 | Move money between own accounts |
| F6.2 | Cross-currency with a snapshotted rate |
| F6.3 | Posts two transactions with **no category** — never income or expense |

---

## Feature map — Finance-Reporting (step 6)

### F7 · Expenses (Pillar 3)
| | Feature | Notes |
|---|---|---|
| F7.1 | Add expense in under 30 seconds | the most-used manual screen |
| F7.2 | Recent-category quick-pick | |
| F7.3 | Multi-photo receipt attachments | `platform_attachments` |
| F7.4 | Post → one `finance_transactions` OUT | |
| F7.5 | Expenses list with category totals | |
| F7.6 | Recurring expense templates | rent, salaries |

### F8 · Other income (Pillar 2)
| | Feature |
|---|---|
| F8.1 | Manual income not from sales |
| F8.2 | Post → one transaction IN |

### F9 · Payables (Pillar 4)
| | Feature |
|---|---|
| F9.1 | Opened by procurement receipts, reduced by payments and supplier returns |
| F9.2 | Aging buckets: current / 1–30 / 31–60 / 60+ |
| F9.3 | Pay action with allocation across several payables |
| F9.4 | Due-this-week alert |
| F9.5 | Supplier statement |

### F10 · Receivables (Pillar 5)
| | Feature |
|---|---|
| F10.1 | Opened when an order completes with a balance, or by a rental claim |
| F10.2 | Aging buckets, overdue highlighting |
| F10.3 | Collect action with oldest-first allocation |
| F10.4 | Customer statement |
| F10.5 | Overdue alert |

### F11 · Dashboard & P&L
| | Feature |
|---|---|
| F11.1 | Six tiles: five pillars + deposits held |
| F11.2 | Net-profit hero with the full calculation shown in words |
| F11.3 | Cash split into total / deposits held / your cash |
| F11.4 | Period: today · week · month · custom; branch filter |
| F11.5 | Income vs expense chart |
| F11.6 | Alerts: overdue A/R, A/P due, unsettled deposits, reconcile mismatch |
| F11.7 | Full P&L statement with both COGS lines and margin percentages |
| F11.8 | Period comparison vs previous period |
| F11.9 | Pillar tiles mirrored on the app Home screen |
| F11.10 | `finance_daily_summaries` snapshot with an `is_stale` flag |
| F11.11 | Export / print |

---

## Screens (implementation order)

| # | Screen | Phase |
|---|--------|-------|
| 1 | Cash & banks + account CRUD | Core |
| 2 | Account statement | Core |
| 3 | Account transfer | Core |
| 4 | Unified ledger | Core |
| 5 | Void modal | Core |
| 6 | Deposits held register | Core |
| 7 | Add expense | Reporting |
| 8 | Expenses / income lists | Reporting |
| 9 | Accounts payable + aging | Reporting |
| 10 | Accounts receivable + aging | Reporting |
| 11 | Collect / pay drawer | Reporting |
| 12 | Dashboard — five pillars | Reporting |
| 13 | Period comparison | Reporting |
| 14 | Profit & loss | Reporting |

---

## Business rules

- Posted sales and procurement payments **must** create a `finance_transactions` row and link to it.
- The dashboard counts `status='posted'` rows only.
- Deposits change Cash and the deposit liability — never Income.
- Account balances are derived; the cached column is reconciled nightly.
- Void inserts a mirrored reversing row and flips the original to `void`. Nothing is deleted.
- Every money-bearing row stores original amount, rate, and `amount_base`.
- All period filters use `business_date` (ADR-011), never `created_at`.
- COGS is recognised at completion, not at draft.
- `finance_daily_summaries` is a cache: any posting on a covered date sets `is_stale`.
- A/P and A/R pillars read only `finance_payables` / `finance_receivables`.

---

## Integrations (inbound)

| Source | Finance effect |
|--------|----------------|
| Sale payment | transaction IN · reduce A/R |
| Rental deposit taken | transaction IN · **deposit liability**, no income |
| Deposit applied / forfeited / refunded | liability down · income up (forfeit) or cash out (refund) |
| Late fee collected | transaction IN · income |
| Sale completed | `sale_cogs` entry |
| Rental completed | `rental_amortisation` entry |
| Sale refund | transaction OUT · reverse COGS |
| Rental claim | forfeited deposit → income · balance → A/R |
| PO receipt posted | open A/P |
| Supplier payment | transaction OUT · reduce A/P |
| Supplier return | reduce A/P or refund IN |
| Manual expense / income | OUT / IN |

---

## Out of scope

- Full double-entry general ledger and chart of accounts
- Bank statement import and auto-reconciliation (v2)
- Tax engine, VAT returns
- Payroll, shareholder splits, cost centres
- Budgeting and forecasting

---

## Acceptance checks

- [ ] After one sale and one expense, Today Net Profit matches a hand calculation.
- [ ] Taking a deposit raises Cash and leaves Income unchanged; the deposits-held tile rises by the same amount.
- [ ] Cash − deposits held = "your cash", and the deposits register totals to the tile exactly.
- [ ] A/P pillar equals the sum of open `finance_payables` balances and matches the supplier aging total.
- [ ] A/R pillar equals the sum of open `finance_receivables` balances.
- [ ] A month with 12 completed rentals shows a non-zero `rental_amortisation` line in the P&L.
- [ ] A dress whose `amortised_cost_to_date` has reached its acquisition cost contributes zero further COGS.
- [ ] Voiding a transaction creates a reversing row; both remain visible and the balance nets out.
- [ ] Deleting a `finance_transactions` row is impossible through the UI and the API.
- [ ] A USD supplier payment shows both USD and AFN, and editing today's rate does not change it.
- [ ] A sale posted at 00:30 with a 02:00 cutoff appears in the previous business day's profit.
- [ ] Recomputing an account from the ledger reproduces its cached balance, or raises a mismatch notification.
- [ ] The owner can read the dashboard and explain their day after one walkthrough.
