# Feature Map — Inventory Module

**Build order:** 3 (after Platform, Finance-Core)
**Depends on:** Platform (tenant, branches, warehouses, currencies, units, sequences) · Finance-Core (COGS ledger)
**Schema:** `specs/database/inventory`
**Wireframes:** `specs/wireframes/{desktop,mobile}/02-Inventory.excalidraw`
**Decisions:** ADR-001 (WAC) · ADR-004 (quantity model) · ADR-005 (immutability) · ADR-010 (double-booking)

---

## Goal

Answer four questions correctly, always:

1. **What do I have?** — on hand, on rent, reserved, available, per warehouse
2. **What is it worth?** — owned quantity × weighted average cost
3. **Where did it go?** — an immutable ledger for every movement
4. **Which dresses earn their keep?** — rental utilisation and payback

---

## The quantity model (read this before building anything)

```
on_hand_qty   = Σ ledger quantity                 physically in the warehouse
on_rent_qty   = Σ rent_out − Σ rent_return        out with customers
owned_qty     = on_hand_qty + on_rent_qty         what the shop owns   ← VALUATION
reserved_qty  = Σ active reservations             NOT from the ledger
available_qty = on_hand_qty − reserved_qty        sellable / bookable today
```

Two rules that the v1 spec got wrong and that everything here depends on:

- **A dress out on rent is still an asset.** Valuation uses `owned_qty`, never `on_hand_qty`.
- **Reservations are not stock movements.** There is no `reserve` or `release` ledger type.

---

## Personas

| Role | Needs |
|------|-------|
| Owner | Stock worth, utilisation/ROI, disposals, valuation reports |
| Manager | Receiving, adjustments, transfers, low-stock follow-up |
| Cashier | Is this dress available on this date? What does it cost to rent? |

---

## Feature map

### I1 · Catalogue structure
| | Feature | Notes |
|---|---|---|
| I1.1 | Main categories CRUD | Bridal Dresses, Rental Wear, Accessories |
| I1.2 | Sub categories CRUD | under a main category; A-Line, Ball Gown, Hijab Set |
| I1.3 | Item types CRUD | Wedding Dress, Engagement Dress, Veil, Jewelry |
| I1.4 | Item models CRUD | designer / model names |
| I1.5 | Soft active/inactive | no hard delete once referenced |
| I1.6 | Reorder within a category | `sort_order` drag handle |

### I2 · Items
| | Feature | Notes |
|---|---|---|
| I2.1 | Create / edit item in a drawer | over the items list — a list and its form never share a page |
| I2.2 | Auto SKU `{PREFIX}{YY}-{#####}` | from `platform_sequences`, unique **per tenant** |
| I2.3 | Bridal attributes | size, colour, fabric, season, quality, components — **no `purpose`** (ADR-013) |
| I2.4 | Serialised flag | `is_serialised` — one physical dress (qty 1) vs fungible accessories |
| I2.5 | Sale pricing | price, currency, unit |
| I2.5a | Channel is derived | sellable = sale price set · rentable = rental price set · both = both (ADR-013) |
| I2.6 | Rental pricing | price (one rental, **any length**), deposit, late fee/day, cleaning-buffer override — **no fixed period** (ADR-013) |
| I2.7 | Cost-recovery settings | `expected_rental_uses` override, `acquisition_cost`, `amortised_cost_to_date` |
| I2.8 | Photos | one main + gallery, reorderable |
| I2.9 | Lifecycle status | active · repairing · discontinued · disposed (**stored**) |
| I2.10 | Derived availability chip | available · reserved · rented · out of stock (**never stored**) |
| I2.11 | Barcode + QR | **generated from the SKU**, never typed; Code 128 stored, QR rendered; both shown on the item profile with Print label / Download (ADR-014) |
| I2.12 | Custom fields | `jsonb` for tenant-specific attributes |
| I2.13 | Duplicate item | clone attributes + pricing, new SKU |

### I3 · Stock ledger
| | Feature | Notes |
|---|---|---|
| I3.1 | All quantity changes go through `inventory_stock_transactions` | no direct qty mutation, anywhere |
| I3.2 | Eight types | `stock_in · stock_out · adjustment · transfer_in · transfer_out · rent_out · rent_return · dispose` |
| I3.3 | Immutable after insert | corrections are reversing transactions |
| I3.4 | Cost on every row | stock-in → landed cost · stock-out → WAC snapshot |
| I3.5 | Reference deep-links | every row links to its source document |
| I3.6 | Ledger screen | filter by type / item / warehouse / date, search by txn # or SKU |
| I3.7 | Running balance column | per item+warehouse |
| I3.8 | Export CSV | |

### I4 · Stock balances & costing
| | Feature | Notes |
|---|---|---|
| I4.1 | `inventory_stock_balances` per (item, warehouse) | maintained in the same DB transaction as the ledger write |
| I4.2 | Weighted average cost | recomputed on every stock-in (ADR-001) |
| I4.3 | Four quantities materialised | on_hand, on_rent, owned, reserved, available |
| I4.4 | Rebuild-from-ledger routine | balances are a cache, the ledger is truth |
| I4.5 | Nightly integrity check | mismatch → `platform_notifications` |
| I4.6 | Per-warehouse breakdown on item detail | the same SKU can hold stock in several warehouses |

### I5 · Stock in
| | Feature | Notes |
|---|---|---|
| I5.1 | Manual entry (opening / ad-hoc) | draft → post, multi-line, per-line cost |
| I5.2 | Procurement receipt (GRN) | posts at **landed** unit cost (ADR-009) |
| I5.3 | Sale return restock | from `sales_sale_returns` when `restock=true` |
| I5.4 | Transfer in | at the source warehouse's cost |
| I5.5 | Found-during-count | via adjustment, positive difference |
| I5.6 | Post shows resulting transaction numbers + new average cost | |

### I6 · Stock out
| | Feature | Notes |
|---|---|---|
| I6.1 | Sale completion | `stock_out` at WAC + `sale_cogs` entry |
| I6.2 | Dispose | draft → post, reason, write-off value at WAC |
| I6.3 | Supplier return | `stock_out` + reduce A/P |
| I6.4 | Transfer out | |
| I6.5 | Lifecycle → `disposed` when owned_qty hits 0 | for serialised dresses |

### I7 · Rental movement
| | Feature | Notes |
|---|---|---|
| I7.1 | `rent_out` when the dress leaves | reduces on_hand, increases on_rent, **owned unchanged** |
| I7.2 | `rent_return` when it comes back | reverses the above |
| I7.3 | Condition on return | good · needs cleaning · damaged · lost |
| I7.4 | Damaged → lifecycle `repairing` | blocks booking until cleared |
| I7.5 | Lost → disposal + rental claim | dress written off, customer charged |
| I7.6 | Cleaning buffer | item unavailable for `rental_buffer_days` after return |

### I8 · Adjustments
| | Feature | Notes |
|---|---|---|
| I8.1 | Draft → post | reasons: count mismatch · damage · lost · found · other |
| I8.2 | Expected vs counted vs difference | expected pre-filled from balances |
| I8.3 | Multi-photo attachments | via `platform_attachments` |
| I8.4 | Void by reversal | |
| I8.5 | Stock-count worksheet | print/export a blank count sheet per warehouse |

### I9 · Transfers
| | Feature | Notes |
|---|---|---|
| I9.1 | Between warehouses / branches | |
| I9.2 | Status: draft → in transit → received | |
| I9.3 | Paired `transfer_out` / `transfer_in` | cost travels with the goods |
| I9.4 | Partial receive | `received_quantity` per line |
| I9.5 | In-transit visibility | shown separately from on-hand |

### I10 · Reservations
| | Feature | Notes |
|---|---|---|
| I10.1 | Reserve an item for a date range | linked to a sales order line |
| I10.2 | **DB-enforced overlap prevention** | Postgres `EXCLUDE` constraint (ADR-010) |
| I10.3 | Cleaning buffer inside the block | `blocked_until = reserved_to + buffer_days` |
| I10.4 | Release / cancel | reservation status only — no ledger write |
| I10.5 | Conflict UI | shows the clashing booking + suggests alternative dresses |
| I10.6 | Availability calendar per item | month grid: free · reserved · on rent · buffer |
| I10.7 | Reservations list | filter by status, item, customer, date range |

### I11 · Alerts
| | Feature | Notes |
|---|---|---|
| I11.1 | Low stock when `available_qty ≤ reorder_level` | |
| I11.2 | Dresses in `repairing` too long | |
| I11.3 | Idle stock (no movement in N days) | |
| I11.4 | Balance/ledger mismatch | integrity alert |

### I12 · Reports
| | Report | Answers |
|---|---|---|
| I12.1 | **Valuation** | What is my stock worth? Per branch/warehouse/category, as-of any date. `owned_qty × avg_cost` |
| I12.2 | **Stock movement** | What came in and went out this period, by type |
| I12.3 | **Stock-in by source** | Receipts vs manual vs returns vs transfers — reconciles to the inventory increase |
| I12.4 | **Rental utilisation & asset ROI** | Per dress: acquisition cost, times rented, revenue to date, amortised cost, ROI %, days idle, revenue per owned day, payback status |
| I12.5 | **Low stock / reorder** | What to buy |
| I12.6 | **Dead stock** | Owned, never rented or sold in N days, with capital tied up |
| I12.7 | **Disposal / write-off** | What was written off, why, at what cost |
| I12.8 | **Stock ageing** | How long each item has been held |
| I12.9 | **Negative stock** | Only when `allow_negative_stock=true` |
| I12.10 | **Item price history** | Purchase cost over time per item |

All reports: branch · warehouse · category · date-range filters, CSV export, print view.

### I13 · List & search UX
| | Feature |
|---|---|
| I13.1 | Search by name, SKU, barcode — **and scan**: camera or USB reader resolves a Code 128 / QR straight to the item |
| I13.2 | Filters: lifecycle, derived availability, sellable / rentable, category, size, colour, branch, warehouse |
| I13.3 | Mobile list cards: photo, name, status chip, available qty, price |
| I13.4 | Desktop table with column chooser |
| I13.5 | Saved filter views |
| I13.6 | Bulk actions: transfer, adjust, change category, export |
| I13.7 | Empty / loading / error states on every list |

---

## Screens (implementation order)

The board reads top to bottom in six groups, and every group starts a fresh row:
**A** dashboard · **B** items · **C** stock ledger · **D** reservations ·
**E** transfers · **F** reports. Every create and edit is a drawer over its list.

| # | Screen | Wireframe |
|---|--------|-----------|
| **A. Dashboard** | | |
| 1 | Inventory dashboard — worth, KPIs, quick actions, low stock, conflicts | desktop A1 · mobile A1 |
| **B. Items** | | |
| 2 | Items list + filters + column chooser | desktop B1 · mobile B1 |
| 3 | New item — **drawer**, SKU issued, barcode + QR previewed live | desktop B2 · mobile B2 |
| 4 | Edit item — **drawer**, identity locked, current label + Reprint | desktop B3 |
| 5 | Item profile · Overview — attributes, channels, label card, stock by warehouse | desktop B4 · mobile B4 |
| 6 | Item profile · Stock & movement — WAC history + ledger for this SKU | desktop B5 · mobile B5 |
| 7 | Item profile · Reservations — bookings, blocked-until, conflicts | desktop B6 · mobile B6 |
| 8 | Item profile · Rentals — history, revenue, amortisation, payback | desktop B7 · mobile B7 |
| 9 | Item profile · Photos — gallery, is_main, condition shots | desktop B8 · mobile B8 |
| 10 | Item profile · Audit — field changes, postings, who and when | desktop B9 · mobile B9 |
| **C. Stock ledger** | | |
| 11 | Stock ledger — immutable movement history | desktop C1 · mobile C1 |
| 12 | Stock in (manual / opening) — **drawer** over the ledger | desktop C2 · mobile C2 |
| 13 | Receive against PO (GRN) — **drawer** over the ledger | desktop C3 · mobile C3 |
| 14 | Adjustment — **drawer** over the ledger | desktop C4 · mobile C4 |
| 15 | Dispose — **drawer** over the ledger | desktop C5 · mobile C5 |
| **D. Reservations** | | |
| 16 | Reservations list — every booking in the shop | desktop D1 · mobile D1 |
| 17 | New reservation — **drawer** + double-booking guard dialog | desktop D2 |
| 18 | Availability calendar — reserved / on rent / cleaning buffer | desktop D3 · mobile D3 |
| **E. Transfers** | | |
| 19 | Transfers list — in transit, partially received, completed | desktop E1 · mobile E1 |
| 20 | New transfer — **drawer** over the transfers list | desktop E2 |
| **F. Reports** | | |
| 21 | Valuation report | desktop F1 · mobile F |
| 22 | Stock movement & stock-in by source | desktop F2 · mobile F |
| 23 | Rental utilisation & asset ROI | desktop F3 · mobile F |
| — | Categories / types / models (Settings → master data) | — |

Dari and Pashto versions of every screen above:
`specs/wireframes/desktop/02-Inventory-Dari.excalidraw`,
`02-Inventory-Pashto.excalidraw`, and the mobile equivalents.

---

## Business rules

- An item is **sellable** if `sales_unit_price > 0` and **rentable** if `rental_price > 0`. There is no `purpose` column; a sale line rejects an item with no sale price, a rental line rejects an item with no rental price (ADR-013).
- A rental has **no fixed period**. Its length is `rental_to − rental_from` on the order; `rental_price` buys one rental of any length, and overrun past the agreed return is charged at `rental_late_fee_per_day` (ADR-013).
- `barcode` is generated from the SKU, `NOT NULL`, unique per tenant and never editable. The QR carries the same payload and is rendered, not stored. Reprint re-renders; it never reissues (ADR-014).
- `available_qty = on_hand − reserved`. Selling or booking beyond it is blocked unless `tenant_settings.allow_negative_stock = true`, in which case the line is flagged and appears in the Negative Stock report.
- Reservations never write to the ledger.
- Valuation always uses `owned_qty × avg_cost` in tenant default currency.
- Weighted average cost is recomputed only on stock-in; stock-out snapshots it.
- Posted documents are immutable — correction is a reversing document (ADR-005).
- A serialised dress reaching `owned_qty = 0` via disposal gets `lifecycle_status='disposed'`.
- Rental amortisation stops once `amortised_cost_to_date >= acquisition_cost`.
- Every posting is idempotent on `idempotency_key`.

---

## Integrations

| From | Inventory effect |
|------|------------------|
| Procurement receipt posted | `stock_in` at landed cost + WAC recompute |
| Procurement return posted | `stock_out` at WAC |
| Manual stock entry posted | `stock_in` |
| Sale line completed | `stock_out` at WAC → `finance_cogs_entries(sale_cogs)` |
| Sale return posted with restock | `stock_in` at original cost |
| Rental confirmed | `inventory_reservations` row (no ledger write) |
| Rental marked out | `rent_out` |
| Rental marked returned | `rent_return` + buffer block |
| Rental claim `loss` | `inventory_disposals` → `dispose` |
| Rental completed | → `finance_cogs_entries(rental_amortisation)` |
| Transfer sent / received | `transfer_out` / `transfer_in` |
| Disposal posted | `dispose` |

---

## Out of scope

- FIFO / specific-identification costing (WAC only — ADR-001)
- Manufacturing / alterations as a production order (alterations are an expense)
- Multi-location putaway, bin locations, WMS
- Barcode scanner hardware integration (v2)

---

## Acceptance checks

- [ ] Hub "Total stock worth" = `Σ owned_qty × avg_cost` and **does not change** when a dress is rented out.
- [ ] Reserving a dress reduces `available_qty` but leaves `on_hand_qty` and stock worth untouched.
- [ ] Two staff booking the same dress for overlapping dates: the second is rejected **by the database**.
- [ ] A dress returned on the 10th with a 2-day buffer cannot be booked for the 11th.
- [ ] Buying a veil at 500 then 700 gives `avg_cost = 600`; selling one posts COGS of 600.
- [ ] Receiving with 1,000 header shipping across two lines allocates pro-rata and the landed cost reaches the ledger.
- [ ] Voiding a posted disposal creates a reversing transaction; the original stays visible as `void`.
- [ ] `Σ ledger quantity` per item+warehouse equals `inventory_stock_balances.on_hand_qty` after a rebuild.
- [ ] Valuation as-of a past date replays the ledger and matches what the hub showed that day.
- [ ] The ROI report shows a gown bought at 40,000, rented 12 times at 2,500 → 30,000 revenue, 24,000 amortised, payback 75%.
- [ ] Posting the same manual entry twice with one `idempotency_key` creates one document.
