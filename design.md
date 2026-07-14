# SanchiSaaS — Workspace Architecture (as-is synthesis)

Last updated: 2026-07-14

The workspace-level architecture document. Synthesizes the seven repos' own `design.md`/`knowledge.md`
findings into the cross-repo picture no single repo's document can see. `[AS-IS]` unless tagged
`[INFERRED — requires validation]`. See `knowledge.md` for the fuller narrative behind each finding and
`api.md`/`database.md` for the call-graph and data-ownership detail this document assumes.

---

## 1. Central architectural fact: three tenancy models plus one stripped fork coexist

SanchiSaaS is not built on one tenancy mechanism — it runs **four different answers to "which tenant does
this request belong to,"** one per repo family, and this is a real, load-bearing fact of the platform, not
a defect:

1. **`sanchiconnect-saas-tenants`** — row-per-tenant in a single shared MySQL DB, keyed by `domain`, one
   TypeORM connection, `synchronize: true`, no migrations.
2. **`sc-saas-backend`** — one deployment per tenant. No per-query tenant guard because there is no
   multi-tenant data to guard within a single process — config/flags are loaded once at bootstrap and held
   in memory for the process lifetime. A `domain` column exists on ~10 entities but is written once at
   creation (always this process's own tenant value) and never read as a query filter — it exists purely so
   *another* tenant's deployment can identify whose data it fetched, via the Ecosystem Directory's
   tenant-to-tenant HTTP calls.
3. **`sc-saas-admin`** — per-tenant DB connection resolved fresh on every HTTP request, via two simultaneous
   Medoo connections (`$mainDatabase` for tenant lookup, `$database` for the resolved tenant's own business
   data).
4. **`sanchiconnect-saas-tenants-admin`** — a deliberate stripped fork of `sc-saas-admin`'s own lineage
   (byte-identical `index.php` dispatch loop, confirmed by direct diff). The per-tenant-DB-resolution logic
   is still physically present in the code, commented out verbatim, and was consciously removed — this repo
   now operates with exactly one connection, directly to the shared tenants DB, as a platform-operator tool
   with no tenancy resolution at all. `modules/scrapper.php` is the one place that mechanism is
   reintroduced ad hoc, in a loop, for a cross-tenant analytics dashboard.

`[Source: sanchiconnect-saas-tenants/database.md §Schema strategy; sc-saas-backend/knowledge.md §The
One-Deployment-Per-Tenant Tenancy Model; sc-saas-admin/knowledge.md §Tenancy Resolution;
sanchiconnect-saas-tenants-admin/knowledge.md §(a), §(c)]`

**Why this matters architecturally**: a contributor moving between repos cannot carry one mental model of
"tenant scoping" across the workspace. The workspace `CLAUDE.md`'s invariant #5 ("every query filters by
domain / per-tenant DB / bootstrap config") is the correct *per-repo* framing precisely because each repo's
mechanism is genuinely different — it is not one rule instantiated four ways, it is four different rules
that happen to be listed together. `[INFERRED — requires validation]`: this framing (four independent
mechanisms rather than "one rule, four implementations") is this document's own synthesis judgment; the
underlying four mechanisms are each a direct restatement of the cited repo's own finding.

---

## 2. The documented call graph vs. the real one

The workspace `CLAUDE.md`'s blast-radius mermaid diagram is correct for the majority of edges it draws
(`tenants → backend`, `tenants → frontend`, `backend → {frontend, admin}`, `backend → 3rdparty-webservices`,
`backend → power-pitch`, `admin → analyzer`, both leaf-node claims for `analyzer` and
`3rdparty-webservices`'s *outbound* direction). It is **wrong or incomplete on three specific edges**,
each independently confirmed by a code-extraction pass on both the caller and callee side where possible:

1. `sc-saas-3rdparty-webservices` is documented as "called only by `sc-saas-backend`." **False** —
   `sc-saas-admin` calls it directly for two routes (VideoSDK v2 sessions, Short.io short-url), one with no
   auth header at all. Since the gateway has zero authentication of its own (confirmed by exhaustive grep),
   it cannot distinguish or reject this second caller even in principle.
2. `sanchiconnect-saas-tenants-admin` is documented (by its own `CLAUDE.md`) as "fully standalone... does
   NOT call `sc-saas-backend`." **False** — it calls `PATCH api/v1/public/global/saas/settings` on every
   `tenant_users` edit and conditionally calls an admin-account-created notification route, both directly
   against that tenant's own backend deployment.
3. `sc-saas-admin` has at least two further undocumented outbound edges beyond what its own `CLAUDE.md`
   states: a direct call into `sanchiconnect-saas-tenants`'s AI-Credits webhook route (via
   `easebuzz_callback.php`, deliberately routed outside the app's own dispatcher) and the
   `sc-saas-3rdparty-webservices` calls in #1.

See `api.md`'s "real call graph" table for the full 16-row inventory with per-row citations. **Net effect**:
the platform's actual integration surface is wider, and its actual trust boundaries are looser, than any
single repo's own documentation states — a contract change to the `saas/settings` route or either of the
two directly-called gateway endpoints would break a consumer with zero visibility from the documented graph
alone. `[Source: sc-saas-admin/knowledge.md §Third-Party Integration Pattern;
sc-saas-3rdparty-webservices/knowledge.md §Reality Check: Who Actually Calls This Service;
sanchiconnect-saas-tenants-admin/knowledge.md §(g)]`

---

## 3. What would break, and where — the two most load-bearing cross-repo contracts

### 3a. `verify_tenant` / `tenant-settings` (the tenant-verification contract)

Already traced end-to-end, on both the producer and consumer sides, by `sanchiconnect-saas-tenants/design.md`
and `sc-saas-frontend/design.md`. Not re-derived here — cited directly:

- **`sc-saas-backend`'s bootstrap depends on `tenant-settings`** (not `verify_tenant` — the two consuming
  repos depend on *different* routes of what the workspace treats as one contract). The dependency is
  **bootstrap-blocking and unguarded**: `onApplicationBootstrap()` has no try/catch around the cockpit
  fetch, so a missing/renamed `features`/`settings` key, a non-2xx response, or the cockpit being
  unreachable at boot time throws inside the NestJS lifecycle hook and the process **never reaches
  `app.listen()`** — a hard crash, not a degraded start, with no retry/backoff and no fallback to a
  previously-cached settings blob even though one exists in the cache manager from any prior successful
  boot. `[Source: sanchiconnect-saas-tenants/design.md §Why a verify_tenant/tenant-settings shape change
  breaks sc-saas-backend bootstrap...; independently reproduced from the consumer side in
  sc-saas-backend/knowledge.md §Bootstrap Sequence]`
- **`sc-saas-frontend`'s app-init depends on `verify_tenant`** (the *other* route). The single
  highest-impact field is `IBrandDetails.apiUrl`: if the cockpit ever renamed or re-nested this key, the
  frontend's `ApiEndpointService.DOMAIN` becomes the literal string `"undefined"`, and every one of ~73
  services' subsequent calls fails independently at the network layer with no central error — a quiet,
  scattered failure mode, not a crash. A shape change to the `features` object similarly degrades to "every
  flag-gated feature silently disappears" (most template reads use `?.`, so a missing/wrong-shaped
  `features` object reads as every flag being off, not an error). `[Source: sc-saas-frontend/design.md §Why
  a verify_tenant Shape Change Breaks This Repo Specifically]`
- **Net asymmetry, stated by `sc-saas-frontend/design.md` itself and worth repeating at the workspace
  level**: the backend's failure mode is loud (a crashed process, visible immediately in any monitoring);
  the frontend's failure mode is quiet (a stuck loader or silently-vanished features, visible only to a
  user or a careful QA pass). A change that passes a smoke test against one consumer can still silently
  break the other, because they depend on two different routes with two different response-assembly
  mechanisms (`verify_tenant` is a hand-maintained `.select()` + object-literal; `tenant-settings` is
  reflection-based over every boolean column) and two different hostname-matching strategies (substring vs.
  effectively-exact `LIKE`). `[Source: sanchiconnect-saas-tenants/knowledge.md §The Tenant-Verification
  Contract]`

### 3b. The `sc-saas-backend` REST API contract

Not separately re-traced by any repo's `design.md` in the same forensic depth as 3a, but the same structural
risk applies, aggregated from each consumer's own findings:

- **`sc-saas-frontend`** consumes it through ~73 services keyed off a static `ApiEndpointService.ENDPOINT`
  map — mostly fully-registered constants (grep-safe), but a real, coexisting minority pattern
  (`payments.service.ts` and others) concatenates a path suffix inline rather than registering it, meaning a
  backend route rename under that context would not be caught by grepping the `ENDPOINT` object alone.
  `[Source: sc-saas-frontend/knowledge.md §ApiEndpointService's Context/Endpoint-Map Pattern]`
- **`sc-saas-admin`** consumes it via plain `curl_init`/Guzzle calls scattered across `includes/*.php`, with
  no generated client and no shared type between the two languages — any DTO shape change on the backend
  side is invisible to PHP until a request actually fails at runtime. `[Source: sc-saas-admin/knowledge.md
  §Third-Party Integration Pattern]`
- **`sanchiconnect-saas-tenants-admin`** is a newly-confirmed third consumer (see §2) of at least one
  backend route, via the same untyped `curl_init` pattern, with the same zero-warning failure mode.
- A repo-wide, undocumented **`:adminMd5`-in-URL-path** convention (695 occurrences across 29 files in
  `sc-saas-backend`) is this repo's de facto server-to-server auth mechanism for admin-panel-initiated
  mutating routes — a bearer-equivalent credential embedded in the URL path rather than a header, with no
  centralizing guard class, and not documented anywhere in `sc-saas-backend`'s own `CLAUDE.md`.
  `[Source: sc-saas-backend/knowledge.md §Representative Business Module Pattern — application-management]`

**Consolidated risk statement**: this contract has **three independent untyped consumers** (frontend via
TypeScript-but-partially-unregistered endpoints, and two PHP admin panels via raw cURL/Guzzle with no shared
schema at all), the same structural shape as the AI-Credits three-mutator finding in `database.md` §3 but
for an API contract instead of a raw table schema. `[INFERRED — requires validation]`: stating these as
structurally parallel risks (shared-schema-with-no-contract vs. shared-API-with-no-generated-client) is this
document's own synthesis; each underlying fact is a direct restatement of the cited repo's finding.

---

## Change Log

- 2026-07-14 | Initial workspace-level architecture synthesis. Built from all seven repos' `design.md` and
  `knowledge.md`, with the two `verify_tenant`/`tenant-settings` and REST-API-contract breakage traces
  pulled directly from `sanchiconnect-saas-tenants/design.md` and `sc-saas-frontend/design.md` rather than
  re-derived. Framed the three/four tenancy-model coexistence as the platform's central architectural fact.
  Consolidated the three real-vs-documented call-graph contradictions (already itemized in `api.md`) into
  the "what would break" narrative. Drew the structural parallel between the AI-Credits three-mutator
  finding (`database.md` §3) and the REST-API-contract's three untyped consumers.
