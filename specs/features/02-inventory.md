# Feature Spec — Inventory Module

**Status:** ready after Platform  
**Depends on:** Platform (tenant, branches, warehouses, currencies, units, users)  
**Schema:** `specs/database/inventory`  
**Wireframes:** `specs/wireframes/03-inventory.md`  
**Flows:** `specs/flows/application-flows.md` § stock movements

---

## Goal

Simple, correct stock for bridal shops: track each dress/accessory, know if it is available / reserved / rented / sold / repairing, and never lose the audit trail of quantity changes.

---

## Personas

| Role | Needs |
|------|--------|
| Owner / Manager | Add dresses, see what’s out on rent, adjust damage |
| Cashier | Search by name/size/SKU, check availability for sale/rent |

---

## Features

### I1 — Catalog structure
- [ ] Main categories & sub categories
- [ ] Item types (Wedding Dress, Veil, Jewelry…)
- [ ] Item models (designer / model names)
- [ ] Soft active/inactive (no hard delete if used)

### I2 — Items
- [ ] Create item with auto SKU `{TENANT_CODE}{YY}-{#####}`
- [ ] Fields: name, size, color, fabric, season, purpose (sale/rental/both)
- [ ] Sale price + rental price / period / deposit / late fee
- [ ] Purchase cost basis + other cost + currency/rate
- [ ] Photos (one main + gallery)
- [ ] Status: available, reserved, rented, sold, repairing, damaged, disposed
- [ ] Optional showcase flags: featured, hot, trending, wanted

### I3 — Stock ledger (required)
- [ ] All qty changes via `inventory_stock_transactions`
- [ ] Types: stock_in, stock_out, adjustment, transfer_in/out, reserve, release, rent_out, rent_return
- [ ] Current qty = SUM(quantity) per item+warehouse
- [ ] Never edit historical transactions; void via reversing entry if needed

### I4 — Adjustments
- [ ] Draft → post adjustment (damage, lost, found, count mismatch)
- [ ] Posting writes stock transaction(s)
- [ ] Optional photo attachment

### I5 — Transfers
- [ ] Transfer between warehouses/branches
- [ ] Status: draft → in_transit → received
- [ ] Paired transfer_out / transfer_in transactions

### I6 — Reservations (rental calendar)
- [ ] Reserve item for date range (linked to sales order when booked)
- [ ] Conflict detection: overlapping active reservations on same item
- [ ] Release / cancel reservation

### I7 — List UX
- [ ] Mobile list with image, status chip, price
- [ ] Filters: status, purpose, category, size, branch
- [ ] Search: name, SKU, barcode, phone-friendly quick find
- [ ] Low-stock alerts when qty ≤ reorder_level

---

## Screens (implementation order)

1. Item list + filters  
2. Add / edit item  
3. Item detail + media  
4. Categories / types / models  
5. Adjust stock  
6. Transfers  
7. Reservations calendar (can follow Sales rental)

---

## Business rules

- Purpose `sale` → cannot start rental order line.
- Purpose `rental` → cannot complete sale order line (unless owner override later).
- Posting sale → `stock_out` + status `sold` when qty reaches 0 for unique dresses.
- Rental out → `rent_out` + status `rented`; return → `rent_return` + `available` (or `repairing` if damaged).
- Unique bridal dresses typically opening qty = 1.

---

## Integrations

| From | To inventory |
|------|----------------|
| Procurement receive | `stock_in` + update purchase cost |
| Sales sale complete | `stock_out` |
| Sales rental confirm | `reserve` + reservation row |
| Sales rental out | `rent_out` |
| Sales rental return | `rent_return` |
| Sales return restock | `stock_in` |

---

## Out of scope

- Production / manufacturing requests  
- Complex multi-location putaway  
- Serial-number matrices beyond single SKU-per-dress  

---

## Acceptance checks

- Create dress → appears in list with auto SKU.
- Adjust damage to 0 → status can move to damaged/disposed; ledger shows adjustment.
- Overlapping reservation blocked with clear message.
- Qty always matches sum of transactions.
