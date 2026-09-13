# Application flows — end-to-end

Step-by-step charts for bridal shop daily work. **v2 — corrected** against
[`specs/review/01-spec-review.md`](../review/01-spec-review.md) and the decisions in
[`02-decisions.md`](../review/02-decisions.md).

---

## 1. Module dependency — build order

```mermaid
flowchart LR
  P[1 · Platform] --> FC[2 · Finance-Core]
  FC --> I[3 · Inventory]
  I --> R[4 · Procurement]
  R --> S[5 · Sales]
  S --> FR[6 · Finance-Reporting]
  I --> S
```

Finance-Core comes **second**, not last: `sales_order_payments` and
`procurement_supplier_payments` hold foreign keys into `finance_accounts`, so the
v1 order was circular (defect A4 · ADR-007).

---

## 2. Master navigation

```mermaid
flowchart TB
  LOGIN[Public: login only] -->|authenticated| HOME[Home dashboard]
  LOGIN --> FORGOT[Forgot password → OTP → reset]
  HOME --> INV[Inventory]
  HOME --> SAL[Sales]
  HOME --> FIN[Finance]
  HOME --> MORE[More]
  MORE --> PRC[Procurement]
  MORE --> REP[Reports]
  MORE --> SET[Settings]
  SET --> TEN[Tenants · Super Admin]
  SET --> USERS[Users · Roles · Permission matrix]
  SET --> BR[Branches → Warehouses]
  SET --> PREF[Preferences · rental uses · buffer · cutoff]
```

No public sign-up. No invite route. Language and direction come from
`tenants.default_language_id` after authentication.

---

## 3. Daily owner loop

```mermaid
flowchart TD
  A[Open Home] --> B[Five pillars + net profit]
  B --> C{Returns due today?}
  C -->|Yes| D[Open rental → Mark returned]
  D --> D2[Condition · late fee · settle deposit]
  C -->|No| E{Customer at the counter?}
  E -->|Buying| F[New sale]
  E -->|Renting| G[New rental]
  E -->|No| H{Stock needed?}
  H -->|Yes| I[Receive PO or manual entry]
  H -->|No| J[Record expenses]
  F --> K[Payment → stock_out → sale COGS]
  G --> L[Deposit → reserve dates]
  L --> M[Event day: mark out → later mark returned]
  M --> N[Rental completes → amortisation COGS]
  D2 --> N
  K & N & I & J --> B
```

---

## 4. Locale and direction

```mermaid
flowchart LR
  T[tenants.default_language_id] --> L{code}
  L -->|en| LTR[Whole UI LTR · sidebar left · drawers from right]
  L -->|fa · Dari| RTL[Whole UI RTL · sidebar right · drawers from left]
  L -->|ps · Pashto| RTL
```

Numbers, SKUs, currency amounts and dates stay LTR inside RTL text.

---

## 5. User creation — tenant-bound, multi-role

```mermaid
sequenceDiagram
  actor Admin as Owner / Super Admin
  participant UI as Users screen
  participant DB
  Admin->>UI: Open Users → Create (drawer)
  Note over UI: Drawer opens right in LTR, left in RTL
  Admin->>UI: Tenant * (Super Admin picks; Owner locked to own)
  Admin->>UI: Name, email or phone, password, default branch
  Admin->>UI: Roles multi-select (1..N)
  UI->>DB: users row + one user_roles row per role
  DB-->>UI: unique (user_id, role_id, coalesce(branch_id,0))
  UI-->>Admin: User ACTIVE immediately — no invitation sent
```

---

## 6. Procurement → inventory → payable

```mermaid
sequenceDiagram
  actor Owner
  participant PRC as Procurement
  participant INV as Inventory
  participant FIN as Finance
  Owner->>PRC: Create PO (supplier, lines, header other cost)
  Owner->>PRC: Approve → status ordered (approved_by recorded)
  Owner->>PRC: Receive goods (GRN)
  Note over PRC: Allocate header other_cost pro-rata by line value<br/>landed_unit_cost = unit_cost + allocated / qty
  PRC->>INV: create items for free-text lines (SKU from sequences)
  PRC->>INV: stock_in at LANDED cost
  INV->>INV: recompute weighted average cost
  PRC->>FIN: open finance_payables
  Owner->>PRC: Pay supplier
  PRC->>FIN: one finance_transactions OUT + reduce payable
```

Voiding a posted GRN writes reversing stock rows and a reversing payable — it is
never an in-place edit (ADR-005).

---

## 7. Sale happy path

```mermaid
sequenceDiagram
  actor Staff
  participant SAL as Sales
  participant INV as Inventory
  participant FIN as Finance
  Staff->>SAL: New sale (customer, or walk-in)
  Staff->>SAL: Add items — blocked if available_qty = 0
  Staff->>SAL: Take payment
  SAL->>INV: stock_out at weighted average cost
  SAL->>FIN: finance_transactions IN
  SAL->>FIN: finance_cogs_entries (kind = sale_cogs)
  alt balance remains
    SAL->>FIN: open finance_receivables
  end
  SAL-->>Staff: Completed · receipt
```

---

## 8. Rental lifecycle — deposits, dates, cost

```mermaid
sequenceDiagram
  actor Staff
  participant SAL as Sales
  participant INV as Inventory
  participant FIN as Finance
  Staff->>SAL: New rental (customer required) + event dates
  SAL->>INV: check availability incl. cleaning buffer
  INV-->>SAL: DB exclusion constraint rejects any overlap
  SAL->>INV: inventory_reservations row (NOT a ledger row)
  Staff->>SAL: Take deposit
  SAL->>FIN: cash IN + finance_customer_deposits (LIABILITY, not income)
  Note over SAL: Event day
  Staff->>SAL: Mark out
  SAL->>INV: rent_out — on_hand down, on_rent up, OWNED UNCHANGED
  Note over SAL: After the event
  Staff->>SAL: Mark returned + condition
  SAL->>INV: rent_return + block dates for rental_buffer_days
  SAL->>SAL: late_days = max(0, actual_return − rental_end)
  Staff->>SAL: Settle deposit — apply / forfeit / refund
  SAL->>FIN: forfeited → income · refund → cash OUT
  SAL->>FIN: finance_cogs_entries (kind = rental_amortisation)
  SAL-->>Staff: Rental completed
```

**Rental amortisation** = `acquisition_cost ÷ expected_rental_uses`, accumulated in
`inventory_items.amortised_cost_to_date` and capped at acquisition cost. Once the
dress has paid for itself, further rentals carry zero COGS (ADR-002).

---

## 9. Rental gone wrong — damage or loss

```mermaid
flowchart TD
  A[Mark returned] --> B{Condition}
  B -->|good| C[Available after buffer]
  B -->|needs cleaning| D[Available after buffer]
  B -->|damaged| E[lifecycle_status = repairing]
  B -->|lost| F[Rental claim — loss]
  E --> G[Rental claim — damage]
  G --> H[Assess charge]
  F --> H
  H --> I[Apply deposit first]
  I --> J{Charge > deposit?}
  J -->|Yes| K[Remainder → finance_receivables]
  J -->|No| L[Refund the unused deposit]
  F --> M[inventory_disposals → dispose at WAC]
  I --> N[Forfeited portion → INCOME]
```

---

## 10. Sale return → refund → restock

```mermaid
sequenceDiagram
  actor Staff
  participant SAL as Sales
  participant INV as Inventory
  participant FIN as Finance
  Staff->>SAL: Open completed sale → Return
  Staff->>SAL: Select lines, qty, reason, restock?
  Staff->>SAL: Post return
  SAL->>FIN: refund OUT
  SAL->>FIN: reverse the original sale_cogs entry
  alt restock = true and condition = good
    SAL->>INV: stock_in at the original cost
  end
  SAL-->>Staff: Return posted
```

A **sale return** (refund + restock of sold goods) is a different document from a
**rental return** (an order lifecycle transition). v1 called both "return" (defect C7).

---

## 11. Inventory movements — the corrected ledger

```mermaid
flowchart TB
  subgraph LEDGER[inventory_stock_transactions · 8 types]
    direction TB
    subgraph IN[Increase]
      PO[Procurement receipt] --> TIN[stock_in]
      MSE[Manual entry] --> TIN
      SRET[Sale return restock] --> TIN
      TRI[Transfer in] --> TTI[transfer_in]
    end
    subgraph OUT[Decrease]
      SO[Sale complete] --> TOUT[stock_out]
      DSP[Dispose] --> TDSP[dispose]
      PRET[Supplier return] --> TOUT
      TRO[Transfer out] --> TTO[transfer_out]
    end
    subgraph RENT[Rental movement]
      RO[Mark out] --> TRO2[rent_out]
      RR[Mark returned] --> TRR[rent_return]
    end
    ADJ[Adjustment] --> TADJ["adjustment ±"]
  end

  RSV[Reservation] -.->|NOT a stock movement| RES[(inventory_reservations)]

  TIN & TOUT & TTI & TTO & TDSP & TADJ & TRO2 & TRR --> BAL[(inventory_stock_balances)]
  RES --> BAL
  BAL --> Q1[on_hand = Σ ledger]
  BAL --> Q2[on_rent = rent_out − rent_return]
  BAL --> Q3[owned = on_hand + on_rent]
  BAL --> Q4[reserved = Σ active reservations]
  BAL --> Q5[available = on_hand − reserved]
  Q3 --> WORTH[Stock worth = owned × avg_cost]
```

Two corrections are visible here:

- **`reserve` and `release` no longer exist as ledger types.** Reservations are their
  own table; v1 made reserving a dress *reduce stock* and then subtracted it again
  for availability (defect B2).
- **Valuation uses `owned`, not `on_hand`.** A gown at a wedding is still an asset;
  v1's total stock worth collapsed every busy weekend (defect B3).

---

## 12. Weighted average cost

```mermaid
flowchart LR
  A[Stock in at landed cost] --> B["new_avg = (on_hand × avg + qty_in × landed) / (on_hand + qty_in)"]
  B --> C[(inventory_stock_balances.avg_cost)]
  C --> D[Stock out snapshots avg onto the transaction]
  D --> E[COGS uses the snapshot]
  C --> F[Stock worth = owned × avg_cost]
```

---

## 13. End-of-day profit

```mermaid
flowchart TD
  A[Sale revenue] --> REV[Revenue]
  B[Rental fees] --> REV
  C[Late fees] --> REV
  D[Forfeited deposits] --> REV
  E[Other income] --> REV
  F[Sale COGS — WAC of dresses sold] --> COGS[COGS]
  G[Rental amortisation — cost per use] --> COGS
  REV --> GP[Gross profit = Revenue − COGS]
  COGS --> GP
  H[Operating expenses] --> NP[Net profit = Gross − Expenses]
  GP --> NP
  NP --> DASH[Home + Finance dashboard]
  I[Deposits still held] -.->|liability, NOT revenue| DASH
```

All filtering is on `business_date`, derived from `tenants.timezone` and
`tenant_settings.day_cutoff_time` — so a sale rung up at 00:30 lands on the correct
trading day (ADR-011).

---

## 14. Correction — void by reversal

```mermaid
flowchart LR
  A[Posted document] --> B{Wrong?}
  B -->|Yes| C[Void with a reason]
  C --> D[Insert a REVERSING document]
  D --> E[reverses_id → original]
  C --> F[Original status = void]
  F --> G[Both stay visible forever]
  D --> H[Reverses stock, cash, A/R, A/P and COGS]
  B -->|No| I[Leave it alone]
```

Nothing posted is ever edited, and nothing is ever deleted — in any module (ADR-005).
