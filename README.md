# BOMS
Bridal Omnichannel Management System

Mobile-first system for bridal shops that **rent** clothes and **sell** bride dresses — simple inventory, easy sales/rentals, light procurement, and a clear daily profit view.

## Specs (current focus)

| Area | Path |
|------|------|
| Database schemas | [`specs/database/`](./specs/database/) |
| Wireframes | [`specs/wireframes/`](./specs/wireframes/) |
| App flows | [`specs/flows/application-flows.md`](./specs/flows/application-flows.md) |
| Feature specs (agent order) | [`specs/features/`](./specs/features/) |

Stack, language, and infrastructure: **deferred** — discuss next.

## Modules

1. **Platform** — tenant, auth, branches, users, master data  
2. **Inventory** — dresses/accessories, stock ledger, reservations  
3. **Sales** — sale + rental + return  
4. **Procurement** — suppliers, PO, receive, pay (minimal)  
5. **Finance** — 5 pillars → end-of-day profit/loss  

## Finance pillars

1. Cash & Banks  
2. Income  
3. Expenses  
4. Accounts Payable (we owe)  
5. Accounts Receivable (they owe us)  
