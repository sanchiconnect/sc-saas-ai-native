---
id: FT-003
title: Ecosystem Directory Sync
repos:
  - sanchiconnect-saas-tenants
  - sc-saas-backend
  - sc-saas-frontend
  - sc-saas-admin
status: draft
contracts:
  api:
    - POST /ecosystem/startups — push a startup profile snapshot to the cross-tenant directory (sanchiconnect-saas-tenants owns)
    - PUT /ecosystem/startups/:id — update an existing ecosystem profile snapshot (sanchiconnect-saas-tenants owns)
    - GET /ecosystem/search — search across all tenants' ecosystem profiles; supports ?type=startups&q= (sanchiconnect-saas-tenants owns)
    - POST /ecosystem/users — push a user/member profile to the ecosystem (sanchiconnect-saas-tenants owns)
    - GET /ecosystem/startups/:id — retrieve a single ecosystem startup profile (sanchiconnect-saas-tenants owns)
  flags:
    - show_ecosystem (TenantUsersEntity) — gates whether this tenant participates in ecosystem sync at all
    - elastic_search (TenantUsersEntity) — controls whether ecosystem search uses Elasticsearch or MySQL full-text
    - search_type (TenantUsersEntity, enum) — selects search backend variant
tenants_modules:
  - sanchiconnect-saas-tenants/src/modules/ecosystem/module.spec.md
  - sanchiconnect-saas-tenants/src/modules/global/module.spec.md
backend_modules:
  - sc-saas-backend/src/modules/ecosystem/module.spec.md
frontend_specs:
  - sc-saas-frontend/src/app/modules/search/module.spec.md
  - sc-saas-frontend/src/app/modules/ecosystem/module.spec.md
admin_modules:
  - sc-saas-admin/modules/stakeholder-crud/module.spec.md
updated: 2026-06-18
---

# FT-003: Ecosystem Directory Sync

## Summary

The ecosystem directory is a cross-tenant profile index stored in the `sanchiconnect-saas-tenants` database. When a startup registers or updates its profile on any tenant's `sc-saas-backend`, the backend pushes a snapshot of that profile to the tenants service ecosystem tables. This allows frontend users on any tenant to search and discover startups that originally registered on a different tenant. The sync is intentionally best-effort: if the push to the tenants service fails, the per-tenant backend operation (registration, profile update) is not rolled back. The ecosystem directory may therefore be stale — it represents a best-effort cross-tenant cache, not a transactionally consistent replica. The `show_ecosystem` flag in `TenantUsersEntity` controls whether a given tenant participates in this sync flow at all. Admin users on any tenant can browse the cross-tenant ecosystem via the admin panel's stakeholder-crud module, which calls the tenants service search API.

## Flow sequence

1. **User creates or updates startup profile on tenant** — a user submits a profile on `sc-saas-frontend`, which calls a `POST /startups` or `PUT /startups/:id` endpoint on `sc-saas-backend`.

2. **Backend validates and persists to per-tenant DB** — the backend writes the canonical startup record to the per-tenant client MySQL database. This is the primary write; it succeeds or fails independently of the ecosystem sync.

3. **Backend checks `show_ecosystem` flag** — `sc-saas-backend/src/modules/ecosystem/` reads `saasFeatures.get(Feature.ShowEcosystem)`. If the flag is `false` or `null`, the sync is skipped entirely. No ecosystem push occurs for this tenant.

4. **Backend pushes snapshot to tenants service (best-effort)** — if the flag is enabled, the backend calls `POST /ecosystem/startups` (or `PUT /ecosystem/startups/:id` for updates) on the tenants service, passing a profile snapshot tagged with the originating `domain`. This call is wrapped in `try/catch`; any error is logged and swallowed. The primary operation's HTTP response is already sent or committed before this call completes.

5. **Tenants service stores the snapshot** — `sanchiconnect-saas-tenants` receives the push, validates it, and writes to `startups.entity.ts` (or an equivalent ecosystem entity) in the shared tenants DB. The row is tagged with the source `domain`.

6. **Frontend searches the ecosystem** — A user on any tenant's `sc-saas-frontend` uses the search module (`modules/search/`), which calls `GET /ecosystem/search?type=startups&q=<query>` on the tenants service (not on their own backend). Results are tagged with the source `domain` so the UI can indicate which platform each startup comes from.

7. **Frontend renders cross-tenant results** — The search results include profiles from all participating tenants. Each result card displays the source domain alongside profile data, enabling cross-tenant discovery while maintaining tenant identity.

8. **Admin browses cross-tenant ecosystem** — `sc-saas-admin/modules/stakeholder-crud/` calls the tenants service search API (or reads directly from the tenants DB via Medoo) to display a cross-tenant view of ecosystem profiles. Admin users can see all tenants' startups in one list.

9. **Profile update sync** — when a startup updates their profile on the per-tenant backend, the same best-effort push fires again (step 4). The tenants service must upsert on a stable profile identifier that is consistent between the per-tenant DB and the ecosystem row.

## Contract ownership

- `sanchiconnect-saas-tenants` owns the ecosystem entity schema (`startups.entity.ts`, `ecosystem-facilities.entity.ts`) and all ecosystem REST endpoints. The field names in the push payload must match what the tenants service entity accepts.
- `sc-saas-backend` owns the push logic in `src/modules/ecosystem/`. It is responsible for mapping per-tenant profile fields to the ecosystem snapshot shape. If the tenants service endpoint changes its accepted payload shape, the backend push silently fails (best-effort, errors are swallowed) and the ecosystem goes stale with no alert.
- `sc-saas-frontend` owns the search module and result rendering. It consumes `GET /ecosystem/search` directly from the tenants service. If the search response shape changes, the frontend template bindings break silently.
- `sc-saas-admin` owns `modules/stakeholder-crud/`. Its ecosystem queries must be kept in sync with ecosystem entity field names, either via API calls or direct-DB Medoo queries.

## Feature flags

- `show_ecosystem` — the primary gate. If `false` or `null` for a tenant, that tenant's profiles are never pushed and never appear in cross-tenant search results. Enabling this flag for an existing tenant does not retroactively sync historical profiles — only future creates/updates trigger a push.
- `elastic_search` — when `true`, ecosystem search routes through Elasticsearch rather than MySQL `LIKE` queries. The frontend search module and the tenants service search handler must both be configured for this mode. A mismatch (flag `true` but Elasticsearch not provisioned) causes search to fail entirely for that tenant's users.
- `search_type` — a string/enum field that selects among search backend variants. The tenants service search handler branches on this value. An unknown `search_type` value should fall back to MySQL but may return empty results or throw depending on implementation.

## Auth & access

- `POST /ecosystem/startups`, `PUT /ecosystem/startups/:id` — called server-to-server from `sc-saas-backend` to the tenants service. These should require a service-level API key or inter-service JWT. If they are public, any caller can inject arbitrary ecosystem profiles tagged with any `domain`.
- `GET /ecosystem/search` — called by `sc-saas-frontend` (user-facing); authentication requirements depend on whether cross-tenant discovery is intended to be public or member-only. If public, anonymous users can enumerate all registered startups across all tenants. If member-only, the frontend must attach the user's JWT.
- `GET /ecosystem/startups/:id` — called by frontend for detail view; same auth considerations as search.
- Admin panel access to ecosystem data — authenticated by the admin panel's own session; the Medoo queries run under the admin's DB credentials.

## Cross-repo impact

If `startups.entity.ts` fields are renamed in the tenants service:
1. `sc-saas-backend` ecosystem push payload field names become mismatched — the push silently fails or the tenants service discards unrecognized fields, causing stale/partial ecosystem records.
2. `sc-saas-frontend` search result rendering breaks — template bindings expecting the old field name return `undefined`, causing blank profile cards.
3. `sc-saas-admin` stakeholder-crud queries break — Medoo string-literal column references return `null`.

If `show_ecosystem` is toggled off for a tenant mid-operation:
- Profiles already in the ecosystem remain there indefinitely (no cleanup sweep).
- New updates from that tenant stop syncing immediately (flag is read per-request in the backend).
- The ecosystem directory accumulates stale "zombie" profiles from tenants that have since opted out.

If the tenants service ecosystem endpoint is down:
- Backend push fails silently (best-effort catch) — no impact to per-tenant operations.
- Frontend search against the tenants service fails hard — users see search errors or empty results.
- The two failure modes are asymmetric: writes degrade silently, reads fail visibly.

## Known issues

1. **Best-effort sync with no reconciliation mechanism creates permanent divergence.** A transient network error, a tenants service deployment, or a payload validation failure causes the sync to fail silently. The per-tenant backend has no retry queue, no dead-letter store, and no reconciliation job. Once a profile update is missed, the ecosystem entry remains stale indefinitely. There is no operator tooling to force a re-sync of a specific profile or a full tenant re-sync. Over time, the ecosystem directory increasingly diverges from per-tenant reality, especially for active tenants with frequent profile updates.

2. **Ecosystem search is public with no tenant-level privacy controls on profile visibility.** All profiles pushed to the ecosystem are discoverable by any user performing a search, regardless of which tenant they belong to. A startup registered on a private or invite-only tenant is fully visible to users on any other tenant (and potentially to unauthenticated users if the search endpoint is public). The `show_ecosystem` flag controls sync participation at the tenant level but does not provide per-profile privacy. There is no mechanism for an individual startup to opt out of cross-tenant discovery while remaining on their home tenant.

3. **No stable cross-system identifier links ecosystem rows back to per-tenant source records.** If the upsert key between the per-tenant profile ID and the ecosystem row is not enforced (e.g., relies on a mutable field like name or email), a profile update can create a duplicate ecosystem row instead of updating the existing one. The ecosystem directory accumulates duplicates that only a manual DB cleanup can resolve.

4. **`elastic_search` flag mismatch causes total search failure for affected tenants.** If the flag is `true` in `TenantUsersEntity` but the Elasticsearch cluster is not provisioned or is unreachable, the tenants service search handler fails for all queries from that tenant's frontend users. There is no automatic fallback to MySQL search. The flag itself has no validation against actual infrastructure state — it can be toggled by any operator without verifying that Elasticsearch is available.
