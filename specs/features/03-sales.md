# Feature Spec — Sales Module

**Status:** ready after Inventory  
**Depends on:** Platform + Inventory  
**Schema:** `specs/database/sales`  
**Wireframes:** `specs/wireframes/*/04-Sales.excalidraw` (+ inventory stock-out / return restock in `03-Inventory.excalidraw`)  
**Flows:** `specs/flows/application-flows.md` § sale & rental & sales return

---

## Goal

Make selling and renting dresses effortless for shop staff: find customer by phone, add items, take money, finish. Cover normal sale, rental lifecycle, and returns — without ERP complexity.

---

## Personas

| Role | Needs |
|------|--------|
| Cashier | Fast checkout, deposits, returns |
| Owner | See today’s orders, due returns, balances |

---

## Features

### S1 — Customers
- [ ] Create customer: name + phone required
- [ ] Optional wedding date, address, notes
- [ ] Search by phone (primary) or name
- [ ] Customer history: past sales & rentals

### S2 — Sale order
- [ ] New sale → customer → add available sale items
- [ ] Discount amount or percent
- [ ] Payment full or partial
- [ ] On complete: stock_out, payment row, finance IN, A/R if balance
- [ ] Status: draft → confirmed/completed → cancelled

### S3 — Rental order
- [ ] New rental → customer → event date + rental window
- [ ] Add rental items; block date conflicts
- [ ] Deposit required (default from settings or item)
- [ ] Status path: draft → confirmed (reserved) → out → returned → completed
- [ ] Mark out / mark returned with condition
- [ ] Late fee auto calc from days × item late fee
- [ ] Collect remaining balance or refund deposit remainder

### S4 — Payments
- [ ] Payment types: deposit, installment, full, refund, late_fee
- [ ] Link to payment method + finance account (cash drawer/bank)
- [ ] Update order `paid_amount` / `balance_amount` / `payment_status`

### S5 — Returns (sold goods)
- [ ] Select order lines + qty
- [ ] Reason + optional restock
- [ ] Refund amount + finance OUT
- [ ] Restock → inventory stock_in when posted

### S6 — Sales home UX
- [ ] Big buttons: New Sale / New Rental
- [ ] Tabs: Open / Due returns / Done
- [ ] Order detail with contextual actions only (no clutter)

---

## Screens (implementation order)

1. Sales home  
2. Customer pick / add  
3. New sale checkout  
4. Collect payment  
5. New rental checkout  
6. Order detail (out / return)  
7. Sales return  
8. Customers list  

---

## Business rules

- Cannot add item that is not `available` (except owner force — later).
- Rental confirm creates `inventory_reservations` + reserve transaction.
- Partial payment allowed; balance creates/updates `finance_receivables`.
- Cancel confirmed rental releases reservation and stock reserve.
- Returned damaged → item status `repairing` or `damaged`; deposit may be withheld (manual note + amount).

---

## Integrations

| Sales event | Inventory | Finance |
|-------------|-----------|---------|
| Sale paid/complete | stock_out | transaction in, AR update |
| Rental confirm | reserve | deposit in |
| Rental out | rent_out | — |
| Rental return | rent_return | late fee / balance / refund |
| Sale return | stock_in if restock | refund out |

---

## Out of scope

- Multi-level quotation → order → invoice pipeline  
- Commissions, gifts, seasons, follow-up CRM  
- Delivery logistics / underloading  

---

## Acceptance checks

- Sale of one dress: stock 1→0, status sold, cash increases, P&L income up.
- Rental overlapping same dress blocked.
- Return path restores availability and updates money correctly.
- Cashier can finish a sale in ≤ 5 taps after customer selected (happy path).
