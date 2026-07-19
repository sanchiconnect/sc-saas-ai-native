# SanchiSaaS — Workspace Knowledge (as-is synthesis)

Last updated: 2026-07-14

This is a **synthesis document**, not a fresh code-extraction pass. Its source material is the seven
per-repo `knowledge.md` files (plus spot-checked `api.md`/`database.md`/`design.md`), all completed earlier
in this same documentation series:

- `sc-saas-admin/knowledge.md`, `sanchiconnect-saas-tenants/knowledge.md`, `sc-saas-backend/knowledge.md`,
  `sc-saas-frontend/knowledge.md`, `ai-startups-analyzer/knowledge.md`, `sc-saas-3rdparty-webservices/knowledge.md`,
  `sanchiconnect-saas-tenants-admin/knowledge.md`

Every claim below is a restatement or connection of a per-repo finding, cited as
`[Source: <repo>/<file> §<section>]`. Claims that go beyond a direct restatement — i.e. the cross-repo
*connections* this document exists to make — are tagged `[INFERRED — requires validation]` only where the
connection itself, not the underlying facts, is a synthesis judgment. Do not use this document as a
replacement for a per-repo `knowledge.md` — it intentionally omits detail that document already owns.

---

## 1. What each repo is and does (one paragraph each, from each repo's own knowledge.md)

**`sanchiconnect-saas-tenants`** — The control-plane/cockpit. NestJS 9 + TypeORM + a single shared MySQL
database (row-per-tenant). Owns the feature-flag *names* (`TenantUsersEntity`, ~180 boolean/enum columns)
and the two tenant-verification endpoints (`verify_tenant`, `tenant-settings`) that `sc-saas-frontend` and
`sc-saas-backend` depend on respectively. Also owns the AI-Credits **purchase-side** schema and the
Ecosystem/IP-Management cross-tenant-sharing features. Has no working tenant-provisioning API — the
`TenantsController` exposes zero routes. `[Source: sanchiconnect-saas-tenants/knowledge.md §Module Map, §Tenant Provisioning]`

**`sc-saas-backend`** — The business API. NestJS 8 + TypeORM + MySQL, **one deployment per tenant**, config
and feature flags loaded once at bootstrap from the cockpit and held in memory for the process lifetime.
Owns the REST API contract (58 wired-in feature modules, not the ~51 its own `CLAUDE.md` claims) that
`sc-saas-frontend` and `sc-saas-admin` both consume. Auth is JWT via an httpOnly cookie (Bearer fallback).
`[Source: sc-saas-backend/knowledge.md §Module Map, §The One-Deployment-Per-Tenant Tenancy Model]`

**`sc-saas-frontend`** — The end-user PWA. Angular 13 + NgRx (34 slices, not "~38"), no database, no
server-side API of its own. Resolves its tenant at runtime via `verify_tenant`, then points every
subsequent business/WebSocket call at the `apiUrl` the cockpit returns. Auth is actually an httpOnly
cookie, not the "JWT in localStorage" its own `CLAUDE.md` claims. `[Source: sc-saas-frontend/knowledge.md
§Bootstrap / Tenant-Verification Flow, §Auth Model]`

**`sc-saas-admin`** — The internal operations panel. Plain PHP ≥5.5, no framework, two simultaneous Medoo
connections per request (`$mainDatabase` = cockpit, `$database` = the resolved tenant's own DB). Owns the
AI-Credits **reserve/settle/refund/debit** spend-side logic (against tables defined by the NestJS tenants
repo) and drives the full AI-scoring lifecycle against `ai-startups-analyzer`. Also calls `sc-saas-backend`
and, directly and undocumented until this pass, `sc-saas-3rdparty-webservices`.
`[Source: sc-saas-admin/knowledge.md §Tenancy Resolution, §AI Credits System, §Third-Party Integration Pattern]`

**`ai-startups-analyzer`** — The AI scoring service. Python 3.10+/FastAPI/SQLAlchemy async, its own small
MySQL schema (`api_keys`, `analyses`, `batches`). Scores startup applications via a swappable LLM provider
(OpenAI/Anthropic/Gemini) on a frozen 0–500→1–5 scale. Called exclusively by `sc-saas-admin`; never
initiates contact with any other repo. `[Source: ai-startups-analyzer/knowledge.md §Application Bootstrap
& Lifespan, §Scoring Orchestration & Batch Pipeline]`

**`sc-saas-3rdparty-webservices`** — The integration gateway. NestJS 9, no database, no auth on any
endpoint (network-trust only, independently confirmed by exhaustive grep). Proxies SMS, email (SendGrid +
SMTP), chat (CometChat), video (VideoSDK), URL shortening (Short.io), and document conversion (ConvertAPI).
Documented as "called only by `sc-saas-backend`" — confirmed false; `sc-saas-admin` also calls it directly
for two routes. `[Source: sc-saas-3rdparty-webservices/knowledge.md §Security Model, §Reality Check: Who
Actually Calls This Service]`

**`sanchiconnect-saas-tenants-admin`** — The platform-operator admin UI over the tenants control-plane DB.
PHP, a fork of `sc-saas-admin`'s own skeleton (byte-identical dispatch loop) with the per-tenant-DB
resolution deliberately stripped out — it opens exactly one Medoo connection, directly to the shared
tenants DB. Documented as "fully standalone, no backend dependency" — confirmed false; it calls
`sc-saas-backend` directly on every `tenant_users` edit. `[Source:
sanchiconnect-saas-tenants-admin/knowledge.md §(a) Routing & Bootstrap, §(c) The Shared-DB Relationship,
§(g) Other Architecturally Significant Findings]`

---

## 2. Cross-repo thread: the AI-Credits schema has three independent direct mutators

The AI-Credits prepaid-wallet system (`ai_credit_wallets`, `ai_credit_ledger`, `ai_credit_orders`,
`ai_credit_task_rates`, `ai_credit_packages`, `ai_credit_grants`, plus GST/invoice tables) lives entirely in
the **shared tenants MySQL database** — not a dedicated AI-Credits database — and is mutated directly by
**three independently-deployed codebases with no shared schema-versioning mechanism between them**:

1. **`sanchiconnect-saas-tenants` (NestJS, TypeORM)** — owns the canonical schema (9 entities under
   `src/modules/ai-credits/`) and implements the **credit (purchase) side only**: a hash-verified Easebuzz
   payment callback increments `balance`/`totalPurchased` and writes a `CREDIT` ledger row, inside one
   transaction with a `pessimistic_write` row lock (added in a same-day fix, commit `0b6f504`). This repo
   has **no** `reserveAiCredits`/`settleAiCredits`/`refundAiCreditReservation`/`debitAiCreditsInstant`
   function anywhere. `[Source: sanchiconnect-saas-tenants/knowledge.md §AI Credits System]`
2. **`sc-saas-admin` (PHP, raw SQL over Medoo's `$mainDatabase`)** — owns the **reserve → settle → refund →
   debit spend side**: `includes/ai_credits_functions.php` implements exactly the four functions the NestJS
   repo lacks, against the identical table names, using raw PDO for the two atomic `WHERE balance >= ?`
   UPDATEs Medoo's query builder can't express, plus caller-level MySQL `GET_LOCK` advisory locks. The
   `credit_type` ENUM is cross-referenced in-code as "matching the canonical schema owned by
   `sanchiconnect-saas-tenants`" — i.e. this repo knows it is a schema *consumer*, not owner.
   `[Source: sc-saas-admin/knowledge.md §AI Credits System (reserve / settle / refund ledger)]`
3. **`sanchiconnect-saas-tenants-admin` (PHP)** — a third, newly-confirmed writer: this repo's
   `modules/ai_credits/{grants,task_rates,packages,orders}.php` perform direct PHP admin CRUD against the
   same `ai_credit_*` tables, gated only by the repo's own inlined
   `super_admin_role_id || developer_role_id` check (not a schema-aware guard). `[Source:
   sanchiconnect-saas-tenants-admin/database.md §AI Credits tables — a second, undocumented writer of the
   same schema `sc-saas-admin` mutates]`

**No cross-repo schema contract exists for any of this.** The NestJS repo has `synchronize: true` and no
migrations (see §5) — a column rename there silently alters or drops a column two independent PHP
codebases already assume exists, with zero compile-time or type-level warning on either PHP side, since PHP
has no visibility into TypeORM entity changes at all. `[Source: sanchiconnect-saas-tenants/knowledge.md
§Shared Database With `sanchiconnect-saas-tenants-admin` — Verified]` `[INFERRED — requires validation]`:
this three-way finding is a workspace-level connection no single repo's own documentation pass could see —
the tenants repo's own knowledge.md correctly identifies the *NestJS/PHP-admin* split but was written before
the tenants-admin pass confirmed the *third* writer.

---

## 3. Cross-repo thread: the documented call graph is wrong in at least three places

The workspace `CLAUDE.md`'s blast-radius graph and at least three repos' own `CLAUDE.md` files state
call-graph claims that this pass's seven independent code-extraction passes found to be **factually false**:

1. **`sc-saas-3rdparty-webservices` claims "called only by `sc-saas-backend`."** False.
   `sc-saas-admin` calls it directly for two routes: `getMeetingSessions()`
   (`includes/core_functions.php:5695`, plain `curl_exec`, **no auth header at all**, hitting
   `GET {3p_api_server_url}/v2/video-sdk/meetings/{code}/sessions`) and
   `acdGenerateProfileShortLink()` (`modules/table.php:124`, Guzzle,
   `POST {3p_api_server_url}/v1/short-io/short-url`). Both repos resolve `3p_api_server_url` /
   `THIRD_PARTY_SERVICE_BASE_URL` from the *same* `global_settings` row, neither aware the other also calls
   it directly. `[Source: sc-saas-admin/knowledge.md §Third-Party Integration Pattern; independently
   confirmed from the receiving side at sc-saas-3rdparty-webservices/knowledge.md §Reality Check: Who
   Actually Calls This Service]`
2. **`sanchiconnect-saas-tenants-admin` claims "fully standalone... does NOT call `sc-saas-backend`."**
   False. `resetAPISaaSSettings()` fires unconditionally on every `tenant_users` edit through this repo's
   generic dynamic-table form, calling `PATCH {api_url}api/v1/public/global/saas/settings` on that tenant's
   own `sc-saas-backend` deployment (a real, unauthenticated route confirmed present on the receiving side).
   A second call site, `sendAccountCreatedEmail()`, calls
   `{api_server_url}v1/admin-actions/admin-account-created/{token}` conditionally, if a `spa_settings` row
   for `api_server_url` happens to exist. `[Source: sanchiconnect-saas-tenants-admin/knowledge.md §(g) Other
   Architecturally Significant Findings, cross-referenced against sc-saas-backend/src/modules/global/global.controller.ts:51]`
3. **`sc-saas-admin` itself calls repos the workspace graph doesn't route through it at all**, beyond the
   documented `sc-saas-backend`/`ai-startups-analyzer` edges: direct Zoho CRM OAuth + REST calls, a direct
   WATI/WhatsApp client, a direct Google Gemini integration for video-pitch transcription (entirely separate
   from `ai-startups-analyzer`'s own multi-provider facade), direct payment-gateway credential validation
   against PayPal/Stripe/Razorpay/Easebuzz/PayU, and (via `easebuzz_callback.php`, deliberately routed
   *outside* `index.php`'s own dispatcher) a direct call to **`sanchiconnect-saas-tenants`**'s
   `/api/v1/ai-credits/webhooks/easebuzz/{success|failure}` — a fourth SanchiSaaS repo this one talks to
   that neither this repo's own `CLAUDE.md` nor the workspace graph names as a consumer relationship.
   `[Source: sc-saas-admin/knowledge.md §Third-Party Integration Pattern]`

**The corrected, real call graph** (workspace-CLAUDE.md edge in parentheses where it differs):

| Caller | Callee | Documented? |
|---|---|---|
| `tenants` | — (upstream, calls nothing inbound) | matches |
| `sc-saas-backend` | `tenants` (bootstrap) | matches |
| `sc-saas-backend` | `sc-saas-3rdparty-webservices` | matches |
| `sc-saas-backend` | `power-pitch-sanchiconnect-api` | matches |
| `sc-saas-frontend` | `tenants` (verify_tenant) | matches |
| `sc-saas-frontend` | `sc-saas-backend` (dynamic apiUrl) | matches |
| `sc-saas-admin` | `tenants` (reads cockpit DB directly) | matches |
| `sc-saas-admin` | `sc-saas-backend` (api_server_url) | matches |
| `sc-saas-admin` | `ai-startups-analyzer` | matches |
| **`sc-saas-admin`** | **`sc-saas-3rdparty-webservices`** (2 routes, direct) | **NOT documented — new edge** |
| **`sc-saas-admin`** | **`tenants`** (Easebuzz webhook, outside dispatcher) | **NOT documented — new edge** |
| `sc-saas-admin` | Zoho / WATI / Gemini / PayPal / Stripe / Razorpay / Easebuzz / PayU (external) | not in graph at all (external, but undocumented in this repo's own `CLAUDE.md`) |
| **`sanchiconnect-saas-tenants-admin`** | **`sc-saas-backend`** (PATCH saas/settings, conditional admin-account-created) | **NOT documented — contradicts this repo's own "fully standalone" claim** |
| `sanchiconnect-saas-tenants-admin` | `tenants` DB (shared, direct) | matches (documented as DB-sharing, not an API call — correct, this one really is DB-only) |
| `ai-startups-analyzer` | (none — leaf, confirmed) | matches |
| `sc-saas-3rdparty-webservices` | external providers only (leaf, confirmed) | matches |

`[INFERRED — requires validation]`: the table above is this document's own synthesis of the seven repos'
independently-confirmed findings; each row is individually sourced as cited above, but their assembly into
one corrected graph is a workspace-level judgment call, not a restatement any single repo's doc makes.

---

## 4. Cross-repo thread: three tenancy models coexist, plus one stripped fork, on this platform

This is a genuine architectural fact of this specific platform, not a defect to fix — four different
mechanisms answer "which tenant does this request belong to," each in a different repo:

1. **`sanchiconnect-saas-tenants`** — single shared MySQL DB, **row-per-tenant** keyed by `domain`, one
   TypeORM connection for the whole process. `[Source: sanchiconnect-saas-tenants/knowledge.md §Database
   Configuration & TypeORM Strategy]`
2. **`sc-saas-backend`** — **one deployment per tenant**. Config/flags loaded once at bootstrap into
   in-memory `saasSettings`/`saasFeatures` objects; no per-query tenant guard because there is only ever one
   tenant's data in the process. A `domain` column *does* exist on ~10 stakeholder entities but is never
   used as a query filter — it is a denormalized label for other tenants' deployments to read over HTTP
   (the Ecosystem Directory pattern), not a scoping mechanism. `[Source: sc-saas-backend/knowledge.md §The
   One-Deployment-Per-Tenant Tenancy Model — Verified Against Entity/Repository Code]`
3. **`sc-saas-admin`** — **per-tenant DB connection resolved per-request** from the shared cockpit DB,
   via two simultaneous Medoo connections (`$mainDatabase` for tenant lookup, `$database` for the resolved
   tenant's own business DB). `[Source: sc-saas-admin/knowledge.md §Tenancy Resolution (per-request,
   per-tenant DB)]`
4. **`sanchiconnect-saas-tenants-admin`** — a **stripped fork of `sc-saas-admin`'s own lineage**
   (byte-identical `index.php` dispatch loop) with the per-tenant-DB-resolution code still present,
   commented out verbatim, and deliberately disabled — this repo opens exactly **one** connection, directly
   to the shared tenants DB, and now operates as a platform-level tool with no tenancy resolution at all.
   One route (`modules/scrapper.php`) reintroduces ad-hoc per-tenant connections in a loop for a
   cross-tenant analytics dashboard, gated only by `checkLoggedIn()` — a legitimate platform-operator
   capability, but one that directly opens live connections into every tenant's own production database with
   plaintext credentials read from the shared DB, undocumented in either this repo's `CLAUDE.md` or
   `module.spec.md`. `[Source: sanchiconnect-saas-tenants-admin/knowledge.md §(c) The Shared-DB Relationship
   — a single, direct connection to the control-plane DB]`

`[INFERRED — requires validation]`: stating this as "three tenancy models plus one stripped fork" (rather
than "four models") is this document's own framing — the underlying four-way mechanism split is a direct
restatement of each repo's own finding.

---

## 5. Cross-repo thread: `synchronize: true` with no migrations is a platform-wide pattern

Confirmed independently, by separate code-extraction passes, in **every NestJS repo in the workspace**:

- **`sanchiconnect-saas-tenants`**: `synchronize: true` hardcoded unconditionally for every `NODE_ENV`
  branch; no migrations directory anywhere in the repo. Combined with `autoLoadEntities: true`, adding a new
  `@Entity` anywhere creates a live table in the shared control-plane DB on next deploy, no review gate
  beyond normal code review. `[Source: sanchiconnect-saas-tenants/knowledge.md §Database Configuration &
  TypeORM Strategy]`
- **`sc-saas-backend`**: independently reproduces the identical finding — `synchronize: true` hardcoded in
  every branch, no migrations directory (the `src/modules/migrations` folder found on grep is an unrelated
  NestJS feature module, not a TypeORM migrations folder). Across 305 entity files, a column rename
  auto-drops or auto-renames the live MySQL column on next deploy. `[Source: sc-saas-backend/knowledge.md
  §Database Configuration & TypeORM Strategy]`

This is the single highest-severity structural finding shared across the two NestJS repos, and it is what
makes §2's three-mutator AI-Credits finding materially worse than an ordinary "poly-repo, coordinate your
deploys" risk: the coupling there is a **raw shared-table schema**, not a versioned REST contract, and one
of the three writers can unilaterally, silently alter the shared schema on any deploy with no migration
safety net at all. `ai-startups-analyzer` is the one repo in the workspace with a *partial* mitigation — an
add-only `_sync_missing_columns()` auto-migration plus one legacy hand-written SQL migration predating it —
which never drops/renames, only adds. `[Source: ai-startups-analyzer/knowledge.md §Configuration & Database
Engine]`

---

## 6. Consolidated security findings across the platform

- **`verify_tenant`/`tenant-settings` plaintext secret exposure** (already flagged in the workspace
  `CLAUDE.md`, refined by this pass): `verify_tenant` exposes `azure_client_secret` in plaintext to any
  unauthenticated caller who knows a tenant hostname; `tenant-settings` (a different, also-unauthenticated
  route) separately exposes `email_password_ses` and other SMTP fields. Both endpoints use two different,
  non-equivalent `LIKE` hostname-matching strategies (substring vs. effectively-exact), and both are fully
  open (`public/global` prefix, no guard). `[Source: sanchiconnect-saas-tenants/knowledge.md §The
  Tenant-Verification Contract]`
- **Per-tenant DB passwords stored plaintext** in `tenant_users` (already flagged in the workspace
  `CLAUDE.md`) — this pass found a *new* consumer of that plaintext column the workspace guardrail didn't
  anticipate: `sanchiconnect-saas-tenants-admin`'s `modules/scrapper.php` reads
  `tenant_users.database_password` in plaintext to open ad-hoc connections into every individual tenant's
  production database. `[Source: sanchiconnect-saas-tenants-admin/knowledge.md §(c) The Shared-DB
  Relationship, Known Issues]`
- **Hardcoded live API keys committed to source** — `sanchiconnect-saas-tenants`'s
  `global.repository.ts` hardcodes a live `factacy_api_key` and `currency_api_key` as TypeORM seed defaults
  (not read from `.env`). `<redacted — see sanchiconnect-saas-tenants/knowledge.md §Shared Database With
  `sanchiconnect-saas-tenants-admin` — Verified>`
- **Plaintext OAuth secrets in `sc-saas-backend`'s `PaymentGatewaysEntity`** — stored as plaintext `varchar`
  columns; a working `CryptoService.encrypt`/`decrypt` exists in the same codebase but is used only by an
  unrelated module (`connections/public/connection.service.ts`), never by payment-management.
  `<redacted — see sc-saas-backend/knowledge.md Change Log entry and sc-saas-backend/database.md §PaymentGatewaysEntity>`
- **Unauthenticated Adminer console with an embedded live DB password** — `sanchiconnect-saas-tenants-admin`
  bundles a full third-party MySQL web console (`adminer/adminer.php`) at the repo root, outside the app's
  own routing/auth entirely (Apache serves it directly since it's a real file); the "DB Administration" menu
  link renders the live `.env`-sourced database password as a plaintext URL query parameter.
  `<redacted — see sanchiconnect-saas-tenants-admin/knowledge.md §(g) Other Architecturally Significant
  Findings>`
- **`sc-saas-3rdparty-webservices` has zero authentication on any endpoint**, confirmed by exhaustive grep —
  anyone with network access can create/delete CometChat users, generate VideoSDK meeting tokens, send
  arbitrary email/SMS billed to the platform's own provider accounts, and generate arbitrary short links,
  with no rate limiting anywhere. This is architecturally-intended (network-perimeter trust), but the §3
  finding that `sc-saas-admin` also calls it directly — one call site with **no auth header at all** — means
  the trust boundary is wider in practice than either caller's own documentation assumes.
  `[Source: sc-saas-3rdparty-webservices/knowledge.md §Security Model: No Auth, Network Trust Only]`
- **Five of six sampled AJAX handlers in `sanchiconnect-saas-tenants-admin` skip the login check entirely**,
  relying on CSRF-token-equality (which any anonymous visitor can obtain by loading any public page) as the
  only access control on endpoints that create/update/delete `spa_settings`, email templates, API-route
  metadata, S3 objects, and — via the generic CRUD handler — arbitrary rows in any table this admin panel
  manages, including `tenant_users` itself. `[Source: sanchiconnect-saas-tenants-admin/knowledge.md §(g)
  Other Architecturally Significant Findings]`
- **Arbitrary raw SQL execution with no login/role gate, confirmed in *two* separate admin repos** (found
  2026-07-16/17, module-spec-level review — see §10): `sc-saas-admin/modules/ajax/crud_actions.php` and
  `sanchiconnect-saas-tenants-admin/modules/ajax/crud_actions.php` each expose a `sql_query` action that
  passes `$_POST['sql']` directly to `$database->query()` with zero allowlist — and the entire file in both
  repos has no `checkLoggedIn()`/`checkRole()` call at all, only `verifyCSRFToken()`. In `sc-saas-admin`,
  the same ungated file is also where `system-admin`'s destructive DDL (CREATE/DROP/ALTER/TRUNCATE/RENAME
  TABLE) actually runs, despite being documented as gated behind `is_dev` — any logged-in admin of any role
  can execute it. `[Source: sc-saas-admin/module.spec.md (ajax), sanchiconnect-saas-tenants-admin/module.spec.md (ajax)]`
- **`facility_management`'s authenticated routes are not actually feature-gated** — three of five
  controllers (`FacilityManagementController`, `BookingFacilityController`, `EcosystemFacilityManagementController`)
  only apply `JwtAuthGuard`; `FeatureGuard` (the guard that reads `@Features` metadata) is never imported or
  applied there. Disabling the `facility_management` flag for a tenant currently does nothing to these
  routes — only the two `Public*` controllers actually enforce the flag. `[Source: sc-saas-backend/module.spec.md (facility_management)]`
- **Two "guard decorator present but not wired" gaps in `sc-saas-backend`**: `startup-kit`'s
  `@Roles(Role.STARTUP)` and `verifications`' `@RateLimit` on the WhatsApp OTP send route are both dead
  metadata — `RolesGuard`/`RateLimiterGuard` are never actually applied on those specific routes, so the
  restriction/rate-limit each decorator implies is not enforced. `[Source: sc-saas-backend/module.spec.md (startup-kit, verifications)]`
- **Worst finding of the entire module-spec sweep (2026-07-19): `sanchiconnect-saas-tenants-admin`'s
  `modules/csv/export.php`/`import.php` have no authentication of any kind** — not even the CSRF-token-
  equality check every other unguarded endpoint in that repo at least has. Traced end-to-end
  (`index.php`'s router → `common.php` → the handler itself: no `checkLoggedIn()`, no `verifyCSRFToken()`
  anywhere in the chain) against the single shared tenants MySQL DB, with the table name taken raw from the
  query string and no allow-list. Any anonymous caller can dump `tenant_users` (plaintext per-tenant DB
  credentials) or `spa_admin_users` (operator password hashes) with one GET request, or insert arbitrary
  rows via `import.php`. Tracked as **Linear SAN-42 (Urgent)** — not yet fixed. `[Source:
  sanchiconnect-saas-tenants-admin/modules/csv/module.spec.md]`
- **The same unauthenticated `filemanager`/`aws` endpoint pattern exists in *both* PHP admin repos** —
  `sc-saas-admin` and `sanchiconnect-saas-tenants-admin` each have a `filemanager/download.php` with zero
  auth (readfile() of any path) and an `ajax.php` whose one `cleanPath()` path-traversal sanitizer is
  defined but never called anywhere in either codebase; both also have an `aws/ajax.php` gated only by a
  CSRF token that `index.php` mints for any anonymous visitor. Tracked as SAN-22/31 (`sc-saas-admin`) and
  SAN-43/46 (`sanchiconnect-saas-tenants-admin`) — same code lineage, same bug, two repos, none fixed yet.
  `[Source: sc-saas-admin/modules/{filemanager,aws}/module.spec.md, sanchiconnect-saas-tenants-admin/modules/{filemanager,aws}/module.spec.md]`
- **`sc-saas-backend`'s WebSocket gateway (`core/sockets/FetchCountGateway`) is fully unauthenticated** — no
  `@UseGuards`, no JWT/handshake identity check anywhere. Its `joinRoom` handler joins any connected client
  to any arbitrary room string with zero validation, so knowing/guessing a `conversation_<uuid>` (or a bare
  numeric user-id room) lets a client eavesdrop on someone else's chat typing indicators, messages, and
  notifications. Confirmed real, actively-used consumers (`chat.service.ts`, `connections.service.ts`,
  `conversations.service.ts`), not dead code. Tracked as **SAN-45**. `[Source: sc-saas-backend/src/core/sockets/module.spec.md]`
- **`sc-saas-frontend`'s `admin-actions` module calls a backend impersonation endpoint
  (`/backdoor-login/:userId/:adminMd5`) that takes a real admin auth token as a raw URL path segment** —
  exposed to browser history/server logs/`Referer` headers by construction — with no per-target-user
  validation and no route guard beyond a no-op `FeatureGuard` (no `@Features()` decorator on that specific
  handler). A leaked link grants permanent impersonation of any user by id. Tracked as **NIR-5**.
  `[Source: sc-saas-frontend/src/app/modules/admin-actions/module.spec.md]`
- **`global.controller.ts`'s zero-auth-guard finding (bullet 1 above) has a new confirmed refinement**:
  `getTenantSettings()`'s query has no `active = true` filter at all in its `where` clause (unlike
  `verifyTenant()`, which does filter on it) — so a **deactivated** tenant's plaintext SMTP password and
  other settings remain fetchable by hostname alone, not just active tenants'. Tracked as **SAN-44**.
  `[Source: sanchiconnect-saas-tenants/src/modules/global/module.spec.md]`

---

## 7. No Docker, CI/CD, or infra-as-code anywhere in the workspace

Confirmed independently in every repo's own `design.md` during this documentation series — no `Dockerfile`,
no CI pipeline config (`.github/workflows`, `.gitlab-ci.yml`, etc.), and no infra-as-code (Terraform,
CloudFormation, Pulumi) was found in any of the seven repos. Deployment is manual/ops-run in every case.
`[Source: each repo's own design.md, Constraints Implied by Code section]`

---

## 8. Verifying the workspace `CLAUDE.md`'s own blast-radius graph

What the graph gets **right**, confirmed by this pass:
- `tenants → backend` (bootstrap-blocking), `tenants → frontend` (verify_tenant, app-init-blocking),
  `backend → {frontend, admin}` via the REST API contract — all confirmed exactly as documented, at the code
  level, from both producer and consumer sides. `[Source: sanchiconnect-saas-tenants/design.md §Why a
  verify_tenant/tenant-settings shape change breaks..., sc-saas-frontend/design.md §Why a verify_tenant
  Shape Change Breaks This Repo Specifically]`
- `ai-startups-analyzer` is correctly a leaf node — confirmed, it never calls back into any SanchiSaaS repo.
  `[Source: ai-startups-analyzer/knowledge.md, repo-wide]`
- `sc-saas-3rdparty-webservices` never calls back into any other SanchiSaaS repo (leaf in the *outbound*
  direction) — confirmed. What's stale is the *inbound* side (see §3).
- `sanchiconnect-saas-tenants-admin ↔ sanchiconnect-saas-tenants` DB-sharing is confirmed exactly as
  documented, at the literal table-name level (`tenant_users`, `global_settings`, `ai_credit_*`, 20 `spa_*`
  entities). `[Source: sanchiconnect-saas-tenants/knowledge.md §Shared Database With
  sanchiconnect-saas-tenants-admin — Verified]`
- The `power-pitch-sanchiconnect-api` external contract (invariant #6) is confirmed accurately described,
  including the `x-hostname` header and the 10-minute-before-expiry token refresh.
  `[Source: sc-saas-backend/knowledge.md §PowerPitch External Integration]`

What the graph gets **stale/wrong**, per §3 above:
- `sc-saas-3rdparty-webservices` is not "called only by `sc-saas-backend`" — `sc-saas-admin` is a confirmed
  second direct caller.
- `sanchiconnect-saas-tenants-admin` is not DB-only toward the tenants repo — it also makes direct outbound
  HTTP calls to `sc-saas-backend`.
- The graph has no edge at all for `sc-saas-admin → sc-saas-3rdparty-webservices` or
  `sc-saas-admin → tenants` (Easebuzz webhook) or `sanchiconnect-saas-tenants-admin → sc-saas-backend` — all
  three are real, confirmed, undocumented edges.

---

## 9. The workspace boundary — SanchiPowerpitch is a sibling poly-repo, not part of this one

`CLAUDE.md` invariant #6 documents the one contract that crosses into SanchiPowerpitch
(`power-pitch-sanchiconnect-api`'s `/v1/externals/*`, called from `sc-saas-backend`'s
`PowerPitchExternalService`), but neither `CLAUDE.md` nor this document previously named the sibling
workspace's other repos or confirmed it actually exists on disk. Verified directly, 2026-07-16:

- SanchiPowerpitch is a separate poly-repo workspace, cloned at `/Users/mac/Desktop/Work/SanchiPowerpitch`
  (a sibling of this `SanchiSaaS` folder, not nested inside it) — its own `CLAUDE.md`/`README.md`/
  `AI-NATIVE-SETUP.md`/`specs/` exist there, mirroring this workspace's own root-level structure.
- It contains **four** repos, each with its own `.git`: `power-pitch-sanchiconnect-api`,
  `power-pitch-sanchiconnect-frontend`, `power-pitch-sanchiconnect-admin`, `power-pitch-partners`.
- **Exactly one** contract crosses the boundary in either direction: `sc-saas-backend` → `power-pitch-
  sanchiconnect-api`'s `/v1/externals/*` (invariant #6, unchanged). PowerPitch never calls back into
  SanchiSaaS. No other SanchiPowerpitch repo (frontend, admin, partners) has any confirmed contract with
  any SanchiSaaS repo.
- **Correction to a claim in this workspace's own repo-map reference (dated 2026-07-15):** that document
  states `power-pitch-sanchiconnect-admin` "had no meaningful commits yet." Checked directly via `git log`
  — this is wrong, not just stale: the repo has 12 commits total, including real feature work ("plans
  management", "add partner user", email-template changes) dated 2022-12-21 through 2023-04-21, then a
  three-year gap before a single docs-only commit (CLAUDE.md + module specs) landed 2026-06-19. So the repo
  has genuine historical business logic, just no active development in over three years as of this check —
  a materially different situation from "no meaningful commits."
- `prabs/` (the evaluated-and-rejected SpecPod framework) lives in this `SanchiSaaS` folder, not
  SanchiPowerpitch's — already covered by this workspace's own memory/decision record, not a SanchiPowerpitch
  concern.

---

## 10. Module-level re-verification (2026-07-16/17) — real bugs found beyond doc drift, at a much higher rate than expected

Following the repo-level re-verification in §8/Change Log, every committed `module.spec.md` in all 7 repos
(139 files total) was individually re-checked against current source code. Most modules were already
accurate — this was a targeted fix pass. The severe security findings from this pass are folded into §6
above; this section covers the broader methodology and the non-security bugs found.

**Real bugs confirmed (not just doc drift), beyond the §6 security items:**
- `sc-saas-3rdparty-webservices`'s `shortIo.service.ts`: `getShortAcceptUrl()` builds the identical
  `/connection-request/reject` URL as `getShortRejectUrl()` — accepting a connection request currently
  generates a reject link. `[Source: sc-saas-3rdparty-webservices/module.spec.md (shortIo)]`
- `sanchiconnect-saas-tenants`'s `ecosystem-facilities.service.ts`: `getTenantUserByDomain()` selects only
  `['facility_module_allowed_domains', 'domain']` from `TenantUsersEntity`, omitting `facility_module_type`
  — every `=== FacilityModuleType.EXTERNAL` check compares against `undefined` and always evaluates false.
  The External Facilities Hub feature is silently non-functional for every tenant, no error surfaced
  anywhere. `[Source: sanchiconnect-saas-tenants/module.spec.md (ip-management + ecosystem-facilities)]`
- `sanchiconnect-saas-tenants`'s `organizations` table was misattributed: the prior spec claimed
  `sc-saas-admin` writes `organizations`/`invoices`/`payments`/`contacts`/`contracts` directly — grepped
  `sc-saas-admin` and found zero references to any of these tables. The actual writer is
  `sanchiconnect-saas-tenants-admin` (registers `organizations` as "Clients" in its generic CRUD engine).
  `[Source: sanchiconnect-saas-tenants/module.spec.md (organizations)]`
- `sc-saas-admin`'s `tickets` module: the documented "closed state" model was wrong — `reopen_ticket` sets
  separate `reopened_at`/`reopened_by_id` columns rather than clearing the closed pair, and there is no
  `tickets.token` column at all (the `{token}` path segment on backend email endpoints is a one-time admin
  backdoor token, not a ticket identifier). `[Source: sc-saas-admin/module.spec.md (tickets)]`
- `sc-saas-frontend`: `dashboard-v2`'s `/market-insights/news/hot-topics` route wires to
  `InnovationsDashboardComponent`, not the declared `HotTopicsComponent` (which is dead code, never
  referenced by any route) — a genuine routing bug, not a doc issue. Separately, `pitch-deck-recorder` is
  confirmed dead code end-to-end (unrouted; its one embed site is itself unreachable), and the `payment`
  module's `/payment-gateways` route has no `loadChildren` anywhere, making it fully unreachable.
  `[Source: sc-saas-frontend/module.spec.md (dashboard-v2, pitch-deck-recorder, payment)]`

**Methodology finding — trust a single verification pass's "no changes" claims with caution:** after this
pass, an adversarial second round sampled 18 modules the first pass had explicitly marked "no changes —
verified accurate" and re-ran them with agents instructed to assume the prior verdict was wrong and try to
disprove it. **16 of 18 (89%) had real, previously-missed gaps** — only 2 modules held up cleanly under
genuine adversarial pressure. A "verify this doc against the code" instruction without adversarial framing
produces confirmation-biased results; agents tend to skim-and-agree rather than genuinely try to break each
claim. Only 18 of the ~125 modules originally marked "no changes" across this workspace have been
adversarially re-checked so far — the remaining ~107 are still resting on the original, now-demonstrated-to-
be-unreliable pass, and would very likely surface more real issues at a similar hit rate if swept.

---

## 11. Module-spec coverage is now complete across all 7 repos (2026-07-17 → 2026-07-20)

Following on from §10, every module directory in every repo in this workspace now has its own
`module.spec.md` — a workspace-wide gap-closing effort spanning four sessions. **101 new module specs were
authored** on top of the pre-existing ones, bringing every repo to full coverage:

| Repo | Module specs | New this pass | Index |
|---|---|---|---|
| `sc-saas-admin` | 68 | 38 | [admin-module-specs-index.md](specs/admin-module-specs-index.md) |
| `sc-saas-backend` | 61 (58 `src/modules` + 3 real bounded contexts in `src/core`) | 3 | [backend-module-specs-index.md](specs/backend-module-specs-index.md) |
| `sc-saas-frontend` | 82 | 52 | [frontend-module-specs-index.md](specs/frontend-module-specs-index.md) |
| `sanchiconnect-saas-tenants` | 8 | 2 | [tenants-module-specs-index.md](specs/tenants-module-specs-index.md) |
| `sanchiconnect-saas-tenants-admin` | 10 (9 modules + root/foundation spec) | 6 | [tenants-admin-module-specs-index.md](specs/tenants-admin-module-specs-index.md) *(new index — this repo had none before)* |
| `sc-saas-3rdparty-webservices` | 7 | 0 (already complete; index refreshed, several stale route paths corrected) | [3rdparty-webservices-module-specs-index.md](specs/3rdparty-webservices-module-specs-index.md) |
| `ai-startups-analyzer` | 1 consolidated spec + `scoring_engine_spec.md` (FastAPI's structure doesn't map to one-spec-per-directory) | 0 (index refreshed; found the scoring-engine spec's rounding-precision text hadn't caught up to a 2026-07-17 code fix) | [ai-analyzer-module-specs-index.md](specs/ai-analyzer-module-specs-index.md) |

**How to use these indexes:** each is the fastest way to find a module's spec, its owned/consumed
contracts, and any known bugs/security findings without grepping the repo directly — start here before
reading a module's code cold. Every index was regenerated (or, for `sanchiconnect-saas-tenants-admin`,
created for the first time) by re-deriving its contents directly from the actual `module.spec.md` files and
directory listings on disk, not by trusting the previous index's claims — each repo's coverage was also
independently re-verified with a fresh directory scan as part of this pass (all showed 0 gaps).

**Naming-collision pattern found repeatedly across repos**: several directories in `sc-saas-admin`,
`sc-saas-frontend`, and the workspace generally contain *only* a `module.spec.md` and no code — older,
broader "combined" docs (e.g. `sc-saas-admin/modules/integrations/`, `content-management/`,
`growth-metrics/`, `finance-memberships/`, `partners-recruitment/`; `sc-saas-frontend/modules/utilities/`
and ~13 other umbrella specs) that predate this workspace's one-spec-per-directory convention and document
several real code directories jointly. These are kept as supplementary/legacy references, cross-linked from
the newer per-directory specs that now supersede them for anything code-specific — not deleted, since they
sometimes contain cross-cutting context (e.g. shared DB-write patterns) the narrower specs don't repeat.

**New security/correctness findings surfaced by this final sweep are folded into §6 above** rather than
repeated here — see the bullets covering `sanchiconnect-saas-tenants-admin`'s unauthenticated `csv`
export/import (the single worst finding across the whole multi-session effort), the repeated
`filemanager`/`aws` unauthenticated-endpoint pattern across both PHP admin repos, `sc-saas-backend`'s
unauthenticated WebSocket gateway, and `sc-saas-frontend`'s `admin-actions` impersonation-endpoint risk.

---

## Change Log

- 2026-07-20 | Added §11 — closed the last remaining module-spec gaps workspace-wide (101 new
  `module.spec.md` files across 4 sessions: 38 in `sc-saas-admin`, 3 in `sc-saas-backend`, 52 in
  `sc-saas-frontend`, 2 in `sanchiconnect-saas-tenants`, 6 in `sanchiconnect-saas-tenants-admin`), and
  regenerated (or, for `sanchiconnect-saas-tenants-admin`, created for the first time) all 7 repos'
  module-specs-index files, independently re-verifying 0-gap coverage in every repo along the way. Added 6
  new §6 security bullets from findings surfaced during this final sweep, the most severe being
  `sanchiconnect-saas-tenants-admin`'s completely unauthenticated `csv/export.php`/`import.php` (full DB
  dump/insert on the shared platform DB, tracked as Linear SAN-42, still unfixed) — arguably the single
  worst finding across this entire multi-session audit effort.
- 2026-07-17 | Added §10 and new §6 security bullets — synced this root synthesis with the module-level
  (`module.spec.md`, all 139 files across 7 repos) re-verification and adversarial re-verification passes
  done in the individual product repos (committed to their own `ai_native_setup` branches). Most
  consequential: two separate repos (`sc-saas-admin`, `sanchiconnect-saas-tenants-admin`) each have an
  ungated `sql_query` arbitrary-SQL-execution action; `facility_management`'s authenticated routes aren't
  actually feature-gated; `ecosystem-facilities` silently can't do External Hub lookups; a real
  `shortIo` accept/reject URL swap bug; and the methodology finding that an adversarial re-check of modules
  previously marked "verified accurate" found real gaps in 16 of 18 (89%) sampled — meaning most of the
  ~125 originally "no changes" modules workspace-wide are still unverified beyond a demonstrated-unreliable
  single pass.
- 2026-07-16 (later same day) | Added §9 — enumerated the SanchiPowerpitch sibling workspace's four repos by
  name (previously only `power-pitch-sanchiconnect-api` was named anywhere in this workspace's docs), confirmed
  its location on disk, and corrected a wrong claim from this workspace's repo-map reference doc (2026-07-15)
  that `power-pitch-sanchiconnect-admin` had no meaningful commits — it has 12, dated 2022-2023, just no
  activity since then until a docs-only commit in 2026-06.
- 2026-07-16 (later same day) | Full re-verification pass across all 7 repos' own `knowledge.md`/`design.md`/
  `database.md`/`api.md` (28 files), not just this workspace-level synthesis — one dedicated agent per repo,
  each re-checking every specific claim against current code and fixing confirmed drift directly. Net effect:
  dozens of precise counts/line-citations corrected (mostly drift from same-day commits shifting line numbers,
  not conceptual errors), and two genuinely new findings worth surfacing at this level: (1) `sc-saas-admin`
  shipped a **Bulk Email Attachments** feature (2026-07-15, after the original 2026-07-14 pass) with S3
  upload/inline-vs-link delivery but **no malware-scanning provider wired up** — every attachment is
  permanently `PENDING` scan status and sends proceed anyway, an accepted product decision, not a bug, but
  worth knowing platform-wide; (2) `sc-saas-3rdparty-webservices` actually exposes **34 routes, not 20** as
  every doc previously stated, and has a real, confirmed config-wiring bug — `OTP_EXPIRATION_TIME_IN_MINUTES`
  is required at boot (Joi) but `configuration.ts` never maps it to the key `AppConfigService.otpExpirationTime`
  reads, so the env var silently has zero effect and `sms.service.ts` always uses its hardcoded 10-minute
  fallback. See each repo's own docs for full detail; not deep-diving either into this synthesis since both are
  single-repo findings without a second-repo consumer.
- 2026-07-16 | Independent re-verification pass: spot-checked 6 of this document's most load-bearing claims
  directly against current code (not re-trusted from the 2026-07-14 synthesis alone) — all 6 confirmed exactly
  as stated: `sc-saas-admin`'s two direct `sc-saas-3rdparty-webservices` call sites (§3.1), the
  `easebuzz_callback.php` direct call into `sanchiconnect-saas-tenants` (§3.1), `sanchiconnect-saas-tenants-admin`'s
  two direct `sc-saas-backend` calls (§3.2), the bundled Adminer console with the plaintext DB-password link
  (§6), the 5-of-6 AJAX-handlers-skip-login finding (§6), and the hardcoded live-looking API keys in
  `global.repository.ts` (§6). **One correction**: the ai-credits Easebuzz webhooks are gated by
  `InternalApiKeyGuard` *and* HMAC signature verification — not unauthenticated as `sanchiconnect-saas-tenants`'s
  own `CLAUDE.md` stated until this pass (now fixed there). Also fixed 5 other confirmed-stale numbers this
  pass surfaced across per-repo `CLAUDE.md` files that this July 14 synthesis had already flagged internally
  but which hadn't propagated to the actual `CLAUDE.md` files themselves: `sc-saas-backend` module count
  (51→58), `sc-saas-frontend` NgRx store count (~38→34), `sc-saas-3rdparty-webservices`'s Swagger-gate
  condition and "called only by backend" framing, and `sanchiconnect-saas-tenants-admin`'s standalone/JWT/SendGrid
  claims (§(a) above already refuted these on 2026-07-14; the `CLAUDE.md` files themselves weren't corrected
  until now). Added `sanchiconnect-saas-tenants-admin`'s new Tenant Data Export feature (built this session,
  see that repo's own `knowledge.md` §h) as a new architectural data point.
- 2026-07-14 | Initial workspace-level synthesis pass. Read all seven repos' `knowledge.md` in full, plus
  spot-checked `design.md` (tenants, frontend — the two `verify_tenant`/`tenant-settings` breakage traces)
  and `database.md`/`api.md` section headers across all seven repos to confirm structure before citing.
  Connected the AI-Credits three-mutator finding across `sanchiconnect-saas-tenants`, `sc-saas-admin`, and
  `sanchiconnect-saas-tenants-admin`. Connected the three call-graph contradictions
  (`sc-saas-3rdparty-webservices`, `sanchiconnect-saas-tenants-admin`, `sc-saas-admin`'s undocumented
  fourth-repo call) into one corrected call-graph table. Stated the four-way tenancy-model split as a
  platform architectural fact. Consolidated six independently-surfaced security findings. Confirmed the
  `synchronize: true`/no-migrations pattern is present in both NestJS repos, not a one-off. Confirmed no
  repo has Docker/CI/CD/IaC. Checked the workspace `CLAUDE.md`'s blast-radius graph against all seven
  repos' findings — most of it holds; three specific edges are stale or missing. Existing workspace
  `README.md` was read and found broadly consistent with these repos' own `CLAUDE.md` framing (still
  useful as an onboarding doc) but is stale in one respect: it lists only five/six repos and predates the
  addition of `sanchiconnect-saas-tenants-admin` as a seventh repo — flagged for the maintainer's attention
  in this pass's final report rather than rewritten here, per this task's instruction to be conservative
  with `README.md`.
