# Feature Spec — Procurement Module

**Status:** ready after Inventory (can parallelize with Sales)  
**Depends on:** Platform + Inventory  
**Schema:** `specs/database/procurement`  
**Wireframes:** `specs/wireframes/05-procurement.md`  
**Flows:** `specs/flows/application-flows.md` § procurement

---

## Goal

Minimal purchasing so inventory cost and accounts payable stay correct. Bridal shops buy occasionally — keep PO → receive → pay only.

---

## Personas

| Role | Needs |
|------|--------|
| Owner / Manager | Add supplier, record purchase, receive dresses, pay |

---

## Features

### R1 — Suppliers
- [ ] CRUD supplier (name, phone, contact, currency, payment term)
- [ ] Active / inactive
- [ ] Supplier purchase history

### R2 — Purchase orders
- [ ] Create PO with supplier, branch, warehouse, dates
- [ ] Lines: existing item OR free-text new item name
- [ ] Qty, unit cost, other cost, line total
- [ ] Header other cost (shipping etc.)
- [ ] Status: draft → ordered → partial_received → received / cancelled
- [ ] Payment status: unpaid / partial / paid

### R3 — Receiving (GRN)
- [ ] Receive against PO (full or partial)
- [ ] For new free-text lines: create `inventory_items` on post (guided mini-form: size/color/purpose)
- [ ] Post → `inventory_stock_transactions` stock_in + update item purchase cost
- [ ] Open/update `finance_payables`

### R4 — Supplier payments
- [ ] Pay against PO / payable
- [ ] Choose finance account + method
- [ ] Update PO paid/balance + payable status
- [ ] Post finance transaction OUT

### R5 — Home UX
- [ ] Open POs count + AP total
- [ ] New purchase CTA
- [ ] List of open / recent POs

---

## Screens (implementation order)

1. Procurement home  
2. Suppliers  
3. Create / view PO  
4. Receive goods  
5. Pay supplier  

---

## Business rules

- Cannot receive more than ordered (soft warn + block unless override).
- Draft PO does not affect stock or finance.
- Only `ordered` (or partial) POs can be received.
- Cancelling PO with receipts not allowed; reverse via adjustment / credit later if needed (v2).

---

## Integrations

| Event | Inventory | Finance |
|-------|-----------|---------|
| Receive posted | stock_in + cost | open A/P |
| Supplier payment | — | cash out, close A/P |

---

## Out of scope (intentionally removed from old ERP)

- Need assessment, RFQ, quotations comparison  
- Shipments, ports, incoterms, freight, landed cost worksheets  
- Multi-level approval thresholds  

---

## Acceptance checks

- Receive 1 new dress → new SKU in inventory with cost, qty 1.
- Unpaid PO shows in Finance A/P pillar.
- Payment clears A/P and reduces cash/bank.
