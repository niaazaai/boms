# Application flows — end-to-end

Step-by-step charts for bridal shop daily work.

---

## 1. Master navigation

```mermaid
flowchart TB
  LOGIN[Public: Login only] -->|authenticated| HOME[Home Dashboard]
  LOGIN --> FORGOT[Forgot password]
  HOME --> INV[Inventory]
  HOME --> SAL[Sales]
  HOME --> MORE[More]
  MORE --> FIN[Finance]
  MORE --> PRC[Procurement]
  MORE --> SET[Settings / Platform]
  SET --> TEN[Tenants Super Admin]
  SET --> USERS[Users / Roles RBAC]
  SET --> BR[Branches → Warehouses]
  SET --> LANG[Tenant language EN/Dari/Pashto → LTR/RTL]
```

---

## 2. Daily owner loop

```mermaid
flowchart TD
  A[Open Home] --> B[Check 5 pillars / profit]
  B --> C{Due returns?}
  C -->|Yes| D[Open rental → Mark returned]
  C -->|No| E{Customer walk-in?}
  E -->|Buy| F[New Sale]
  E -->|Rent| G[New Rental]
  E -->|No| H{Need stock?}
  H -->|Yes| I[PO receive or Manual stock entry]
  H -->|No| J[Record expenses if any]
  F --> K[Payment → stock_out]
  G --> L[Deposit → reserve]
  L --> M[Later: Out → Return]
  D --> N[Collect balance / refund]
  K & N & J --> B
```

---

## 3. User creation (tenant-bound, multi-role)

```mermaid
sequenceDiagram
  actor Admin as Owner / Super Admin
  participant Users
  participant DB
  Admin->>Users: Open Users → Create (drawer)
  Note over Users: Drawer side = right if LTR, left if RTL
  Admin->>Users: Select Tenant * (required)
  Admin->>Users: Name, phone/email, password, branch
  Admin->>Users: Roles multi-select (1..N)
  Users->>DB: users + user_roles rows
  Users-->>Admin: User active — no invite
```

---

## 4. Locale / direction

```mermaid
flowchart LR
  T[Tenant default_language_id] --> L{code}
  L -->|en| LTR[Whole UI LTR · drawers from right]
  L -->|fa Dari| RTL[Whole UI RTL · drawers from left]
  L -->|ps Pashto| RTL
```

---

## 5. Sale happy path

```mermaid
sequenceDiagram
  actor Staff
  participant Sales
  participant Inventory
  participant Finance
  Staff->>Sales: New Sale + customer
  Staff->>Sales: Add available items
  Staff->>Sales: Take payment
  Sales->>Inventory: stock_out + status sold
  Sales->>Finance: transaction IN + clear A/R
  Sales-->>Staff: Completed receipt
```

---

## 6. Rental happy path

```mermaid
sequenceDiagram
  actor Staff
  participant Sales
  participant Inventory
  participant Finance
  Staff->>Sales: New Rental + dates
  Sales->>Inventory: check conflict + reserve
  Staff->>Sales: Take deposit
  Sales->>Finance: transaction IN (deposit)
  Note over Sales: Event day
  Staff->>Sales: Mark rented out
  Sales->>Inventory: rent_out + status rented
  Note over Sales: After event
  Staff->>Sales: Mark returned + condition
  Sales->>Inventory: rent_return + available
  Staff->>Sales: Collect balance / late fee / refund
  Sales->>Finance: settle remaining
  Sales-->>Staff: Rental completed
```

---

## 7. Sales return → restock

```mermaid
sequenceDiagram
  actor Staff
  participant Sales
  participant Inventory
  participant Finance
  Staff->>Sales: Open completed sale → Return
  Staff->>Sales: Select lines + reason + restock?
  Staff->>Sales: Post return
  Sales->>Finance: refund OUT if needed
  alt restock = true
    Sales->>Inventory: stock_in (reference sales_return)
  end
  Sales-->>Staff: Return posted
```

---

## 8. Inventory movements

```mermaid
flowchart TB
  subgraph IN[Stock In]
    PO[Procurement receive] --> TXN_IN[stock_in txn]
    MSE[Manual stock entry] --> TXN_IN
    RET[Sales return restock] --> TXN_IN
    RR[Rent return] --> TXN_RR[rent_return txn]
  end
  subgraph OUT[Stock Out]
    SO[Sales order complete] --> TXN_OUT[stock_out txn]
    DSP[Dispose] --> TXN_DSP[dispose txn]
    RO[Rent out] --> TXN_RO[rent_out txn]
  end
  subgraph HOLD[Hold / Move]
    RSV[Reserve] --> TXN_RSV[reserve txn]
    REL[Release] --> TXN_REL[release txn]
    TR[Transfer] --> TXN_TR[transfer_out + transfer_in]
    ADJ[Adjustment] --> TXN_ADJ[adjustment +/-]
  end
  TXN_IN & TXN_OUT & TXN_DSP & TXN_RSV & TXN_REL & TXN_TR & TXN_ADJ & TXN_RR & TXN_RO --> LEDGER[Stock ledger]
  LEDGER --> BAL[On hand / Reserved / Available]
  BAL --> WORTH[Stock worth = qty × unit_cost]
```

---

## 9. Procurement → stock → finance

```mermaid
sequenceDiagram
  actor Owner
  participant PRC as Procurement
  participant INV as Inventory
  participant FIN as Finance
  Owner->>PRC: Create PO + lines
  Owner->>PRC: Mark ordered
  Owner->>PRC: Receive goods (basic)
  PRC->>INV: stock_in + cost update
  PRC->>FIN: open A/P payable
  Owner->>PRC: Pay supplier
  PRC->>FIN: cash OUT + close A/P
```

---

## 10. Manual stock entry

```mermaid
sequenceDiagram
  actor Staff
  participant INV as Inventory
  Staff->>INV: New manual entry drawer
  Staff->>INV: Warehouse + lines (item, qty, unit cost)
  Staff->>INV: Post entry
  INV->>INV: stock_in txns (reference_type=manual_entry)
  INV-->>Staff: Ledger + balances updated
```

---

## 11. Adjust / Dispose

```mermaid
sequenceDiagram
  actor Staff
  participant INV as Inventory
  alt Adjustment
    Staff->>INV: Draft adjust (reason + counted qty)
    Staff->>INV: Post
    INV->>INV: adjustment txn
  else Dispose
    Staff->>INV: Draft dispose (reason + qty)
    Staff->>INV: Post
    INV->>INV: dispose txn + maybe status disposed
  end
```

---

## 12. End-of-day profit check

```mermaid
flowchart LR
  A[Sales payments today] --> I[Income]
  B[Rental fees / late fees] --> I
  C[Other income] --> I
  D[Posted expenses] --> E[Expenses]
  F[COGS of sold items] --> G[COGS]
  I --> P[Net = Income − Expenses − COGS]
  E --> P
  G --> P
  P --> H[Home / Finance dashboard]
```

---

## 13. Module dependency (build order for agents)

```mermaid
flowchart LR
  P[1 Platform] --> I[2 Inventory]
  I --> S[3 Sales]
  I --> R[4 Procurement]
  S --> F[5 Finance]
  R --> F
```

Build/implement in this order so FKs and flows stay correct.
