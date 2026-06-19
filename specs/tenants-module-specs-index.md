---
type: index
repo: tenants
updated: 2026-06-18
---

# Tenants Module Specs Index

Master index of all `sanchiconnect-saas-tenants` module specs. This is the **control plane** of SanchiSaaS with the highest blast radius. It uses a **single shared MySQL database with row-per-tenant isolation** — `TenantUsersEntity` has one row per tenant, scoped by `domain`. Every query MUST filter by `domain`.

**Cross-repo invariant:** `TenantUsersEntity` column names ARE the contract. A column rename breaks `sc-saas-backend` Feature enum, `sc-saas-frontend` IFeatures, and `sc-saas-admin` config.php simultaneously. Run `/trace-flag` before any column change.

**TypeORM `synchronize: true` risk:** In dev, adding a column auto-creates it; removing a column auto-drops it. Existing rows get `null` (not `false`) for new boolean columns. Production needs explicit migrations.

> **How to use:** When working on a module, read its spec first — it records owned entities, consumed flags, cross-repo blast radius, known bugs, and security findings surfaced during spec authoring. When adding a flag column or endpoint, update the spec's `owns` / `consumes` frontmatter and `updated` date.

---

## Foundation

| Module | Spec | Description |
|---|---|---|
| core-bootstrap | [module.spec.md](../sanchiconnect-saas-tenants/src/core/module.spec.md) | NestJS bootstrap (helmet, CORS, Swagger), env validation, TypeORM factory, TransformInterceptor, @ClientDomainHeader, GlobalExceptionFilter |

---

## Tenant Contract (Highest blast radius)

| Module | Spec | Description |
|---|---|---|
| tenants | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/tenants/module.spec.md) | TenantUsersEntity — 150+ flag/config columns; the cross-repo contract source of truth; TenantMaintenanceEntity |
| global-verification | [global-verification.spec.md](../sanchiconnect-saas-tenants/src/modules/global/global-verification.spec.md) | `verify_tenant/:hostname` + `tenant-settings/:hostname` — FROZEN contract; frontend and backend bootstrap from these |

---

## Global System

| Module | Spec | Description |
|---|---|---|
| global-system | [global-system.spec.md](../sanchiconnect-saas-tenants/src/modules/global/global-system.spec.md) | Currency rates, system messages, program promotions + tracking, SaaS leads, global settings |
| global-admin | [global-admin.spec.md](../sanchiconnect-saas-tenants/src/modules/global/global-admin.spec.md) | 28 `spa_*` entities — TypeORM definitions for admin panel config tables (PHP writes directly, NestJS owns schema) |

---

## Billing & Subscriptions

| Module | Spec | Description |
|---|---|---|
| organizations | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/organizations/module.spec.md) | Billing org entity; invoices, payments, contacts, contracts — note `organizations-contracts.entityt.ts` typo in filename |
| subscriptions | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/subscriptions/module.spec.md) | Subscription lifecycle; links org to a plan; tenant access implications on expiry |

---

## Ecosystem Directory

| Module | Spec | Description |
|---|---|---|
| ecosystem | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/ecosystem/module.spec.md) | Multi-tenant profile directory — 8 entity types (startups, investors, mentors, corporates, partners, service providers, individuals, program office members); powered by best-effort sync from per-tenant backends |

---

## Hub Features (Cross-tenant sharing)

| Module | Spec | Description |
|---|---|---|
| ip-management | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/ip-management/module.spec.md) | Patents + IP connect requests (IP hub); facility bookings (facility hub); PHP admin writes directly to these tenants-DB tables — schema changes must account for Medoo direct-writes |
| ecosystem-facilities | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/ecosystem-facilities/module.spec.md) | Facility directory (list/detail/types); GET-only public endpoints; domain-scoped; no auth guard; no updatedAt |

---

## Security & architectural findings

| Severity | Area | Finding |
|---|---|---|
| 🔴 Critical | global-verification | `verify_tenant` response exposes plaintext DB credentials (`databasePassword`) and SMTP secrets for every tenant |
| 🔴 Critical | global-verification | No rate limiting on public `verify_tenant` / `tenant-settings` endpoints — tenant enumeration possible |
| 🔴 Critical | tenants | Per-tenant DB credentials stored plaintext in `tenant_users` row — read access to tenants DB = credentials for ALL tenant DBs |
| 🟠 High | tenants | No uniqueness constraint on `domain`, `customDomain`, `apiDomain`, `admin_domain` columns — two tenants can share a domain |
| 🟠 High | tenants | New boolean flag columns default to `null` (not `false`) for existing tenant rows — consumers using strict `=== true` behave differently |
| 🟠 High | ip-management | PHP admin writes patents directly to tenants DB bypassing NestJS validation — malformed data possible |
| 🟠 High | ecosystem-facilities | Facility soft-delete is dual cross-DB write (client DB + tenants DB) with no transaction — partial failure leaves inconsistent state |
| 🟡 Medium | global-verification | Single point of failure — if tenants service is down, ALL tenant backends and frontends fail to bootstrap |
| 🟡 Medium | ecosystem | Best-effort sync means ecosystem directory can show stale profiles with no reconciliation mechanism |
| 🟡 Medium | ip-management | JSON `allowed_domains` columns have no FK constraint — non-existent domains can be added to allowlists |
| 🟡 Medium | organizations | `organizations-contracts.entityt.ts` — typo in filename (double-t) never caught — TypeORM uses glob, file is found but name is wrong |
| 🟡 Medium | tenants | TypeORM `synchronize: true` in dev — column removal auto-drops without migration safety net |

Updated: 2026-06-18
