# Feature Map — Sales Module

**Build order:** 5 (after Procurement)
**Depends on:** Platform · Finance-Core · Inventory · Procurement
**Schema:** `specs/database/sales`
**Wireframes:** `specs/wireframes/{desktop,mobile}/04-Sales.excalidraw`
**Decisions:** ADR-003 (deposits) · ADR-002 (rental cost) · ADR-008 (mixed orders) · ADR-010 (double-booking)

---

## Goal

Let a cashier serve a bride in under a minute, and let the owner see exactly what the day earned.

Three things the v1 spec got wrong that this map fixes:

- **Deposits were booked as income** — they are a liability until the dress comes back.
- **Rentals had no cost** — a rented gown now carries a per-use share of its purchase price.
- **A sale and a rental could not share one order** — but "rent the gown, buy the veil" is the normal counter case.

---

## Order model

```
sales_order_items.line_type  ('sale' | 'rental')   ← AUTHORITATIVE
sales_orders.order_kind      ('sale' | 'rental' | 'mixed')   ← DERIVED on save, display only
```

- One order may contain both kinds. The header badge is computed, never used for logic.
- `customer_id` is **nullable** — a walk-in buying a veil needs no customer record.
- **Any rental line requires a named customer.** You must know who has the dress.

---

## Personas

| Role | Needs |
|------|-------|
| Cashier | Find customer by phone, add items, take money, finish |
| Manager | Today's pickups and returns, overdue chasing, damage decisions |
| Owner | Revenue split, margin, which dresses earn, who owes what |

---

## Feature map

### S1 · Customers
| | Feature | Notes |
|---|---|---|
| S1.1 | Create customer: name + phone required | everything else optional |
| S1.2 | Search by phone first, then name | phone is how shop staff think |
| S1.3 | Wedding date | drives reminders and seasonality |
| S1.4 | Walk-in mode | no record created; `walk_in_name` on the order |
| S1.5 | Customer detail: profile + order history | sales and rentals in one timeline |
| S1.6 | Customer ledger | balances owed, deposits held, lifetime value |
| S1.7 | Duplicate-phone warning on create | |
| S1.8 | Quick-create from checkout | drawer, does not lose the cart |

### S2 · Sale orders
| | Feature | Notes |
|---|---|---|
| S2.1 | Add items by search, SKU or barcode | blocks items with no availability |
| S2.2 | Line discount + order discount (amount or %) | |
| S2.3 | Totals panel: subtotal, discount, other charges, total | |
| S2.4 | Full or partial payment, split across methods | |
| S2.5 | Complete → `stock_out` at WAC + `sale_cogs` entry | |
| S2.6 | Balance → `finance_receivables` | |
| S2.7 | Print / share receipt | |
| S2.8 | Status: draft → completed → void | |

### S3 · Rental orders
| | Feature | Notes |
|---|---|---|
| S3.1 | Event date + rental window pickers | |
| S3.2 | Live availability check against reservations | including the cleaning buffer |
| S3.3 | **Conflict UI** when dates clash | shows the clashing booking + alternative dresses |
| S3.4 | Per-line deposit, defaulted from item or tenant setting | |
| S3.5 | Confirm → creates `inventory_reservations` | **not** a stock movement |
| S3.6 | Mark out → `rent_out` | dress leaves; owned qty unchanged |
| S3.7 | Mark returned → `rent_return` + condition | good / needs cleaning / damaged / lost |
| S3.8 | Late fee computed on return | `late_days × Σ line late fee`, waivable with a reason |
| S3.9 | Deposit settlement panel | apply / forfeit / refund, in one screen |
| S3.10 | Complete → `rental_amortisation` COGS entry | ADR-002 |
| S3.11 | Cleaning buffer blocks the dress after return | `rental_buffer_days` |
| S3.12 | Status timeline on the order | draft → confirmed → out → returned → completed |

### S4 · Mixed orders
| | Feature |
|---|---|
| S4.1 | Sale and rental lines in one order, one payment, one receipt |
| S4.2 | Header badge derived (`sale` / `rental` / `mixed`) |
| S4.3 | Rental lines enforce a customer; sale-only orders do not |
| S4.4 | Totals separate rental revenue from deposit (liability) |

### S5 · Payments
| | Feature | Notes |
|---|---|---|
| S5.1 | Types: deposit · installment · full · refund · late_fee | |
| S5.2 | **Deposit → `finance_customer_deposits`, never Income** | ADR-003 |
| S5.3 | Choose account + method | |
| S5.4 | Every payment creates exactly one `finance_transactions` row | linked by `finance_transaction_id` |
| S5.5 | Order caches recompute: paid, balance, payment status | truth stays in `finance_receivables` |
| S5.6 | Partial refunds | `partially_refunded` status |
| S5.7 | Void by reversal | |

### S6 · Sale returns (sold goods)
| | Feature | Notes |
|---|---|---|
| S6.1 | Select order lines + quantity | |
| S6.2 | Reason + optional restock | |
| S6.3 | Refund out of a chosen account | |
| S6.4 | Restock → `stock_in` at the original cost | |
| S6.5 | Reverses the original `sale_cogs` entry | |
| S6.6 | Condition per line: good / damaged / unusable | damaged does not restock |

### S7 · Rental claims (damage · loss · late · cleaning)
| | Feature | Notes |
|---|---|---|
| S7.1 | Assess a charge against the customer | |
| S7.2 | Apply the deposit first, remainder → A/R | |
| S7.3 | `loss` → linked `inventory_disposals` write-off | the dress is gone |
| S7.4 | `damage` → item `lifecycle_status = repairing` | blocks booking |
| S7.5 | Forfeited deposit → Income | appears in P&L as "forfeited deposits" |
| S7.6 | Waive a claim with a reason | |

### S8 · Hub & list UX
| | Feature |
|---|---|
| S8.1 | One **New ticket** CTA — the counter, not two wizards | Phone search · register in a drawer · Rent/Sell switch per line · price input defaults to catalogue |
| S8.2 | KPIs: today revenue · open orders · due returns · overdue · deposits held · unpaid A/R |
| S8.3 | Today's schedule — pickups and returns by hour |
| S8.4 | Tabs: All / Sale / Rental / Mixed, filtered by status |
| S8.5 | Order detail shows only contextual actions |
| S8.6 | Empty / loading / error states everywhere |
| S8.7 | Cashier completes a sale in ≤ 5 taps after the customer is chosen |

### S9 · Reports
| | Report | Answers |
|---|---|---|
| S9.1 | **Sales summary** | Revenue by period, split sale vs rental, with margin. Daily bar chart. |
| S9.2 | **Sales by item / category** | What sells, what rents, what sits |
| S9.3 | **Rental performance** | Per dress: times rented, revenue, utilisation %, avg days, late returns, damage incidents |
| S9.4 | **Customer ledger & top customers** | Who spends, who owes, lifetime value |
| S9.5 | **Staff / cashier sales** | Who sold what, for commission or review |
| S9.6 | **Deposits & refunds** | Taken, applied, forfeited, refunded, still held |
| S9.7 | **Returns & claims** | Return rate, damage rate, cost of damage |
| S9.8 | **Due & overdue returns** | Operational chase list |
| S9.9 | **Discount analysis** | How much margin is given away, by whom |

All reports: period · branch · customer · category filters, CSV export, print view.

---

## Screens (implementation order)

| # | Screen |
|---|--------|
| 1 | Sales dashboard |
| 2 | Counter — phone search, Rent/Sell per line, editable price |
| 3 | Register customer drawer (over the counter) |
| 4 | Printed slip with order barcode + QR |
| 5 | Orders list |
| 6 | Order detail |
| 7 | Scan return drawer (collect / refund / restock) |
| 8 | Sale return (scan slip) |
| 9 | Customers list + new-customer drawer + profile |
| 10 | Sales summary · Rental performance · Deposits & refunds |

---

## Business rules

- An item with `available_qty = 0` cannot be added, unless `allow_negative_stock` is on (then the line is flagged).
- Sellable = has a sale price; rentable = has a rental price. There is no `purpose` field. Each counter line has a Rent | Sell switch; the default price is the catalogue price and staff may type a higher amount.
- Rental confirm creates a reservation; the DB exclusion constraint rejects overlaps (ADR-010).
- Cancelling a confirmed rental releases its reservation.
- Deposits never enter Income. They move Cash and the deposit liability only.
- Late fee = `max(0, actual_return − rental_end) × Σ line late fee per day`, waivable with a reason.
- Returned damaged → `repairing`; returned lost → claim + disposal.
- COGS is recognised at completion: `sale_cogs` for sale lines, `rental_amortisation` for rental lines.
- A/R truth is `finance_receivables`; the order's balance column is a display cache.
- Posted orders are corrected by **void**, which reverses stock, payments, A/R and COGS.
- Every posting is idempotent on `idempotency_key`.

---

## Integrations

| Sales event | Inventory | Finance |
|-------------|-----------|---------|
| Sale line completed | `stock_out` at WAC | cash IN · A/R if balance · `sale_cogs` |
| Rental confirmed | reservation row | deposit IN → **liability** |
| Rental marked out | `rent_out` | — |
| Rental marked returned | `rent_return` + buffer | late fee IN · deposit settled |
| Rental completed | — | `rental_amortisation` COGS |
| Rental claim posted | disposal if `loss` | deposit forfeited → income · balance → A/R |
| Sale return posted | `stock_in` if restock | refund OUT · reverse `sale_cogs` |
| Order voided | reversing stock rows | reversing finance rows |

---

## Out of scope

- Quotation → order → invoice pipeline
- Commissions, loyalty points, gift cards, CRM campaigns
- Delivery logistics and routing
- Alterations as a tracked production job (record as an expense)
- Online storefront ordering (website module, deferred)

---

## Acceptance checks

- [ ] Selling one dress: stock 1 → 0, cash up, Income up, `sale_cogs` posted at WAC, P&L net profit correct.
- [ ] Taking a 20,000 rental deposit increases Cash by 20,000 and **Income by zero**; the dashboard shows deposits held 20,000.
- [ ] Applying 8,000 of that deposit and forfeiting 12,000 for damage moves 12,000 into Income as "forfeited deposits".
- [ ] Booking the same gown for overlapping dates is rejected by the database, with alternatives offered in the UI.
- [ ] A dress returned on the 10th with a 2-day buffer cannot be booked for the 11th.
- [ ] Returning 2 days late at 500/day produces a 1,000 late fee, and waiving it records the reason.
- [ ] A mixed order rents a gown and sells a veil, takes one payment, and produces one receipt with the deposit shown separately.
- [ ] A walk-in sale completes with no customer record.
- [ ] A completed rental posts `rental_amortisation` of `acquisition_cost ÷ expected_rental_uses`.
- [ ] A lost dress creates a claim, consumes the deposit, writes off the stock, and puts the remainder in A/R.
- [ ] Voiding a completed sale restores stock, reverses cash, reopens nothing that was not open, and reverses COGS.
- [ ] A cashier completes the happy-path sale in ≤ 5 taps after the customer is selected.
