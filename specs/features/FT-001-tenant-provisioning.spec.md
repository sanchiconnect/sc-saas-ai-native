---
id: FT-001
title: Tenant Provisioning
repos:
  - sanchiconnect-saas-tenants
  - sc-saas-backend
  - sc-saas-frontend
  - sc-saas-admin
status: draft
contracts:
  api:
    - POST /organizations — create billing organization (sanchiconnect-saas-tenants owns)
    - POST /subscriptions — link organization to a plan (sanchiconnect-saas-tenants owns)
    - POST /tenant-users — create the TenantUsersEntity row (sanchiconnect-saas-tenants owns)
    - GET /public/global/tenant-settings/:hostname — bootstrap endpoint called by sc-saas-backend at startup (sanchiconnect-saas-tenants owns)
    - GET /public/global/verify_tenant/:hostname — startup endpoint called by sc-saas-frontend (sanchiconnect-saas-tenants owns)
  flags:
    - All boolean columns on TenantUsersEntity (default false on new rows; null on existing rows until backfilled)
tenants_modules:
  - sanchiconnect-saas-tenants/src/modules/organizations/module.spec.md
  - sanchiconnect-saas-tenants/src/modules/subscriptions/module.spec.md
  - sanchiconnect-saas-tenants/src/modules/tenants/module.spec.md
  - sanchiconnect-saas-tenants/src/modules/global/module.spec.md
backend_modules:
  - sc-saas-backend/src/core/services/module.spec.md
frontend_specs:
  - sc-saas-frontend/src/app/core/domain/module.spec.md
admin_modules:
  - sc-saas-admin/modules/config/module.spec.md
updated: 2026-06-18
---

# FT-001: Tenant Provisioning

## Summary

Tenant provisioning is the end-to-end onboarding process that brings a new customer onto the SanchiSaaS platform. It spans all four repos: `sanchiconnect-saas-tenants` creates the authoritative records (organization, subscription, and the central `tenant_users` row carrying domain names, credentials, and feature-flag defaults); `sc-saas-backend` is deployed for the tenant and bootstraps itself from the tenants service; `sc-saas-frontend` boots from the same service on first page load; and `sc-saas-admin` connects to the tenants DB for domain resolution and to the per-tenant client DB using credentials stored in the `tenant_users` row. A provisioning failure or misconfiguration at any step leaves the tenant partially operational or completely dark.

## Flow sequence

1. **Organization created** — a `POST /organizations` call (or admin UI action in the tenants service) creates a row in the `organizations` table. This is the billing account that may own multiple tenants.

2. **Subscription created** — a `POST /subscriptions` call links the new organization to a plan, setting billing tier and plan-level entitlements.

3. **`tenant_users` row created** — the central provisioning step. A `POST /tenant-users` (or equivalent internal call) writes the `TenantUsersEntity` row with:
   - `domain` — the primary hostname used as the routing key throughout the platform (must match the `x-client-domain` header in every downstream call).
   - `customDomain`, `apiDomain`, `admin_domain` — the four URL contexts for this tenant.
   - `databaseHost`, `databaseUser`, `databasePassword`, `databasePort`, `databaseName` — per-tenant MySQL credentials consumed by the admin panel (`config.php`) and used for identity/credential-passing to the backend.
   - `apiUrl` — the public URL of this tenant's `sc-saas-backend` deployment; frontend reads this to know where to send business calls.
   - All feature-flag boolean columns default to `false` on a newly-inserted row.

4. **`sc-saas-backend` deployed** — infrastructure step (manual or CI/CD, outside this codebase). On startup, the backend calls `GET /public/global/tenant-settings/:hostname` to load its feature flags into `AppConfigService` and the `saasFeatures` map. This call happens before any user traffic; the backend is non-functional if it cannot reach the tenants service.

5. **Admin panel connects** — `sc-saas-admin/config/config.php` queries the tenants DB directly using Medoo (`$mainDatabase->get('tenant_users', ...)`) to resolve `admin_domain` and retrieve `databaseName`, `databaseHost`, `databaseUser`, `databasePassword` for the per-tenant client DB connection. No REST call is involved; it is a raw SQL lookup.

6. **Frontend loads** — Angular bootstraps, calls `GET /public/global/verify_tenant/:hostname`, receives `apiUrl` and the full feature map, stores in the `brand` NgRx slice, then issues all subsequent business calls to the `apiUrl` retrieved here.

7. **Post-provisioning flag configuration** — once the tenant is live, operator manually enables feature flags by updating the `tenant_users` row (or via a tenants-admin UI). Each flag change requires no redeployment: the backend re-reads `saasFeatures` at runtime (depending on caching strategy); the frontend reads flags from its NgRx store which is seeded at boot.

## Contract ownership

- `sanchiconnect-saas-tenants` owns the `tenant_users` schema, the `organizations` table, the `subscriptions` table, and both public bootstrap endpoints. It is the sole source of truth for domain routing and feature-flag state.
- `sc-saas-backend` owns its bootstrap logic in `sanchiconnect.service.ts`. If the shape of `tenant-settings` changes, `AppConfigService` and `FeatureGuard` break.
- `sc-saas-frontend` owns `brand.model.ts` (`IFeatures`). If field names in `verify_tenant` response change, the NgRx brand slice silently drops values (no TS error at runtime, just `undefined`).
- `sc-saas-admin` owns `config/config.php`. It reads column names from `tenant_users` by string literal — any column rename in `TenantUsersEntity` breaks the PHP query silently (Medoo returns `null`, config falls back to defaults or throws).

## Feature flags

All boolean columns on `TenantUsersEntity` act as feature flags. On initial provisioning, all are `false` for new rows. The operator enables flags post-provisioning. Critical provisioning-time flags:

- `single_session_login_enabled` — affects auth behavior immediately at first user login; must be consciously set.
- `show_ecosystem` — controls whether this tenant's profiles are pushed to the cross-tenant ecosystem directory.
- `is_patent_hub`, `is_facility_hub` — mark this tenant as a resource hub; enabling these without configuring `allowed_domains` leaves the hub open to no one.

## Auth & access

- `POST /organizations`, `POST /subscriptions`, `POST /tenant-users` — protected; require a platform-level operator JWT or internal service token. Not accessible to tenant end-users.
- `GET /public/global/tenant-settings/:hostname` — public, no auth. Called by the backend at startup before any user JWT exists.
- `GET /public/global/verify_tenant/:hostname` — public, no auth. Called by the frontend at boot before the user has logged in.
- `sc-saas-admin config.php` — direct DB query; auth is the MySQL credential stored in `tenant_users`.

## Cross-repo impact

If the `tenant_users` schema changes:
1. `sanchiconnect-saas-tenants` — entity update, TypeORM migration needed for prod (not just `synchronize`).
2. `sc-saas-backend` — `sanchiconnect.service.ts` must be updated if a consumed field is renamed or removed; `AppConfigService` breaks silently if a field disappears.
3. `sc-saas-frontend` — `brand.model.ts` `IFeatures` interface must be updated; field removal causes silent runtime `undefined` in templates.
4. `sc-saas-admin` — `config.php` string-literal column references must be manually updated; Medoo fails silently.

If `apiUrl` is changed for a live tenant:
- The tenants DB row is updated.
- The frontend will pick up the new value on next boot (or hard refresh, since it caches in NgRx).
- The backend deployment at the old URL is now orphaned; the new deployment must be running before changing `apiUrl`.

If the tenants service is unavailable during a new tenant's first boot:
- The backend cannot complete startup — it will crash-loop or serve 503s until tenants service recovers.
- The frontend will fail to load for any end-user on that tenant.

## Known issues

1. **No DB-level uniqueness constraint on domain columns.** `domain`, `customDomain`, `apiDomain`, and `admin_domain` have no `UNIQUE` index in the `tenant_users` table. Two tenants can be accidentally provisioned with the same domain string. The tenants service will return the first matching row, causing one tenant's frontend to silently load another tenant's config (`apiUrl`, feature flags, branding). This is a data-integrity issue with no runtime error or log — it manifests as "wrong tenant" behavior that is hard to diagnose.

2. **New flag columns are `null` on existing rows, not `false`.** TypeORM `synchronize: true` adds the column but does not backfill `DEFAULT false` on existing rows — MySQL sets them to `null`. Any consumer doing a strict `=== true` check correctly treats `null` as disabled. But consumers doing a truthy check (`if (feature)`) or a loose `== true` will behave inconsistently between new tenants (get `false`) and existing tenants (get `null`). This divergence grows with every new flag added and requires an explicit `UPDATE tenant_users SET new_flag = false WHERE new_flag IS NULL` migration that is easy to forget.

3. **Per-tenant DB credentials stored plaintext in `tenant_users`.** `databasePassword` (and SMTP credentials, if stored on the same entity) sit in the shared tenants DB in plaintext. Any operator or internal service with `SELECT` access to the tenants DB has the MySQL password for every tenant's client database. A single credential leak compromises all tenant data. There is no envelope encryption, secret manager reference, or at-rest encryption for these fields.

4. **`apiUrl` is write-once in practice but has no immutability guard.** The field can be updated at any time via the tenants admin. Changing it for a live tenant creates a split-brain window: the old backend is still serving existing sessions; the frontend picks up the new `apiUrl` on next cold start. Users mid-session will continue hitting the old backend until they reload, potentially seeing divergent data if any migration has run on the new deployment.
