# Feature Map — Platform Module

**Build order:** 1 (build first — everything depends on it)
**Depends on:** nothing
**Schema:** `specs/database/platform`
**Wireframes:** `specs/wireframes/{desktop,mobile}/01-Platform.excalidraw`
**Decisions:** ADR-006 (multi-tenancy) · ADR-011 (business day) · ADR-012 (idempotency)

---

## Goal

A multi-tenant foundation: Super Admin creates tenants, staff sign in, users are created **directly inside a tenant** with **multi-role** RBAC, and the whole UI flips LTR/RTL from one tenant setting.

Plus the infrastructure every other module needs on day one: document numbering, exchange-rate history, attachments, notifications, and an audit trail that records **posts and voids**, not just logins.

---

## Personas

| Role | Needs |
|------|-------|
| Super Admin | Create and manage tenants, create users into any tenant |
| Owner | Tenant profile, users and roles, branches, master data, preferences |
| Manager | Branch settings, create cashiers |
| Cashier / Staff | Sign in, work in their assigned branch only |

---

## Feature map

### P1 · Auth (public surface)
| | Feature | Notes |
|---|---|---|
| P1.1 | **Login is the only public page** | plus forgot-password. No sign-up, **no invite route** |
| P1.2 | Sign in with **email or phone** + password | both **globally unique** — login has no tenant context (corrected flaw A8) |
| P1.3 | **No language switcher on login** | locale comes from the tenant after auth |
| P1.4 | Forgot password → OTP → reset | single-use, time-limited code |
| P1.5 | Secure session, remember me, logout everywhere | |
| P1.6 | Rate limiting + lockout on repeated failures | |
| P1.7 | Login, logout and failures written to `audit_logs` | |

### P2 · Users
| | Feature | Notes |
|---|---|---|
| P2.1 | Users table: search + filter by status, role, branch, tenant | tenant filter is Super Admin only |
| P2.2 | Create / edit in a **drawer** | right in LTR, left in RTL |
| P2.3 | **Tenant \* required on create** | Super Admin picks; an Owner sees their own, locked |
| P2.4 | **Roles multi-select** | one person, many roles; effective permissions = union |
| P2.5 | Default branch assignment | |
| P2.6 | Soft deactivate | no hard delete — `created_by` FKs must survive |
| P2.7 | **No invite feature anywhere** | no token, no `invited` status, no resend |
| P2.8 | Password reset by an admin | |
| P2.9 | Last-login column | |

### P3 · Roles & permissions
| | Feature | Notes |
|---|---|---|
| P3.1 | Roles table: search, filter system vs custom | |
| P3.2 | **System roles are COPIED to the tenant on creation** | never shared or edited globally (corrected flaw A7) |
| P3.3 | `copied_from_role_id` records the origin | shown as a badge |
| P3.4 | CRUD custom roles | |
| P3.5 | **Permission matrix: module × action** | select-all per row and per column |
| P3.6 | Actions: **view · create · edit · post · void · export · approve** | `post` and `void` are new — they move stock and money |
| P3.7 | Branch-scoped role grants | `user_roles.branch_id` |
| P3.8 | Permission changes are audited | before/after captured |

**Permission seed list** — 6 modules × up to 7 actions ≈ 48 codes:

```
platform.tenants.{view,create,edit,export}
platform.users.{view,create,edit,export}
platform.roles.{view,create,edit,export}
platform.branches.{view,create,edit}
platform.masterdata.{view,create,edit}
platform.settings.{view,edit}
platform.audit.{view,export}

inventory.items.{view,create,edit,export}
inventory.ledger.{view,export}
inventory.entries.{view,create,post,void}
inventory.adjustments.{view,create,post,void}
inventory.disposals.{view,create,post,void}
inventory.transfers.{view,create,post,void}
inventory.reservations.{view,create,edit,void}
inventory.reports.{view,export}

sales.customers.{view,create,edit,export}
sales.orders.{view,create,edit,post,void,export}
sales.payments.{view,create,void}
sales.returns.{view,create,post,void}
sales.claims.{view,create,post,void}
sales.reports.{view,export}

procurement.suppliers.{view,create,edit,export}
procurement.orders.{view,create,edit,approve,void,export}
procurement.receipts.{view,create,post,void}
procurement.payments.{view,create,void}
procurement.returns.{view,create,post,void}
procurement.reports.{view,export}

finance.accounts.{view,create,edit}
finance.transactions.{view,void,export}
finance.expenses.{view,create,post,void,export}
finance.income.{view,create,post,void}
finance.payables.{view,post,export}
finance.receivables.{view,post,export}
finance.deposits.{view,export}
finance.reports.{view,export}

reports.dashboard.{view,export}
```

### P4 · Tenants (Super Admin)
| | Feature | Notes |
|---|---|---|
| P4.1 | Full CRUD — **Super Admin only** | search, filter by type and status |
| P4.2 | Type enum: shop · mall · boutique · other | extensible |
| P4.3 | Create / edit in a **drawer** | |
| P4.4 | **Three separate fields**: default currency · default language · timezone | never combined |
| P4.5 | **City select, then Address textarea** | |
| P4.6 | Logo, phone, email, website | |
| P4.7 | `tenants.code` is globally unique and becomes the SKU prefix | ADF → ADF26-0042 |
| P4.8 | Creating a tenant seeds: role copies, finance categories, currencies, units, payment methods, a main branch with a default warehouse | |
| P4.9 | Suspend a tenant | blocks login, preserves data |

### P5 · Branches & warehouses
| | Feature |
|---|---|
| P5.1 | Branches CRUD + search/filter, city then address |
| P5.2 | Exactly one main branch |
| P5.3 | **Warehouses belong to exactly one branch** (1 → many) |
| P5.4 | One default warehouse per branch |
| P5.5 | Branch detail lists its warehouses with item counts and stock worth |
| P5.6 | Branch switcher in the sidebar re-scopes every list |

### P6 · Master data
Each is the same shape — list + drawer + search/filter:

| | Feature | Notes |
|---|---|---|
| P6.1 | Currencies | default flag; **rates live in `platform_exchange_rates`** |
| P6.2 | **Exchange rate history** | documents snapshot their rate; editing today's rate never restates history |
| P6.3 | Units | pcs, set, box |
| P6.4 | Payment methods | cash, card, transfer, wallet |
| P6.5 | Payment terms | immediate, deposit %, net days |
| P6.6 | Languages (seeded, system) | English · دری Dari · پښتو Pashto — direction is derived from the language, never shown as a label |

### P7 · Preferences (`tenant_settings`)
| | Group | Settings |
|---|---|---|
| P7.1 | Inventory policy | business type, SKU prefix, costing method, allow negative stock, low-stock alerts |
| P7.2 | Rental policy | default days, deposit %, **cleaning buffer days**, **expected rental uses**, rental cost method |
| P7.3 | Accounting | **business day cutoff time** |
| P7.4 | UI | date format, mobile nav style, form drawer side |

> `expected_rental_uses` and `rental_buffer_days` are load-bearing: the first drives rental COGS (ADR-002), the second extends the double-booking guard (ADR-010).

### P8 · Infrastructure (used by every module)
| | Feature | Notes |
|---|---|---|
| P8.1 | **`platform_sequences`** | atomic document numbering; no `MAX()+1` races (ADR-006) |
| P8.2 | Numbers unique **per tenant**, never globally | corrected flaw A1 |
| P8.3 | **`platform_attachments`** | polymorphic, many files per document |
| P8.4 | **`platform_notifications`** | low stock, due returns, overdue A/R, A/P due, reconcile mismatch |
| P8.5 | **Idempotency keys** on every posting endpoint | ADR-012 |
| P8.6 | **`business_date`** derived from tenant timezone + cutoff | ADR-011 |
| P8.7 | Audit log UI with filters | module, action, user, date |
| P8.8 | **Mandatory audit events**: every post, every void (with reason), permission changes, setting changes, price changes, login/logout | corrected flaw F4 |

### P9 · Shell UX
| | Feature |
|---|---|
| P9.1 | Sidebar: icon + label, grouped MAIN / OPERATIONS / MONEY / INSIGHT / SYSTEM |
| P9.2 | Active pill, count badges, contextual sub-navigation |
| P9.3 | Collapsed 72px icon rail, state persisted per user |
| P9.4 | Branch switcher + user block pinned to the bottom |
| P9.5 | Mobile bottom tabs: Home · Inventory · Sales · Finance · More |
| P9.6 | Home dashboard mirroring the Finance pillars + today's schedule |
| P9.7 | **Whole UI RTL for Dari and Pashto**; drawers open from the left |
| P9.8 | Permission-hidden nav items (hidden, not disabled) |
| P9.9 | Empty / loading / error / offline states on every screen |

---

## Screens (implementation order)

| # | Screen |
|---|--------|
| 1 | Login |
| 2 | Forgot password → OTP → reset |
| 3 | App shell (sidebar + tabs) + Home dashboard |
| 4 | Users list |
| 5 | Create / edit user drawer |
| 6 | Roles list |
| 7 | Permission matrix |
| 8 | Settings hub |
| 9 | Tenants list (Super Admin) |
| 10 | Tenant drawer |
| 11 | Preferences |
| 12 | Branches → warehouses |
| 13 | Master data (currencies, units, methods, terms) |
| 14 | Audit log |
| 15 | RTL reference (Dari) |

---

## Business rules

- Unauthenticated users see only login and forgot-password. **No invite routes exist.**
- Tenants are created by Super Admin; there is no public registration.
- Every user belongs to exactly one tenant (`users.tenant_id` not null).
- `users.email` and `users.phone` are **globally unique** — they are the login identifier.
- A user may hold multiple roles; effective permissions are the union.
- System role templates are read-only outside seeding; tenants get copies.
- `unique (user_id, role_id, coalesce(branch_id, 0))` — nullable branch must not defeat the constraint.
- Branch scoping: if every role row for a user carries a `branch_id`, all lists filter to that set; a row with `branch_id IS NULL` is tenant-wide.
- `tenants.code` is unique globally; every other number is unique per tenant.
- Soft-deactivate over hard delete for users, branches and warehouses.
- Warehouses belong to exactly one branch.
- Locale: `en` → LTR, `fa` → RTL, `ps` → RTL. Changing it remounts the shell direction.

---

## Out of scope

- SSO / social login
- Billing and SaaS subscription management
- Staff invite-by-email tokens
- Per-user language override
- Website / storefront CMS (deferred module)
- Public self-serve tenant signup

---

## Acceptance checks

- [ ] Cold start shows login only — no register CTA, no language pills, no invite route.
- [ ] Two users in different tenants cannot share an email; login resolves deterministically.
- [ ] Super Admin creates a tenant with Currency, Language and Timezone as three fields, and City before Address.
- [ ] Creating a tenant seeds its own copies of the system roles; editing one tenant's Manager role leaves every other tenant untouched.
- [ ] Super Admin creates a user with a Tenant and two Roles; the user appears only under that tenant, active immediately, with no invitation sent.
- [ ] Granting the same role twice to one user is rejected by the unique constraint.
- [ ] Switching the tenant language to Dari flips the whole app RTL and drawers open from the left.
- [ ] The permission matrix exposes view/create/edit/post/void/export/approve with select-all per module and per action.
- [ ] A branch-scoped cashier sees only their branch's orders, stock and money.
- [ ] Branch detail manages multiple warehouses with exactly one default.
- [ ] Two concurrent requests for a new order number receive different numbers.
- [ ] The audit log shows a `post` row for a receipt and a `void` row with its reason.
- [ ] A sale posted at 00:30 with a 02:00 cutoff carries the previous day's `business_date`.
