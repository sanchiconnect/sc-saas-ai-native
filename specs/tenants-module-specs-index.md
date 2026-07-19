---
type: index
repo: tenants
updated: 2026-07-19
---

# Tenants Module Specs Index

Master index of all `sanchiconnect-saas-tenants` module specs. This is the **control plane** of SanchiSaaS with the highest blast radius. It uses a **single shared MySQL database with row-per-tenant isolation** — `TenantUsersEntity` has one row per tenant, scoped by `domain`. Every query MUST filter by `domain`.

**Cross-repo invariant:** `TenantUsersEntity` column names ARE the contract. A column rename breaks `sc-saas-backend` Feature enum, `sc-saas-frontend` IFeatures, and `sc-saas-admin` config.php simultaneously. Run `/trace-flag` before any column change.

**TypeORM `synchronize: true` risk:** In dev, adding a column auto-creates it; removing a column auto-drops it. Existing rows get `null` (not `false`) for new boolean columns. Production needs explicit migrations.

> **How to use:** When working on a module, read its spec first — it records owned entities, consumed flags, cross-repo blast radius, known bugs, and security findings surfaced during spec authoring. When adding a flag column or endpoint, update the spec's `owns` / `consumes` frontmatter and `updated` date.

**Coverage:** all 8 module directories under `src/modules/` have a `module.spec.md` (verified 2026-07-19) — `ai-credits`, `ecosystem`, `ecosystem-facilities`, `global`, `ip-management`, `organizations`, `subscriptions`, `tenants`. Zero gaps.

---

> ## 🔴 Read this first — `verify_tenant` / `tenant-settings` are completely unauthenticated
>
> `global/module.spec.md` (added 2026-07-19) re-verified `global.controller.ts` line by line and confirmed: **all five routes on `GlobalController` — including `verify_tenant/:hostname` and `tenant-settings/:hostname` — have no `@UseGuards(...)` of any kind**, there is no global `APP_GUARD` in `app.module.ts`/`main.ts`, and even the response-shaping `TransformInterceptor` is commented out. This is not a doc gap being closed after the fact — it is the current, live behavior of production code.
>
> The practical consequence: **anyone who can reach this endpoint and knows (or guesses) a tenant's hostname gets that tenant's plaintext secrets back in the response body** — `azure_client_secret`, `analyzer_api_token`, `email_password_ses`, and per-tenant DB credentials (`databasePassword`) among ~160 other config fields. No auth, no rate limiting, no enumeration protection. This is arguably the single most consequential finding across every spec in this repo, because the endpoint is *supposed* to be public (every tenant frontend/backend bootstraps from it before any JWT exists) — the bug isn't "this got exposed," it's "sensitive fields were put on the one endpoint in the whole platform that's designed to have zero auth."
>
> See the full finding table below for related items (no rate limiting, no domain uniqueness constraint, plaintext DB credentials at rest).

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
| global | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/global/module.spec.md) | Entry point / 2026-07-19 re-verification of `GlobalModule`, the pre-auth bootstrap surface every repo calls before a JWT exists; confirms **all 5 routes (incl. verify_tenant/tenant-settings) are unauthenticated** by direct code read, not inference — see callout above. Points to the 3 sub-specs below for field-level detail. |
| global-verification | [global-verification.spec.md](../sanchiconnect-saas-tenants/src/modules/global/global-verification.spec.md) | `verify_tenant/:hostname` + `tenant-settings/:hostname` — FROZEN contract; frontend and backend bootstrap from these |

---

## Global System

| Module | Spec | Description |
|---|---|---|
| global-system | [global-system.spec.md](../sanchiconnect-saas-tenants/src/modules/global/global-system.spec.md) | Currency rates, system messages, program promotions + tracking, SaaS leads, global settings |
| global-admin | [global-admin.spec.md](../sanchiconnect-saas-tenants/src/modules/global/global-admin.spec.md) | 22 `spa_*` entities — TypeORM definitions for admin panel config tables (PHP writes directly, NestJS owns schema) |

---

## Billing & Subscriptions

| Module | Spec | Description |
|---|---|---|
| organizations | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/organizations/module.spec.md) | Billing org entity; invoices, payments, contacts, contracts — note `organizations-contracts.entityt.ts` typo in filename |
| subscriptions | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/subscriptions/module.spec.md) | Subscription lifecycle; links org to a plan; tenant access implications on expiry |
| ai-credits | [module.spec.md](../sanchiconnect-saas-tenants/src/modules/ai-credits/module.spec.md) | Prepaid AI-credit wallet/ledger schema; implements only the **purchase path** (catalog, Easebuzz order + webhook, GST invoicing) — one of three independent writers in the cross-repo AI-Credits system (see `specs/features/FT-005-ai-credits-system.spec.md`); `InternalApiKeyGuard` fails open if its env var is unset |

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
| 🔴 Critical | global | **All 5 `GlobalController` routes — including `verify_tenant` and `tenant-settings` — have zero auth guards**, confirmed by direct 2026-07-19 code read (no `@UseGuards`, no global `APP_GUARD`, `TransformInterceptor` commented out). Combined with the finding below, this means plaintext per-tenant secrets are fetchable by hostname with no authentication of any kind. |
| 🔴 Critical | global-verification | `verify_tenant` / `tenant-settings` responses expose plaintext secrets for the requested tenant — `azure_client_secret`, `analyzer_api_token`, `email_password_ses`, and DB credentials (`databasePassword`) — among ~160 other config fields |
| 🔴 Critical | global-verification | No rate limiting on public `verify_tenant` / `tenant-settings` endpoints — tenant enumeration possible |
| 🔴 Critical | tenants | Per-tenant DB credentials stored plaintext in `tenant_users` row — read access to tenants DB = credentials for ALL tenant DBs |
| 🟠 High | tenants | No uniqueness constraint on `domain`, `customDomain`, `apiDomain`, `admin_domain` columns — two tenants can share a domain |
| 🟠 High | tenants | New boolean flag columns default to `null` (not `false`) for existing tenant rows — consumers using strict `=== true` behave differently |
| 🟠 High | ip-management | PHP admin writes patents directly to tenants DB bypassing NestJS validation — malformed data possible |
| 🟠 High | ecosystem-facilities | Facility soft-delete is dual cross-DB write (client DB + tenants DB) with no transaction — partial failure leaves inconsistent state |
| 🟡 Medium | global-verification | Single point of failure — if tenants service is down, ALL tenant backends and frontends fail to bootstrap |
| 🟡 Medium | global | Dead imports in `global.controller.ts` (`ClientDomainHeaderDto`, `UserUUIDHeaderDto`, etc.) suggest a header-based auth scheme was planned but never wired in — worth confirming intent before assuming the unauth state is permanent |
| 🟡 Medium | ai-credits | `InternalApiKeyGuard` fails open (`return true`) when `AI_CREDITS_INTERNAL_API_KEY` is unset — opt-in enforcement by design (documented in the guard's own comment), but a misconfiguration silently disables auth on `/purchase` and `/invoices*`; the Easebuzz webhook routes are separately protected by an unconditional HMAC-SHA512 check that does not depend on this env var |
| 🟡 Medium | ecosystem | Best-effort sync means ecosystem directory can show stale profiles with no reconciliation mechanism |
| 🟡 Medium | ip-management | JSON `allowed_domains` columns have no FK constraint — non-existent domains can be added to allowlists |
| 🟡 Medium | organizations | `organizations-contracts.entityt.ts` — typo in filename (double-t) never caught — TypeORM uses glob, file is found but name is wrong |
| 🟡 Medium | tenants | TypeORM `synchronize: true` in dev — column removal auto-drops without migration safety net |

Updated: 2026-07-19
