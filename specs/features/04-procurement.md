# Feature Map — Procurement Module

**Build order:** 4 (after Inventory)
**Depends on:** Platform · Finance-Core · Inventory
**Schema:** `specs/database/procurement`
**Wireframes:** `specs/wireframes/{desktop,mobile}/03-Procurement.excalidraw`
**Decisions:** ADR-009 (landed cost) · ADR-005 (immutability) · ADR-001 (WAC)

---

## Goal

Buy stock and know exactly what it cost. Three things must come out right:

1. **Inventory cost** — the landed cost of a dress, including its share of shipping and customs
2. **Accounts payable** — what is owed to whom, and when it is due
3. **A provable stock-in trail** — every unit that entered the building, traced to its source document

The v1 spec was "PO → receive → pay" with no reports and an undefined cost model. This map makes it comprehensive without turning it into an SCM suite.

---

## Landed cost (the rule that makes valuation deterministic)

Header-level `other_cost` — shipping, customs, freight — is allocated to receipt lines **pro-rata by line value** at receipt time:

```
allocated_i        = header_other_cost × (line_value_i / Σ line_value)
landed_unit_cost_i = unit_cost_i + (allocated_i + line_other_cost_i) / qty_received_i
```

`landed_unit_cost` is stored on `procurement_receipt_items` and is the **only** cost that reaches `inventory_stock_transactions.unit_cost` and the weighted-average recompute. It is shown as its own column on the GRN screen so the owner can see it.

---

## Personas

| Role | Needs |
|------|-------|
| Owner | Approve purchases, see total spend and what is owed |
| Manager | Create POs, receive goods, chase deliveries |
| Accountant / Owner | Pay suppliers, reconcile A/P, run the purchase register |

---

## Feature map

### R1 · Suppliers
| | Feature | Notes |
|---|---|---|
| R1.1 | CRUD in a drawer | name, code, contact person, phone, email, address, city, country |
| R1.2 | Default currency + payment term | drives PO defaults |
| R1.3 | Active / inactive | no hard delete once referenced |
| R1.4 | Search by name / phone / code | |
| R1.5 | Supplier detail tabs | Purchase orders · Receipts · Payments · Items supplied |
| R1.6 | A/P balance on the supplier record | derived from `finance_payables` |
| R1.7 | Supplier price history | what each item has cost over time, per supplier |
| R1.8 | Supplier performance | on-time delivery %, average lead time, return rate |

### R2 · Purchase orders
| | Feature | Notes |
|---|---|---|
| R2.1 | Create PO | supplier, branch, receive warehouse, order date, expected date |
| R2.2 | Currency + snapshotted exchange rate | defaults from the supplier, rate from `platform_exchange_rates` |
| R2.3 | Lines: existing item **or** free-text new item | new lines capture size/colour/category **and both prices** in `item_spec_json` — no `purpose`, no rental period (ADR-013) |
| R2.4 | Per line: qty, unit cost, line other cost, line total | |
| R2.5 | Header: discount, tax, other cost (shipping/customs) | |
| R2.6 | Status: draft → ordered → partial received → received / cancelled / void | |
| R2.7 | **No PO approval** | Place order writes `status='ordered'` immediately. There is no `approved_by` step. |
| R2.8 | Draft POs touch neither stock nor finance | |
| R2.9 | Duplicate PO / reorder from history | |
| R2.10 | Expected-delivery tracking | upcoming and overdue deliveries on the hub |
| R2.11 | Attach supplier invoice / proforma | via `platform_attachments` |
| R2.12 | Print / export PO | |

### R3 · Receiving (GRN)
| | Feature | Notes |
|---|---|---|
| R3.1 | Receive against a PO, full or partial | only `ordered` / `partial_received` POs |
| R3.2 | Line table: ordered · already received · receiving now | |
| R3.3 | **Allocated other cost + landed unit cost columns** | visible, auditable (ADR-009) |
| R3.4 | **Over-receipt blocked** | receive qty is capped at remaining — no approval path |
| R3.5 | **Creates `inventory_items` for free-text lines on post** | generates SKU, writes the id back to the PO line |
| R3.6 | Guided mini-form for new items | pre-filled from `item_spec_json` |
| R3.7 | Choose receive warehouse per receipt | |
| R3.8 | Post → `stock_in` at landed cost + WAC recompute | |
| R3.9 | Post → open / increase `finance_payables` | |
| R3.10 | Post → recompute PO `quantity_received` and status | recomputed from receipts, never incremented |
| R3.11 | Posted GRN is immutable — **void only** | reversing stock + reversing payable |
| R3.12 | Confirmation screen | new SKUs, transaction numbers, updated average costs, payable opened |

### R4 · Supplier payments
| | Feature | Notes |
|---|---|---|
| R4.1 | Pay against a payable or a PO | |
| R4.2 | Allocate one payment across several payables | |
| R4.3 | Choose finance account + payment method | |
| R4.4 | Partial payments | |
| R4.5 | Post → `finance_transactions` OUT (linked via `finance_transaction_id`) | |
| R4.6 | Post → reduce `finance_payables` balance | |
| R4.7 | Void by reversal | |
| R4.8 | Payment receipt print | |

### R5 · Supplier returns (debit notes)
| | Feature | Notes |
|---|---|---|
| R5.1 | Return received goods to the supplier | reason: damaged · wrong item · quality |
| R5.2 | Select from receipt lines | |
| R5.3 | Settlement: reduce payable · refund · credit note | |
| R5.4 | Post → `stock_out` at WAC + A/P effect | |

### R6 · Hub UX
| | Feature |
|---|---|
| R6.1 | KPIs: open POs · awaiting receipt · received this month · total A/P · overdue A/P · spend MTD |
| R6.2 | Quick actions: new PO · receive goods · pay supplier · add supplier |
| R6.3 | Open POs table with received % progress |
| R6.4 | Upcoming and overdue deliveries |
| R6.5 | A/P due this week |

### R7 · Reports
| | Report | Answers |
|---|---|---|
| R7.1 | **Purchase register** | Every PO in a period: supplier, date, items, total, received, paid, balance. Spend by supplier chart. |
| R7.2 | **Stock-in report** | Every stock-in grouped by **source** (purchase receipt · manual entry · sale return · rental return · transfer in) with qty and value, plus a reconciliation line proving `Σ stock-ins = inventory increase`. Deep-links to each source document. |
| R7.3 | **Supplier ledger & aging** | Per supplier: invoices, payments, running balance; A/P buckets current / 1–30 / 31–60 / 60+ |
| R7.4 | **PO status & fulfilment** | Ordered vs received vs outstanding, by PO and by supplier; overdue deliveries |
| R7.5 | **Price history** | Unit cost per item over time and across suppliers — is this supplier getting more expensive? |
| R7.6 | **Landed cost analysis** | How much of stock cost is freight/customs vs goods, per PO and per period |
| R7.7 | **Receiving variance** | Ordered vs received quantity and cost differences |
| R7.8 | **Spend by category** | Which categories consume the purchase budget |

All reports: period · supplier · branch · warehouse filters, CSV export, print view.

> **R7.2 is the report the brief asked for.** It is the join point between procurement and inventory: it proves that what procurement says it received equals what inventory says it gained.

---

## Screens (implementation order)

| # | Screen |
|---|--------|
| 1 | Procurement dashboard |
| 2 | Suppliers list (sheet table) |
| 3 | New / edit supplier drawers |
| 4 | Supplier profile — Overview · POs · Receipts · Payments · Items supplied · Price history |
| 5 | Purchase orders list |
| 6 | New PO drawer (Place order — no approval) |
| 7 | PO detail |
| 8 | Receipts list + receive drawer |
| 9 | New item on GRN drawer |
| 10 | GRN posted confirmation |
| 11 | Pay supplier drawer |
| 12 | Supplier return drawer |
| 13 | Purchase register · Stock-in · Supplier aging |

---

## Business rules

- Draft POs affect neither stock nor finance.
- Only `ordered` or `partial_received` POs can be received.
- `quantity_received` is recomputed from receipts, never incremented in place.
- Receiving more than ordered is blocked — the receive qty cannot exceed remaining. There is no over-receipt approval.
- Header `other_cost` is allocated pro-rata by line value at receipt time (ADR-009).
- `landed_unit_cost` is the only cost that reaches inventory.
- A posted receipt is never edited — only voided, which reverses stock and payable.
- A PO with posted receipts cannot be cancelled; void the receipts first.
- A/P truth is `finance_payables`; the PO's balance column is a display cache.
- Cross-currency POs snapshot the exchange rate; later rate changes never restate history.
- Every posting is idempotent on `idempotency_key`.

---

## Integrations

| Event | Inventory | Finance |
|-------|-----------|---------|
| PO approved (draft → ordered) | — | — |
| Receipt posted | `stock_in` at landed cost + WAC recompute + create new items | open / increase `finance_payables` |
| Receipt voided | reversing `stock_out` | reversing payable |
| Supplier payment posted | — | `finance_transactions` OUT + reduce payable |
| Supplier return posted | `stock_out` at WAC | reduce payable or refund IN |

---

## Out of scope (deliberately)

- Need assessment, RFQ, quotation comparison
- Shipments, ports, incoterms, freight forwarders, landed-cost worksheets beyond the pro-rata rule
- Multi-level approval thresholds and delegation
- Supplier contracts, blanket orders, scheduled releases
- Three-way match against a supplier invoice document (v2)

---

## Acceptance checks

- [ ] Receiving a brand-new dress creates the SKU, sets qty 1, writes the item id back to the PO line.
- [ ] A PO with 1,000 AFN header shipping over lines worth 6,000 and 4,000 allocates 600 / 400; landed unit costs reflect it; the ledger shows the landed cost, not the raw cost.
- [ ] Receiving 3 against an order of 2 is blocked — the qty input cannot exceed remaining.
- [ ] An unpaid receipt appears in the Finance A/P pillar at exactly its payable balance.
- [ ] Paying a supplier reduces cash, reduces A/P, and creates exactly one `finance_transactions` row linked from the payment.
- [ ] Voiding a posted GRN reverses the stock transactions and the payable; both documents remain visible.
- [ ] Partial receipt sets the PO to `partial_received`; completing it sets `received`.
- [ ] A USD PO received when the rate is 70 keeps 70 forever, even after the rate is edited to 72.
- [ ] The stock-in report's total for a period equals the inventory increase from the same period's ledger.
- [ ] Posting the same GRN twice with one `idempotency_key` creates one receipt.
