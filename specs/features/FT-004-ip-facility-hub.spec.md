---
id: FT-004
title: IP & Facility Hub
repos:
  - sanchiconnect-saas-tenants
  - sc-saas-backend
  - sc-saas-frontend
  - sc-saas-admin
status: draft
contracts:
  api:
    - GET /ecosystem/patents — list patents for an IP hub; filtered by requesting tenant domain (sanchiconnect-saas-tenants owns)
    - POST /ecosystem/patents — create a patent record in the tenants DB (sanchiconnect-saas-tenants owns)
    - POST /ecosystem/patents/:id/connect — startup submits an IP connection request to a patent holder (sanchiconnect-saas-tenants owns)
    - GET /ecosystem/facilities — list facilities for a facility hub; filtered by requesting tenant domain (sanchiconnect-saas-tenants owns)
    - POST /ecosystem/facilities — create a facility record in the tenants DB (sanchiconnect-saas-tenants owns)
    - PATCH /ecosystem/facilities/:id — update or soft-delete a facility record (sanchiconnect-saas-tenants owns)
  flags:
    - is_patent_hub (TenantUsersEntity) — marks this tenant as an IP hub; enables patent management UI and cross-tenant patent visibility
    - patent_hub_allowed_domains (TenantUsersEntity, JSON array) — allowlist of tenant domains permitted to access this hub's patents
    - intellectual_property_section (TenantUsersEntity) — gates IP section in sc-saas-admin panel
    - is_facility_hub (TenantUsersEntity) — marks this tenant as a facility hub; enables facility management and cross-tenant booking
    - facility_hub_allowed_domains (TenantUsersEntity, JSON array) — allowlist of tenant domains permitted to access this hub's facilities
    - facility_module_allowed_domains (TenantUsersEntity, JSON array) — secondary domain allowlist for facility module access
    - facility_management (TenantUsersEntity) — gates facility management section in sc-saas-admin panel
tenants_modules:
  - sanchiconnect-saas-tenants/src/modules/ecosystem/module.spec.md
  - sanchiconnect-saas-tenants/src/modules/tenants/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/ecosystem/module.spec.md
frontend_specs:
  - sc-saas-frontend/src/app/modules/ecosystem/module.spec.md
admin_modules:
  - sc-saas-admin/modules/integrations/module.spec.md
  - sc-saas-admin/modules/facilities/module.spec.md
updated: 2026-06-18
---

# FT-004: IP & Facility Hub

## Summary

The IP hub and facility hub features allow one tenant to act as a shared resource provider that other tenants can access. An IP hub tenant manages a portfolio of patents in the tenants-service DB; startups from other allowed tenants can browse those patents and submit connection requests to patent holders. A facility hub tenant manages physical facilities in the same tenants DB; users from allowed tenants can discover and book those facilities. Both hubs are controlled by a set of flags on `TenantUsersEntity` (`is_patent_hub`, `is_facility_hub`) and domain allowlists stored as JSON columns (`patent_hub_allowed_domains`, `facility_hub_allowed_domains`). Critically, the PHP admin panel writes patent and facility records directly to the tenants MySQL database via Medoo — bypassing the NestJS API and all TypeORM validation. This means the tenants service is the schema authority, but the PHP admin is a silent direct-DB writer that does not respect entity-level constraints. Any TypeORM migration on the patents or facilities tables must account for the Medoo queries in `sc-saas-admin/modules/integrations/` and `sc-saas-admin/modules/facilities/`.

## Flow sequence

### IP Hub flow

1. **Tenant marked as IP hub** — operator sets `is_patent_hub = true` on the hub tenant's `TenantUsersEntity` row. Optionally sets `patent_hub_allowed_domains` to the JSON array of tenant `domain` strings that may access the hub.

2. **IP section enabled in admin** — `intellectual_property_section = true` causes the IP management panel to appear in `sc-saas-admin/modules/integrations/intellectual_property/`. The panel is only visible if this flag is set.

3. **Admin writes patent records directly to tenants DB** — the admin panel's IP module calls Medoo directly against `$mainDatabase` (the tenants DB connection in `config.php`), inserting rows into the patents table (`patents.entity.ts`). No NestJS API call is made. The NestJS entity's validation decorators are never invoked. Fields are passed as PHP arrays, with no schema awareness.

4. **Frontend of allowed tenant discovers patents** — a user on a tenant whose `domain` is in the hub's `patent_hub_allowed_domains` navigates to the IP section. The frontend calls the tenants service patent listing endpoint. The tenants service checks that the requesting tenant's domain is in the hub's allowlist before returning results.

5. **Startup submits IP connection request** — the user selects a patent and submits a connection request via `POST /ecosystem/patents/:id/connect`. The tenants service records the request, associating it with the startup's profile and the patent.

6. **Hub admin reviews connections** — the IP hub's admin panel shows incoming connection requests from allowed tenants, allowing the hub operator to respond.

### Facility Hub flow

1. **Tenant marked as facility hub** — operator sets `is_facility_hub = true` and populates `facility_hub_allowed_domains` (and optionally `facility_module_allowed_domains`) on the hub tenant's row.

2. **Facility management enabled in admin** — `facility_management = true` causes the facility panel to appear in `sc-saas-admin/modules/facilities/`. This is checked at render time; the admin panel reads the flag from the tenants DB via `config.php`.

3. **Admin manages facility records with dual writes** — the admin panel's facilities module writes soft-delete and update operations as follows:
   - **Per-tenant client DB write** — updates the facility's status in the per-tenant client database.
   - **Tenants DB write** — updates the same facility's status in `ecosystem_facilities` in the tenants (`$mainDatabase`) database.
   - These two writes are sequential with no wrapping transaction. If the tenants DB write fails, the client DB write has already committed. No rollback occurs.

4. **Frontend of allowed tenant browses facilities** — a user on a tenant listed in `facility_hub_allowed_domains` calls `GET /ecosystem/facilities`. The tenants service filters results to facilities owned by hubs that have listed this user's tenant domain in their allowlist.

5. **User books a facility** — booking logic may involve both the tenants service (to record the booking against the shared facility) and the per-tenant backend (to associate the booking with the user's member profile).

## Contract ownership

- `sanchiconnect-saas-tenants` owns the patents and facilities entity schemas and all REST endpoints over them. It is the authoritative schema source.
- `sc-saas-admin` writes to the same DB tables directly via Medoo without going through the NestJS API. This creates a **dual-writer** situation: the NestJS service and the PHP admin are both writing to the same tables with no coordination layer. TypeORM-level constraints, lifecycle hooks, and validators are bypassed on every admin-originated write.
- `sc-saas-frontend` owns the IP and facilities UI sections. It consumes the tenants service REST endpoints and reads `is_patent_hub`, `is_facility_hub`, and associated flags from the `brand.features` NgRx slice (seeded at boot by `verify_tenant`).
- `sc-saas-backend` owns any booking or connection-request logic that touches the per-tenant client DB, but defers to the tenants service for the shared resource records themselves.

## Feature flags

- `is_patent_hub` — the primary gate for IP hub participation. When `false` or `null`, no patent management UI appears and the tenant's patents are not discoverable by others. Flipping this `true` on an existing tenant does not automatically populate `patent_hub_allowed_domains`; the allowlist must be set separately or the hub is accessible to no other tenants.
- `patent_hub_allowed_domains` — a JSON array column. Stored as a string in MySQL; parsed by the NestJS entity. The tenants service reads this array on every patent listing request to enforce access. PHP admin writes to the patents table bypass this allowlist check — the NestJS guard is never invoked.
- `intellectual_property_section` — independent of `is_patent_hub`; controls admin UI visibility only. A tenant can have the IP admin section visible without being a hub (e.g., to manage their own IP before enabling cross-tenant access).
- `is_facility_hub`, `facility_hub_allowed_domains`, `facility_module_allowed_domains` — mirror the IP hub pattern. `facility_module_allowed_domains` is a second allowlist for a more granular sub-module of facility access; its precise semantics depend on which facility sub-features it gates.
- `facility_management` — admin UI gate only; does not affect whether the tenant's facilities appear in cross-tenant listings.

## Auth & access

- Patent and facility listing endpoints (`GET /ecosystem/patents`, `GET /ecosystem/facilities`) — require the requesting tenant's domain to be in the hub's allowlist. The tenants service enforces this check. If the check relies solely on a query parameter or header (rather than a JWT claim), a caller can spoof their domain.
- Connection request endpoint (`POST /ecosystem/patents/:id/connect`) — must be authenticated with the user's JWT so the request is associated with a verified startup profile, not an anonymous submission.
- Admin panel direct DB writes — authenticated only by the MySQL credential in `config.php`. Any admin user with access to the IP or facility panels can write arbitrary records to the tenants DB, with no per-operation audit trail beyond MySQL's binary log.
- Admin panel session — the standard PHP session mechanism; no additional authorization check before the Medoo write is executed.

## Cross-repo impact

If `patents.entity.ts` column names or types change:
1. The NestJS migration updates the tenants DB schema.
2. `sc-saas-admin/modules/integrations/intellectual_property/` Medoo queries use the old column names — inserts reference columns that may no longer exist, causing MySQL errors that surface as silent failures in the PHP admin (no exception bubbles to the user if the Medoo call is not checked).
3. `sc-saas-frontend` patent listing templates break if API response field names change.
4. `sc-saas-backend` ecosystem push payload must be updated if it maps to patents fields.

If `facility_hub_allowed_domains` or `patent_hub_allowed_domains` JSON format changes (e.g., from a flat array to an object):
- The NestJS entity parser must be updated.
- Any PHP admin code that reads or writes these JSON columns via Medoo must be updated separately — it has its own JSON encode/decode logic.
- Existing DB values with the old format break the NestJS parser for all affected tenant rows until migrated.

If `is_patent_hub` or `is_facility_hub` is toggled off for a live hub:
- Active ecosystem records (patents, facilities) remain in the tenants DB — they are not deleted or hidden automatically.
- Other tenants' frontend users may still see the hub's resources until those records are explicitly removed or the allowlist is cleared.

## Known issues

1. **`patent_hub_allowed_domains` and `facility_hub_allowed_domains` are JSON arrays with no foreign-key enforcement.** Any string value can be inserted into these arrays — including domain names that do not exist in `tenant_users`. An operator can add a non-existent domain to the allowlist, which has no visible effect but creates a confusing state where the allowlist contains phantom entries. Conversely, if a tenant is deprovisioned (its `tenant_users` row deleted), its domain is not automatically removed from any hub's allowlist; the allowlist entry becomes a dangling reference. There is no periodic cleanup or validation job.

2. **Facility soft-delete is a dual cross-DB write with no transaction, creating a split-brain risk.** The admin panel's facility soft-delete operation writes to the per-tenant client DB first, then writes to `$mainDatabase` (tenants DB). These are two separate MySQL connections with no distributed transaction. If the second write fails (tenants DB timeout, connection drop, maintenance window), the client DB marks the facility inactive while the tenants DB ecosystem listing continues to show it as active. Users on other tenants can still discover and attempt to book a facility that the hub operator has already soft-deleted. There is no reconciliation job to detect or heal this divergence.

3. **Admin direct-writes to patents bypass all NestJS validation, enabling malformed data insertion.** The PHP admin inserts patent records via Medoo with raw PHP arrays. NestJS class-validator decorators, entity transformers, and any service-layer business rules (e.g., required field checks, format validation, ownership verification) are never executed. A PHP admin user can insert a patent row with a `null` required field, an invalid enum value, or a foreign-key value that does not exist in the NestJS-managed parent table. TypeORM does not protect against this at read time — it will attempt to hydrate the malformed row and may throw or return corrupted data to the frontend.

4. **No audit trail for hub access or connection requests at the tenants-DB level.** Patent connection requests and facility bookings are recorded in the tenants DB, but there is no per-operation log linking a specific admin write, a specific connection request, or a specific booking to an authenticated user identity with a timestamp. If a patent record is modified or deleted via the PHP admin, there is no record of who performed the action or when. This makes debugging data corruption and responding to access disputes difficult.
