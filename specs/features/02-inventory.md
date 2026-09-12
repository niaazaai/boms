# Feature Spec — Inventory Module

**Status:** ready after Platform  
**Depends on:** Platform (tenant, branches, warehouses, currencies, units, users)  
**Schema:** `specs/database/inventory`  
**Wireframes:** `specs/wireframes/*/03-Inventory.excalidraw`  
**Flows:** `specs/flows/application-flows.md` § inventory movements

---

## Goal

Correct, auditable stock for bridal shops: know **on hand / reserved / available**, answer **how much inventory is worth**, move stock via tidy **stock-in / stock-out** transactions, and cover procurement receive, manual entry, adjust, dispose, reserve, sales order out, and sales return restock.

---

## Personas

| Role | Needs |
|------|--------|
| Owner / Manager | Valuation, procurement receive, dispose, adjust, transfers |
| Cashier | Search availability, reserve for rental, see qty before sale |

---

## Features

### I1 — Catalog structure
- [ ] Main categories & sub categories
- [ ] Item types (Wedding Dress, Veil, Jewelry…)
- [ ] Item models (designer / model names)
- [ ] Soft active/inactive (no hard delete if used)

### I2 — Items
- [ ] Create item with auto SKU `{TENANT_CODE}{YY}-{#####}` in **drawer**
- [ ] Fields: name, size, color, fabric, season, purpose (sale/rental/both)
- [ ] Sale price + rental price / period / deposit / late fee
- [ ] Purchase cost basis + other cost + currency/rate (feeds valuation)
- [ ] Photos (one main + gallery)
- [ ] Status: available, reserved, rented, sold, repairing, damaged, disposed
- [ ] Optional showcase flags: featured, hot, trending, wanted

### I3 — Stock ledger (required)
- [ ] All qty changes via `inventory_stock_transactions`
- [ ] Types: stock_in, stock_out, adjustment, transfer_in/out, reserve, release, rent_out, rent_return, **dispose**
- [ ] Current on-hand = SUM(quantity) per item+warehouse
- [ ] Reserved / available derived for UI
- [ ] Never edit historical transactions; void via reversing entry if needed
- [ ] Transactions list: tidy filters (In / Out / Adjust / Reserve / Dispose) + search by SKU / ref #

### I4 — Stock entry (stock-in)
- [ ] **From procurement (basic):** pick PO / receive lines → post → `stock_in` + cost update
- [ ] **Manual stock entry:** opening or ad-hoc qty + unit cost → draft → post → `stock_in` (`reference_type=manual_entry`)
- [ ] Both flows in drawers; show resulting transaction numbers

### I5 — Adjustments
- [ ] Draft → post adjustment (damage, lost, found, count mismatch)
- [ ] Posting writes stock transaction(s) type `adjustment`
- [ ] Optional photo attachment

### I6 — Dispose
- [ ] Draft → post disposal (damaged, scrap, lost, expired)
- [ ] Posting writes `dispose` transactions (negative qty)
- [ ] When on-hand hits 0 for unique dress → status `disposed`

### I7 — Transfers
- [ ] Transfer between warehouses/branches
- [ ] Status: draft → in_transit → received
- [ ] Paired transfer_out / transfer_in transactions

### I8 — Reservations
- [ ] Reserve item for date range (linked to sales order when booked)
- [ ] Conflict detection: overlapping active reservations on same item
- [ ] Release / cancel reservation → `release` transaction
- [ ] Reserved qty visible on item + hub KPIs

### I9 — Sales order impact (inventory side)
- [ ] Sale complete → `stock_out` (+ status sold when unique qty 0)
- [ ] Rental confirm → `reserve`; out → `rent_out`; return → `rent_return`
- [ ] **Sales return** restock → `stock_in` when return posted with restock=true
- [ ] Inventory screens deep-link to related SO / return numbers

### I10 — Valuation & reports
- [ ] Hub KPIs: **Total stock worth**, On hand units, Reserved, Available, Low stock count
- [ ] Valuation report: SKU · on hand · reserved · available · unit cost · **stock worth** · totals
- [ ] Movement report: stock in vs stock out for date range
- [ ] Filters: branch, warehouse, category, as-of date

### I11 — List UX
- [ ] Mobile list with image, status chip, price, available qty
- [ ] Filters: status, purpose, category, size, branch
- [ ] Search: name, SKU, barcode
- [ ] Low-stock alerts when available ≤ reorder_level
- [ ] Create/edit/adjust/dispose/entry forms in **drawers** (RTL/LTR aware)

---

## Screens (implementation order)

1. Inventory hub (worth + KPIs + quick actions)  
2. Item list + filters  
3. Item detail + media + qty breakdown  
4. Add / edit item drawer  
5. Stock entry — procurement receive (basic)  
6. Stock entry — manual  
7. Adjust stock  
8. Dispose  
9. Transfers  
10. Reservations  
11. Transactions ledger  
12. Valuation / movement reports  
13. Categories / types / models  

---

## Business rules

- Purpose `sale` → cannot start rental order line.
- Purpose `rental` → cannot complete sale order line (unless owner override later).
- Posting sale → `stock_out` + status `sold` when qty reaches 0 for unique dresses.
- Rental out → `rent_out` + status `rented`; return → `rent_return` + `available` (or `repairing` if damaged).
- Unique bridal dresses typically opening qty = 1.
- Available = on_hand − reserved; block oversell/over-reserve.
- Stock worth uses average / last unit_cost × on_hand in tenant default currency.
- Dispose is permanent write-off (not the same as temporary adjust).

---

## Integrations

| From | To inventory |
|------|----------------|
| Procurement receive | `stock_in` + update purchase cost |
| Manual stock entry | `stock_in` |
| Sales sale complete | `stock_out` |
| Sales rental confirm | `reserve` + reservation row |
| Sales rental out | `rent_out` |
| Sales rental return | `rent_return` |
| Sales return restock | `stock_in` |
| Dispose post | `dispose` |

---

## Out of scope

- Production / manufacturing requests  
- Complex multi-location putaway  
- Serial-number matrices beyond single SKU-per-dress  
- Full WMS barcode scanners (v2)  

---

## Acceptance checks

- Hub shows total inventory worth matching sum of on_hand × unit_cost.
- Manual stock entry posts → transaction appears in ledger as Stock In.
- Basic PO receive posts → stock_in + cost updated.
- Adjust damage → ledger adjustment; Dispose → dispose txn + status disposed.
- Reserve blocks overlapping dates; available qty decreases.
- Complete sale → stock_out; sales return restock → stock_in.
- Qty always matches sum of transactions.
