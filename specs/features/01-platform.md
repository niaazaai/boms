# Feature Spec — Platform Module

**Status:** ready for implementation  
**Depends on:** nothing (build first)  
**Schema:** `specs/database/platform`  
**Wireframes:** `specs/wireframes/*/01-Auth.excalidraw`, `specs/wireframes/*/02-Platform-Settings.excalidraw`  
**Flows:** `specs/flows/application-flows.md`

---

## Goal

Multi-tenant foundation for bridal / retail tenants: Super Admin creates tenants, staff authenticate via login, invite flows, RBAC, branches/warehouses, and shared master data used by every module.

---

## Personas

| Role | Needs |
|------|--------|
| Super Admin | Create/manage tenants (type enum), see all tenants |
| Owner | Tenant profile, users/roles, branches, master data |
| Manager | Branch settings, invite cashiers |
| Cashier / Staff | Login, use assigned branch only |

---

## Features

### P1 — Auth (public)
- [ ] **Login-only public entry** — when unauthenticated, only the login page is visible (no public shop self-registration)
- [ ] Login with phone **or** email + password
- [ ] Language switch on login (EN / Dari / Pashto / Arabic)
- [ ] Remember session / secure logout
- [ ] Forgot password (OTP or reset link)
- [ ] Accept staff invite (token link → set name/password, join tenant)

### P2 — Users (authorized)
- [ ] Users datatable: list, **search**, **filter** (status, role, branch)
- [ ] Create / edit user
- [ ] Delete or soft-deactivate user
- [ ] **Send invitation** (phone/email + role + branch)
- [ ] **Change role** action on user
- [ ] Default branch assignment

### P3 — Roles & permissions (authorized)
- [ ] Roles datatable: list, search, filter (system / custom)
- [ ] CRUD custom roles
- [ ] Permission matrix by module × action (view / create / edit / void)
- [ ] System roles (e.g. Owner) locked from delete

### P4 — Tenant (Super Admin + tenant profile)
- [ ] **Tenants** full CRUD — **Super Admin only** (search/filter by type, status)
- [ ] Tenant **type enum** (extensible): Shop, Mall, Boutique, Other…
- [ ] **Tenant profile** (renamed from shop profile): name, code, type, logo, business mode
- [ ] Address + contact info on tenant
- [ ] Default currency + language + timezone
- [ ] Tenant settings for rental defaults, low-stock alerts, nav style

### P5 — Branches & warehouses
- [ ] Branches CRUD + search/filter
- [ ] One branch marked main
- [ ] **Warehouses under a branch** (1 branch → many warehouses) with CRUD + search/filter
- [ ] One default warehouse per branch

### P6 — Master data (each: CRUD + search/filter)
- [ ] Currencies (+ exchange rate to default)
- [ ] Units (piece, set, box…)
- [ ] Payment methods (cash, card, transfer…)
- [ ] Payment terms (immediate, deposit %, net days)
- [ ] Languages catalog
- [ ] Preferences UI
- [ ] Audit log UI (login + critical settings changes)

### P7 — Shell UX
- [ ] Mobile bottom nav: Home · Inventory · Sales · More
- [ ] Home dashboard cards (profit, cash, A/R, A/P, due returns) — data wired later from Finance/Sales
- [ ] RTL layout support

---

## Screens (implementation order)

1. Login / Forgot / Accept invite  
2. App shell + Home placeholder  
3. Users list + form + invite + change role  
4. Roles list + permission matrix  
5. Settings hub  
6. Tenants (Super Admin) + Tenant profile  
7. Branches → Warehouses  
8. Currencies / Units / Payment methods / Terms / Preferences / Languages / Audit log  

---

## Business rules

- Unauthenticated users only see login (plus forgot-password and invite-accept routes).
- Tenants are created by Super Admin — not via public registration.
- `tenants.code` is unique and used in SKU prefix.
- Soft-deactivate preferred over hard delete for users/branches.
- Only Owner / Super Admin can change tenant code / delete roles marked `is_system`.
- All tenant-scoped rows carry `tenant_id`.
- Warehouses always belong to exactly one branch.

---

## Out of scope (later)

- SSO / social login  
- Billing / SaaS subscriptions  
- Full website CMS (hero/featured) — separate website module  
- Public self-serve tenant signup  

---

## Acceptance checks

- Cold start shows login only; no register-shop CTA.
- Super Admin can create a tenant with type Shop/Mall and full address/contact.
- Invited cashier can login and only sees assigned branch data.
- Users list supports search/filter and invite / change-role / edit / delete.
- Roles support permission matrix CRUD.
- Branch detail manages multiple warehouses.
- Master data lists work offline-friendly (simple CRUD + search/filter).
