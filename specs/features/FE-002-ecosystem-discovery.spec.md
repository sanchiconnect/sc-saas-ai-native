---
id: FE-002
title: Ecosystem Discovery
type: feature
status: draft
repos:
  - frontend
  - backend
contracts:
  api:
    - GET api/v1/public/search/startups
    - GET api/v1/public/search/startups/profile/:name
    - GET api/v1/public/search/investors
    - GET api/v1/public/search/investors/profile/:name
    - GET api/v1/public/search/corporates
    - GET api/v1/public/search/corporates/profile/:name
    - GET api/v1/public/search/mentors
    - GET api/v1/public/search/mentors/profile/:name
    - GET api/v1/public/search/service-providers
    - GET api/v1/public/search/service-providers/profile/:name
    - GET api/v1/public/search/partners
    - GET api/v1/public/search/partners/profile/:name
    - GET api/v1/public/search/program-office-members
    - GET api/v1/public/search/program-office-members/profile/:name
    - GET api/v1/public/search/individuals
    - GET api/v1/public/search/individuals/profile/:name
    - GET api/v1/public/search/live-deals
    - GET api/v1/elastic-search/search-startups/:query
    - GET api/v1/elastic-search/search-investors/:query
    - GET api/v1/elastic-search/search-corporates/:query
    - GET api/v1/elastic-search/search-mentors/:query
    - GET api/v1/elastic-search/search-service-providers/:query
    - GET api/v1/elastic-search/search-partners/:query
    - GET api/v1/elastic-search/search-individuals/:query
    - GET api/v1/elastic-search/search-global/:query
    - GET api/v1/elastic-search/search-news/:query
    - GET api/v1/ecosystem/startups/search
    - GET api/v1/ecosystem/startups/:uuid/info
    - GET api/v1/ecosystem/investors/search
    - GET api/v1/ecosystem/investors/:uuid/info
    - GET api/v1/ecosystem/corporates/search
    - GET api/v1/ecosystem/corporates/:uuid/info
    - GET api/v1/ecosystem/mentors/search
    - GET api/v1/ecosystem/mentors/:uuid/info
    - GET api/v1/ecosystem/service_providers/search
    - GET api/v1/ecosystem/service_providers/:uuid/info
    - GET api/v1/ecosystem/program_office_members/search
    - GET api/v1/ecosystem/program_office_members/:uuid/info
    - GET api/v1/ecosystem/partners/search
    - GET api/v1/ecosystem/partners/:uuid/info
    - GET api/v1/ecosystem/individuals/search
    - GET api/v1/ecosystem/individuals/:uuid/info
    - GET api/v1/ip-management/patents
    - GET api/v1/ip-management/patents/:patentUUID/info
    - POST api/v1/ip-management/patents/:patentUUID/connect
  flags:
    - elastic_search
    - ecosystem_enabled
    - startups
    - investors
    - corporates
    - mentors
    - service_providers
    - partners
    - individuals
    - program_offices
    - intellectual_property_section
    - ip_management
  events: []
tenant_scoped: true
depends_on: []
updated: 2026-06-17
---

# FE-002 — Ecosystem Discovery

## Summary
Provides the discovery layer for all stakeholder types: paginated full-text search and typeahead across nine profile types (startups, investors, corporates, mentors, service-providers, partners, program-office-members, individuals, live-deals), a global typeahead page, and an IP/patent search and connection-request surface. Two independent search paths co-exist — local text search via the `public/search/*` backend module and Elasticsearch via `elastic-search/*` — with the active path toggled per tenant by the `elastic_search` flag and `search_type` setting. Ecosystem profile lookups are proxied through the backend to the central cockpit directory.

## Frontend entry points
Angular modules:
- `sc-saas-frontend/src/app/modules/search/` — `SearchModule` and `GlobalSearchPageModule`
- `sc-saas-frontend/src/app/modules/search/` also contains `IpSearchModule` and `IpRequestModule`

Routes (all lazy-loaded):

| Path | Module | Feature flag |
|---|---|---|
| `/search/startups` | `SearchModule` | `startups` |
| `/search/investors` | `SearchModule` | `investors` |
| `/search/corporates` | `SearchModule` | `corporates` |
| `/search/mentors` | `SearchModule` | `mentors` |
| `/search/service-providers` | `SearchModule` | `service_providers` |
| `/search/partners` | `SearchModule` | `partners` |
| `/search/individuals` | `SearchModule` | `individuals` |
| `/search/program-offices` | `SearchModule` | `program_offices` |
| `/search/live-deals` | `SearchModule` | none (no dedicated flag) |
| `/global-search` | `GlobalSearchPageModule` | `elastic_search` recommended |
| `/ip-search` | `IpSearchModule` | `intellectual_property_section` / `ip_management` |
| `/ip-request` | `IpRequestModule` | `ip_management` |

Services: `search.service.ts` (pagination + typeahead + elastic branch), `ips.service.ts` (IP management).

No dedicated NgRx slice — all search state is component-local. `SearchService` caches `brandDetails` from the NgRx global store at construction to make synchronous flag decisions per typeahead call.

## Backend modules
- `sc-saas-backend/src/modules/search/module.spec.md` — public text search and typeahead endpoints for all 9 stakeholder types
- `sc-saas-backend/src/modules/elastic-search/module.spec.md` — Elasticsearch typeahead, global search, and re-index endpoints
- `sc-saas-backend/src/modules/ecosystem/module.spec.md` — cockpit-proxy profile search and per-profile detail lookups (8 stakeholder types, gated by `ecosystem_enabled`)

## Data flow

### Full-text paginated search
1. User navigates to `/search/:type` (e.g. `/search/startups`).
2. Component reads `brandDetails.features.startups` from NgRx; redirects to 404 if flag is off.
3. User applies filters; component calls `SearchService.searchStartUp(filters)`.
4. Service: `GET api/v1/public/search/startups` with query params (filters, `pageNumber`, `limit`).
5. Backend `SearchController` applies `@Features(Feature.STARTUP)`, `OptionalJwtAuthGuard` (identity used for partner-scoping and approval-type filtering), and `RateLimiter (100/min)`.
6. `SearchService` resolves `approvalType` + `partnerId` from the caller's profile, queries the startup repository, then issues secondary DB calls per result page item to resolve industry and technology IDs to names (N+1 pattern).
7. Response: paginated `{ message, data: { results, total, page } }` envelope.
8. Component renders result cards; `InfiniteScrollModule` triggers next page load.

### Typeahead — dual-path (`elastic_search` flag)
1. User types in a search typeahead field (3+ characters to activate).
2. `SearchService` checks `brandDetails.features.search_type === 'elastic'`.
   - **Elastic path:** `GET api/v1/elastic-search/search-startups/:query`. Backend returns up to 5 UUID hits, hydrates from MySQL, returns `{ uuid, name, logo }` objects. **No JWT required on the backend.**
   - **Text path:** `GET api/v1/public/search/startups/profile/:name`. Backend returns `SearchProfileType[]` `{ uuid, name, logo }`. No feature gate, no JWT.
3. Both paths return the same `SearchProfileType[]` shape.
4. For program-office typeahead, the elastic path does not exist — always falls through to the text endpoint regardless of flag state.

### Global typeahead (`/global-search`)
1. User types into `GlobalSearchPageComponent`.
2. If `features.search_type === 'elastic'`: `GET api/v1/elastic-search/search-global/:query` — fans across all 9 indices, returns up to 10 hits per type. Response includes raw Elasticsearch metadata (`_index`, `_score`, `_source`) — must not be rendered directly to users.
3. If not elastic: `GET api/v1/public/search/:accountType/profile/:name` for the active type.

### Ecosystem profile lookup (cockpit proxy)
1. User clicks on a stakeholder profile from search results.
2. `SearchService` (or the profile component) calls `GET api/v1/ecosystem/startups/:uuid/info`.
3. Backend `EcosystemController` (`@Features(Feature.ECOSYSTEM_ENABLED) + JwtAuthGuard`) proxies to `GET {cockpit}/v1/ecosystem/startups/:uuid/info` with `x-client-domain` and `requested_client_domain` headers.
4. Cockpit returns full profile data; backend forwards the response to the frontend.
5. Component renders the profile detail view.

### IP / patent search
1. User navigates to `/ip-search` (gated by `intellectual_property_section` / `ip_management` flags).
2. `IpsService.getIpsList(filters)` → `GET api/v1/ip-management/patents` with filter params.
3. Backend proxies to the cockpit; patent data lives in the cockpit DB, not the tenant DB.
4. User clicks a patent → `GET api/v1/ip-management/patents/:patentUUID/info`.
5. User submits connect request → `POST api/v1/ip-management/patents/:patentUUID/connect`.
6. Connect requests tracked under `/ip-request`; user can message and upload attachments via `IpRequestDetailsComponent`.

## Feature flags
- `elastic_search` — backend: class-level `FeatureGuard` + method-level `@Features(Feature.ELASTIC_SEARCH)` on every elastic-search route; frontend: branch decision in `SearchService` via `features.search_type === 'elastic'` check (see Known issues below).
- `ecosystem_enabled` — backend: class-level guard on `EcosystemController`; frontend: ecosytem profile cards/links only appear when flag is active.
- Per-type flags (`startups`, `investors`, `corporates`, `mentors`, `service_providers`, `partners`, `individuals`, `program_offices`) — backend: `@Features(Feature.X)` on the paginated full-search endpoint for each type; frontend: each search page component checks its flag and redirects to 404 if off.
- `intellectual_property_section` / `ip_management` — frontend: gates IP search routes; backend: `@Features(Feature.IP_MANAGEMENT)` on all `ip-management/*` routes.

## API contract

### Full-text search: `GET api/v1/public/search/startups`
Query params: filters vary by type (industry, technology, funding stage, location, keyword, etc.); common: `pageNumber` (default 1), `limit`.
Response: `{ message, data: { results: StartupSearchResult[], total, pageNumber } }`

### Typeahead: `GET api/v1/public/search/startups/profile/:name`
Response: `{ message, data: SearchProfileType[] }` where `SearchProfileType = { uuid, name, logo }`.
Minimum 3-character guard: `name.length < 3` returns `[]` with HTTP 200 (not 400).

### Elastic typeahead: `GET api/v1/elastic-search/search-startups/:query`
Response: raw Elasticsearch hit list hydrated to `{ uuid, name, logo }[]`. Same shape as text typeahead for the client but response also contains `responseArr` with raw ES metadata on the `search-global` variant.

### Ecosystem search: `GET api/v1/ecosystem/startups/search`
Query: `SearchEcosystemProfilesDto` — `{ name?, limit (default SearchQueryLimit), pageNumber (default 1) }`.
Response: proxied from cockpit; shape owned by the cockpit contract, not this backend.

No shape mismatch is currently documented between frontend models and backend DTOs for search results, but the ecosystem proxy response shape is cockpit-owned and may drift independently.

## Auth & security

**Frontend:**
- No Angular `FeatureGuard` wired in search routing — each per-type search component performs its own flag check and shows a 403/404 view. A tenant with a flag off will still load the route JavaScript bundle before the redirect.
- All text-path typeahead and paginated search calls are public — no JWT required by the backend. The frontend HTTP interceptor attaches the Bearer token if present, but it is not consumed.

**Backend:**
- Full-search endpoints use `OptionalJwtAuthGuard` to optionally read caller identity for access-level filtering. Unauthenticated callers see publicly-filtered results.
- Elastic-search endpoints have **no `JwtAuthGuard`** — all are unauthenticated. `index-*` re-index endpoints are equally unprotected; any caller who can reach the API can trigger a full stakeholder data re-index.
- Ecosystem search/profile endpoints require `JwtAuthGuard` in addition to `@Features(Feature.ECOSYSTEM_ENABLED)`.
- IP management routes require `JwtAuthGuard + @Features(Feature.IP_MANAGEMENT)`.
- `EcoSystemAdminController` push-all endpoints use only `adminMd5` token — no JWT.

**Gaps:**
- Elastic `index-*` endpoints are completely open. They should be restricted to internal/admin callers.
- Search result pages have no Angular `FeatureGuard` in the route config — flag enforcement is component-level only.

## Known issues / Watch out for

- **`elastic_search` flag vs `search_type` value mismatch.** The flag enabling Elasticsearch is `elastic_search` (the `tenant_users` column), but `SearchService` reads `features.search_type === 'elastic'` to branch. These are distinct: `elastic_search` is a boolean feature flag; `search_type` may be a settings value. If `search_type` is not populated in `IBrandDetails.features`, the elastic branch is never activated even when the flag is on. Run `/trace-flag elastic_search` to audit the full data path before modifying this logic.
- **No elastic branch for program-office typeahead.** `searchProgramOfficeByName` always uses the text endpoint even when `elastic_search` is active — no `search-program-offices` elastic endpoint exists on the backend.
- **`search-global` leaks raw Elasticsearch metadata.** `GET api/v1/elastic-search/search-global/:query` response includes raw `_index`, `_score`, `_source` fields in `responseArr`. `GlobalSearchPageComponent` must filter these before rendering.
- **Shared mutable `requestHeader` in `EcoSystemService`.** The service mutates a single constructor-built header object per-request to set `requested_client_domain`. Under concurrent requests this can leak one request's domain into another's cockpit call — not request-scoped.
- **`SearchProgramOfficeMember` enrichment loop is discarded.** The enrichment loop that adds `partnerDetails` per result runs in the backend service but the function returns `programOfficesDetail` (the raw repo result) instead of the enriched `response`. Program office results never carry partner details.
- **`StakeholderAccess` is a no-op.** The backend `SearchService` resolves `StakeholderAccess` per search call but never forwards it to any repository method; the variable is assigned then unused. Only `partnerId` actually scopes partner-cohort results.
- **`/search/challenges` endpoint is ungated.** `GET api/v1/public/search/challenges` on the backend has no `@Features` gate — it fires regardless of tenant configuration (unlike all other search endpoints). This appears to be an oversight.
- **Cockpit latency for IP and ecosystem routes.** IP patent data and ecosystem profiles live in the cockpit DB. All requests are proxied via HTTP; latency is higher than local DB queries. Ensure visible loading states exist in the UI for these paths.
- **`onApplicationBootstrap` race in elastic-search.** If `ElasticSearchModule` bootstraps before `GlobalModule` populates `saasFeatures`, `createIndicesIfNotExist()` is skipped silently. Indices must be created manually via the `index-*` endpoints or the cron job.
