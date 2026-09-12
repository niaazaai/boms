# Feature Spec — Platform Module

**Status:** ready for implementation  
**Depends on:** nothing (build first)  
**Schema:** `specs/database/platform`  
**Wireframes:** `specs/wireframes/*/01-Auth.excalidraw`, `specs/wireframes/*/02-Platform-Settings.excalidraw`  
**Flows:** `specs/flows/application-flows.md`

---

## Goal

Multi-tenant foundation for bridal / retail tenants: Super Admin creates tenants, staff authenticate via login, **tenant-bound user creation** with **multi-role** RBAC, branches/warehouses, and shared master data. UI language (English / Dari / Pashto) comes from **tenant settings** and flips the whole app LTR/RTL.

---

## Personas

| Role | Needs |
|------|--------|
| Super Admin | Create/manage tenants (type enum), create users into a chosen tenant, see all tenants |
| Owner | Tenant profile, users/roles (multi-select), branches, master data |
| Manager | Branch settings, create cashiers for their tenant |
| Cashier / Staff | Login, use assigned branch only |

---

## Features

### P1 — Auth (public)
- [ ] **Login-only public entry** — when unauthenticated, only the login page is visible (no public shop self-registration, **no invite accept**)
- [ ] Login with phone **or** email + password
- [ ] **No language switcher on login** — after auth, UI language + direction come from `tenants.default_language_id`
- [ ] Remember session / secure logout
- [ ] Forgot password (OTP or reset link)

### P2 — Users (authorized, tenant-bound)
- [ ] Users datatable: list, **search**, **filter** (status, role, branch, **tenant** for Super Admin)
- [ ] Create / edit user in a **drawer** (LTR → opens from right; RTL → opens from left)
- [ ] **Tenant * field** required on create (Super Admin picks tenant; tenant Owner sees own tenant locked)
- [ ] **Roles multi-select** — one person can have many roles (`user_roles`)
- [ ] Delete or soft-deactivate user
- [ ] Default branch assignment
- [ ] **Invite feature removed** — no send invitation, no invite token, no `invited` status

### P3 — Roles & permissions (authorized)
- [ ] Roles datatable: list, search, filter (system / custom)
- [ ] CRUD custom roles
- [ ] **Permission matrix** by module × action (view / create / edit / void / export / approve)
- [ ] System roles (e.g. Owner) locked from delete
- [ ] Role edit screen shows clear matrix with select-all per module / per action

### P4 — Tenant (Super Admin + tenant profile)
- [ ] **Tenants** full CRUD — **Super Admin only** (search/filter by type, status)
- [ ] Tenant **type enum** (extensible): Shop, Mall, Boutique, Other…
- [ ] Create / edit tenant in **drawer**; fields mirror DB columns
- [ ] **Separate fields** (not combined): Default currency · Default language · Timezone
- [ ] **City select** then **Address textarea** (street / building)
- [ ] Logo, business mode, contact phone/email/website
- [ ] Tenant settings for rental defaults, low-stock alerts, nav style, drawer side = auto

### P5 — Branches & warehouses
- [ ] Branches CRUD + search/filter (city then address pattern)
- [ ] One branch marked main
- [ ] **Warehouses under a branch** (1 branch → many warehouses) with CRUD + search/filter
- [ ] One default warehouse per branch

### P6 — Master data (each: CRUD + search/filter in drawers)
- [ ] Currencies (+ exchange rate to default)
- [ ] Units (piece, set, box…)
- [ ] Payment methods (cash, card, transfer…)
- [ ] Payment terms (immediate, deposit %, net days)
- [ ] **System languages** seeded: English (ltr), Dari / دری (rtl), Pashto / پښتو (rtl)
- [ ] Preferences UI (no separate “pick language per page” — language is tenant default)
- [ ] Audit log UI (login + critical settings changes; no invite events)

### P7 — Shell UX
- [ ] Mobile bottom nav: Home · Inventory · Sales · More
- [ ] Home dashboard cards (profit, cash, A/R, A/P, due returns) — data wired later from Finance/Sales
- [ ] **Whole UI RTL when language is Dari or Pashto; LTR when English**
- [ ] Drawers for all create/edit forms follow page direction

---

## Screens (implementation order)

1. Login / Forgot password  
2. App shell + Home placeholder (direction from tenant language)  
3. Users list + **drawer** create/edit (tenant + multi-role)  
4. Roles list + enhanced permission matrix  
5. Settings hub  
6. Tenants (Super Admin) drawer + Tenant profile  
7. Branches → Warehouses  
8. Currencies / Units / Payment methods / Terms / Preferences / Audit log  

---

## Business rules

- Unauthenticated users only see login (+ forgot-password). **No invite routes.**
- Tenants are created by Super Admin — not via public registration.
- Every user **must** belong to a tenant (`users.tenant_id` not null).
- A user may hold **multiple roles**; effective permissions = union of role permissions.
- `tenants.code` is unique and used in SKU prefix.
- Soft-deactivate preferred over hard delete for users/branches.
- Only Owner / Super Admin can change tenant code / delete roles marked `is_system`.
- All tenant-scoped rows carry `tenant_id`.
- Warehouses always belong to exactly one branch.
- UI locale: `en`→LTR, `fa`→RTL, `ps`→RTL. Changing tenant default language remounts shell direction.

---

## Out of scope (later)

- SSO / social login  
- Billing / SaaS subscriptions  
- Staff invite-by-email tokens  
- Per-user language override  
- Full website CMS (hero/featured) — separate website module  
- Public self-serve tenant signup  

---

## Acceptance checks

- Cold start shows login only; no register-shop CTA; no language pills on login.
- Super Admin creates a tenant with separate Currency, Language, Timezone + City then Address.
- Super Admin creates a user with Tenant + multiple Roles; user appears under that tenant only.
- Owner creates a cashier with roles Cashier + Staff (multi-select); no invite button anywhere.
- Selecting Dari/Pashto on tenant flips whole app to RTL (drawers open from left).
- Roles permission matrix supports view/create/edit/void/export/approve with module select-all.
- Branch detail manages multiple warehouses.
