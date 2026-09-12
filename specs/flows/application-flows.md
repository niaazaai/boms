# Application flows — end-to-end

Step-by-step charts for bridal shop daily work.

---

## 1. Master navigation

```mermaid
flowchart TB
  LOGIN[Public: Login only] -->|authenticated| HOME[Home Dashboard]
  LOGIN --> FORGOT[Forgot password]
  INVITE[Accept invite link] --> LOGIN
  HOME --> INV[Inventory]
  HOME --> SAL[Sales]
  HOME --> MORE[More]
  MORE --> FIN[Finance]
  MORE --> PRC[Procurement]
  MORE --> SET[Settings / Platform]
  SET --> TEN[Tenants Super Admin]
  SET --> USERS[Users / Roles RBAC]
  SET --> BR[Branches → Warehouses]
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
  H -->|Yes| I[Simple PO → Receive]
  H -->|No| J[Record expenses if any]
  F --> K[Payment → stock_out]
  G --> L[Deposit → reserve]
  L --> M[Later: Out → Return]
  D --> N[Collect balance / refund]
  K & N & J --> B
```

---

## 3. Sale happy path

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

## 4. Rental happy path

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

## 5. Procurement → stock → finance

```mermaid
sequenceDiagram
  actor Owner
  participant PRC as Procurement
  participant INV as Inventory
  participant FIN as Finance
  Owner->>PRC: Create PO + lines
  Owner->>PRC: Mark ordered
  Owner->>PRC: Receive goods
  PRC->>INV: stock_in + cost update
  PRC->>FIN: open A/P payable
  Owner->>PRC: Pay supplier
  PRC->>FIN: cash OUT + close A/P
```

---

## 6. End-of-day profit check

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

## 7. Module dependency (build order for agents)

```mermaid
flowchart LR
  P[1 Platform] --> I[2 Inventory]
  I --> S[3 Sales]
  I --> R[4 Procurement]
  S --> F[5 Finance]
  R --> F
```

Build/implement in this order so FKs and flows stay correct.
