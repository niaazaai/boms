# Wireframes index

Clean mobile-first wireframes for BOMS (bridal rental + sale).

Reference Excalidraw files under `specs/reference_to_remove_later/wireframes/` were from a full SCM ERP. These replace them with a simpler bridal-shop IA.

| # | File | Module |
|---|------|--------|
| 1 | [01-auth.md](./01-auth.md) | Login, register, invite |
| 2 | [02-platform-settings.md](./02-platform-settings.md) | Home shell, tenant, settings |
| 3 | [03-inventory.md](./03-inventory.md) | Items, stock, adjust, transfer |
| 4 | [04-sales.md](./04-sales.md) | Sale, rental, return, customers |
| 5 | [05-procurement.md](./05-procurement.md) | Suppliers, PO, receive, pay |
| 6 | [06-finance.md](./06-finance.md) | 5 pillars + P&L |

End-to-end charts: [`../flows/application-flows.md`](../flows/application-flows.md)

## UX principles (all screens)

- Mobile first, large taps, bottom navigation
- Phone-number search for customers (not email-first)
- Rental calendar conflict check before confirm
- Owner home = profit + cash + due returns in one glance
- RTL-ready (Dari / Pashto / Arabic)
- Avoid multi-step approvals unless voiding money/stock
