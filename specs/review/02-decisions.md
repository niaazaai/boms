# BOMS — Design Decisions (ADR)

Resolutions for the blocking defects in [`01-spec-review.md`](./01-spec-review.md).
Each decision is implemented in `specs/database/` and drawn in `specs/wireframes/`.

**Anything marked 🔶 is a business call made on your behalf with a stated default — override it and I will rework the schema.**

---

## ADR-001 · Inventory costing = Weighted Average Cost 🔶

**Decides:** B4, D1
**Options:** FIFO cost layers · Weighted Average Cost (WAC) · Specific identification

**Decision: Weighted Average Cost**, maintained per `(inventory_item_id, warehouse_id)`.

```
on stock-in:
  new_avg_cost = (qty_on_hand × avg_cost + qty_in × landed_unit_cost)
               / (qty_on_hand + qty_in)

on stock-out:
  snapshot the current avg_cost onto the transaction row (unit_cost)
  qty changes; avg_cost does not
```

**Why:** most bridal stock is unique (qty 1), where WAC, FIFO and specific-ID are identical. For the multi-qty accessories where they differ, WAC needs no cost-layer table, survives back-dated entries, and is what a shop owner intuitively expects ("what did a veil cost me on average"). FIFO would add a cost-layer table and consumption logic for almost no accuracy gain at this scale.

**Consequences:**
- New table `inventory_stock_balances` (physical, not a view) holds `avg_cost`, updated inside the posting transaction.
- `inventory_items.purchase_amount` is demoted to display-only "last purchase price" and is never used for valuation.
- Valuation as-of a past date replays the ledger; the balance table is the fast path for "now".

---

## ADR-002 · Rental cost recognition = per-use amortisation 🔶

**Decides:** C2, E6 — **the most consequential decision in the system.**

A sold dress is straightforward: COGS = its average cost, recognised at sale. A **rented** dress is not consumed — so what does a rental cost?

**Options considered**

| | Approach | Effect |
|---|---|---|
| A | No cost on rentals | Rental margin looks like ~100% forever. Owner never sees the asset wearing out. **Wrong.** |
| B | Full cost on first rental | The first rental of a 40,000 AFN gown shows a huge loss, then infinite profit. **Wrong.** |
| C | **Per-use amortisation** | Each rental carries `purchase_cost / expected_rental_uses`. |
| D | Straight-line time depreciation | Cost accrues monthly whether or not the dress is rented. |

**Decision: (C) per-use amortisation**, with the divisor as a setting.

```
rental_cogs_per_use = item_purchase_cost / expected_rental_uses
```
- `tenant_settings.default_expected_rental_uses` — **default 20**
- overridable per item (`inventory_items.expected_rental_uses`)
- accumulates in `inventory_items.amortised_cost_to_date`, capped at purchase cost — once fully amortised, further rentals carry zero COGS and are pure margin (which is correct: the dress has paid for itself)
- recognised on **rental completion**, written to `finance_cogs_entries` with `kind='rental_amortisation'`

**Why (C) over (D):** a bridal dress wears out by being worn, not by sitting on a rack. Per-use matches cost to the revenue that caused it, and it makes the *"has this dress paid for itself yet?"* question directly answerable — which is the inventory decision an owner actually makes.

**Consequences:**
- Enables the Rental Utilisation / Asset ROI report (B12).
- A dress that never rents accrues no cost — deliberate. Idle stock shows up in the ROI report as "0 uses, 0 payback", not as a P&L drip.
- `expected_rental_uses` is an estimate; changing it re-bases future amortisation only, never restates history.

---

## ADR-003 · Customer deposits are a liability, not income

**Decides:** C1, E4

A rental deposit is the customer's money held as security. Booking it as income overstates daily profit — the headline number the owner trusts.

**Decision:** deposits live in `finance_customer_deposits` and never touch Income.

| Event | Cash | Deposits held (liability) | Income |
|-------|------|---------------------------|--------|
| Take deposit | + | + | — |
| Apply to final balance | — | − | + (as rental revenue) |
| Forfeit (damage / late) | — | − | + (as forfeited-deposit income) |
| Refund | − | − | — |

**Dashboard consequence** — Cash is presented in three parts:
```
Cash & banks            412,000 AFN
  of which deposits held  68,000 AFN   ← not yours
  your cash              344,000 AFN
```

---

## ADR-004 · Reservations are not stock movements

**Decides:** B2, B3

The old ledger made `reserve` a negative quantity while also defining `on_hand = SUM(quantity)` — so reserving reduced stock, and `available = on_hand − reserved` subtracted the same reservation twice. `rent_out` had the same flaw at the valuation level: a dress out on rent vanished from "total stock worth".

**Decision:** four quantities, one ledger, one reservations table.

```
on_hand_qty   = Σ ledger qty for types (stock_in, stock_out, adjustment,
                                        transfer_in, transfer_out, dispose,
                                        rent_out, rent_return)
on_rent_qty   = Σ rent_out(−) reversed − Σ rent_return          → currently with customers
owned_qty     = on_hand_qty + on_rent_qty                        → what the shop owns
reserved_qty  = Σ inventory_reservations WHERE status='active'   → NOT from the ledger
available_qty = on_hand_qty − reserved_qty                       → what can be sold/booked today
```

- **Valuation uses `owned_qty`** — a gown at a wedding is still an asset.
- **Availability uses `available_qty`.**
- `reserve` and `release` are **removed** from `inventory_stock_transactions.type`.

---

## ADR-005 · Every posted document is immutable; correction is by reversal

**Decides:** B9, C11, D6, E5

**Decision:** `draft → posted → void`. A posted document is never edited and never deleted.
- `void` writes a **reversing document** (mirrored quantities and amounts) linked by `reverses_id`.
- The original keeps `status='void'`, `voided_by`, `voided_at`, `void_reason`.
- Applies uniformly to stock entries, adjustments, disposals, transfers, receipts, orders, payments, and finance transactions.

This is what makes the ledger auditable and makes "why did stock change?" answerable.

---

## ADR-006 · Multi-tenancy: scoped uniqueness + a sequence table

**Decides:** A1, A2

- Every document number and SKU: `unique (tenant_id, <number>)` — never globally unique.
- Numbers come from `platform_sequences` with an atomic increment, not `MAX()+1`.
- Login identifiers (`users.email`, `users.phone`) are the **exception** — globally unique, because login has no tenant context (A8).

```
platform_sequences(tenant_id, doc_type, period_key, last_value)
  → 'SO', '26'  → SO26-000019
```

---

## ADR-007 · Build order: Finance-Core moves to step 2

**Decides:** A4

The old order (Platform → Inventory → Sales → Procurement → Finance) is circular: `sales_order_payments.finance_account_id` requires `finance_accounts` to exist.

**New order:**

| # | Module | Contains |
|---|--------|----------|
| 1 | Platform | tenant, auth, RBAC, branches, warehouses, master data, sequences |
| 2 | **Finance-Core** | accounts, categories, `finance_transactions`, deposits, COGS ledger |
| 3 | Inventory | catalogue, ledger, balances, WAC, reservations, movements |
| 4 | Procurement | suppliers, PO, GRN, landed cost, supplier payments, A/P |
| 5 | Sales | customers, orders, payments, rentals, returns, claims, A/R |
| 6 | Finance-Reporting | 5 pillars, P&L, A/P & A/R aging, deposits register, daily summaries |

Procurement before Sales because receiving is what puts costed stock in the system for Sales to consume.

---

## ADR-008 · Mixed sale + rental orders are first-class

**Decides:** C3, C4

The real counter case is *rent the gown, buy the veil, one payment*. Forcing two orders is worse UX and splits the customer's balance.

**Decision:**
- `sales_order_items.line_type` (`sale` | `rental`) is **authoritative**.
- `sales_orders.order_kind` (`sale` | `rental` | `mixed`) is **derived** on save — used for filtering and badges only, never for logic.
- `customer_id` is **nullable**: sale-only orders may be a walk-in. Any order containing a rental line **requires** a customer (you must know who has the dress).

---

## ADR-009 · Landed cost allocation is pro-rata by line value

**Decides:** D1

Header `other_cost` (shipping, customs) is allocated to receipt lines proportionally to line value:

```
allocated_i     = header_other_cost × (line_value_i / Σ line_value)
landed_unit_cost_i = unit_cost_i + (allocated_i + line_other_cost_i) / qty_received_i
```

`landed_unit_cost` is stored on `procurement_receipt_items` and is the **only** cost that posts to `inventory_stock_transactions.unit_cost` and feeds the WAC recompute. Auditable, deterministic, visible on the GRN screen.

---

## ADR-010 · Double-booking is prevented in the database

**Decides:** B6, B7

Application-level conflict checks race. For a bridal shop, a double-booked gown on a wedding day is the worst possible failure.

```sql
ALTER TABLE inventory_reservations ADD CONSTRAINT no_overlap
EXCLUDE USING gist (
  inventory_item_id WITH =,
  daterange(reserved_from, reserved_until_with_buffer, '[]') WITH &&
) WHERE (status = 'active');
```

`reserved_until_with_buffer = reserved_to + tenant_settings.rental_buffer_days` (default **2**) — the cleaning/turnaround window, stored as a generated column so the constraint covers it.

---

## ADR-011 · The business day is explicit

**Decides:** A11

"End-of-day profit" needs an unambiguous day. Every posting stores:

```
business_date = (posted_at AT TIME ZONE tenants.timezone)::date
                adjusted by tenant_settings.day_cutoff_time (default 00:00)
```

All reports filter on `business_date`, never on raw `created_at`. A sale rung up at 00:30 with a 02:00 cutoff belongs to the previous business day.

---

## ADR-012 · Postings are idempotent

**Decides:** A5

Every posting endpoint accepts a client-generated `idempotency_key uuid`. Replaying the same key returns the original result instead of posting twice. Stored on the document; `unique (tenant_id, idempotency_key)`.

Non-negotiable for a mobile app on unreliable connectivity where the buttons move stock and money.

---

## Pillar formulas (exact — E10)

All in tenant default currency via `amount_base`, filtered by `business_date` and `status='posted'`.

```sql
-- 1 · Cash & banks
Σ finance_accounts.opening_balance
  + Σ finance_transactions.amount_base × (direction='in' ? +1 : −1)
of which deposits held:
  Σ finance_customer_deposits.held_amount WHERE status='held'

-- 2 · Income
Σ finance_transactions.amount_base
  WHERE direction='in' AND category.kind='income'
  -- excludes deposit receipts (they are a liability, ADR-003)

-- 3 · Expenses
Σ finance_transactions.amount_base
  WHERE direction='out' AND category.kind='expense'

-- 4 · Accounts payable
Σ finance_payables.balance_amount WHERE status IN ('open','partial')

-- 5 · Accounts receivable
Σ finance_receivables.balance_amount WHERE status IN ('open','partial')

-- COGS
Σ finance_cogs_entries.amount_base          -- sale_cogs + rental_amortisation

-- Profit
gross_profit = Income − COGS
net_profit   = Gross profit − Expenses
```

---

## ADR-013 · An item's channel and its rental length are derived, never stored

**Context.** `inventory_items` carried `purpose enum('sale','rental','both')` and
`rental_period_days int default 3`. Both restate something the record already
knows, and neither is kept in step with it. (Defects B14, B15.)

**Decision.**

```
sellable       = sales_unit_price > 0
rentable       = rental_price     > 0
rental length  = sales_orders.rental_to − sales_orders.rental_from
```

`purpose` and `rental_period_days` are removed from the schema, from every form
and from every filter.

**Consequences.**

- Turning a dress into a sale-only item is a price edit, not a second edit to a
  status field that can disagree with the price.
- A rental is **open**: two days or two weeks, the booking decides. The item
  carries `rental_price` (one rental, any length),
  `rental_late_fee_per_day` (overrun past the agreed return — the thing that
  really does vary by time), `rental_deposit_amount` and `rental_buffer_days`.
- The items list filters on "sellable / rentable" as a computed predicate.
  Index `(tenant_id, rental_price)` and `(tenant_id, sales_unit_price)` if those
  filters get hot.
- Migration: `purpose` and `rental_period_days` are dropped. Any row whose
  `purpose` disagreed with its prices was already broken; the prices win.

---

## ADR-014 · Barcode and QR are generated from the SKU

**Context.** `barcode` was free text and nullable, so it could be missing,
mistyped or duplicated — and a bridal shop scans a printed garment tag dozens of
times a day. There was no QR at all, although the staff's phones are the only
scanners most of these shops own. (Defect B16.)

**Decision.** One identity, two symbols, both derived:

```
sku      = platform_sequences.next('inventory_item')   -- ADF26-0042
barcode  = code128_payload(sku)                        -- stored, NOT NULL
qr       = render(sku)                                 -- rendered, never stored
```

- `barcode` is written in the same statement that issues the SKU and is
  `unique (tenant_id, barcode)`, so a scan is one indexed lookup.
- The QR carries the **same payload**. Nothing to keep in sync, and a torn tag
  can be reprinted from either symbol.
- Both are read-only in the UI. The New item drawer shows a live preview; the
  Edit item drawer shows the current label and offers **Reprint**, which
  re-renders the same codes rather than reissuing them.
- `sku` therefore becomes immutable after insert. It is already referenced by
  ledger rows, reservations and purchase-order lines, and now by a tag hanging
  in the shop.

**Consequences.**

- Items created by a GRN from a free-text purchase-order line get their SKU,
  barcode and QR at post time, in the same transaction (defect D2).
- Scanning is available wherever an item is picked: the items search, the
  stock-in drawer, the reservation drawer and the point of sale.
- If a tenant ever needs to honour a manufacturer's EAN, that is a **second**
  column (`supplier_barcode`), not a change to this one.

---

## Open questions for you 🔶

These are implemented with the stated default. Say the word and I will change them.

| # | Question | Default taken |
|---|----------|---------------|
| 1 | Expected rental uses per dress (ADR-002 divisor) | **20** |
| 2 | Cleaning/turnaround buffer between rentals (ADR-010) | **2 days** |
| 3 | Is VAT/tax charged on sales or rentals? | **No tax** — `tax_amount` columns kept but unused |
| 4 | Should cashiers see finance at all? | **No** — expenses only, if granted |
| 5 | Do you need stock per warehouse, or is one warehouse per branch enough? | **Per warehouse** — full support kept |
| 6 | Is the website/storefront module in scope? | **Deferred** — showcase flags removed from `inventory_items` |
