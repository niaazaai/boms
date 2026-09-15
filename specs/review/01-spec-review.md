# BOMS — Specification Review

**Reviewed:** `specs/database/*`, `specs/features/*`, `specs/flows/application-flows.md`, `specs/wireframes/*`
**Verdict:** the shape is right (procurement → inventory → sales → finance), but the spec is **not yet buildable**. 46 defects below; 12 are blocking.

Severity: **S1** = data will be wrong / corruption or double-booking · **S2** = module cannot be built as written · **S3** = gap vs. stated goal · **S4** = hygiene.

---

## A. Cross-cutting (affects every module)

### A1 — Every document number is globally unique, not per-tenant · **S1**
`inventory_items.sku`, `transaction_number`, `entry_number`, `adjustment_number`, `disposal_number`, `transfer_number`, `order_number`, `payment_number`, `return_number`, `po_number`, `receipt_number`, `expense_number`, `income_number`, `payable_number`, `receivable_number` are all declared `unique`.

In a shared multi-tenant database, tenant A creating `SO26-000001` **blocks tenant B from ever creating its own `SO26-000001`**. Every tenant after the first hits collisions on day one.

**Fix:** every one becomes `unique (tenant_id, <number>)`.

### A2 — No sequence generator → duplicate numbers under concurrency · **S1**
Numbers like `SO26-000001` are described but nothing generates them. `MAX(number)+1` in application code races: two cashiers posting at once produce the same number, and the unique index then fails the second sale at checkout.

**Fix:** add `platform_sequences` (tenant, doc_type, period, last_value) with atomic increment, or Postgres sequences per tenant+type.

### A3 — `exchange_rate_to_default` is a mutable scalar with no history · **S1**
`currencies.exchange_rate_to_default` is a single current value. Documents snapshot `exchange_rate` (good), but the catalog encourages reading the live scalar. The day the AFN/USD rate is edited, every report that reads the scalar silently restates history.

**Fix:** add `platform_exchange_rates` (currency, as_of_date, rate); make the document snapshot mandatory; keep the scalar as a *default for new documents only*.

### A4 — Build order is circular · **S2**
`specs/features/README.md` orders Platform → Inventory → Sales → Procurement → Finance. But `sales_order_payments.finance_account_id` and `procurement_supplier_payments.finance_account_id` are FKs to `finance_accounts`. Sales cannot be built before Finance exists.

**Fix:** split Finance into **Finance-Core** (accounts, categories, transactions — build at step 2, before Sales) and **Finance-Reporting** (P&L, pillars, AR/AP views — build last).

### A5 — No posting idempotency · **S1**
Mobile-first app, intermittent connectivity, "Post" buttons that write stock + money. A double tap or a retried request creates duplicate stock transactions and duplicate cash movements, with no way to detect it.

**Fix:** client-generated `idempotency_key uuid unique` on every posting endpoint; unique partial index on `(tenant_id, reference_type, reference_id)` for ledger writes.

### A6 — `user_roles` unique constraint does not work · **S2**
`unique (user_id, role_id, branch_id)` with `branch_id` nullable. In SQL, `NULL != NULL`, so the same user can be granted the same tenant-wide role unlimited times.

**Fix:** `unique (user_id, role_id, coalesce(branch_id, 0))` or a generated non-null column.

### A7 — System roles are shared, editable objects · **S1**
`roles.tenant_id nullable — null = system role template` and `role_permissions` hangs off `roles.id`. A tenant editing the "Manager" role's permission matrix mutates **every tenant's** Manager role.

**Fix:** system roles are templates only; on tenant creation, copy template → tenant-owned role rows. Block writes where `tenant_id is null` outside seeding.

### A8 — Login is ambiguous · **S2**
P1 says "Login with phone **or** email". `users` has `unique (tenant_id, email)` but **no constraint on phone**, and login has no tenant context (the user hasn't signed in yet, so `tenant_id` is unknown). Two users in different tenants with the same email make login non-deterministic.

**Fix:** make `email` globally unique (or `phone` globally unique) as the login identifier, OR add a tenant slug/code to the login screen. Recommended: global-unique email + optional global-unique phone.

### A9 — No `deleted_at`, but specs say "delete" · **S3**
P2 says "Delete or soft-deactivate user"; business rules say "soft-deactivate preferred". Only `status` enums exist. "Delete" has no defined behaviour and would orphan `created_by` FKs.

**Fix:** drop hard delete from the spec; `status='inactive'` only. Add `deleted_at` only if archival is genuinely needed.

### A10 — Attachments are single-file scalars · **S3**
`attachment_path varchar(255)` on adjustments, disposals, expenses, transactions. A damage claim needs several photos.

**Fix:** one polymorphic `platform_attachments` (tenant, entity_type, entity_id, file_path, caption, sort_order).

### A11 — Business day / timezone undefined · **S2**
`tenants.timezone` exists, all document dates are `date`, and the headline feature is "end-of-day profit". A shop closing at 01:00 posts sales that land on the wrong day in UTC. "Today" is undefined.

**Fix:** define `business_date = (created_at AT TIME ZONE tenants.timezone)::date`, store it explicitly as a column on every posting, and add `tenant_settings.day_cutoff_time`.

### A12 — Branch scoping is declared but never enforced · **S2**
`user_roles.branch_id` exists and "Cashier / Staff → use assigned branch only" is a persona requirement, but no rule says how rows are filtered. Without it, a branch cashier sees every branch's money.

**Fix:** spec a `branch_scope` rule: if a user's roles all carry `branch_id`, every list query is filtered to that set; roles with `branch_id IS NULL` are tenant-wide.

---

## B. Inventory

### B1 — `inventory_items.status` cannot represent quantity > 1 · **S1**
`status enum('available','reserved','rented','sold',…)` is one scalar per item, but the spec's own example has `Veil set` with **qty 4**. If 2 of 4 veils are rented, the item is simultaneously `available` and `rented`. The scalar will always be a lie for non-unique items, and code will branch on it.

**Fix:** split the two concepts.
- `inventory_items.lifecycle_status enum('active','repairing','discontinued','disposed')` — a property of the *item record*.
- Availability (`available / reserved / rented / out_of_stock`) is **always derived** from the ledger. Never stored.

### B2 — `reserve` / `release` as ledger types corrupt on-hand · **S1**
The schema states `on_hand = SUM(quantity)` over all transactions, *and* makes `reserve` a **negative** quantity. Reserving a dress therefore **reduces on-hand stock** — but nothing left the building. Valuation drops, low-stock alerts fire, and `available = on_hand − reserved` double-subtracts the same reservation.

It also declares two sources of truth in one line: *"Reserved qty = SUM(active reservations) **OR** net of reserve/release transactions."*

**Fix:** reservations are **not** stock movements. Remove `reserve` and `release` from `inventory_stock_transactions.type`. `inventory_reservations` is the single source of reserved qty.

### B3 — Rented-out stock disappears from valuation · **S1**
`rent_out` is a negative ledger quantity. For a **rental business**, the dress is still owned, still an asset, still worth money — it is just not on the rack. As written, the owner's "Total stock worth" **drops every time a dress goes out on rent** and jumps back on return. The single headline KPI of the inventory module is wrong on any busy weekend.

**Fix:** three buckets, not one.
```
on_hand_qty   = physically in warehouse      (ledger, excl. rented)
on_rent_qty   = out with a customer          (rent_out − rent_return)
owned_qty     = on_hand + on_rent            ← valuation uses this
available_qty = on_hand − reserved
```

### B4 — Costing method is undefined and contradicted three ways · **S1**
- `inventory_items.purchase_amount` — a "last purchase" scalar
- `inventory_stock_transactions.unit_cost` — per movement
- the valuation view says `avg_unit_cost`
- `02-inventory.md` says *"average / last unit_cost"*
- `sales_order_items.unit_cost_snapshot` feeds COGS

For a veil set bought at 500 then 700, COGS and stock worth are non-deterministic.

**Fix:** commit to **weighted average cost (WAC)**, maintained per `(item, warehouse)`, recomputed on every stock-in, snapshotted onto every stock-out. See `02-decisions.md` ADR-001. Drop `purchase_amount` from the item master as a costing input (keep it as a display-only "last purchase price").

### B5 — Item master carries a single `branch_id` / `warehouse_id` · **S1**
`inventory_items.branch_id` + `warehouse_id` are single FKs, yet `inventory_transfers` moves stock between warehouses and the ledger is keyed per warehouse. After one transfer the item master points at the wrong place, or the same SKU needs duplicating per warehouse.

**Fix:** remove location from `inventory_items`. Location belongs to the ledger and to `inventory_stock_balances`. Keep `default_warehouse_id` as a form convenience only.

### B6 — No DB-level overlap guard on reservations · **S1**
I8 requires "conflict detection: overlapping active reservations on same item", but nothing enforces it. Two staff booking the same gown for the same wedding date will both succeed. **For a bridal shop this is the single most damaging bug possible.**

**Fix:** Postgres exclusion constraint:
```sql
EXCLUDE USING gist (
  inventory_item_id WITH =,
  daterange(reserved_from, reserved_to, '[]') WITH &&
) WHERE (status = 'active')
```

### B7 — No cleaning / turnaround buffer between rentals · **S3**
`return_condition='needs_cleaning'` exists, but availability math lets the dress be rented the very next day. Real bridal operations need 1–3 days of turnaround.

**Fix:** `tenant_settings.rental_buffer_days`; reservations block `reserved_to + buffer`; item can carry an override.

### B8 — Reservations cannot be traced to an order line · **S2**
`inventory_reservations.sales_order_id` exists, but not `sales_order_item_id`. A rental order with two dresses produces two reservations that cannot be matched to their lines — releasing one line is impossible.

**Fix:** add `sales_order_item_id`.

### B9 — Posted documents are not locked · **S2**
Entries, adjustments, disposals have `status='posted'` but nothing prevents editing lines afterwards, and there is no `posted_by`. The "immutable ledger" guarantee is unenforceable.

**Fix:** `posted_by`, `posted_at`, and a rule: after `posted`, only `void` is permitted, which writes a reversing document.

### B10 — `allow_negative_stock` contradicts "block oversell" · **S3**
`tenant_settings.allow_negative_stock` (default false) vs. the business rule "Available = on_hand − reserved; block oversell/over-reserve". Which wins, and what happens at the checkout screen when it's `true`?

**Fix:** `false` → hard block with an inline error. `true` → allow, flag the line, and surface a "Negative stock" report. Spec both paths.

### B11 — Valuation "as-of date" is not achievable from the item master · **S2**
I10 promises an as-of-date valuation filter. Reconstructing it needs running cost from the ledger, not `items.purchase_amount`.

**Fix:** valuation always computes from `inventory_stock_transactions` filtered by `business_date <= as_of`. (Fixed by B4 + A11.)

### B12 — Missing: rental utilisation / asset ROI · **S3**
For a rental business the key inventory question is *"which dress earns its purchase price back, and how fast?"* Nothing in the spec answers it.

**Fix:** new report — per item: purchase cost, times rented, revenue to date, ROI %, days idle, revenue per owned day. Added to the feature map.

### B13 — `inventory_items` mixes five concerns · **S4**
One table holds identity, bridal attributes, sale pricing, rental pricing, purchase cost, website flags, repair notes, and location — ~45 columns. It will become unmaintainable and every form loads all of it.

**Fix:** keep the core table lean; split rental pricing into `inventory_item_rental_terms` and website flags into the (currently empty) website module.

### B14 — `purpose` duplicates the prices and can contradict them · **S2**
`inventory_items.purpose enum('sale','rental','both')` says what an item is *for*, and the two price columns say the same thing again. Nothing keeps them agreeing. An item saved as `purpose='rental'` with only `sales_unit_price` set is neither sellable nor rentable, and no screen can explain why. Staff also have to answer a question the form already knows the answer to.

**Fix:** drop the column. The channel is derived — `sellable = sales_unit_price > 0`, `rentable = rental_price > 0`. One fact, one place. See ADR-013.

### B15 — `rental_period_days` on the item contradicts the booking · **S2**
The item master fixes a rental at `rental_period_days` (default 3) while `sales_orders` carries `rental_from` / `rental_to`, chosen per booking. Two sources for one duration. A four-day wedding hire against a three-day item reads as an overrun that nobody agreed to, and the availability calendar cannot tell which number to block.

**Fix:** drop the column. A rental is **open** — its length is `rental_to − rental_from` on the order. `rental_price` is the price of one rental whatever its length; time-based variation is already handled by `rental_late_fee_per_day`. See ADR-013.

### B16 — `barcode` is free text, so it can be wrong, duplicated or absent · **S2**
`barcode varchar(100) nullable`, typed by hand. In a shop where every garment carries a printed tag this guarantees three failures: items with no barcode that cannot be scanned at the till, typos that scan to nothing, and the same code on two dresses. There is also no QR anywhere, though a phone camera is the only scanner most Afghan bridal shops own.

**Fix:** derive it. `barcode = code128_payload(sku)`, generated in the same statement that issues the SKU, `NOT NULL`, unique per tenant, never editable. The QR shown beside it carries the same payload and is rendered at display time, so there is nothing to keep in sync. See ADR-014.

---

## C. Sales

### C1 — Customer deposits are booked as income · **S1**
`sales_order_payments.payment_type='deposit'` → "finance IN" → Income pillar → daily profit.

A refundable rental deposit is a **liability**, not revenue. As specified, a day with ten rental bookings shows a large profit that partly has to be handed back. **The headline number the owner is trusting is wrong.**

**Fix:** deposits increase Cash (pillar 1) and a new **Customer Deposits Held** liability bucket. They never touch Income. On return: forfeit portion → Income, remainder → refund OUT. See ADR-003.

### C2 — Rental COGS is undefined — the core money question · **S1**
P&L is `Income − Expenses − COGS`, COGS from `unit_cost_snapshot`. But a rental does not consume the dress.
- If rental lines write COGS → the dress is expensed on its first rental and profit is destroyed.
- If they write nothing → rental profit is overstated **forever**; a 40,000 AFN gown that earns 2,500 per rental looks like pure margin and the owner never sees the asset being consumed.

`05-finance.md` defers this as "optional rental cost policy later". It is not optional — it is the entire economics of the business.

**Fix:** rental cost recognition as a tenant setting, defaulting to **per-use amortisation**: `rental_cogs = purchase_cost / expected_rental_uses`, recognised on each completed rental, accumulated until the asset is fully amortised. See ADR-002.

### C3 — Header `order_type` conflicts with line `line_type` · **S2**
`sales_orders.order_type enum('sale','rental')` and `sales_order_items.line_type enum('sale','rental')` allow a `sale` header with `rental` lines. Nothing reconciles them. Meanwhile the real bridal counter case — *rent the gown, buy the veil* — is exactly a mixed order.

**Fix:** support mixed orders properly. `line_type` is authoritative; header becomes `order_kind enum('sale','rental','mixed')`, **derived** on save, used only for filtering and labelling.

### C4 — `customer_id` is effectively required · **S3**
A walk-in buying a 500 AFN veil should not force customer creation. `sales_orders.customer_id` is not marked nullable and the flow is "pick customer → add items".

**Fix:** `customer_id` nullable; UI offers "Walk-in customer" as the default for **sale** lines. Rentals always require a customer (you must know who has the dress).

### C5 — Lost / never-returned rental has no document · **S2**
`return_condition` includes `'lost'`, but nothing converts that into money or stock. The dress is gone: inventory must be written off, the customer must be charged, the deposit must be consumed.

**Fix:** new `sales_rental_claims` (damage / loss / late) → charge amount, deposit applied, balance to A/R, and for `loss` a linked `inventory_disposals` row.

### C6 — Late fees are modelled in three places with no rule · **S2**
`inventory_items.rental_late_fee_per_day`, `sales_orders.late_fee_amount`, and `payment_type='late_fee'`. Nothing says who computes it, when, against which date, or whether it is waivable. There is no `late_days` anywhere.

**Fix:** compute on "Mark returned": `late_days = max(0, actual_return_date − rental_end_date)`; amount = `Σ line late_fee_per_day × late_days`; store on the order with `late_fee_waived_amount` and a reason.

### C7 — `sales_returns` only covers sold goods · **S3**
Returns reference `sales_order_item_id` and restock. The rental return path is on the order itself (`actual_return_date`, `return_condition`). Two different mechanisms, and the feature spec calls both "return" — the wireframes and flows conflate them.

**Fix:** rename to `sales_sale_returns` (refund + restock of *sold* goods). Rental return stays an order lifecycle transition. Make the naming explicit everywhere.

### C8 — A/R exists in two tables · **S1**
`sales_orders.balance_amount` and `finance_receivables.balance_amount` both hold what the customer owes. Two writers, no reconciliation, guaranteed drift. The acceptance check *"A/R pillar equals sum of open order balances"* assumes they agree by magic.

**Fix:** `finance_receivables` is the **only** A/R record. `sales_orders.balance_amount` becomes a derived/cached display column, recomputed from payments, never read by Finance.

### C9 — Partial refund state is unrepresentable · **S3**
`payment_status enum('unpaid','partial','paid','refunded')` — a 12,000 sale refunded 1,500 is neither `paid` nor `refunded`.

**Fix:** add `partially_refunded`, or derive payment status from `Σ payments` and drop the enum.

### C10 — No sales reports at all · **S3**
S1–S6 contain zero reports, yet the brief asks for *"comprehensive report that shows proper sales report that is easy to understand"*.

**Fix:** six reports added to the feature map — Sales Summary, Sales by Item/Category, Rental Performance, Customer Ledger, Staff/Cashier Sales, Deposits & Refunds.

### C11 — No order void after completion · **S3**
Only `cancelled`. A completed sale posted in error has no reversal, while Finance has `void` and Inventory has reversing entries. Inconsistent.

**Fix:** `void` transition on completed orders → reverses stock, payments, A/R, and COGS via linked reversing documents.

---

## D. Procurement

### D1 — Landed cost allocation is undefined across three fields · **S1**
`other_cost` exists on the PO **header**, on the PO **line**, and on the **receipt line**. Nothing says which one reaches `inventory_stock_transactions.unit_cost`. Inventory valuation is therefore non-deterministic — three developers will implement it three ways.

**Fix:** header `other_cost` is allocated to lines **pro-rata by line value** at receipt time; landed unit cost = `unit_cost + (allocated_other_cost / qty)`; that single number is what posts to the ledger. Store `landed_unit_cost` on the receipt line so it is auditable.

### D2 — Receipt cannot create the item it is supposed to create · **S2**
`procurement_purchase_order_items.inventory_item_id` is nullable ("create item on receive"), but `procurement_receipt_items.inventory_item_id` is **not nullable** and nothing back-fills the PO line. The stated flow cannot execute.

**Fix:** receipt posting creates the `inventory_items` row first, writes the id onto both the receipt line **and** the originating PO line.

### D3 — Over-receipt is unguarded · **S2**
`quantity_received` on the PO line is described as maintained by receipts, with a "soft warn + block unless override" rule, but there is no constraint and no override field.

**Fix:** DB check `quantity_received <= quantity_ordered` unless `over_receipt_approved_by` is set; recompute `quantity_received` from receipts, never increment in place.

### D4 — A/P exists in two tables · **S1**
Same defect as C8: `procurement_purchase_orders.balance_amount` and `finance_payables.balance_amount`.

**Fix:** `finance_payables` is the only A/P record; the PO column is derived/cached.

### D5 — No procurement reports · **S3**
The brief explicitly asks for *"a flow where we can generate accurate report for procurement and inventory stock-ins"*. R1–R5 have none.

**Fix:** five reports added — Purchase Register, Stock-In Report (by source: PO / manual / return / transfer), Supplier Ledger & Aging, PO Status & Fulfilment, Price History per item.

### D6 — Receipt has no void · **S2**
`status enum('draft','posted','cancelled')`. Once posted it has moved stock and opened A/P; "cancelled" after posting has no defined effect on either.

**Fix:** `void` → reversing stock transactions + reversing payable, never an in-place edit.

### D7 — Supplier returns / credit notes missing · **S3**
A faulty dress sent back to the supplier has no document. Marked "v2" in the spec, but it strands stock and A/P when it happens.

**Fix:** minimal `procurement_returns` (supplier debit note) → `stock_out` + reduce A/P.

### D8 — PO has no approval step but permissions imply one · **S3**
`permissions.action` includes `approve`, and POs go `draft → ordered` with no approver recorded.

**Fix:** record `approved_by` / `approved_at` on the `draft → ordered` transition; keep threshold-based approval out of scope.

---

## E. Finance

### E1 — `finance_accounts.current_balance` is a maintained scalar · **S1**
A stored running balance updated by application code, with no stated locking. Concurrent postings lose updates; one failed write desynchronises the account permanently, and nothing detects it.

**Fix:** balance is **derived** — `opening_balance + Σ posted finance_transactions`. Keep `current_balance` only as a cached column refreshed inside the posting transaction, with a nightly reconciliation report.

### E2 — The "unified ledger" is not unified · **S1**
`finance_transactions` is declared the single source of truth, but:
- `finance_expenses` and `finance_other_income` carry `finance_transaction_id` (linked ✓)
- `sales_order_payments` and `procurement_supplier_payments` carry **no such link** ✗

So the two highest-volume money sources cannot be traced to the ledger, and `F6 — void with reversing logic` has nothing to reverse against.

**Fix:** add `finance_transaction_id` to both payment tables; make it `not null` once posted. Every money movement in the system has exactly one ledger row.

### E3 — Pillars 4 and 5 double-count with source documents · **S1**
See C8 / D4. The A/R and A/P pillars will not equal the order balances.

**Fix:** as above — payables/receivables tables own the number.

### E4 — No liability bucket for deposits held · **S1**
Consequence of C1. Cash includes money that is not the shop's. Without a "Deposits held" line the owner cannot tell how much of the drawer is actually theirs.

**Fix:** `finance_customer_deposits` tracking held / applied / forfeited / refunded per order, surfaced as a **6th tile** on the dashboard (still "5 pillars" conceptually — it's a contra to Cash).

### E5 — Voiding has no defined reversal semantics · **S2**
"Voiding a transaction reverses account balance and linked payable/receivable effects" — but the mechanism (reversing row vs. status flip) is unspecified, and with `current_balance` as a scalar (E1) it cannot be done safely.

**Fix:** void = insert a mirrored reversing `finance_transactions` row linked via `reverses_transaction_id`; original keeps `status='void'`; nothing is ever deleted or mutated.

### E6 — COGS has no home · **S2**
P&L needs COGS, but COGS is neither a `finance_transaction` (no cash moves) nor stored anywhere. It exists only as `sales_order_items.unit_cost_snapshot`, which is not queryable as a period total alongside income and expenses.

**Fix:** `finance_cogs_entries` (order, line, business_date, amount_base, kind: `sale_cogs` | `rental_amortisation`) written at completion. P&L then reads three tables with identical shape.

### E7 — `finance_daily_summaries` can silently disagree with the ledger · **S3**
A snapshot table with no invalidation rule. A back-dated expense makes yesterday's snapshot wrong forever.

**Fix:** mark snapshots `stale` when any posting lands on a covered date; recompute on read or via job. Treat as a cache, never as a source.

### E8 — Multi-currency P&L is under-specified · **S3**
`amount_base` is on `finance_transactions` only — not on expenses, income, payables, receivables, or order totals. A P&L over mixed AFN/USD rows cannot be summed.

**Fix:** `amount_base` (tenant default currency) + `exchange_rate` on **every** money-bearing table, snapshotted at posting.

### E9 — Broken spec reference · **S4**
`05-finance.md` points at `specs/wireframes/06-finance.md`, which does not exist. The file is `specs/wireframes/{mobile,desktop}/06-Finance.excalidraw`.

### E10 — "Five pillars" never defined as formulas · **S3**
The dashboard is the module's whole purpose, but no pillar has an exact query. Two developers will produce two different numbers.

**Fix:** exact definitions in `02-decisions.md` § Pillar formulas.

---

## F. Platform

### F1 — `tenant_settings.custom_json` is an escape hatch · **S4**
`jsonb` "extra UI / feature flags" invites undocumented behaviour to accumulate there.

**Fix:** enumerate real settings as columns; keep `custom_json` for tenant-specific UI preferences only, documented.

### F2 — Empty `website` schema, but item flags reference it · **S3**
`specs/database/website` is **0 bytes**, while `inventory_items` carries `is_featured` / `is_hot` / `is_trending` / `is_wanted` and the README lists a website module.

**Fix:** either move the four flags into a `website_showcase_items` table when the module is specced, or drop them from `inventory_items` now. Recommended: **drop now**, re-add with the module.

### F3 — No notifications table, but the UI promises alerts · **S3**
Low-stock alerts (`tenant_settings.low_stock_alert`), due-return reminders, overdue A/R — all appear in wireframes and feature specs with nowhere to live.

**Fix:** `platform_notifications` (tenant, user, kind, entity, message, read_at).

### F4 — Audit log coverage is undefined · **S3**
"login + critical settings changes" — but `void`, `post`, price changes, and permission edits are exactly what an owner needs to audit.

**Fix:** enumerate audited actions; make `post` and `void` on every document mandatory audit events.

### F5 — `permissions` has no seed list · **S2**
P3 promises a "permission matrix by module × action", but no permission codes are enumerated anywhere. The matrix screen cannot be built.

**Fix:** seed list per module × action in the platform feature map.

---

## G. Wireframes & flows

### G1 — Sidebar has no icons and no grouping · **S3**
Flat list: Home · Inventory · Sales · Procurement · Finance · Settings. No icons, no sub-navigation, no counts, no branch switcher, no user menu. Explicitly called out in the brief.

### G2 — Screen coverage is very uneven · **S3**
Inventory has 12 desktop screens; **Sales has 4, Procurement 4, Finance 3** — despite Sales and Finance being where the owner spends their day. No report screens exist in any module.

### G3 — Flow diagram §8 hard-codes the broken reserve model · **S3**
`application-flows.md` shows `RSV[Reserve] --> TXN_RSV[reserve txn]` feeding the same ledger that computes on-hand — i.e. it draws defect B2. Must be redrawn.

### G4 — No error, empty, or loading states · **S3**
Every wireframe shows the happy path with populated tables. Nothing shows "no results", "insufficient stock", "date conflict", "offline".

### G5 — Right-to-left is asserted, never drawn beyond one frame · **S3**
Two frames demonstrate the mirrored shell. With Dari and Pashto as primary locales, every screen needs a mirrored form, not a rule set nobody can see.

**Fix:** the Dari and Pashto boards are now generated by reflecting the English board and substituting strings, so all three stay in step by construction — `specs/wireframes/desktop/02-Inventory-Dari.excalidraw`, and the same for Pashto. The direction badges that used to sit in the language switcher are gone: the switcher names the language, and the direction follows from it.

### G6 — Screens mix a list and its form on one page · **S3**
Several screens show a table and, below it, the form that creates a row in that table. The user loses their place in the list, the page scrolls twice, and on a phone the form is below the fold.

**Fix:** every create and edit is a drawer over its list, with its own title and subtitle. The list stays on screen behind it. Redrawn across the Inventory board.

---

## Blocking defects (must be resolved before development starts)

| # | Defect | Module |
|---|--------|--------|
| A1 | Global unique numbers break multi-tenancy | all |
| A2 | No sequence generator → duplicate numbers | all |
| A4 | Circular build order (Sales needs Finance) | all |
| A5 | No posting idempotency | all |
| B2 | `reserve` in ledger corrupts on-hand | inventory |
| B3 | Rented stock vanishes from valuation | inventory |
| B4 | Costing method undefined | inventory |
| B6 | No overlap guard → double-booked dresses | inventory |
| C1 | Deposits booked as income | sales / finance |
| C2 | Rental COGS undefined | sales / finance |
| D1 | Landed cost allocation undefined | procurement |
| E2 | "Unified" ledger misses sales & supplier payments | finance |

Resolutions for all twelve are in [`02-decisions.md`](./02-decisions.md); the corrected schema is in [`specs/database/`](../database/).
