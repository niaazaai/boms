# Feature Spec — Platform Module

**Status:** ready for implementation  
**Depends on:** nothing (build first)  
**Schema:** `specs/database/platform`  
**Wireframes:** `specs/wireframes/01-auth.md`, `specs/wireframes/02-platform-settings.md`  
**Flows:** `specs/flows/application-flows.md`

---

## Goal

Multi-tenant foundation for bridal shops: register a shop, invite staff, manage branches/warehouses, and shared master data used by every module.

---

## Personas

| Role | Needs |
|------|--------|
| Owner | Register shop, see everything, manage users |
| Manager | Manage branch settings, invite cashiers |
| Cashier / Staff | Login, use assigned branch only |

---

## Features

### P1 — Auth
- [ ] Welcome screen with language switch (EN / Dari / Pashto / Arabic)
- [ ] Login with phone **or** email + password
- [ ] Remember session / secure logout
- [ ] Forgot password (OTP or reset link)
- [ ] Register new shop (tenant + owner) in 3 steps
- [ ] Accept staff invite (set password, join tenant)

### P2 — Tenant & shop profile
- [ ] Shop name, code (SKU prefix), phone, address, logo
- [ ] Business type: sale / rental / both
- [ ] Default currency + language + timezone
- [ ] Tenant settings (`tenant_settings`) for rental defaults, low-stock alerts, nav style

### P3 — Branches & warehouses
- [ ] CRUD branches (one marked main)
- [ ] CRUD warehouses under a branch (one default)
- [ ] User default branch assignment

### P4 — Users & RBAC
- [ ] Invite user by phone/email + role
- [ ] Roles: Owner, Manager, Cashier, Staff (customizable)
- [ ] Permissions by module action (view/create/edit/void)
- [ ] Deactivate user without delete

### P5 — Master data
- [ ] Currencies (+ exchange rate to default)
- [ ] Units (piece, set, box…)
- [ ] Payment methods (cash, card, transfer…)
- [ ] Payment terms (immediate, deposit %, net days)
- [ ] Languages catalog

### P6 — Shell UX
- [ ] Mobile bottom nav: Home · Inventory · Sales · More
- [ ] Home dashboard cards (profit, cash, A/R, A/P, due returns) — data wired later from Finance/Sales
- [ ] RTL layout support
- [ ] Audit log for login + critical settings changes

---

## Screens (implementation order)

1. Welcome / Login / Register / Invite  
2. App shell + Home placeholder  
3. Settings hub  
4. Shop profile  
5. Branches & warehouses  
6. Users & roles  
7. Currencies / Units / Payment methods / Terms  

---

## Business rules

- `tenants.code` is unique and used in SKU prefix.
- Soft-deactivate preferred over hard delete for users/branches.
- Only Owner can change tenant code / delete roles marked `is_system`.
- All tenant-scoped rows carry `tenant_id`.

---

## Out of scope (later)

- SSO / social login  
- Billing / SaaS subscriptions  
- Full website CMS (hero/featured) — separate website module  

---

## Acceptance checks

- New shop registration creates tenant, owner user, main branch, default warehouse, default cash account hooks ready, default currency.
- Invited cashier can login and only sees assigned branch data.
- Master data lists work offline-friendly (simple CRUD).
